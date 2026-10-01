@echo off
chcp 65001 > nul
echo ===================================================================
echo   ร้านขายหนังสือและอีบุ๊กออนไลน์ Lampara Books
echo   โครงงานพัฒนาระบบฐานข้อมูล รหัสวิชา 31-407-102-301
echo ===================================================================
echo.
echo กำลังตรวจสอบฐานข้อมูลและเตรียมระบบ...

if exist ebook_store.db goto db_ready
echo กำลังสร้างฐานข้อมูลและข้อมูลตัวอย่าง 36 คำสั่งซื้อ...
python database/init_db.py
python create_sample_files.py
:db_ready

rem ตรวจสอบและติดตั้ง Flask อัตโนมัติหากยังไม่มี
python -c "import flask" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo กำลังติดตั้งไลบรารีที่จำเป็น (Flask)...
    python -m pip install -r requirements.txt
)

echo.
echo ===================================================================
echo   ระบบพร้อมทำงาน! เปิดเบราว์เซอร์แล้วไปที่:
echo   - หน้าร้านค้า (Storefront): http://127.0.0.1:5000/
echo   - จัดการหลังบ้าน (Admin):  http://127.0.0.1:5000/admin
echo.
echo   บัญชีทดสอบสำหรับอาจารย์ผู้ตรวจ:
echo   - บัญชี Admin:    admin     / admin123
echo   - บัญชี Customer: customer1 / user123
echo ===================================================================
echo.
python app.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [แจ้งเตือน] ไม่สามารถรัน Python ได้ กรุณาตรวจสอบว่าได้ติดตั้ง Python และเพิ่มใน PATH แล้ว
)
pause