$WshShell = New-Object -ComObject WScript.Shell

$workingDir = $PSScriptRoot
if (-not $workingDir) {
    $workingDir = (Get-Location).Path
}

# Locate real pythonw.exe (strictly excluding 0-byte WindowsApps alias stubs)
$pythonwPath = $null

try {
    $detected = & py -c "import sys, os; p = os.path.join(os.path.dirname(sys.executable), 'pythonw.exe'); print(p if os.path.exists(p) else '')" 2>$null
    if ($detected -and (Test-Path $detected) -and (Get-Item $detected).Length -gt 0) {
        $pythonwPath = $detected.Trim()
    }
} catch {}

if (-not $pythonwPath) {
    $candidates = @(
        "$env:LOCALAPPDATA\Python\pythoncore-3.14-64\pythonw.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python314\pythonw.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python313\pythonw.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\pythonw.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\pythonw.exe",
        "$env:ProgramFiles\Python314\pythonw.exe",
        "$env:ProgramFiles\Python313\pythonw.exe",
        "$env:ProgramFiles\Python312\pythonw.exe",
        "$env:ProgramFiles\Python311\pythonw.exe"
    )
    foreach ($c in $candidates) {
        if ((Test-Path $c) -and (Get-Item $c).Length -gt 0) {
            $pythonwPath = $c
            break
        }
    }
}

if (-not $pythonwPath) {
    $all = Get-Command pythonw -All -ErrorAction SilentlyContinue
    foreach ($cmd in $all) {
        if ($cmd.Source -notlike "*WindowsApps*" -and (Test-Path $cmd.Source) -and (Get-Item $cmd.Source).Length -gt 0) {
            $pythonwPath = $cmd.Source
            break
        }
    }
}

if (-not $pythonwPath) {
    $pythonwPath = "pythonw.exe"
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

# 3. Local Directory Shortcut
$destLocal = Join-Path $workingDir "Celestial Whisper.lnk"
$shortcutLocal = $WshShell.CreateShortcut($destLocal)
$shortcutLocal.TargetPath = $pythonwPath
$shortcutLocal.Arguments = "`"$scriptPath`""
$shortcutLocal.WorkingDirectory = $workingDir
if (Test-Path $iconPath) {
    $shortcutLocal.IconLocation = "$iconPath,0"
}
$shortcutLocal.Description = "Spotify Floating Lyrics Overlay"
$shortcutLocal.Save()
Write-Host "Created Local Folder Shortcut: $destLocal"
