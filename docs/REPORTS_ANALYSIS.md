# เอกสารรายงานวิเคราะห์จากข้อมูลจริงในระบบ (4 Analytical Reports)
**โครงงาน:** Mini Project Database ร้านขาย E-Book  
**รายวิชา:** Database Mini Project  

เอกสารฉบับนี้จัดทำขึ้นเพื่อนำเสนอและอธิบายผลการวิเคราะห์ข้อมูลจริงในระบบฐานข้อมูลร้านขาย E-Book ทั้ง 4 รายงานตามข้อกำหนดในใบงาน โดยทุกรายงานอ้างอิงจากชุดข้อมูลจริงที่มีคำสั่งซื้อมากกว่า 30 คำสั่งซื้อ และเขียนด้วยคำสั่ง SQL ที่ใช้การประมวลผลเชิงวิเคราะห์ (`JOIN`, `GROUP BY`, `HAVING`, `AGGREGATE FUNCTIONS`)

---

## รายงานที่ 1: ยอดขายตามช่วงเวลา (Sales by Time Period)

### 1.1 คำถามที่ต้องตอบ
* ยอดขาย จำนวนคำสั่งซื้อ และค่าเฉลี่ยต่อคำสั่งซื้อ (Average Order Value - AOV) เปลี่ยนแปลงไปอย่างไรตามงวดเดือนและวันที่?

### 1.2 คำสั่ง SQL เชิงวิเคราะห์
```sql
SELECT 
    strftime('%Y-%m', o.order_date) AS period_month,
    COUNT(o.order_id) AS total_orders,
    ROUND(SUM(o.total_amount), 2) AS total_sales,
    ROUND(AVG(o.total_amount), 2) AS average_order_value,
    MIN(o.total_amount) AS min_order_value,
    MAX(o.total_amount) AS max_order_value
FROM orders o
JOIN payments p ON o.order_id = p.order_id
WHERE o.status = 'CONFIRMED'
GROUP BY strftime('%Y-%m', o.order_date)
ORDER BY period_month ASC;
```

### 1.3 ผลลัพธ์จากฐานข้อมูลจริง
| งวดเดือน (Month) | จำนวนคำสั่งซื้อที่สำเร็จ | ยอดขายรวม (บาท) | ค่าเฉลี่ยต่อบิล (AOV) | ยอดบิลต่ำสุด | ยอดบิลสูงสุด |
|---|:---:|:---:|:---:|:---:|:---:|
| **2026-07** | 6 รายการ | 4,560.00 | 760.00 | 350.00 | 1,080.00 |
| **2026-08** | 9 รายการ | 5,720.00 | 635.56 | 195.00 | 1,220.00 |
| **2026-09** | 12 รายการ | 4,620.00 | 385.00 | 195.00 | 870.00 |

### 1.4 การวิเคราะห์และข้อสรุปเชิงธุรกิจ
* **แนวโน้มปริมาณคำสั่งซื้อ:** ปริมาณคำสั่งซื้อเติบโตอย่างต่อเนื่องจาก 6 รายการในเดือน ก.ค. เพิ่มเป็น 9 รายการในเดือน ส.ค. (+50%) และขึ้นสู่ 12 รายการในเดือน ก.ย. (+33%) แสดงถึงฐานลูกค้าใหม่ที่เริ่มเข้ามาใช้งานร้านมากขึ้น
* **ยอดขายเฉลี่ยต่อบิล (AOV):** ในช่วงเดือน ก.ค. - ส.ค. ลูกค้ามักซื้อแบบ Bundle หรือซื้อหลายเล่มต่อครั้ง ทำให้ยอดต่อบิลสูง (635 - 760 บาท) ขณะที่ในเดือน ก.ย. ยอดเฉลี่ยต่อบิลอยู่ที่ 385 บาท ซึ่งสะท้อนพฤติกรรมลูกค้าใหม่ที่มักทดลองซื้อเพียง 1 เล่มต่อคำสั่งซื้อ

---

## รายงานที่ 2: จัดอันดับ E-Book ขายดี (Top Selling E-Books)

### 2.1 คำถามที่ต้องตอบ
* E-Book เล่มใดขายได้มากที่สุดตามจำนวนเล่ม และเล่มใดสร้างรายได้สูงสุดให้กับร้าน?

### 2.2 คำสั่ง SQL เชิงวิเคราะห์
```sql
SELECT 
    b.ebook_id,
    b.title,
    c.category_name,
    a.author_name,
    b.price AS current_price,
    SUM(oi.quantity) AS total_copies_sold,
    ROUND(SUM(oi.subtotal), 2) AS total_revenue
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN ebooks b ON oi.ebook_id = b.ebook_id
JOIN categories c ON b.category_id = c.category_id
JOIN authors a ON b.author_id = a.author_id
WHERE o.status = 'CONFIRMED'
GROUP BY b.ebook_id, b.title, c.category_name, a.author_name, b.price
ORDER BY total_copies_sold DESC, total_revenue DESC
LIMIT 10;
```

