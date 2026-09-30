# ฟังก์ชันที่ 6: การจัดการหนังสือและหมวดหมู่หลังบ้าน (Admin Catalog & Category)
**โครงงาน:** Mini Project Database ร้านขาย E-Book  
**หมวดหมู่:** ระบบบริหารจัดการร้าน (ผู้ดูแลร้าน) ตามข้อกำหนดหัวข้อ 3  

---

## 1. วัตถุประสงค์ของฟังก์ชัน
เพื่อให้ผู้ดูแลระบบ (Admin) สามารถจัดการฐานข้อมูลหนังสือดิจิทัลได้อย่างสมบูรณ์ ได้แก่ การเพิ่มหนังสือใหม่, แก้ไขข้อมูลราคาและเรื่องย่อ, การปิดการขายชั่วคราวหรือเปิดเผยแพร่ใหม่, และการบริหารจัดการหมวดหมู่หนังสือเพื่อใช้ในการจัดกลุ่ม

---

## 2. หน้าจอและเส้นทางที่เกี่ยวข้อง (Routes & Templates)
* **`/admin/ebooks`** (`templates/admin/ebooks.html`): หน้ารวมแคตตาล็อกหนังสือทั้งหมดสำหรับผู้ดูแล พร้อมปุ่มเปิด/ปิดการขาย
* **`/admin/ebooks/add`** (`templates/admin/ebook_form.html`): หน้าฟอร์มเพิ่มหนังสือเล่มใหม่เข้าระบบ
* **`/admin/ebooks/edit/<int:ebook_id>`** (`templates/admin/ebook_form.html`): หน้าฟอร์มแก้ไขหนังสือเดิม
* **`/admin/ebooks/toggle/<int:ebook_id>`** [POST]: เส้นทางสำหรับสลับสถานะเปิดขาย/ปิดการขาย
* **`/admin/categories`** (`templates/admin/categories.html`): หน้าจัดการหมวดหมู่หนังสือ (เพิ่ม, แก้ไข, ดูจำนวนเล่ม)

---

## 3. ลำดับขั้นตอนการทำงาน (Step-by-Step Flow)

### 3.1 การเพิ่มหนังสือ E-Book เล่มใหม่ (Add E-Book)
1. แอดมินเข้าเมนู "จัดการ E-Book" และกดปุ่ม **"เพิ่ม E-Book เล่มใหม่"**
2. กรอกข้อมูลหนังสือ:
   * ชื่อเรื่อง (`title`)
   * เลือกผู้แต่งจากดรอปดาวน์ (`author_id`)
   * เลือกหมวดหมู่จากดรอปดาวน์ (`category_id`)
   * กำหนดราคาขาย (`price` ต้องไม่ติดลบ)
   * คำอธิบาย/เรื่องย่อ (`description`)
   * URL รูปภาพปก (`cover_url`)
   * ที่อยู่ไฟล์ดาวน์โหลด (`download_file_url`)
   * สวิตช์เปิดสถานะพร้อมขาย (`is_active`)
3. ระบบตรวจสอบความถูกต้อง และสั่ง `INSERT` ข้อมูลลงในตาราง `ebooks`
4. หน้าร้านค้าจะแสดงหนังสือเล่มใหม่ทันที

### 3.2 การแก้ไขข้อมูลหนังสือ (Edit E-Book)
1. แอดมินคลิกไอคอนดินสอที่แถวหนังสือที่ต้องการแก้ไข
2. ระบบดึงข้อมูลเดิมจากฐานข้อมูลมาแสดงในแบบฟอร์ม
3. แอดมินปรับเปลี่ยนราคา หรือแก้ไขคำอธิบาย แล้วกดบันทึก
4. ระบบสั่ง `UPDATE` ข้อมูลในตาราง `ebooks`

### 3.3 การเปิดขาย / ปิดการขายชั่วคราว (Toggle Active Status)
* แอดมินสามารถคลิกไอคอนรูปดวงตา เพื่อสลับสถานะหนังสือ:
  * หากสถานะเดิมคือ `1` (เปิดขาย) -> เปลี่ยนเป็น `0` (ปิดการขาย): หนังสือจะไม่ปรากฏบนหน้าร้านค้าของลูกค้า
  * หากสถานะเดิมคือ `0` (ปิดการขาย) -> เปลี่ยนเป็น `1` (เปิดขาย): นำหนังสือกลับมาวางจำหน่ายใหม่
