import os
import sys
import sqlite3

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stdin.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'ebook_store.db')

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    if not os.path.exists(DB_PATH):
        print(f"Error: ไม่พบไฟล์ฐานข้อมูลที่ {DB_PATH}")
        input("กด Enter เพื่อออก...")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    while True:
        clear_screen()
        print("=" * 65)
        print("  📚 เครื่องมือแก้ไขข้อมูลฐานข้อมูลด่วน (Quick DB Editor)")
        print("=" * 65)
        print("  [1] แก้ไขราคา E-Book (Edit Book Price)")
        print("  [2] แก้ไขชื่อ E-Book (Edit Book Title)")
        print("  [3] ดูรายการหนังสือและราคาทั้งหมด (View All Books)")
        print("  [4] ปรับสถานะคำสั่งซื้อ (Update Order Status)")
        print("  [5] รันคำสั่ง SQL อิสระ (Custom SQL)")
        print("  [0] ออกจากโปรแกรม (Exit)")
        print("=" * 65)
        
        choice = input("กรุณาเลือกเมนู (0-5): ").strip()
        
        if choice == '0':
            print("ปิดโปรแกรมเรียบร้อย")
            break
            
        elif choice == '1':
            clear_screen()
            print("--- 📚 รายการ E-Book ทั้งหมด ---")
            cursor.execute("SELECT ebook_id, title, price FROM ebooks ORDER BY ebook_id ASC")
            books = cursor.fetchall()
            for b in books:
                print(f"  ID [{b[0]:2d}] : {b[1][:38]:<40} | ราคาปัจจุบัน: {b[2]:.2f} บาท")
            print("-" * 65)
            
            book_id = input("ใส่ ID หนังสือที่ต้องการแก้ไข (หรือกด Enter เพื่อยกเลิก): ").strip()
            if not book_id:
                continue
            
            new_price = input("ใส่ราคาใหม่ (บาท): ").strip()
            if not new_price:
                continue
                
            try:
                price_val = float(new_price)
                cursor.execute("UPDATE ebooks SET price = ? WHERE ebook_id = ?", (price_val, int(book_id)))
                conn.commit()
                print("\n✅ อัปเดตราคาสำเร็จเรียบร้อย!")
                print("👉 สลับไปที่หน้าเว็บแล้วกด F5 ข้อมูลจะเปลี่ยนทันทีครับ")
            except Exception as e:
                print(f"\n❌ เกิดข้อผิดพลาด: {e}")
            input("\nกด Enter เพื่อกลับสู่เมนูหลัก...")

        elif choice == '2':
            clear_screen()
            cursor.execute("SELECT ebook_id, title FROM ebooks ORDER BY ebook_id ASC")
            for b in cursor.fetchall():
                print(f"  ID [{b[0]:2d}] : {b[1]}")
            print("-" * 65)
            book_id = input("ใส่ ID หนังสือที่ต้องการแก้ไข (หรือ Enter เพื่อยกเลิก): ").strip()
            if not book_id:
                continue
            new_title = input("ใส่ชื่อหนังสือใหม่: ").strip()
            if not new_title:
                continue
            try:
                cursor.execute("UPDATE ebooks SET title = ? WHERE ebook_id = ?", (new_title, int(book_id)))
                conn.commit()
                print("\n✅ อัปเดตชื่อหนังสือสำเร็จเรียบร้อย!")
            except Exception as e:
                print(f"\n❌ เกิดข้อผิดพลาด: {e}")
            input("\nกด Enter เพื่อกลับสู่เมนูหลัก...")

        elif choice == '3':
            clear_screen()
            print("--- 📚 รายการ E-Book และราคาทั้งหมดในฐานข้อมูล ---")
            cursor.execute("""
                SELECT b.ebook_id, b.title, c.category_name, b.price, b.is_active 
                FROM ebooks b 
                JOIN categories c ON b.category_id = c.category_id 
                ORDER BY b.ebook_id ASC
            """)
            for row in cursor.fetchall():
                status = "เปิดขาย" if row[4] == 1 else "ปิดขาย"
                print(f"[{row[0]:2d}] {row[1][:30]:<32} | หมวด: {row[2][:15]:<16} | ราคา: {row[3]:6.2f} บ. | {status}")
            print("-" * 65)
            input("\nกด Enter เพื่อกลับสู่เมนูหลัก...")

        elif choice == '4':
            clear_screen()
            print("--- 🛒 คำสั่งซื้อล่าสุด 10 รายการ ---")
            cursor.execute("SELECT order_id, order_number, total_amount, status FROM orders ORDER BY order_id DESC LIMIT 10")
            for o in cursor.fetchall():
                print(f"  Order ID [{o[0]:2d}] : {o[1]} | ยอดรวม: {o[2]:.2f} บ. | สถานะ: {o[3]}")
            print("-" * 65)
            order_id = input("ใส่ Order ID ที่ต้องการเปลี่ยนสถานะ (หรือ Enter เพื่อยกเลิก): ").strip()
            if not order_id:
                continue
            print("สถานะที่รองรับ: PENDING_PAYMENT, PAYMENT_SUBMITTED, CONFIRMED, CANCELLED")
            new_status = input("ใส่สถานะใหม่: ").strip().upper()
            if not new_status:
                continue
            try:
                cursor.execute("UPDATE orders SET status = ? WHERE order_id = ?", (new_status, int(order_id)))
                conn.commit()
                print("\n✅ อัปเดตสถานะคำสั่งซื้อสำเร็จเรียบร้อย!")
            except Exception as e:
                print(f"\n❌ เกิดข้อผิดพลาด: {e}")
            input("\nกด Enter เพื่อกลับสู่เมนูหลัก...")

        elif choice == '5':
            clear_screen()
            print("--- 💻 รันคำสั่ง SQL อิสระ ---")
            print("ตัวอย่าง: UPDATE ebooks SET price = 199 WHERE ebook_id = 1;")
            sql = input("\nพิมพ์คำสั่ง SQL: ").strip()
            if not sql:
                continue
            try:
                cursor.execute(sql)
                if sql.strip().upper().startswith(("SELECT", "PRAGMA")):
                    rows = cursor.fetchall()
                    for r in rows:
                        print(r)
                else:
                    conn.commit()
                    print(f"\n✅ ดำเนินการสำเร็จ! (มีผลต่อ {cursor.rowcount} แถว)")
            except Exception as e:
                print(f"\n❌ เกิดข้อผิดพลาดใน SQL: {e}")
            input("\nกด Enter เพื่อกลับสู่เมนูหลัก...")

    conn.close()

if __name__ == '__main__':
    main()
