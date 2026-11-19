@echo off
title Harvey Local
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1"
if errorlevel 1 (
  echo.
  echo Harvey could not start. Read the error above before closing this window.
  pause
)
