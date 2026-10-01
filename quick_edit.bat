@echo off
title Quick DB Editor
python quick_edit.py
if %ERRORLEVEL% NEQ 0 (
    "C:\Users\uuuu\.local\bin\python.exe" quick_edit.py
)
pause
