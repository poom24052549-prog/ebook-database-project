# พจนานุกรมข้อมูล (Data Dictionary)
**โครงงาน:** Mini Project Database ร้านขาย E-Book  
**รายวิชา:** Database Mini Project  

ระบบฐานข้อมูลประกอบด้วยตารางเชิงสัมพันธ์ทั้งหมด **11 ตาราง** (เกินเกณฑ์ขั้นต่ำ 8 ตาราง) โดยมีการกำหนด Primary Key (PK), Foreign Key (FK), และ Constraints ไว้อย่างรัดกุม

---

### 1. ตาราง `roles` (บทบาทสิทธิ์ผู้ใช้งาน)
| ชื่อฟิลด์ (Field Name) | ชนิดข้อมูล (Data Type) | คีย์ (Key) | ข้อกำหนด (Constraints) | ความหมายและเงื่อนไขทางธุรกิจ |
|---|---|---|---|---|
| `role_id` | INTEGER | PK | AUTOINCREMENT | รหัสบทบาทหลัก |
| `role_name` | TEXT | - | NOT NULL, UNIQUE, CHECK IN ('customer', 'admin') | ชื่อบทบาท ('customer'=ลูกค้า, 'admin'=ผู้ดูแล) |
| `description` | TEXT | - | NULLABLE | รายละเอียดสิทธิ์หน้าที่ |

---

### 2. ตาราง `users` (ผู้ใช้งานระบบ)
| ชื่อฟิลด์ | ชนิดข้อมูล | คีย์ | ข้อกำหนด | ความหมายและเงื่อนไขทางธุรกิจ |
|---|---|---|---|---|
| `user_id` | INTEGER | PK | AUTOINCREMENT | รหัสสมาชิก |
| `role_id` | INTEGER | FK | NOT NULL, DEFAULT 1, REFERENCES roles(role_id) | รหัสบทบาท (Default: customer) |
| `username` | TEXT | - | NOT NULL, UNIQUE | ชื่อสำหรับใช้ Login เข้าสู่ระบบ |
| `email` | TEXT | - | NOT NULL, UNIQUE | อีเมลสำหรับติดต่อและ Login |
| `password_hash` | TEXT | - | NOT NULL | รหัสผ่านที่เข้ารหัสความปลอดภัย (Hash) |
| `full_name` | TEXT | - | NOT NULL | ชื่อและนามสกุลจริงของสมาชิก |
| `phone` | TEXT | - | NULLABLE | หมายเลขโทรศัพท์ติดต่อ |
| `created_at` | TIMESTAMP | - | NOT NULL, DEFAULT CURRENT_TIMESTAMP | วันและเวลาที่ลงทะเบียนสมาชิก |

---

### 3. ตาราง `categories` (หมวดหมู่หนังสือ)
| ชื่อฟิลด์ | ชนิดข้อมูล | คีย์ | ข้อกำหนด | ความหมายและเงื่อนไขทางธุรกิจ |
|---|---|---|---|---|
| `category_id` | INTEGER | PK | AUTOINCREMENT | รหัสหมวดหมู่ |
| `category_name` | TEXT | - | NOT NULL, UNIQUE | ชื่อหมวดหมู่หนังสือ |
| `description` | TEXT | - | NULLABLE | รายละเอียดและขอบเขตหมวดหมู่ |

---

### 4. ตาราง `authors` (ผู้แต่งหนังสือ)
| ชื่อฟิลด์ | ชนิดข้อมูล | คีย์ | ข้อกำหนด | ความหมายและเงื่อนไขทางธุรกิจ |
|---|---|---|---|---|
| `author_id` | INTEGER | PK | AUTOINCREMENT | รหัสประจำตัวนักเขียน |
| `author_name` | TEXT | - | NOT NULL | ชื่อหรือนามปากกาผู้เขียน |
| `bio` | TEXT | - | NULLABLE | ประวัติหรือคำแนะนำตัวนักเขียน |
| `email` | TEXT | - | NULLABLE | อีเมลติดต่อของผู้เขียน |

---

