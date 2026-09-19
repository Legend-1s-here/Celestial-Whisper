[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Add-Type -AssemblyName System.Runtime.WindowsRuntime
$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | ? { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]

Function Await($WinRtTask, $ResultType) {
    $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
    $netTask = $asTask.Invoke($null, @($WinRtTask))
    $netTask.Wait(-1) | Out-Null
    $netTask.Result
}

[Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager, Windows.Media.Control, ContentType = WindowsRuntime] | Out-Null
[Windows.Media.Control.GlobalSystemMediaTransportControlsSessionMediaProperties, Windows.Media.Control, ContentType = WindowsRuntime] | Out-Null

$manager = Await ([Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager]::RequestAsync()) ([Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager])

while ($true) {
    try {
        $sessions = $manager.GetSessions()
        $targetSession = $null
        foreach ($s in $sessions) {
            if ($s.SourceAppUserModelId -like "*Spotify*") {
                $targetSession = $s
                break
            }
        }
        if (-not $targetSession) {
            $targetSession = $manager.GetCurrentSession()
        }

        if ($targetSession) {
            $props = Await ($targetSession.TryGetMediaPropertiesAsync()) ([Windows.Media.Control.GlobalSystemMediaTransportControlsSessionMediaProperties])
            $info = $targetSession.GetPlaybackInfo()
            $status = if ($info) { $info.PlaybackStatus.ToString() } else { "Unknown" }
            $timeline = $targetSession.GetTimelineProperties()

            $currSec = 0.0
            $durSec = 0.0
            if ($timeline) {
                $pos = $timeline.Position.TotalSeconds
                $durSec = [Math]::Max(0.0, $timeline.EndTime.TotalSeconds)
                if ($status -eq "Playing") {
                    $elapsed = ([DateTimeOffset]::UtcNow - $timeline.LastUpdatedTime).TotalSeconds
                    $currSec = [Math]::Max(0.0, [Math]::Min($durSec, $pos + $elapsed))
                } else {
                    $currSec = [Math]::Max(0.0, $pos)
                }
            }

            $obj = [PSCustomObject]@{
                app_id = $targetSession.SourceAppUserModelId
                title = if ($props.Title) { $props.Title } else { "" }
                artist = if ($props.Artist) { $props.Artist } else { "" }
                album = if ($props.AlbumTitle) { $props.AlbumTitle } else { "" }
                status = $status
                position_sec = [Math]::Round($currSec, 2)
                duration_sec = [Math]::Round($durSec, 2)
            }
            $json = $obj | ConvertTo-Json -Compress
            [Console]::WriteLine($json)
        } else {
            [Console]::WriteLine('{"status": "Stopped", "title": "", "artist": "", "position_sec": 0, "duration_sec": 0}')
        }
    } catch {
        [Console]::WriteLine('{"error": "poll_error"}')
        try {
            $manager = Await ([Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager]::RequestAsync()) ([Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager])
        } catch {}
    }
    Start-Sleep -Milliseconds 250
}
