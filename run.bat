@echo off
chcp 65001 > nul
echo ===================================================================
echo   ระบบร้านขาย E-Book ออนไลน์ (Mini Project Database)
echo ===================================================================
echo.
echo กำลังตรวจสอบฐานข้อมูลและเตรียมระบบ...

if not exist ebook_store.db (
    echo กำลังสร้างฐานข้อมูลและข้อมูลตัวอย่าง (30+ คำสั่งซื้อ)...
    python database/init_db.py
    python create_sample_files.py
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
pause
