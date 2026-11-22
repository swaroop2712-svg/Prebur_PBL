@echo off
title PreBurn System Launcher
echo ======================================================
echo   PreBurn - Stubble Burning Predictive Warning System
echo ======================================================
echo.
echo [1/2] Starting FastAPI Backend on port 8000...
start "PreBurn Backend" cmd /k "cd /d %~dp0backend && .\venv\Scripts\uvicorn.exe app.main:app --reload --port 8000"

timeout /t 2 /nobreak >nul

echo [2/2] Starting Frontend Web Server on port 3000...
start "PreBurn Frontend" cmd /k "cd /d %~dp0 && python -m http.server 3000"

timeout /t 1 /nobreak >nul

echo Opening PreBurn Dashboard in default browser...
start http://127.0.0.1:3000/index.html

echo.
echo PreBurn is online!
echo Dashboard: http://127.0.0.1:3000/index.html
echo Backend API Docs: http://127.0.0.1:8000/docs
