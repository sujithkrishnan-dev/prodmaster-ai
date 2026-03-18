@echo off
:: ProdMaster AI -- SessionStart hook runner (Windows)
:: Invokes run-hook.ps1 via PowerShell for robust string handling.
:: Usage: run-hook.cmd session-start

setlocal
set "SCRIPT_DIR=%~dp0"

powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass ^
  -File "%SCRIPT_DIR%run-hook.ps1" session-start

exit /b %ERRORLEVEL%