* ทำงานผ่านคำสั่ง `UPDATE ebooks SET is_active = ? WHERE ebook_id = ?`

### 3.4 การจัดการหมวดหมู่หนังสือ (Category Management)
1. แอดมินเข้าเมนู "จัดการหมวดหมู่"
2. หน้าจอแสดงตารางรายชื่อหมวดหมู่ทั้งหมด พร้อมสถิติคำนวณจำนวนหนังสือที่มีอยู่ในแต่ละหมวดแบบอัตโนมัติ
3. แอดมินสามารถกรอกชื่อหมวดหมู่และคำอธิบายในฟอร์มด้านข้างเพื่อกด **เพิ่มหมวดหมู่ใหม่**
4. หากต้องการแก้ไข ให้กดปุ่ม **แก้ไข** ข้อมูลจะถูกดึงขึ้นมาบนฟอร์มทันที เมื่อกดบันทึกจะสั่ง `UPDATE`

---

## 4. ตารางฐานข้อมูลที่เกี่ยวข้อง (Database Tables)

| ชื่อตาราง | บทบาทในฟังก์ชันนี้ | ฟิลด์สำคัญที่เกี่ยวข้อง |
|---|---|---|
| **`ebooks`** | ตารางข้อมูลหนังสือ | `ebook_id`, `title`, `author_id`, `category_id`, `price`, `description`, `cover_url`, `download_file_url`, `is_active` |
| **`categories`** | ตารางหมวดหมู่ | `category_id`, `category_name`, `description` |
| **`authors`** | ตารางข้อมูลผู้แต่ง | `author_id`, `author_name`, `bio` |

---

## 5. คำสั่ง SQL เบื้องหลังการทำงาน (Underlying SQL)

### ดึงรายการหนังสือทั้งหมดสำหรับหลังบ้าน พร้อมนับยอดคำสั่งซื้อสำเร็จ
```sql
SELECT 
    b.*, 
    a.author_name, 
    c.category_name,
    (SELECT COUNT(*) 
     FROM order_items oi 
     JOIN orders o ON oi.order_id = o.order_id 
     WHERE oi.ebook_id = b.ebook_id AND o.status = 'CONFIRMED') AS sales_count
FROM ebooks b
JOIN authors a ON b.author_id = a.author_id
JOIN categories c ON b.category_id = c.category_id
ORDER BY b.ebook_id DESC;
```

### เพิ่มหนังสือใหม่เข้าระบบ
```sql
INSERT INTO ebooks (title, author_id, category_id, price, description, cover_url, download_file_url, is_active)
VALUES (:title, :author_id, :category_id, :price, :description, :cover_url, :download_file_url, :is_active);
```

### สลับสถานะเปิด/ปิดการขาย
```sql
UPDATE ebooks 
SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END 
WHERE ebook_id = ?;
```

### ดึงหมวดหมู่ทั้งหมดพร้อมนับจำนวนหนังสือในแต่ละหมวด (Aggregate Query)
```sql
SELECT 
    c.category_id,
    c.category_name,
    c.description,
    COUNT(b.ebook_id) AS ebook_count
FROM categories c
LEFT JOIN ebooks b ON c.category_id = b.category_id
GROUP BY c.category_id
ORDER BY c.category_id ASC;
```

---

## 6. ข้อจำกัดข้อมูลและความปลอดภัย (Constraints & Security)
* **Role-Based Access Control (`@admin_required`):** ทุกเส้นทางในโมดูลนี้ถูกป้องกันด้วย Decorator หากผู้ใช้ไม่ใช่สิทธิ์ `admin` ระบบจะปฏิเสธการเข้าถึงทันที
* **Foreign Key On Delete Restrict:** การผูกความสัมพันธ์ระหว่างหมวดหมู่และหนังสือใช้ `ON DELETE RESTRICT` ป้องกันการลบหมวดหมู่ที่มีหนังสือผูกอยู่โดยไม่ได้ตั้งใจ
* **`CHECK(price >= 0)`:** ป้องกันไม่ให้แอดมินเผลอใส่ราคาติดลบในฐานข้อมูล
