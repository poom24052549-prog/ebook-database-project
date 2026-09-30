# ฟังก์ชันที่ 9: รายงานวิเคราะห์ข้อมูลจริง 4 รายงานและการส่งออก (Analytical Reports & Export)
**โครงงาน:** Mini Project Database ร้านขาย E-Book  
**หมวดหมู่:** รายงานวิเคราะห์จากข้อมูลจริง ตามข้อกำหนดหัวข้อ 3 และหัวข้อ 5  

---

## 1. วัตถุประสงค์ของฟังก์ชัน
เพื่อให้ผู้บริหารหรือผู้ดูแลร้านสามารถวิเคราะห์ภาพรวมธุรกิจ, ตรวจสอบแนวโน้มยอดขายตามช่วงเวลา, จัดอันดับสินค้าขายดี, วิเคราะห์ความนิยมตามหมวดหมู่, และดูพฤติกรรมลูกค้าชั้นยอด ผ่านคำสั่ง SQL เชิงวิเคราะห์ขั้นสูง (`JOIN`, `GROUP BY`, `HAVING`, `AGGREGATE FUNCTIONS`) พร้อมแสดงผลเป็นแผนภูมิ (Charts) และสามารถดาวน์โหลดเป็นไฟล์ CSV สำหรับเปิดใน Microsoft Excel ได้

---

## 2. หน้าจอและเส้นทางที่เกี่ยวข้อง (Routes & Templates)
* **`/admin/reports`** (`templates/admin/reports.html`): หน้าจอรวมรายงานทั้ง 4 ฉบับ แสดงผลแบบแท็บ (Tabs) พร้อมกราฟ Interactive Chart.js
* **`/admin/reports/export/<int:report_id>`**: เส้นทางดาวน์โหลดไฟล์ CSV รายงานที่ 1, 2, 3 หรือ 4

---

## 3. รายละเอียดและขั้นตอนของแต่ละรายงาน (The 4 Reports)

### 📊 รายงานที่ 1: ยอดขายตามช่วงเวลา (Sales by Time Period)
* **คำถามที่ตอบ:** ยอดขาย จำนวนคำสั่งซื้อ และค่าเฉลี่ยต่อคำสั่งซื้อ (AOV) เปลี่ยนแปลงไปอย่างไรตามวันหรือเดือน?
* **คำสั่ง SQL:**
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
* **การแสดงผล:** กราฟเส้น (Line Chart) แสดงแนวโน้มยอดขาย และตารางสรุปรายเดือน พร้อมตารางเจาะลึก 15 วันล่าสุด

---

### 🏆 รายงานที่ 2: จัดอันดับ E-Book ขายดี (Top Selling E-Books)
* **คำถามที่ตอบ:** E-Book เล่มใดขายได้มากที่สุดตามจำนวนเล่ม หรือสร้างยอดขายสูงสุด?
* **คำสั่ง SQL:**
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
* **การแสดงผล:** แผนภูมิแท่งแนวนอน (Horizontal Bar Chart) และตารางจัดอันดับ Top 10 พร้อมเหรียญรางวัล 🥇 🥈 🥉

---

### 🏷️ รายงานที่ 3: ยอดขายตามหมวดหมู่ (Sales by Category)
* **คำถามที่ตอบ:** หมวดหมู่ใดสร้างยอดขายและจำนวนเล่มสูงสุด และมีส่วนแบ่งยอดขายกี่เปอร์เซ็นต์?
* **คำสั่ง SQL:**
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
* **การแสดงผล:** แผนภูมิวงกลม (Doughnut Chart) และตารางสัดส่วนมาร์เก็ตแชร์ของแต่ละหมวดหมู่

---

### 👥 รายงานที่ 4: ลูกค้าและคำสั่งซื้อ (Customer Behavior & Status Breakdown)
* **คำถามที่ตอบ:** ลูกค้ารายใดซื้อบ่อยหรือมียอดซื้อสะสมสูง และแต่ละสถานะมีจำนวนเท่าใด?
* **คำสั่ง SQL 4A (ลูกค้าชั้นยอด - ใช้ `HAVING`):**
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
  LIMIT 10;
  ```
* **คำสั่ง SQL 4B (สัดส่วนสถานะคำสั่งซื้อทั้งหมด):**
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
* **การแสดงผล:** ตารางจัดอันดับลูกค้า Customer Lifetime Value (LTV) และตารางแสดงสัดส่วนสถานะทั้ง 3 แบบ (`CONFIRMED`, `PENDING`, `CANCELLED`)

---

## 4. ระบบการส่งออกข้อมูล (Export to CSV Feature)
* ในแต่ละรายงานจะมีปุ่มสีเขียว **"ส่งออก CSV (Excel)"**
* **เทคนิคการเข้ารหัสภาษาไทย (UTF-8 with BOM):** เซิร์ฟเวอร์จะแนบไบต์ Byte Order Mark (`\ufeff`) ไว้ที่จุดเริ่มต้นของไฟล์ CSV ทำให้เมื่อเปิดด้วยโปรแกรม **Microsoft Excel บน Windows** ตัวหนังสือภาษาไทยจะไม่กลายเป็นภาษาต่างดาวและอ่านได้อย่างสวยงามสมบูรณ์แบบ
