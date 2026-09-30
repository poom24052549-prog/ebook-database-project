# ฟังก์ชันที่ 7: การจัดการคำสั่งซื้อและการตรวจสอบสลิป (Admin Orders & Slip Verification)
**โครงงาน:** Mini Project Database ร้านขาย E-Book  
**หมวดหมู่:** ระบบบริหารจัดการร้าน (ผู้ดูแลร้าน) ตามข้อกำหนดหัวข้อ 3  

---

## 1. วัตถุประสงค์ของฟังก์ชัน
เพื่อให้ผู้ดูแลร้านสามารถติดตามรายการคำสั่งซื้อทั้งหมด, กรองดูเฉพาะรายการที่รอการตรวจสอบ, ดูหลักฐานสลิปการโอนเงินจำลอง, และเปลี่ยนสถานะคำสั่งซื้อเป็น **"ยืนยันแล้ว (CONFIRMED)"**, **"รอตรวจสอบ (PENDING)"**, หรือ **"ยกเลิก (CANCELLED)"** พร้อมทั้งระบบจะทำการสร้างหรือเพิกถอนสิทธิ์ดาวน์โหลดให้อัตโนมัติ

---

## 2. หน้าจอและเส้นทางที่เกี่ยวข้อง (Routes & Templates)
* **`/admin/orders`** (`templates/admin/orders.html`): หน้ารวมคำสั่งซื้อทั้งหมด พร้อมตัวกรองสถานะ และปุ่มลัดเปลี่ยนสถานะ
* **`/admin/orders/<int:order_id>`** (`templates/admin/order_detail.html`): หน้าตรวจสอบรายละเอียดคำสั่งซื้อ ตรวจสอบภาพสลิปขนาดเต็ม และบันทึกหมายเหตุ
* **`/admin/orders/update-status/<int:order_id>`** [POST]: เส้นทางประมวลผลการเปลี่ยนสถานะและจัดการโทเค็นดาวน์โหลด

---

## 3. ลำดับขั้นตอนการทำงาน (Step-by-Step Flow)

### 3.1 การตรวจสอบคำสั่งซื้อใหม่ (Inspect Pending Orders)
1. แอดมินเข้าเมนู "จัดการคำสั่งซื้อ & สลิป"
2. คลิกตัวกรองสีส้ม **"รอตรวจสอบ (PENDING)"** เพื่อดูรายการที่ลูกค้าสั่งซื้อและแนบสลิปเข้ามาใหม่
3. คลิกดูภาพสลิปจำลอง หรือกดเข้าไปดูรายละเอียดเต็ม (`/admin/orders/<id>`)
4. ในหน้ารายละเอียด แอดมินจะเห็น:
   * ข้อมูลลูกค้า (ชื่อ, อีเมล, เบอร์โทรศัพท์)
   * รายการหนังสือที่ลูกค้าสั่งซื้อ และยอดรวมสุทธิ
   * วิธีชำระเงินที่ลูกค้าเลือก (PromptPay QR, Bank, Card)
   * ภาพสลิปหลักฐานการโอนจำลอง
   * หมายเหตุที่ลูกค้าพิมพ์แนบมา

### 3.2 การอนุมัติและเปลี่ยนสถานะเป็น "ยืนยันแล้ว" (Approve to CONFIRMED)
1. เมื่อแอดมินตรวจสอบยอดเงินและสลิปเรียบร้อย ให้เลือกสถานะเป็น **`CONFIRMED`** (ยืนยันแล้ว) และพิมพ์บันทึกข้อความ (เช่น *"ยอดเงินโอนถูกต้อง เรียบร้อย"*) แล้วกดบันทึก
2. **ระบบฐานข้อมูลประมวลผลอัตโนมัติ (Business Logic):**
   * อัปเดต `orders.status = 'CONFIRMED'`
   * อัปเดต `payments.payment_status = 'VERIFIED'`
   * **สร้างสิทธิ์ดาวน์โหลดอัตโนมัติ:** วนลูปอ่านรายการหนังสือใน `order_items` ของคำสั่งซื้อนี้ หากยังไม่เคยมีโทเค็น ระบบจะสุ่มสร้างรหัส UUIDv4 เฉพาะตัว และบันทึกลงในตาราง `download_links` โดยเปิด `is_active = 1`
