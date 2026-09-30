# ฟังก์ชันที่ 2: แคตตาล็อก การค้นหา และการคัดกรองหมวดหมู่ (Catalog, Search & Filter)
**โครงงาน:** Mini Project Database ร้านขาย E-Book  
**หมวดหมู่:** ส่วนหน้าร้าน (ผู้ใช้งาน) ตามข้อกำหนดหัวข้อ 2.1  

---

## 1. วัตถุประสงค์ของฟังก์ชัน
เพื่อให้ผู้ใช้งานสามารถเรียกดูรายการ E-Book ทั้งหมด, ค้นหาหนังสือที่สนใจด้วยคำสำคัญ, กรองหนังสือตามหมวดหมู่ที่ต้องการ, เรียงลำดับราคา, และกดดูรายละเอียดเชิงลึกของหนังสือแต่ละเล่มได้

---

## 2. หน้าจอและเส้นทางที่เกี่ยวข้อง (Routes & Templates)
* **`/`** (`templates/index.html`): หน้าร้านค้าหลัก แสดงแคตตาล็อกหนังสือ ช่องค้นหา ปุ่มหมวดหมู่ และตัวเลือกเรียงลำดับ
* **`/ebook/<int:ebook_id>`** (`templates/ebook_detail.html`): หน้ารายละเอียดของหนังสือเล่มที่เลือก พร้อมประวัตินักเขียน และหนังสือที่เกี่ยวข้องในหมวดเดียวกัน

---

## 3. ลำดับขั้นตอนการทำงาน (Step-by-Step Flow)

### 3.1 การแสดงผลหน้าร้านค้าเริ่มต้น (Browsing Catalog)
1. ผู้ใช้เข้าหน้าแรก (`/`)
2. ระบบดึงรายชื่อหมวดหมู่ทั้งหมดจากตาราง `categories` มาแสดงเป็นเมนูดรอปดาวน์และปุ่มเม็ด (Category Pills)
3. ระบบคิวรีรายการ E-Book ที่มีสถานะเปิดขาย (`is_active = 1`) โดยเชื่อมข้อมูลชื่อผู้แต่งและชื่อหมวดหมู่มาแสดงผล
4. แสดงการ์ดหนังสือประกอบด้วย รูปภาพหน้าปก, ป้ายชื่อหมวดหมู่, ชื่อหนังสือ, ชื่อผู้แต่ง, ราคา, คำอธิบายย่อ และปุ่มใส่ตะกร้า

### 3.2 การค้นหาด้วยคำสำคัญ (Keyword Search)
1. ผู้ใช้พิมพ์คำค้นลงในช่อง Search Bar (เช่น *"Python"*, *"การลงทุน"*, หรือชื่อผู้แต่ง) แล้วกดค้นหา
2. ระบบส่งพารามิเตอร์ `q` ผ่าน HTTP GET
3. คำสั่ง SQL ฝั่งเซิร์ฟเวอร์จะใช้เงื่อนไข `LIKE %...%` ค้นหาทั้งใน:
   * ชื่อเรื่องหนังสือ (`b.title`)
   * คำอธิบายเรื่องย่อ (`b.description`)
   * ชื่อผู้แต่ง (`a.author_name`)
4. ระบบแสดงผลลัพธ์หนังสือที่ตรงกับคำค้น พร้อมแจ้งจำนวนเล่มที่พบ

### 3.3 การคัดกรองตามหมวดหมู่ (Category Filtering)
1. ผู้ใช้คลิกเลือกปุ่มหมวดหมู่ เช่น *"วิทยาศาสตร์ข้อมูล & AI"*
2. ระบบส่งพารามิเตอร์ `category=5` ผ่าน HTTP GET
3. คำสั่ง SQL เพิ่มเงื่อนไข `AND b.category_id = ?` เพื่อดึงเฉพาะหนังสือในหมวดนั้น
4. ปุ่มหมวดหมู่ที่ถูกเลือกจะเปลี่ยนสถานะเป็นสีน้ำเงิน (Active Pill) เพื่อให้ผู้ใช้ทราบว่ากำลังดูหมวดใดอยู่

