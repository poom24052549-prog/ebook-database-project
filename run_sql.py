import sys
import sqlite3

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stdin.reconfigure(encoding='utf-8')
    except Exception:
        pass

def run():
    try:
        with open('update.sql', 'r', encoding='utf-8') as f:
            sql = f.read()
        conn = sqlite3.connect('ebook_store.db')
        conn.executescript(sql)
        conn.commit()
        conn.close()
        print(">>> ดำเนินการรันคำสั่ง SQL และบันทึกเรียบร้อย 100% <<<")
        print("👉 ตอนนี้ข้อมูลในฐานข้อมูลเปลี่ยนแล้ว สลับไปที่หน้าเว็บแล้วกด F5 เพื่อดูผลได้เลยครับ!")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    run()
