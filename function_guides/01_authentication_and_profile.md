# ฟังก์ชันที่ 1: ระบบสมาชิก การยืนยันตัวตน และข้อมูลส่วนตัว (Authentication & Profile)
**โครงงาน:** Mini Project Database ร้านขาย E-Book  
**หมวดหมู่:** ส่วนหน้าร้าน (ผู้ใช้งาน) ตามข้อกำหนดหัวข้อ 2.1  

---

## 1. วัตถุประสงค์ของฟังก์ชัน
เพื่อให้ผู้ใช้งานสามารถสมัครสมาชิกใหม่, เข้าสู่ระบบอย่างปลอดภัย, จัดการข้อมูลส่วนตัว และเป็นจุดเริ่มต้นในการระบุตัวตนสำหรับทำคำสั่งซื้อและรับสิทธิ์ดาวน์โหลด E-Book ในระบบ

---

## 2. หน้าจอและเส้นทางที่เกี่ยวข้อง (Routes & Templates)
* **`/register`** (`templates/register.html`): หน้าฟอร์มสำหรับสมัครสมาชิกใหม่
* **`/login`** (`templates/login.html`): หน้าฟอร์มเข้าสู่ระบบ พร้อมปุ่ม Quick Login ทดสอบ
* **`/logout`** : เส้นทางสำหรับเคลียร์ Session และออกจากระบบ
* **`/profile`** (`templates/profile.html`): หน้าดูและแก้ไขข้อมูลส่วนตัว พร้อมสรุปยอดการซื้อ

---

## 3. ลำดับขั้นตอนการทำงาน (Step-by-Step Flow)

### 3.1 ขั้นตอนการสมัครสมาชิก (User Registration)
1. **ผู้ใช้กรอกข้อมูลในฟอร์ม:** ประกอบด้วย ชื่อ-นามสกุล, Username, Email, เบอร์โทรศัพท์, รหัสผ่าน และยืนยันรหัสผ่าน
2. **ระบบตรวจสอบความถูกต้อง (Validation):**
   * ตรวจสอบว่ากรอกข้อมูลครบถ้วนทุกช่องที่มีดอกจัน `*`
   * ตรวจสอบว่ารหัสผ่านและยืนยันรหัสผ่านตรงกัน
   * ตรวจสอบในฐานข้อมูลว่า `username` หรือ `email` เคยมีคนใช้ไปแล้วหรือไม่ (UNIQUE Check)
3. **การประมวลผลความปลอดภัย:**
   * นำรหัสผ่านดิบ (Plaintext Password) ไปทำการเข้ารหัสแบบทางเดียว (Password Hashing) ด้วยอัลกอริทึม Scrypt ผ่านไลบรารี Werkzeug
4. **บันทึกลงฐานข้อมูล:**
   * สั่ง `INSERT` ข้อมูลผู้ใช้ใหม่ลงในตาราง `users` โดยกำหนด `role_id = 1` (ลูกค้าทั่วไป)
   * **สร้างตะกร้าสินค้าอัตโนมัติ:** สั่ง `INSERT` ตะกร้าเปล่าลงในตาราง `carts` ผูกกับ `user_id` ใหม่ทันที (เพื่อพร้อมให้ใช้งานระบบตะกร้า)
5. **ผลลัพธ์:** แสดงข้อความแจ้งเตือนสีเขียวว่า *"สมัครสมาชิกสำเร็จแล้ว! กรุณาเข้าสู่ระบบ"* และ Redirect ไปหน้า Login

### 3.2 ขั้นตอนการเข้าสู่ระบบ (User Login)
1. **ผู้ใช้กรอกข้อมูล:** ป้อน Username (หรือ Email) และรหัสผ่าน
2. **ระบบค้นหาบัญชี:** รันคำสั่ง SQL ค้นหาข้อมูลผู้ใช้และชื่อบทบาท (`role_name`) จากตาราง `users` เชื่อมกับ `roles`
3. **ตรวจสอบรหัสผ่าน:** ใช้ฟังก์ชัน `check_password_hash()` ตรวจสอบว่ารหัสผ่านที่ป้อนเข้ามาตรงกับค่า Hash ในฐานข้อมูลหรือไม่
4. **สร้าง Session:** เมื่อถูกต้อง ระบบจะบันทึกสถานะลงใน Session:
   * `session['user_id']`: รหัสประจำตัวสมาชิก
   * `session['username']`: ชื่อผู้ใช้
   * `session['full_name']`: ชื่อ-นามสกุลจริง
   * `session['role_name']`: บทบาท (`customer` หรือ `admin`)
