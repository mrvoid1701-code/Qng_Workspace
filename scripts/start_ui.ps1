param(
    [switch]$Lan,
    [int]$Port = 8765
)

$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root

if ($Port -lt 1 -or $Port -gt 65535) {
    throw "Invalid -Port '$Port'. Use a value between 1 and 65535."
}

$hostBind = if ($Lan) { "0.0.0.0" } else { "127.0.0.1" }
$env:QNG_UI_HOST = $hostBind
$env:QNG_UI_PORT = "$Port"

Write-Host "Starting QNG UI on ${hostBind}:$Port"
if ($Lan) {
    Write-Host "LAN mode enabled. Open from phone using your PC local IP and this port."
}

if (Test-Path -LiteralPath ".venv\Scripts\python.exe") {
    & ".\.venv\Scripts\python.exe" ".\scripts\workspace_ui.py"
} else {
    python ".\scripts\workspace_ui.py"
}