### 3.4 การจัดเรียงลำดับ (Sorting)
ผู้ใช้สามารถเลือกตัวเลือกเรียงลำดับจากเมนูดรอปดาวน์:
* **มาใหม่ล่าสุด:** `ORDER BY b.ebook_id DESC`
* **ราคาต่ำไปสูง:** `ORDER BY b.price ASC`
* **ราคาสูงไปต่ำ:** `ORDER BY b.price DESC`
* **ชื่อหนังสือ (ก-ฮ):** `ORDER BY b.title ASC`

### 3.5 การดูรายละเอียดหนังสือเชิงลึก (E-Book Details)
1. เมื่อคลิกที่การ์ดหนังสือ ระบบจะเปิดเส้นทาง `/ebook/<ebook_id>`
2. ดึงข้อมูลหนังสือเล่มนั้น พร้อมประวัตินักเขียน (`author_bio`)
3. **ตรวจสอบสิทธิ์การซื้อซ้ำ:** ตรวจสอบว่าผู้ใช้ที่กำลังล็อกอินอยู่เคยซื้อหนังสือเล่มนี้ในคำสั่งซื้อที่ยืนยันแล้วหรือไม่ หากเคยซื้อแล้ว จะแสดงปุ่ม *"ดาวน์โหลด E-Book (PDF)"* ให้ทันที
4. **แนะนำหนังสือที่เกี่ยวข้อง:** คิวรีหนังสือเล่มอื่นๆ ในหมวดหมู่เดียวกันอีกสูงสุด 4 เล่มมาแสดงที่ด้านล่าง

---

## 4. ตารางฐานข้อมูลที่เกี่ยวข้อง (Database Tables)

| ชื่อตาราง | บทบาทในฟังก์ชันนี้ | ฟิลด์สำคัญที่เกี่ยวข้อง |
|---|---|---|
| **`ebooks`** | แคตตาล็อกหนังสือ | `ebook_id`, `title`, `author_id`, `category_id`, `price`, `description`, `cover_url`, `is_active` |
| **`categories`** | หมวดหมู่หนังสือ | `category_id`, `category_name`, `description` |
| **`authors`** | ผู้แต่ง/นักเขียน | `author_id`, `author_name`, `bio` |

---

## 5. คำสั่ง SQL เบื้องหลังการทำงาน (Underlying SQL)

### คิวรีรายการหนังสือพร้อมเงื่อนไขค้นหา กรองหมวด และเรียงลำดับ
```sql
SELECT 
    b.ebook_id,
    b.title,
    b.price,
    b.description,
    b.cover_url,
    b.is_active,
    a.author_name,
    c.category_name
FROM ebooks b
JOIN authors a ON b.author_id = a.author_id
JOIN categories c ON b.category_id = c.category_id
WHERE b.is_active = 1
  -- เงื่อนไขเมื่อมีการเลือกหมวดหมู่ (Optional)
  AND b.category_id = :category_id
  -- เงื่อนไขเมื่อมีการพิมพ์ค้นหา (Optional)
  AND (b.title LIKE :search OR b.description LIKE :search OR a.author_name LIKE :search)
ORDER BY b.price ASC;
```

### คิวรีรายละเอียดหนังสือเล่มเดียว
```sql
SELECT 
    b.*, 
    a.author_name, 
    a.bio AS author_bio, 
    c.category_name 
FROM ebooks b
JOIN authors a ON b.author_id = a.author_id
JOIN categories c ON b.category_id = c.category_id
WHERE b.ebook_id = ?;
```

### คิวรีหนังสือที่เกี่ยวข้องในหมวดเดียวกัน
```sql
SELECT b.ebook_id, b.title, b.price, b.cover_url, a.author_name 
FROM ebooks b
JOIN authors a ON b.author_id = a.author_id
WHERE b.category_id = ? AND b.ebook_id != ? AND b.is_active = 1
LIMIT 4;
```

---

## 6. ข้อจำกัดข้อมูลและความปลอดภัย (Constraints & Security)
* **Parameterized Query:** คำสั่งค้นหาใช้ตัวแปรแบบ Parameter Binding (`?`) ป้องกันช่องโหว่ **SQL Injection** 100%
* **Filter `is_active = 1`:** ซ่อนหนังสือที่ผู้ดูแลร้านกดปิดการขายชั่วคราว ไม่ให้ปรากฏบนหน้าร้านค้า
* **Foreign Key Constraints:** `FOREIGN KEY (category_id) REFERENCES categories` ป้องกันการเชื่อมโยงหมวดหมู่ที่ไม่ถูกต้อง
