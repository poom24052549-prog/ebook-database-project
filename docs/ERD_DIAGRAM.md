# เอกสารการออกแบบฐานข้อมูล (Entity-Relationship Diagram: ERD)
**โครงงาน:** Mini Project Database ร้านขาย E-Book  
**รายวิชา:** Database Mini Project  

---

## 1. แผนภาพแสดงความสัมพันธ์ของข้อมูล (ER Diagram - Mermaid Notation)

```mermaid
erDiagram
    ROLES ||--o{ USERS : "defines role for (1:N)"
    USERS ||--|| CARTS : "owns (1:1)"
    CARTS ||--o{ CART_ITEMS : "contains (1:N)"
    EBOOKS ||--o{ CART_ITEMS : "added as (1:N)"
    CATEGORIES ||--o{ EBOOKS : "classifies (1:N)"
    AUTHORS ||--o{ EBOOKS : "writes (1:N)"
    USERS ||--o{ ORDERS : "places (1:N)"
    ORDERS ||--|{ ORDER_ITEMS : "includes (1:N)"
    EBOOKS ||--o{ ORDER_ITEMS : "sold in (1:N)"
    ORDERS ||--|| PAYMENTS : "paid via (1:1)"
    ORDERS ||--o{ DOWNLOAD_LINKS : "generates (1:N)"
    EBOOKS ||--o{ DOWNLOAD_LINKS : "target of (1:N)"
    USERS ||--o{ DOWNLOAD_LINKS : "granted to (1:N)"

    ROLES {
        int role_id PK
        string role_name "UNIQUE, CHECK('customer', 'admin')"
        string description
    }

    USERS {
        int user_id PK
        int role_id FK
        string username "UNIQUE, NOT NULL"
        string email "UNIQUE, NOT NULL"
        string password_hash "NOT NULL"
        string full_name "NOT NULL"
        string phone
        timestamp created_at "DEFAULT CURRENT_TIMESTAMP"
    }

    CATEGORIES {
        int category_id PK
        string category_name "UNIQUE, NOT NULL"
        string description
    }

    AUTHORS {
        int author_id PK
        string author_name "NOT NULL"
        string bio
        string email
    }

    EBOOKS {
        int ebook_id PK
        string title "NOT NULL"
        int author_id FK
        int category_id FK
        real price "CHECK(price >= 0)"
        string description
        string cover_url
        string download_file_url "NOT NULL"
        int is_active "CHECK(is_active IN (0,1))"
        timestamp created_at
    }

    CARTS {
        int cart_id PK
        int user_id FK "UNIQUE"
        timestamp updated_at
    }

    CART_ITEMS {
        int cart_item_id PK
        int cart_id FK
        int ebook_id FK
        int quantity "CHECK(quantity > 0)"
        timestamp added_at
    }

    ORDERS {
        int order_id PK
        string order_number "UNIQUE, NOT NULL"
        int user_id FK
        real total_amount "CHECK(total_amount >= 0)"
        string status "CHECK IN ('PENDING', 'CONFIRMED', 'CANCELLED')"
        timestamp order_date "DEFAULT CURRENT_TIMESTAMP"
        string notes
    }

    ORDER_ITEMS {
        int order_item_id PK
        int order_id FK
        int ebook_id FK
        real unit_price "CHECK(unit_price >= 0)"
        int quantity "CHECK(quantity > 0)"
        real subtotal "CHECK(subtotal >= 0)"
    }

    PAYMENTS {
        int payment_id PK
        int order_id FK "UNIQUE"
        string payment_method "CHECK IN ('PROMPTPAY_QR', 'BANK_TRANSFER', 'MOCK_CREDIT')"
        real amount "CHECK(amount >= 0)"
        string slip_image
        timestamp payment_date
        string payment_status "CHECK IN ('PENDING', 'VERIFIED', 'REJECTED')"
        string admin_notes
    }

    DOWNLOAD_LINKS {
        int download_id PK
        int order_id FK
        int ebook_id FK
        int user_id FK
        string download_token "UNIQUE, NOT NULL"
        timestamp expiry_date
        int download_count "DEFAULT 0, CHECK(>= 0)"
        int is_active "CHECK IN (0, 1)"
        timestamp created_at
    }
```

---

## 2. อธิบายความสัมพันธ์หลักและ Cardinality

1. **ROLES (1) to USERS (N):** ผู้ใช้งาน 1 คนมีบทบาทเดียว (`customer` หรือ `admin`) แต่ 1 บทบาทมีผู้ใช้สังกัดได้หลายคน (One-to-Many)
2. **CATEGORIES (1) to EBOOKS (N):** 1 หมวดหมู่มี E-Book ได้หลายเล่ม แต่ E-Book 1 เล่มสังกัดหมวดหมู่หลัก 1 หมวดหมู่ (One-to-Many)
3. **AUTHORS (1) to EBOOKS (N):** 1 ผู้แต่งสามารถเขียน E-Book ได้หลายเล่ม (One-to-Many)
4. **USERS (1) to CARTS (1):** สมาชิก 1 คนมีตะกร้าประจำตัว 1 ตะกร้า (One-to-One)
5. **CARTS (1) to CART_ITEMS (N) & EBOOKS (1) to CART_ITEMS (N):** ความสัมพันธ์ Many-to-Many ระหว่างตะกร้ากับหนังสือ ผ่านตารางเชื่อม `cart_items`
6. **USERS (1) to ORDERS (N):** ลูกค้า 1 คนสามารถมีประวัติคำสั่งซื้อได้หลายครั้ง (One-to-Many)
7. **ORDERS (1) to ORDER_ITEMS (N) & EBOOKS (1) to ORDER_ITEMS (N):** ความสัมพันธ์ Many-to-Many ระหว่างคำสั่งซื้อกับหนังสือ ผ่านตารางย่อย `order_items` โดยบันทึกราคาประวัติ ณ วันที่ซื้อ (`unit_price`)
8. **ORDERS (1) to PAYMENTS (1):** 1 คำสั่งซื้อผูกกับ 1 บันทึกการชำระเงิน (One-to-One)
9. **ORDERS (1) to DOWNLOAD_LINKS (N):** เมื่อคำสั่งซื้อได้รับการยืนยัน ระบบจะสร้างโทเค็นดาวน์โหลดสำหรับหนังสือแต่ละเล่มในคำสั่งซื้อ (One-to-Many)