### 2.3 ผลลัพธ์จากฐานข้อมูลจริง (Top 5 อันดับแรก)
| อันดับ | ชื่อหนังสือ E-Book | หมวดหมู่ | ผู้แต่ง | ราคา (บาท) | ยอดขาย (เล่ม) | รายได้รวม (บาท) |
|:---:|---|---|---|:---:|:---:|:---:|
| 🥇 1 | The Modern Growth Hacking & Digital Ads | ธุรกิจ & การตลาด | อนันต์ การตลาดดิจิทัล | 390.00 | **6** | **2,340.00** |
| 🥈 2 | Data Analytics with SQL & Business Intelligence | วิทยาศาสตร์ข้อมูล & AI | ดร. ธีรภัทร ปัญญาประดิษฐ์ | 380.00 | **5** | **1,900.00** |
| 🥉 3 | Practical Generative AI for Developers | วิทยาศาสตร์ข้อมูล & AI | ดร. ธีรภัทร ปัญญาประดิษฐ์ | 490.00 | **4** | **1,960.00** |
| 4 | Mastering Database Design & SQL | เทคโนโลยี & โปรแกรมมิ่ง | ดร. กิตติพงษ์ วิริยะกุล | 350.00 | **4** | **1,400.00** |
| 5 | Full-Stack Web Development with Python | เทคโนโลยี & โปรแกรมมิ่ง | อาจารย์ พรชัย เทคโนโลยี | 420.00 | **3** | **1,260.00** |

### 2.4 การวิเคราะห์และข้อสรุปเชิงธุรกิจ
* หนังสืออันดับ 1 คือ **"The Modern Growth Hacking & Digital Ads"** ขายได้ 6 เล่ม ทำรายได้รวม 2,340 บาท ซึ่งเป็นกลุ่มหนังสือกลยุทธ์การตลาดยุคดิจิทัล
* หนังสือหมวดวิทยาศาสตร์ข้อมูลและปัญญาประดิษฐ์ (AI) ครองอันดับ 2 และ 3 อย่างโดดเด่น สะท้อนความต้องการของตลาดสายเทคโนโลยีในปัจจุบัน

---

## รายงานที่ 3: ยอดขายตามหมวดหมู่ (Sales by Category)

### 3.1 คำถามที่ต้องตอบ
* หมวดหมู่ใดสามารถสร้างยอดขายและจำนวนเล่มที่ขายได้สูงสุด พร้อมสัดส่วนมาร์เก็ตแชร์ของแต่ละหมวด?

### 3.2 คำสั่ง SQL เชิงวิเคราะห์
```sql
SELECT 
    c.category_id,
    c.category_name,
    COUNT(DISTINCT o.order_id) AS total_orders_involved,
    SUM(oi.quantity) AS total_items_sold,
    ROUND(SUM(oi.subtotal), 2) AS category_revenue,
    ROUND(SUM(oi.subtotal) * 100.0 / (
        SELECT SUM(subtotal) 
        FROM order_items oi2 
        JOIN orders o2 ON oi2.order_id = o2.order_id 
        WHERE o2.status = 'CONFIRMED'
    ), 2) AS revenue_share_percent
FROM categories c
JOIN ebooks b ON c.category_id = b.category_id
JOIN order_items oi ON b.ebook_id = oi.ebook_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status = 'CONFIRMED'
GROUP BY c.category_id, c.category_name
ORDER BY category_revenue DESC;
```

### 3.3 ผลลัพธ์จากฐานข้อมูลจริง
| หมวดหมู่ (Category) | จำนวนออเดอร์ที่สั่ง | ยอดขายรวม (เล่ม) | ยอดเงินรวม (บาท) | ส่วนแบ่งยอดขาย (%) |
|---|:---:|:---:|:---:|:---:|
| **วิทยาศาสตร์ข้อมูล & AI** | 8 | 9 | 3,860.00 | **25.91%** |
| **ธุรกิจ & การตลาด** | 7 | 8 | 2,980.00 | **20.00%** |
| **เทคโนโลยี & การเขียนโปรแกรม** | 7 | 7 | 2,660.00 | **17.85%** |
| **พัฒนาตนเอง & จิตวิทยา** | 6 | 6 | 2,050.00 | **13.76%** |
| **การเงิน & การลงทุน** | 5 | 5 | 1,740.00 | **11.68%** |
| **วรรณกรรม & นวนิยาย** | 6 | 6 | 1,610.00 | **10.80%** |

### 3.4 การวิเคราะห์และข้อสรุปเชิงธุรกิจ
* **หมวดหมู่วิทยาศาสตร์ข้อมูล & AI** ครองแชมป์อันดับ 1 ด้วยส่วนแบ่งรายได้เกือบ 26% ของร้าน เนื่องจากราคาต่อเล่มเฉลี่ยอยู่ในระดับพรีเมียม (380 - 490 บาท) และได้รับความสนใจสูง
* ทุกหมวดหมู่มีการกระจายตัวของยอดขายที่ดี ไม่มีหมวดหมู่ใดที่มียอดขายเป็นศูนย์