5. **ผลลัพธ์:** แสดงข้อความต้อนรับ และนำทางไปยังหน้าแรก (หรือหน้า Admin หากเป็นผู้ดูแลระบบ)

### 3.3 ขั้นตอนการแก้ไขข้อมูลส่วนตัว (Profile Update)
1. ผู้ใช้เข้าหน้า `/profile` ระบบจะดึงข้อมูลส่วนตัวและสถิติยอดซื้อมาแสดง
2. ผู้ใช้แก้ไขชื่อ-นามสกุล หรือเบอร์โทรศัพท์ (และสามารถกรอกเปลี่ยนรหัสผ่านใหม่ได้)
3. ระบบสั่ง `UPDATE` ข้อมูลในตาราง `users` และอัปเดต Session ให้เป็นปัจจุบันทันที

---

## 4. ตารางฐานข้อมูลที่เกี่ยวข้อง (Database Tables)

| ชื่อตาราง | บทบาทในฟังก์ชันนี้ | ฟิลด์สำคัญที่เกี่ยวข้อง |
|---|---|---|
| **`roles`** | กำหนดสิทธิ์บทบาท | `role_id`, `role_name` ('customer', 'admin') |
| **`users`** | เก็บข้อมูลบัญชีและรหัสผ่าน Hash | `user_id`, `role_id`, `username`, `email`, `password_hash`, `full_name`, `phone`, `created_at` |
| **`carts`** | ตะกร้าสินค้าประจำตัวสมาชิก | `cart_id`, `user_id` (สัมพันธ์แบบ 1:1 กับ Users) |

---

## 5. คำสั่ง SQL เบื้องหลังการทำงาน (Underlying SQL)

### ตรวจสอบชื่อผู้ใช้หรืออีเมลซ้ำ (ตอนสมัคร)
```sql
SELECT user_id 
FROM users 
WHERE username = ? OR email = ?;
```

### บันทึกสมาชิกใหม่และสร้างตะกร้า
```sql
-- 1. บันทึกผู้ใช้ใหม่
INSERT INTO users (role_id, username, email, password_hash, full_name, phone)
VALUES (1, 'somchai99', 'somchai@email.com', 'scrypt:...', 'นายสมชาย ใจดี', '0812345678');

-- 2. สร้างตะกร้าผูกกับ user_id ล่าสุด
INSERT INTO carts (user_id) 
VALUES (last_insert_rowid());
```

### ค้นหาผู้ใช้ตอนล็อกอินพร้อมบทบาท
```sql
SELECT u.user_id, u.username, u.password_hash, u.full_name, r.role_name 
FROM users u
JOIN roles r ON u.role_id = r.role_id
WHERE u.username = ? OR u.email = ?;
```

### ดึงสรุปประวัติการสั่งซื้อในหน้า Profile
```sql
SELECT 
    COUNT(*) AS total_orders,
    SUM(CASE WHEN status = 'CONFIRMED' THEN 1 ELSE 0 END) AS confirmed_orders,
    COALESCE(SUM(CASE WHEN status = 'CONFIRMED' THEN total_amount ELSE 0 END), 0) AS total_spent
FROM orders 
WHERE user_id = ?;
```

---

## 6. ข้อจำกัดข้อมูลและความปลอดภัย (Constraints & Security)
* **`UNIQUE(username)` & `UNIQUE(email)`:** ป้องกันไม่ให้มีชื่อผู้ใช้หรืออีเมลซ้ำกันในระบบ
* **Password Hashing:** ไม่มีการเก็บรหัสผ่านเป็นตัวอักษรธรรมดา (Plaintext) ในฐานข้อมูล ป้องกันข้อมูลรั่วไหล
* **`CHECK(role_name IN ('customer', 'admin'))`:** บังคับให้บทบาทมีได้เฉพาะที่กำหนดไว้เท่านั้น
