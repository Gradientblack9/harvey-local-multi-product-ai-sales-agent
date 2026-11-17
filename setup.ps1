param([ValidateSet('qwen3:0.6b','qwen3:1.7b','qwen3:4b','qwen3:8b')][string]$Model='qwen3:4b')
$ErrorActionPreference='Stop'
Set-Location -LiteralPath $PSScriptRoot
$env:PYTHONUTF8='1'
if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.11+ is required.' }
}
& '.\.venv\Scripts\python.exe' -m pip install --disable-pip-version-check --progress-bar off -r requirements-local.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
if (-not (Test-Path -LiteralPath '.runtime\ollama.exe')) {
    & '.\.venv\Scripts\python.exe' scripts/download_runtime.py
    if ($LASTEXITCODE -ne 0) { throw 'Portable Ollama download failed.' }
}
& '.\.venv\Scripts\python.exe' scripts/download_embeddings.py
if ($LASTEXITCODE -ne 0) { throw 'Embedding model download failed.' }
& "$PSScriptRoot\start-ollama.ps1"
& '.\.runtime\ollama.exe' pull $Model
if ($LASTEXITCODE -ne 0) { throw 'Language model download failed.' }
$env:HARVEY_LOCAL_MODEL=$Model
& '.\.venv\Scripts\python.exe' -c "from local_sales import db;db.init();db.execute('UPDATE settings SET value=? WHERE key=?',('$Model','model'))"
if ($LASTEXITCODE -ne 0) { throw 'Database initialisation failed.' }
Write-Host 'Setup complete. Run .\start.ps1, then open http://127.0.0.1:8000.'