### 5. ตาราง `ebooks` (รายการหนังสือ E-Book)
| ชื่อฟิลด์ | ชนิดข้อมูล | คีย์ | ข้อกำหนด | ความหมายและเงื่อนไขทางธุรกิจ |
|---|---|---|---|---|
| `ebook_id` | INTEGER | PK | AUTOINCREMENT | รหัสประจำหนังสือ |
| `title` | TEXT | - | NOT NULL | ชื่อเรื่องของ E-Book |
| `author_id` | INTEGER | FK | NOT NULL, REFERENCES authors(author_id) | รหัสผู้แต่ง |
| `category_id` | INTEGER | FK | NOT NULL, REFERENCES categories(category_id) | รหัสหมวดหมู่หลัก |
| `price` | REAL | - | NOT NULL, CHECK(price >= 0) | ราคาขาย (ต้องไม่ติดลบ) |
| `description` | TEXT | - | NULLABLE | บทคัดย่อ เรื่องย่อ หรือเนื้อหาโดยสังเขป |
| `cover_url` | TEXT | - | DEFAULT '/static/images/default_cover.png' | ลิงก์รูปภาพปกหนังสือ |
| `download_file_url` | TEXT | - | NOT NULL | พาธหรือที่อยู่ไฟล์หนังสือดิจิทัล |
| `is_active` | INTEGER | - | NOT NULL, DEFAULT 1, CHECK(is_active IN (0,1)) | สถานะวางจำหน่าย (1=เปิดขาย, 0=ปิดการขาย) |
| `created_at` | TIMESTAMP | - | NOT NULL, DEFAULT CURRENT_TIMESTAMP | วันที่เพิ่มหนังสือเข้าระบบ |

---

### 6. ตาราง `carts` (ตะกร้าสินค้าของสมาชิก)
| ชื่อฟิลด์ | ชนิดข้อมูล | คีย์ | ข้อกำหนด | ความหมายและเงื่อนไขทางธุรกิจ |
|---|---|---|---|---|
| `cart_id` | INTEGER | PK | AUTOINCREMENT | รหัสตะกร้าสินค้า |
| `user_id` | INTEGER | FK | NOT NULL, UNIQUE, REFERENCES users(user_id) | รหัสสมาชิกเจ้าของตะกร้า (1:1 กับ User) |
| `updated_at` | TIMESTAMP | - | NOT NULL, DEFAULT CURRENT_TIMESTAMP | เวลาที่มีการปรับปรุงล่าสุด |

---

### 7. ตาราง `cart_items` (รายการย่อยในตะกร้า)
| ชื่อฟิลด์ | ชนิดข้อมูล | คีย์ | ข้อกำหนด | ความหมายและเงื่อนไขทางธุรกิจ |
|---|---|---|---|---|
| `cart_item_id` | INTEGER | PK | AUTOINCREMENT | รหัสรายการในตะกร้า |
| `cart_id` | INTEGER | FK | NOT NULL, REFERENCES carts(cart_id) | รหัสตะกร้าที่สังกัด |
| `ebook_id` | INTEGER | FK | NOT NULL, REFERENCES ebooks(ebook_id) | รหัส E-Book |
| `quantity` | INTEGER | - | NOT NULL, DEFAULT 1, CHECK(quantity > 0) | จำนวนที่เลือก (ต้องมากกว่า 0) |
| `added_at` | TIMESTAMP | - | NOT NULL, DEFAULT CURRENT_TIMESTAMP | เวลาที่หยิบใส่ตะกร้า |
| *Composite Constraint* | - | - | UNIQUE(cart_id, ebook_id) | ห้ามหนังสือซ้ำแถวในตะกร้าเดียวกัน |

---

### 8. ตาราง `orders` (หัวเอกสารคำสั่งซื้อ)
| ชื่อฟิลด์ | ชนิดข้อมูล | คีย์ | ข้อกำหนด | ความหมายและเงื่อนไขทางธุรกิจ |
|---|---|---|---|---|
| `order_id` | INTEGER | PK | AUTOINCREMENT | รหัสคำสั่งซื้อในระบบ |
| `order_number` | TEXT | - | NOT NULL, UNIQUE | หมายเลขอ้างอิงคำสั่งซื้อ (เช่น ORD-20260927-1001) |
| `user_id` | INTEGER | FK | NOT NULL, REFERENCES users(user_id) | รหัสลูกค้าผู้สั่งซื้อ |
| `total_amount` | REAL | - | NOT NULL, CHECK(total_amount >= 0) | ยอดรวมราคาสุทธิของคำสั่งซื้อ |
| `status` | TEXT | - | NOT NULL, DEFAULT 'PENDING', CHECK IN ('PENDING', 'CONFIRMED', 'CANCELLED') | สถานะคำสั่งซื้อ ('PENDING'=รอชำระ, 'CONFIRMED'=ยืนยันแล้ว, 'CANCELLED'=ยกเลิก) |
| `order_date` | TIMESTAMP | - | NOT NULL, DEFAULT CURRENT_TIMESTAMP | วันและเวลาที่สั่งซื้อ |
| `notes` | TEXT | - | NULLABLE | ข้อความหรือหมายเหตุคำสั่งซื้อ |

