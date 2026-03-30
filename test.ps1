# Unified Test Script for Architecture Intelligence

$ProjectRoot = Get-Location
$BackendDir = Join-Path $ProjectRoot "backend"
$FrontendDir = Join-Path $ProjectRoot "frontend"
$PythonExe = Join-Path $BackendDir "venv\Scripts\python.exe"

Write-Host "`n=== [1/3] Running Backend & AI Tests ===" -ForegroundColor Cyan
if (Test-Path $PythonExe) {
    & $PythonExe -m pytest backend/tests/
} else {
    Write-Host "ERROR: Backend venv not found! Run setup first." -ForegroundColor Red
}

Write-Host "`n=== [2/3] Running Frontend Tests ===" -ForegroundColor Cyan
Set-Location $FrontendDir
if (Test-Path "node_modules") {
    npm run test -- --run 
} else {
    Write-Host "ERROR: Frontend node_modules not found!" -ForegroundColor Red
}

Write-Host "`n=== [3/3] Testing Complete ===" -ForegroundColor Green
Set-Location $ProjectRoot
