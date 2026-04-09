Start-Process powershell -ArgumentList '-NoExit', '-File', "$PSScriptRoot\backend\run_backend.ps1"
Start-Process powershell -ArgumentList '-NoExit', '-File', "$PSScriptRoot\frontend\run_frontend.ps1"
