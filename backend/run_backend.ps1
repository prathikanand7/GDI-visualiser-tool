Set-Location $PSScriptRoot
$env:PYTHONPATH = "$PSScriptRoot"

if (-not (Test-Path .\.venv)) {
  python -m venv .venv
}

if (-not (Test-Path .\.venv\Scripts\python.exe)) {
  throw "Python virtual environment not found in .venv"
}

& "$PSScriptRoot\.venv\Scripts\python.exe" -m pip install -r "$PSScriptRoot\requirements.txt"
& "$PSScriptRoot\.venv\Scripts\python.exe" -m uvicorn app.main:app --reload --port 8000