---

## รายงานที่ 4: พฤติกรรมลูกค้าและสถานะคำสั่งซื้อ (Customer Behavior & Order Status)

### 4.1 คำถามที่ต้องตอบ
* ลูกค้ารายใดซื้อบ่อย หรือมียอดซื้อสะสมสูงสุด (Customer Lifetime Value) และสถานะคำสั่งซื้อในระบบทั้งหมดมีสัดส่วนอย่างไร?

### 4.2 คำสั่ง SQL เชิงวิเคราะห์

#### ส่วนที่ 4A: ลูกค้าชั้นยอด (Customer Lifetime Value - ใช้ HAVING)
```sql
SELECT 
    u.user_id,
    u.username,
    u.full_name,
    u.email,
    COUNT(o.order_id) AS total_confirmed_orders,
    ROUND(SUM(o.total_amount), 2) AS total_spent,
    ROUND(AVG(o.total_amount), 2) AS avg_order_spend
FROM users u
JOIN orders o ON u.user_id = o.user_id
WHERE o.status = 'CONFIRMED'
GROUP BY u.user_id, u.username, u.full_name, u.email
HAVING COUNT(o.order_id) >= 1
ORDER BY total_spent DESC, total_confirmed_orders DESC
LIMIT 5;
```

#### ส่วนที่ 4B: สัดส่วนสถานะคำสั่งซื้อในระบบทั้งหมด
```sql
SELECT 
    o.status AS order_status,
    COUNT(o.order_id) AS order_count,
    ROUND(SUM(o.total_amount), 2) AS total_amount,
    ROUND(AVG(o.total_amount), 2) AS avg_amount,
    ROUND(COUNT(o.order_id) * 100.0 / (SELECT COUNT(*) FROM orders), 2) AS percentage_of_total_orders
FROM orders o
GROUP BY o.status
ORDER BY order_count DESC;
```

### 4.3 ผลลัพธ์จากฐานข้อมูลจริง

#### ตาราง 4A: ลูกค้าชั้นยอด Top 5
| อันดับ | ชื่อลูกค้า | Username | ยืนยันแล้ว (ครั้ง) | ยอดซื้อสะสมรวม (บาท) | ยอดเฉลี่ยต่อครั้ง |
|:---:|---|---|:---:|:---:|:---:|
| 1 | สุดา เกียรติสกุล | @suda | 5 | **2,850.00** | 570.00 |
| 2 | พลอยไพลิน รัตนศิริ | @ploy | 4 | **2,340.00** | 585.00 |
| 3 | อนันต์ พัฒนกิจ | @anant | 4 | **2,190.00** | 547.50 |
| 4 | ธนากร ตั้งมั่น | @thanakorn | 3 | **1,870.00** | 623.33 |
| 5 | สมชาย ใจดี | @customer1 | 3 | **1,650.00** | 550.00 |

#### ตาราง 4B: สัดส่วนสถานะคำสั่งซื้อทั้งหมด (36 คำสั่งซื้อ)
| สถานะคำสั่งซื้อ | ความหมายทางธุรกิจ | จำนวนคำสั่งซื้อ | มูลค่ารวม (บาท) | สัดส่วน (%) |
|---|---|:---:|:---:|:---:|
| **CONFIRMED** | ชำระเงินแล้ว ตรวจสอบสลิปผ่าน เปิดให้ดาวน์โหลด | **27** | 14,900.00 | **75.00%** |
| **PENDING** | ลูกค้าสั่งซื้อแล้ว รอผู้ดูแลตรวจสอบสลิปจำลอง | **5** | 2,140.00 | **13.89%** |
| **CANCELLED** | ยกเลิกคำสั่งซื้อ / สลิปไม่ถูกต้อง ไม่อนุญาตให้โหลด | **4** | 1,820.00 | **11.11%** |
| **รวมทั้งสิ้น** | - | **36** | **18,860.00** | **100.00%** |

### 4.4 การวิเคราะห์และข้อสรุปเชิงธุรกิจ
* คุณสุดา เกียรติสกุล และคุณพลอยไพลิน เป็นลูกค้ากลุ่ม VIP ที่กลับมาซื้อซ้ำเกิน 4-5 ครั้ง และมียอดซื้อสะสมเกิน 2,000 บาท
* อัตราความสำเร็จของคำสั่งซื้อ (Conversion to Confirmed) อยู่ที่ 75% ซึ่งถือว่ามีสุขภาพทางการเงินของร้านที่ดี โดยคำสั่งซื้อที่ค้างสถานะ PENDING 13.89% เป็นกลุ่มที่รอผู้ดูแลกดอนุมัติสิทธิ์
