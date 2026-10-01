# คู่มือการทำงานฟังก์ชันที่ 10: เครื่องมือรัน SQL ดึงข้อมูลจากตาราง (SQL Console)
**โครงงาน:** Mini Project Database ร้านขาย E-Book ออนไลน์  
**รายวิชา:** Database Mini Project  

---

## 1. วัตถุประสงค์และการทำงานของฟังก์ชัน (Objective & Overview)
ฟังก์ชันนี้ถูกพัฒนาขึ้นสำหรับ **ผู้ดูแลระบบ (Admin)** และ **อาจารย์ผู้ตรวจประเมิน** เพื่อให้สามารถทดสอบสืบค้น ดึงข้อมูลจากตาราง หรือวิเคราะห์ข้อมูลในฐานข้อมูลเชิงสัมพันธ์ SQLite3 (`ebook_store.db`) ได้โดยตรงผ่านหน้าเว็บ โดยไม่จำเป็นต้องเปิดโปรแกรมภายนอกอย่าง DB Browser for SQLite

### จุดเด่นของระบบ SQL Console:
1. **Interactive SQL Editor:** กล่องเขียนคำสั่ง SQL พร้อมไฮไลต์รูปแบบและคีย์ลัด <kbd>Ctrl</kbd> + <kbd>Enter</kbd> เพื่อรันคำสั่งได้ทันที
2. **Table & Schema Explorer:** แสดงรายชื่อตารางครบทั้ง 11 ตาราง พร้อมจำนวนแถวข้อมูลจริง (Row Count) และสามารถคลิกดูคอลัมน์ ชนิดข้อมูล (Data Type), คีย์หลัก (PK) และ NOT NULL ได้ทันที
3. **Preset Queries:** มีปุ่มคลิกเดียวเพื่อโหลดตัวอย่างคำสั่ง SQL ยอดนิยม เช่น ค้นหาหนังสือพร้อมผู้แต่งและหมวดหมู่, คำสั่งซื้อพร้อมสลิป, ยอดขายแยกตามหมวดหมู่, หรือยอดซื้อสะสมของลูกค้า
4. **Dynamic Result Table:** แสดงตารางผลลัพธ์แบบไดนามิกตามคอลัมน์ที่ SELECT ออกมา พร้อมตัวกรองค้นหาแบบเรียลไทม์ (Live Search) และการพรีวิวรูปสลิป
5. **CSV Export:** ส่งออกผลลัพธ์จากการรันคำสั่ง SQL ออกมาเป็นไฟล์ `.csv` รองรับภาษาไทยใน Microsoft Excel ได้อย่างถูกต้องสมบูรณ์

---

## 2. หน้าจอและเส้นทางที่เกี่ยวข้อง (Routes & UI)

| รายการ | เส้นทาง URL (Route) | เมธอด (Method) | สิทธิ์การเข้าถึง | แม่แบบหน้าจอ (Template) |
|---|---|:---:|:---:|---|
| หน้ารัน SQL Console | `/admin/sql` | `GET` / `POST` | Admin เท่านั้น | `templates/admin/sql_runner.html` |
| ส่งออกผลลัพธ์เป็น CSV | `/admin/sql/export` | `POST` | Admin เท่านั้น | ดาวน์โหลดไฟล์ CSV โดยตรง |

---

## 3. ตัวอย่างคำสั่ง SQL สำหรับดึงข้อมูลและทดสอบ

### ตัวอย่างที่ 1: ดึงรายชื่อหนังสือพร้อมผู้แต่งและหมวดหมู่ (Multi-table JOIN)
```sql
SELECT b.ebook_id, b.title, c.category_name, a.author_name, b.price, b.is_active
FROM ebooks b
JOIN authors a ON b.author_id = a.author_id
JOIN categories c ON b.category_id = c.category_id
ORDER BY b.ebook_id ASC;
```

### ตัวอย่างที่ 2: ดึงข้อมูลคำสั่งซื้อ ลูกค้า และหลักฐานการชำระเงิน
```sql
SELECT o.order_id, o.order_number, u.username, u.full_name, o.total_amount, 
       o.status, p.payment_method, p.payment_status, p.slip_image, o.order_date
FROM orders o
JOIN users u ON o.user_id = u.user_id
LEFT JOIN payments p ON o.order_id = p.order_id
ORDER BY o.order_id DESC LIMIT 20;
```

### ตัวอย่างที่ 3: สรุปยอดขายแยกตามหมวดหมู่ (Aggregate & GROUP BY)
```sql
SELECT c.category_name, 
       COUNT(DISTINCT o.order_id) as total_orders, 
       SUM(oi.quantity) as items_sold, 
       ROUND(SUM(oi.subtotal), 2) as category_revenue
FROM categories c
JOIN ebooks b ON c.category_id = b.category_id
JOIN order_items oi ON b.ebook_id = oi.ebook_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status = 'CONFIRMED'
GROUP BY c.category_id, c.category_name
ORDER BY category_revenue DESC;
```

### ตัวอย่างที่ 4: ตรวจสอบข้อมูลสิทธิ์ดาวน์โหลดและรหัส Token
```sql
SELECT dl.download_id, u.username, b.title, dl.download_token, 
       dl.download_count, dl.is_active
FROM download_links dl
JOIN users u ON dl.user_id = u.user_id
JOIN ebooks b ON dl.ebook_id = b.ebook_id
ORDER BY dl.download_id DESC LIMIT 20;
```
