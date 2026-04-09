Start-Process powershell -ArgumentList '-NoExit', '-File', "$PSScriptRoot\apps\api\run_backend.ps1"
Start-Process powershell -ArgumentList '-NoExit', '-File', "$PSScriptRoot\apps\web\run_frontend.ps1"
