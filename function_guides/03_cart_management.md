# ฟังก์ชันที่ 3: ระบบจัดการตะกร้าสินค้า (Cart Management)
**โครงงาน:** Mini Project Database ร้านขาย E-Book  
**หมวดหมู่:** ส่วนหน้าร้าน (ผู้ใช้งาน) ตามข้อกำหนดหัวข้อ 2.1  

---

## 1. วัตถุประสงค์ของฟังก์ชัน
เพื่อให้ลูกค้าสามารถเลือกเก็บหนังสือที่ต้องการซื้อไว้ในตะกร้าชั่วคราว, สามารถปรับเพิ่มหรือลดจำนวนเล่ม, ลบรายการที่ไม่ต้องการออก, และระบบคำนวณยอดเงินรวมและยอดแต่ละรายการแบบอัตโนมัติก่อนเข้าสู่ขั้นตอนสั่งซื้อ

---

## 2. หน้าจอและเส้นทางที่เกี่ยวข้อง (Routes & Templates)
* **`/cart`** (`templates/cart.html`): หน้าแสดงรายการสินค้าในตะกร้า ปรับจำนวน และสรุปยอดชำระ
* **`/cart/add/<int:ebook_id>`** [POST]: เส้นทางสำหรับกดปุ่มเพิ่มหนังสือลงตะกร้า
* **`/cart/update/<int:item_id>`** [POST]: เส้นทางสำหรับปรับเปลี่ยนจำนวนเล่ม (เพิ่ม/ลด)
* **`/cart/remove/<int:item_id>`** [POST]: เส้นทางสำหรับลบรายการหนังสือออกจากตะกร้า

---

## 3. ลำดับขั้นตอนการทำงาน (Step-by-Step Flow)

### 3.1 การเพิ่มหนังสือลงในตะกร้า (Add to Cart)
1. ลูกค้าคลิกปุ่ม **"ใส่ตะกร้า"** จากหน้าแรกหรือหน้ารายละเอียดหนังสือ
2. ระบบตรวจสอบสิทธิ์: หากยังไม่ได้เข้าสู่ระบบ จะ Redirect ไปยังหน้า Login ก่อน
3. ระบบตรวจสอบว่าหนังสือนั้นเปิดขายอยู่หรือไม่ (`is_active = 1`)
4. ค้นหา `cart_id` ของผู้ใช้จากตาราง `carts`
5. **ตรวจสอบว่ามีหนังสือเล่มนี้อยู่ในตะกร้าแล้วหรือไม่:**
   * **หากมีอยู่แล้ว:** อัปเดตเพิ่มจำนวน `quantity = quantity + 1`
   * **หากยังไม่มี:** บันทึกแถวใหม่ลงในตาราง `cart_items` ด้วยจำนวนเริ่มต้น `quantity = 1`
6. ป้ายตัวเลข (Badge) แสดงจำนวนสินค้าบน Navbar จะอัปเดตแบบอัตโนมัติ

### 3.2 การเปิดดูและคำนวณราคาในตะกร้า (View Cart & Calculations)
1. ลูกค้าคลิกที่ไอคอนตะกร้าบน Navbar (`/cart`)
2. ระบบดึงรายการจาก `cart_items` เชื่อมกับ `ebooks` เพื่อนำราคาปัจจุบัน (`price`) มาคำนวณ:
   $$\text{item\_total} = \text{quantity} \times \text{price}$$
3. คำนวณยอดรวมสุทธิของตะกร้า (Grand Total):
   $$\text{total\_amount} = \sum (\text{item\_total})$$
4. แสดงตารางรายการพร้อมปุ่มปรับจำนวน `(+)` และ `(-)`

### 3.3 การปรับเพิ่มหรือลดจำนวน (Update Quantity)
* **เมื่อกดปุ่ม `(+)`:** ระบบสั่ง `UPDATE cart_items SET quantity = quantity + 1`
* **เมื่อกดปุ่ม `(-)`:**
  * หากจำนวนเดิมมากกว่า 1: ระบบสั่ง `UPDATE cart_items SET quantity = quantity - 1`
  * หากจำนวนเดิมเท่ากับ 1 แล้วกดลด: ระบบจะทำการลบรายการนั้นออกจากตะกร้าอัตโนมัติ (`DELETE`)