3. **ผลลัพธ์:** ทันทีที่คำสั่งซื้อกลายเป็น `CONFIRMED` ลูกค้าจะเห็นปุ่มดาวน์โหลดไฟล์ E-Book สีเขียวขึ้นในหน้าจอของตนเองทันที

### 3.3 การปรับเป็น "รอตรวจสอบ" หรือ "ยกเลิกคำสั่งซื้อ" (Pending or Cancelled)
* **กรณีเลือก `CANCELLED` (ยกเลิก):**
  * อัปเดต `orders.status = 'CANCELLED'`
  * อัปเดต `payments.payment_status = 'REJECTED'`
  * **เพิกถอนสิทธิ์ดาวน์โหลด:** สั่ง `UPDATE download_links SET is_active = 0 WHERE order_id = ?` เพื่อปิดการเข้าถึงไฟล์ทั้งหมดทันที ป้องกันไม่ให้ลูกค้าดาวน์โหลดได้

---

## 4. ตารางฐานข้อมูลที่เกี่ยวข้อง (Database Tables)

| ชื่อตาราง | บทบาทในฟังก์ชันนี้ | ฟิลด์สำคัญที่เกี่ยวข้อง |
|---|---|---|
| **`orders`** | บันทึกสถานะคำสั่งซื้อหลัก | `order_id`, `status` ('PENDING', 'CONFIRMED', 'CANCELLED'), `notes` |
| **`payments`** | บันทึกผลการตรวจสอบการชำระเงิน | `payment_id`, `payment_status` ('PENDING', 'VERIFIED', 'REJECTED'), `admin_notes` |
| **`download_links`** | สร้างและเปิด/ปิดการเข้าถึงไฟล์ | `download_id`, `order_id`, `ebook_id`, `user_id`, `download_token`, `is_active` |
| **`users`** | ข้อมูลลูกค้าผู้สั่งซื้อ | `user_id`, `full_name`, `email`, `phone` |

---

## 5. คำสั่ง SQL เบื้องหลังการทำงาน (Underlying SQL)

### ดึงรายการคำสั่งซื้อพร้อมข้อมูลลูกค้าและสลิป (มีตัวกรองสถานะ)
```sql
SELECT 
    o.order_id,
    o.order_number,
    o.total_amount,
    o.status,
    o.order_date,
    u.full_name,
    u.username,
    p.payment_method,
    p.payment_status,
    p.slip_image
FROM orders o
JOIN users u ON o.user_id = u.user_id
LEFT JOIN payments p ON o.order_id = p.order_id
WHERE o.status = :filter_status  -- หรือไม่ระบุหากเลือกดูทั้งหมด
ORDER BY o.order_date DESC;
```

### อัปเดตสถานะคำสั่งซื้อและการชำระเงิน
```sql
-- 1. อัปเดตตาราง orders
UPDATE orders 
SET status = 'CONFIRMED' 
WHERE order_id = :order_id;

-- 2. อัปเดตตาราง payments
UPDATE payments 
SET payment_status = 'VERIFIED', 
    admin_notes = 'ตรวจสอบยอดเงินและสลิปการโอนเรียบร้อยแล้ว' 
WHERE order_id = :order_id;
```

### สร้างโทเค็นสิทธิ์ดาวน์โหลดอัตโนมัติเมื่อคำสั่งซื้อได้รับการยืนยัน
```sql
INSERT INTO download_links (order_id, ebook_id, user_id, download_token, is_active)
VALUES (:order_id, :ebook_id, :user_id, :uuid_token, 1);
```

---

## 6. ข้อจำกัดข้อมูลและความปลอดภัย (Constraints & Security)
* **One-to-One Payment Constraint:** `UNIQUE(order_id)` ในตาราง `payments` ป้องกันการบันทึกการชำระเงินซ้ำซ้อนในคำสั่งซื้อเดิม
* **Atomic Status Transitions:** การปรับสถานะคำสั่งซื้อจะซิงโครไนซ์สถานะการชำระเงินและสิทธิ์ดาวน์โหลดพร้อมกันในทรานแซกชันเดียว ไม่เกิดกรณีสถานะขัดแย้งกัน
