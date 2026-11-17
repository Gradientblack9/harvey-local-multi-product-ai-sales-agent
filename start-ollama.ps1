$ErrorActionPreference='Stop'
$env:OLLAMA_HOST='127.0.0.1:11434'
$env:OLLAMA_NO_CLOUD='1'
$env:OLLAMA_MODELS=Join-Path $PSScriptRoot 'models\ollama'
$env:OLLAMA_NUM_PARALLEL='1'
$env:OLLAMA_MAX_LOADED_MODELS='1'
$env:OLLAMA_CONTEXT_LENGTH='4096'
$env:OLLAMA_FLASH_ATTENTION='1'
$runtimeExe=Join-Path $PSScriptRoot '.runtime\ollama.exe'
$logDir=Join-Path $PSScriptRoot '.runtime'
if (-not (Test-Path -LiteralPath $runtimeExe)) { throw 'Run setup.ps1 first to install the local runtime.' }
$listening=$false
try { $null=Invoke-RestMethod 'http://127.0.0.1:11434/api/tags' -TimeoutSec 3; $listening=$true } catch {}
if (-not $listening) {
    $process=Start-Process -FilePath $runtimeExe -ArgumentList 'serve' -WorkingDirectory $logDir -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logDir 'ollama-stdout.log') -RedirectStandardError (Join-Path $logDir 'ollama-stderr.log') -PassThru
    Set-Content -LiteralPath (Join-Path $logDir 'ollama.pid') -Value $process.Id
    for ($i=0;$i -lt 30;$i++) {
        try { $null=Invoke-RestMethod 'http://127.0.0.1:11434/api/tags' -TimeoutSec 2; $listening=$true;break } catch { Start-Sleep -Milliseconds 500 }
    }
    if (-not $listening) { throw 'Ollama failed to start. Inspect .runtime\ollama-stderr.log.' }
} else {
    Write-Host 'Using the existing local Ollama service. Ensure it was started with OLLAMA_NO_CLOUD=1.'
}
