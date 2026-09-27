@echo off
chcp 65001 > nul
echo ===================================================
echo   กำลังปิดการทำงานของเว็บเซิร์ฟเวอร์ (Port 5000)...
echo ===================================================

for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a > nul 2>&1
    echo ปิดโปรเซส PID: %%a เรียบร้อยแล้ว
)

echo.
echo เว็บเซิร์ฟเวอร์ถูกปิดเรียบร้อยแล้ว
timeout /t 2 > nul
