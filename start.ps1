# PreBurn - Stubble Burning Predictive Warning System Launcher
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  PreBurn - Stubble Burning Predictive Warning System" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/2] Launching PreBurn Backend on http://127.0.0.1:8000..." -ForegroundColor Green
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; .\venv\Scripts\uvicorn.exe app.main:app --reload --port 8000"

Start-Sleep -Seconds 2

Write-Host "[2/2] Launching PreBurn Frontend on http://127.0.0.1:3000..." -ForegroundColor Green
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; python -m http.server 3000"

Start-Sleep -Seconds 1

Write-Host "Opening PreBurn Dashboard in browser..." -ForegroundColor Yellow
Start-Process "http://127.0.0.1:3000/index.html"

Write-Host ""
Write-Host "PreBurn is online!" -ForegroundColor Cyan
Write-Host "Dashboard: http://127.0.0.1:3000/index.html" -ForegroundColor White
Write-Host "Backend Swagger UI: http://127.0.0.1:8000/docs" -ForegroundColor White
