@echo off
cd /d "%~dp0"
powershell.exe -NoProfile -File "%~dp0Recovery.ps1"
pause
