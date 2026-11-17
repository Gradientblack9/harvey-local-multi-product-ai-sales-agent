param([int]$Port=8000)
$ErrorActionPreference='Stop'
Set-Location -LiteralPath $PSScriptRoot
$env:PYTHONUTF8='1'
if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) { throw 'Run .\setup.ps1 first.' }
& "$PSScriptRoot\start-ollama.ps1"
Write-Host "Harvey Local: http://127.0.0.1:$Port (Ctrl+C stops the dashboard)"
& '.\.venv\Scripts\python.exe' -m local_sales.cli --port $Port
