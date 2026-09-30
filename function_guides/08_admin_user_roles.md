# ฟังก์ชันที่ 8: การจัดการผู้ใช้และการกำหนดบทบาท (Admin User & Role Management)
**โครงงาน:** Mini Project Database ร้านขาย E-Book  
**หมวดหมู่:** ระบบบริหารจัดการร้าน (ผู้ดูแลร้าน) ตามข้อกำหนดหัวข้อ 3  

---

## 1. วัตถุประสงค์ของฟังก์ชัน
เพื่อให้ผู้ดูแลระบบสามารถตรวจสอบรายชื่อสมาชิกทั้งหมดในระบบ, ดูสถิติการสั่งซื้อและยอดเงินที่ใช้จ่ายสะสมของลูกค้าแต่ละราย, และสามารถปรับเปลี่ยนบทบาทสิทธิ์ (Roles) ระหว่าง **"ลูกค้าทั่วไป (Customer)"** และ **"ผู้ดูแลระบบ (Admin)"** ได้ตามข้อกำหนดของโครงงาน

---

## 2. หน้าจอและเส้นทางที่เกี่ยวข้อง (Routes & Templates)
* **`/admin/users`** (`templates/admin/users.html`): หน้าแสดงรายชื่อสมาชิก สถิติยอดซื้อสะสม และปุ่มเปลี่ยนบทบาท
* **`/admin/users/role/<int:user_id>`** [POST]: เส้นทางประมวลผลการปรับเปลี่ยนบทบาทสมาชิก

---

## 3. ลำดับขั้นตอนการทำงาน (Step-by-Step Flow)

### 3.1 การตรวจสอบข้อมูลสมาชิก (Inspect Users)
1. แอดมินคลิกเมนู **"จัดการผู้ใช้งาน"** ในแถบเมนูหลังบ้าน
2. ระบบดึงรายชื่อสมาชิกทั้งหมดจากตาราง `users` มาแสดง โดยคำนวณสถิติย่อย:
   * จำนวนคำสั่งซื้อทั้งหมดที่ผู้ใช้เคยสั่ง
   * ยอดเงินรวมที่สั่งซื้อสำเร็จ (`status = 'CONFIRMED'`)
3. แสดงป้ายกำกับบทบาทปัจจุบัน:
   * ป้ายสีแดง: **ADMIN** (ผู้ดูแลระบบ)
   * ป้ายสีเทา: **CUSTOMER** (ลูกค้าทั่วไป)

### 3.2 การปรับเปลี่ยนบทบาทผู้ใช้ (Change Role)
1. แอดมินคลิกปุ่ม **"ตั้งเป็น Admin"** หรือ **"ปรับเป็น Customer"** ที่แถวของผู้ใช้คนนั้น
2. ระบบมีหน้าต่างยืนยันความปลอดภัย (Confirmation Prompt) ก่อนดำเนินการ
3. **ระบบตรวจสอบความปลอดภัย (Self-Demotion Protection):**
   * ระบบจะตรวจสอบว่า `user_id` นั้นเป็นบัญชีของแอดมินที่กำลังล็อกอินอยู่หรือไม่
   * หากเป็นบัญชีตนเอง ระบบจะปฏิเสธไม่อนุญาตให้ลดสิทธิ์ของตนเอง เพื่อป้องกันปัญหาไม่มีผู้ดูแลระบบหลงเหลือในระบบ
4. หากเป็นบัญชีอื่น ระบบสั่งคำสั่ง SQL `UPDATE users SET role_id = ? WHERE user_id = ?`
5. ผู้ใช้คนนั้นจะได้รับสิทธิ์ใหม่ทันทีในการเข้าสู่ระบบครั้งถัดไป

---

## 4. ตารางฐานข้อมูลที่เกี่ยวข้อง (Database Tables)

| ชื่อตาราง | บทบาทในฟังก์ชันนี้ | ฟิลด์สำคัญที่เกี่ยวข้อง |
|---|---|---|
| **`users`** | บันทึกข้อมูลสมาชิกและรหัสบทบาท | `user_id`, `role_id`, `username`, `email`, `full_name`, `phone`, `created_at` |
| **`roles`** | ตารางนิยามบทบาทสิทธิ์ | `role_id`, `role_name` ('customer', 'admin') |
| **`orders`** | นำมาคำนวณยอดซื้อสะสม | `order_id`, `user_id`, `total_amount`, `status` |

---

## 5. คำสั่ง SQL เบื้องหลังการทำงาน (Underlying SQL)

### ดึงรายชื่อสมาชิกพร้อมคำนวณสถิติคำสั่งซื้อและยอดใช้จ่ายสะสม (Subquery)
```sql
SELECT 
    u.user_id,
    u.username,
    u.full_name,
    u.email,
    u.phone,
    u.role_id,
    u.created_at,
    r.role_name,
    (SELECT COUNT(*) 
     FROM orders o 
     WHERE o.user_id = u.user_id) AS total_orders,
    (SELECT COALESCE(SUM(total_amount), 0) 
     FROM orders o 
     WHERE o.user_id = u.user_id AND o.status = 'CONFIRMED') AS total_spent
FROM users u
JOIN roles r ON u.role_id = r.role_id
ORDER BY u.user_id ASC;
```

### เปลี่ยนบทบาทผู้ใช้งาน
```sql
UPDATE users 
SET role_id = :new_role_id 
WHERE user_id = :user_id;
```

---

## 6. ข้อจำกัดข้อมูลและความปลอดภัย (Constraints & Security)
* **Foreign Key Protection:** `FOREIGN KEY (role_id) REFERENCES roles(role_id) ON UPDATE CASCADE ON DELETE RESTRICT` ป้องกันการกำหนด `role_id` ที่ไม่มีอยู่จริง
* **Self-Demotion Guard:** ป้องกันไม่ให้แอดมินคนปัจจุบันกดลดสิทธิ์บัญชีตนเองจนไม่สามารถเข้าหลังบ้านได้
* **Least Privilege Principle:** บัญชีที่สมัครใหม่ผ่านหน้าร้านจะถูกกำหนดให้เป็น `customer` (role_id = 1) เสมอโดย Default
