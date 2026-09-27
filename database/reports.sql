-- ====================================================================
-- E-Book Store Analytical Reports (4 Required Reports)
-- Database Mini Project - Course Requirements
-- ====================================================================

-- --------------------------------------------------------------------
-- รายงานที่ 1: รายงานยอดขายตามช่วงเวลา (Sales by Time Period)
-- คำถามที่ต้องตอบ: ยอดขาย จำนวนคำสั่งซื้อ และค่าเฉลี่ยต่อคำสั่งซื้อ เปลี่ยนไปอย่างไรตามวันที่หรือเดือน
-- ไวยากรณ์ SQL: JOIN, GROUP BY, SUM, COUNT, AVG, ตัวกรองวันที่/เดือน
-- --------------------------------------------------------------------
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

-- รายงานที่ 1 (แบบรายวัน สำหรับเจาะลึก 30 วันล่าสุด):
SELECT 
    date(o.order_date) AS sale_date,
    COUNT(o.order_id) AS daily_orders,
    ROUND(SUM(o.total_amount), 2) AS daily_sales,
    ROUND(AVG(o.total_amount), 2) AS daily_avg_order
FROM orders o
WHERE o.status = 'CONFIRMED'
  AND o.order_date >= date('now', '-30 days')
GROUP BY date(o.order_date)
ORDER BY sale_date DESC;


-- --------------------------------------------------------------------
-- รายงานที่ 2: รายงาน E-Book ขายดี (Top Selling E-Books)
-- คำถามที่ต้องตอบ: E Book ใดขายได้มากที่สุดตามจำนวนเล่มหรือยอดขาย
-- ไวยากรณ์ SQL: JOIN, GROUP BY, SUM หรือ COUNT, LIMIT
-- --------------------------------------------------------------------
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


-- --------------------------------------------------------------------
-- รายงานที่ 3: รายงานยอดขายตามหมวดหมู่ (Sales by Category)
-- คำถามที่ต้องตอบ: หมวดหมู่ใดสร้างยอดขายและจำนวนรายการสูงสุด
-- ไวยากรณ์ SQL: JOIN หลายตาราง (categories, ebooks, order_items, orders), GROUP BY, SUM
-- --------------------------------------------------------------------
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


-- --------------------------------------------------------------------
-- รายงานที่ 4A: รายงานพฤติกรรมลูกค้าและยอดซื้อสะสม (Customer Purchase Behavior)
-- คำถามที่ต้องตอบ: ลูกค้ารายใดซื้อบ่อยหรือมียอดซื้อสะสมสูง
-- ไวยากรณ์ SQL: JOIN, GROUP BY, HAVING, COUNT, SUM, เงื่อนไขสถานะ
-- --------------------------------------------------------------------
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
LIMIT 15;


-- --------------------------------------------------------------------
-- รายงานที่ 4B: รายงานสถานะคำสั่งซื้อทั้งหมด (Order Status Distribution)
-- คำถามที่ต้องตอบ: แต่ละสถานะมีจำนวนเท่าใด และมูลค่ารวมเท่าใด
-- ไวยากรณ์ SQL: GROUP BY, COUNT, SUM, คำนวณร้อยละ
-- --------------------------------------------------------------------
SELECT 
    o.status AS order_status,
    COUNT(o.order_id) AS order_count,
    ROUND(SUM(o.total_amount), 2) AS total_amount,
    ROUND(AVG(o.total_amount), 2) AS avg_amount,
    ROUND(COUNT(o.order_id) * 100.0 / (SELECT COUNT(*) FROM orders), 2) AS percentage_of_total_orders
FROM orders o
GROUP BY o.status
ORDER BY order_count DESC;