---

### 9. ตาราง `order_items` (รายการหนังสือในคำสั่งซื้อ)
| ชื่อฟิลด์ | ชนิดข้อมูล | คีย์ | ข้อกำหนด | ความหมายและเงื่อนไขทางธุรกิจ |
|---|---|---|---|---|
| `order_item_id` | INTEGER | PK | AUTOINCREMENT | รหัสรายการย่อย |
| `order_id` | INTEGER | FK | NOT NULL, REFERENCES orders(order_id) | รหัสคำสั่งซื้อหลัก |
| `ebook_id` | INTEGER | FK | NOT NULL, REFERENCES ebooks(ebook_id) | รหัสหนังสือที่ซื้อ |
| `unit_price` | REAL | - | NOT NULL, CHECK(unit_price >= 0) | ราคาประวัติต่อหน่วย ณ วันที่สั่งซื้อ |
| `quantity` | INTEGER | - | NOT NULL, DEFAULT 1, CHECK(quantity > 0) | จำนวนเล่ม |
| `subtotal` | REAL | - | NOT NULL, CHECK(subtotal >= 0) | มูลค่ารวมของรายการ (unit_price * quantity) |

---

### 10. ตาราง `payments` (การชำระเงินและหลักฐานจำลอง)
| ชื่อฟิลด์ | ชนิดข้อมูล | คีย์ | ข้อกำหนด | ความหมายและเงื่อนไขทางธุรกิจ |
|---|---|---|---|---|
| `payment_id` | INTEGER | PK | AUTOINCREMENT | รหัสการชำระเงิน |
| `order_id` | INTEGER | FK | NOT NULL, UNIQUE, REFERENCES orders(order_id) | รหัสคำสั่งซื้อที่ชำระ (1:1 กับ Orders) |
| `payment_method` | TEXT | - | NOT NULL, CHECK IN ('PROMPTPAY_QR', 'BANK_TRANSFER', 'MOCK_CREDIT') | วิธีการชำระเงินจำลอง |
| `amount` | REAL | - | NOT NULL, CHECK(amount >= 0) | ยอดเงินที่แจ้งชำระ |
| `slip_image` | TEXT | - | NULLABLE | ที่อยู่ไฟล์ภาพสลิปจำลอง |
| `payment_date` | TIMESTAMP | - | NOT NULL, DEFAULT CURRENT_TIMESTAMP | วันที่และเวลาที่โอนเงิน |
| `payment_status` | TEXT | - | NOT NULL, DEFAULT 'PENDING', CHECK IN ('PENDING', 'VERIFIED', 'REJECTED') | สถานะการตรวจสอบหลักฐาน |
| `admin_notes` | TEXT | - | NULLABLE | บันทึกการตรวจสอบจากผู้ดูแลร้าน |

---

### 11. ตาราง `download_links` (โทเค็นและสิทธิ์การดาวน์โหลด E-Book)
| ชื่อฟิลด์ | ชนิดข้อมูล | คีย์ | ข้อกำหนด | ความหมายและเงื่อนไขทางธุรกิจ |
|---|---|---|---|---|
| `download_id` | INTEGER | PK | AUTOINCREMENT | รหัสสิทธิ์ดาวน์โหลด |
| `order_id` | INTEGER | FK | NOT NULL, REFERENCES orders(order_id) | คำสั่งซื้อที่ให้สิทธิ์ |
| `ebook_id` | INTEGER | FK | NOT NULL, REFERENCES ebooks(ebook_id) | หนังสือที่ได้รับสิทธิ์ |
| `user_id` | INTEGER | FK | NOT NULL, REFERENCES users(user_id) | ลูกค้าผู้ได้รับสิทธิ์ |
| `download_token` | TEXT | - | NOT NULL, UNIQUE | รหัสโทเค็นลับ (UUID) สำหรับเข้าถึงไฟล์ |
| `expiry_date` | TIMESTAMP | - | NULLABLE | วันหมดอายุสิทธิ์ดาวน์โหลด |
| `download_count` | INTEGER | - | NOT NULL, DEFAULT 0, CHECK(download_count >= 0) | จำนวนครั้งที่ลูกค้ากดดาวน์โหลดไปแล้ว |
| `is_active` | INTEGER | - | NOT NULL, DEFAULT 1, CHECK(is_active IN (0,1)) | สถานะอนุญาตให้ดาวน์โหลด |
| `created_at` | TIMESTAMP | - | NOT NULL, DEFAULT CURRENT_TIMESTAMP | เวลาที่สร้างสิทธิ์ดาวน์โหลด |
