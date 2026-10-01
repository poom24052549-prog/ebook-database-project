@echo off
title Quick SQL Runner
python run_sql.py
if %ERRORLEVEL% NEQ 0 (
    "C:\Users\uuuu\.local\bin\python.exe" run_sql.py
)
pause