### 3.4 การลบรายการออกจากตะกร้า (Remove Item)
* ลูกค้าคลิกไอคอนถังขยะสีแดง
* ระบบทำการลบแถวที่มี `cart_item_id` นั้นออกจากตาราง `cart_items` พร้อมแจ้งเตือนผู้ใช้

---

## 4. ตารางฐานข้อมูลที่เกี่ยวข้อง (Database Tables)

| ชื่อตาราง | บทบาทในฟังก์ชันนี้ | ฟิลด์สำคัญที่เกี่ยวข้อง |
|---|---|---|
| **`carts`** | ตะกร้าหลักของลูกค้า (1 คน มี 1 ตะกร้า) | `cart_id`, `user_id`, `updated_at` |
| **`cart_items`** | รายการหนังสือที่อยู่ในตะกร้า | `cart_item_id`, `cart_id`, `ebook_id`, `quantity`, `added_at` |
| **`ebooks`** | ข้อมูลราคาและสถานะหนังสือ | `ebook_id`, `title`, `price`, `cover_url`, `is_active` |

---

## 5. คำสั่ง SQL เบื้องหลังการทำงาน (Underlying SQL)

### ค้นหาตะกร้าของผู้ใช้
```sql
SELECT cart_id FROM carts WHERE user_id = ?;
```

### ตรวจสอบและเพิ่มสินค้าลงในตะกร้า
```sql
-- 1. ตรวจสอบว่ามีอยู่แล้วหรือไม่
SELECT cart_item_id, quantity 
FROM cart_items 
WHERE cart_id = :cart_id AND ebook_id = :ebook_id;

-- 2. กรณีมีอยู่แล้ว: เพิ่มจำนวนขึ้น 1
UPDATE cart_items 
SET quantity = quantity + 1 
WHERE cart_item_id = :cart_item_id;

-- 3. กรณีเพิ่มครั้งแรก: บันทึกแถวใหม่
INSERT INTO cart_items (cart_id, ebook_id, quantity) 
VALUES (:cart_id, :ebook_id, 1);
```

### ดึงรายการสินค้าทั้งหมดในตะกร้าพร้อมคำนวณยอดเงิน
```sql
SELECT 
    ci.cart_item_id,
    ci.cart_id,
    ci.ebook_id,
    ci.quantity,
    b.title,
    b.price,
    b.cover_url,
    a.author_name,
    (ci.quantity * b.price) AS item_total
FROM cart_items ci
JOIN ebooks b ON ci.ebook_id = b.ebook_id
JOIN authors a ON b.author_id = a.author_id
WHERE ci.cart_id = ?
ORDER BY ci.added_at DESC;
```

### ลบรายการสินค้าออกจากตะกร้า (ตรวจสอบสิทธิ์ความเป็นเจ้าของ)
```sql
DELETE FROM cart_items 
WHERE cart_item_id = ? 
  AND cart_id IN (SELECT cart_id FROM carts WHERE user_id = ?);
```

---

## 6. ข้อจำกัดข้อมูลและความปลอดภัย (Constraints & Security)
* **`UNIQUE(cart_id, ebook_id)`:** ป้องกันไม่ให้มีหนังสือเล่มเดียวกันซ้ำกันมากกว่า 1 แถวในตะกร้าใบเดียวกัน
* **`CHECK(quantity > 0)`:** ข้อจำกัดระดับตาราง บังคับให้จำนวนสินค้าในตะกร้าต้องเป็นจำนวนเต็มบวกเสมอ (ไม่สามารถติดลบหรือเป็น 0 ได้)
* **Foreign Key Cascade:** `ON DELETE CASCADE` หากผู้ใช้ลบบัญชี ข้อมูลตะกร้าและรายการย่อยจะถูกลบตามโดยอัตโนมัติ ไม่เกิดข้อมูลตกค้าง (Orphan Rows)
