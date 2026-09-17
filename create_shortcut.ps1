$WshShell = New-Object -ComObject WScript.Shell

$workingDir = $PSScriptRoot
if (-not $workingDir) {
    $workingDir = (Get-Location).Path
}

# Locate pythonw.exe
$pythonw = Get-Command pythonw -ErrorAction SilentlyContinue
if ($pythonw) {
    $pythonwPath = $pythonw.Source
} elseif (Test-Path "$env:LOCALAPPDATA\Python\pythoncore-3.14-64\pythonw.exe") {
    $pythonwPath = "$env:LOCALAPPDATA\Python\pythoncore-3.14-64\pythonw.exe"
} else {
    $pythonwPath = "pyw.exe"
}

$scriptPath = Join-Path $workingDir "main.py"
$iconPath = Join-Path $workingDir "app.ico"

# 1. Desktop Shortcut
$desktopPath = [Environment]::GetFolderPath("Desktop")
$destDesktop = Join-Path $desktopPath "Celestial Whisper.lnk"
$shortcutDesktop = $WshShell.CreateShortcut($destDesktop)
$shortcutDesktop.TargetPath = $pythonwPath
$shortcutDesktop.Arguments = "`"$scriptPath`""
$shortcutDesktop.WorkingDirectory = $workingDir
if (Test-Path $iconPath) {
    $shortcutDesktop.IconLocation = "$iconPath,0"
}
$shortcutDesktop.Description = "Spotify Floating Lyrics Overlay"
$shortcutDesktop.Save()
Write-Host "Created Desktop Shortcut: $destDesktop"

# 2. Start Menu Shortcut
$programsPath = [Environment]::GetFolderPath("Programs")
$destStart = Join-Path $programsPath "Celestial Whisper.lnk"
$shortcutStart = $WshShell.CreateShortcut($destStart)
$shortcutStart.TargetPath = $pythonwPath
$shortcutStart.Arguments = "`"$scriptPath`""
$shortcutStart.WorkingDirectory = $workingDir
if (Test-Path $iconPath) {
    $shortcutStart.IconLocation = "$iconPath,0"
}
$shortcutStart.Description = "Spotify Floating Lyrics Overlay"
$shortcutStart.Save()
Write-Host "Created Start Menu Shortcut: $destStart"
