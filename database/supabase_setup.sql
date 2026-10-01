-- ====================================================================
-- โครงงานพัฒนาระบบฐานข้อมูล (31-407-102-301)
-- สคริปต์สร้างฐานข้อมูลและข้อมูลตัวอย่างสำหรับ Supabase (PostgreSQL)
-- ครอบคลุม 9 ตารางเชิงสัมพันธ์ (3NF) ตามข้อกำหนดโครงงาน
-- ====================================================================

-- 1. ล้างตารางเดิม (เรียงลำดับตามความสัมพันธ์ Foreign Key)
DROP TABLE IF EXISTS download_links CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS books CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS authors CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS roles CASCADE;

-- ====================================================================
-- โครงสร้างตารางทั้ง 9 ตาราง (DDL: Data Definition Language)
-- ====================================================================

-- 1. ตาราง roles: สิทธิ์และบทบาทผู้ใช้งาน
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 2. ตาราง users: ข้อมูลสมาชิกและผู้ดูแลระบบ
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    role_id INT NOT NULL REFERENCES roles(id) ON DELETE RESTRICT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    phone VARCHAR(30),
    bank_account_name VARCHAR(150),
    bank_account_number VARCHAR(50),
    bank_name VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 3. ตาราง authors: ข้อมูลผู้แต่ง
CREATE TABLE authors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    bio TEXT,
    email VARCHAR(255),
    avatar_url VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 4. ตาราง categories: หมวดหมู่หนังสือ
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 5. ตาราง books: ข้อมูลหนังสือดิจิทัล E-Book
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author_id INT REFERENCES authors(id) ON DELETE SET NULL,
    category_id INT REFERENCES categories(id) ON DELETE SET NULL,
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    cover_color VARCHAR(20) DEFAULT '#2F5D50',
    description TEXT,
    pages INT CHECK (pages >= 0),
    isbn VARCHAR(30) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    file_url VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 6. ตาราง orders: ข้อมูลคำสั่งซื้อหลัก
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE SET NULL,
    checkout_email VARCHAR(255) NOT NULL,
    checkout_name VARCHAR(150) NOT NULL,
    total DECIMAL(10,2) NOT NULL CHECK (total >= 0),
    status VARCHAR(30) NOT NULL DEFAULT 'Confirmed' CHECK (status IN ('Pending', 'Confirmed', 'Completed', 'Cancelled', 'Paid')),
    email_sent BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 7. ตาราง order_items: รายการสินค้าในคำสั่งซื้อ
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    book_id INT NOT NULL REFERENCES books(id) ON DELETE RESTRICT,
    title VARCHAR(255) NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    price_at_time DECIMAL(10,2) NOT NULL CHECK (price_at_time >= 0),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 8. ตาราง payments: ข้อมูลการชำระเงินและสลิปหลักฐาน
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    order_id INT NOT NULL UNIQUE REFERENCES orders(id) ON DELETE CASCADE,
    payment_method VARCHAR(50) NOT NULL CHECK (payment_method IN ('PromptPay', 'BankTransfer', 'CreditCard', 'BANK_TRANSFER', 'PROMPTPAY_QR')),
    slip_url VARCHAR(500),
    amount DECIMAL(10,2) NOT NULL CHECK (amount >= 0),
    status VARCHAR(30) NOT NULL DEFAULT 'Verified' CHECK (status IN ('Pending', 'Verified', 'Rejected')),
    paid_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    verified_at TIMESTAMPTZ
);

-- 9. ตาราง download_links: สิทธิ์และโทเค็นดาวน์โหลดปลอดภัย
CREATE TABLE download_links (
    id SERIAL PRIMARY KEY,
    token VARCHAR(64) UNIQUE NOT NULL,
    order_id INT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    book_id INT NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    download_count INT DEFAULT 0 CHECK (download_count >= 0),
    max_downloads INT DEFAULT 5,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ====================================================================
-- ข้อมูลเริ่มต้น (DML: Data Manipulation Language)
-- ====================================================================

-- 1. เพิ่มข้อมูล roles
INSERT INTO roles (id, name, description) VALUES
(1, 'Admin', 'ผู้ดูแลระบบ มีสิทธิ์จัดการหนังสือ คำสั่งซื้อ และดูรายงานวิเคราะห์'),
(2, 'Customer', 'ลูกค้าทั่วไป มีสิทธิ์เลือกซื้อ สั่งซื้อ แนบสลิป และดาวน์โหลด E-Book');

-- 2. เพิ่มข้อมูล users
INSERT INTO users (id, role_id, email, password_hash, full_name, phone, bank_account_name, bank_account_number, bank_name) VALUES
(1, 1, 'admin@ebookstore.local', 'scrypt:admin123hash', 'ผู้ดูแลระบบ (Admin Store)', '0812345678', 'Admin E-Book', '123-4-56789-0', 'ธนาคารกสิกรไทย'),
(2, 2, 'firts.zx99@gmail.com', 'scrypt:user123hash', 'KANNITI YASO', '0891112222', 'กานต์นิธิ ยะโส', '456-7-89012-3', 'ธนาคารไทยพาณิชย์'),
(3, 2, 'peerat.dev@outlook.com', 'scrypt:user123hash', 'พีรณัฐ สายซอฟต์แวร์', '0842223333', 'พีรณัฐ พัฒนา', '789-0-12345-6', 'ธนาคารกรุงเทพ'),
(4, 2, 'somchai.tech@gmail.com', 'scrypt:user123hash', 'สมชาย สายโค้ด', '0853334444', 'สมชาย ใจมั่น', '234-5-67890-1', 'ธนาคารกสิกรไทย'),
(5, 2, 'tanawat.design@gmail.com', 'scrypt:user123hash', 'ธนวัฒน์ ศิลป์สว่าง', '0864445555', 'ธนวัฒน์ สว่าง', '345-6-78901-2', 'ธนาคารกรุงไทย'),
(6, 2, 'wanida.read@hotmail.com', 'scrypt:user123hash', 'วนิดา นักอ่านตัวยง', '0875556666', 'วนิดา ชื่นชม', '567-8-90123-4', 'ธนาคารไทยพาณิชย์');

-- 3. เพิ่มข้อมูล authors
INSERT INTO authors (id, name, bio, email, avatar_url) VALUES
(1, 'ภรณ์ ภรณ์ภาพ', 'นักเขียนวรรณกรรมรางวัลยอดเยี่ยมและบทกวีร่วมสมัย', 'pornpap@author.com', 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100'),
(2, 'Daniel Reyes', 'Senior Software Architect and Machine Learning Researcher', 'daniel.reyes@techpress.io', 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100'),
(3, 'James Park', 'Full-Stack Lead and Clean Architecture Advocate', 'james.park@devguild.com', 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100'),
(4, 'รัชต์ ทวีวงศ์', 'นักสำรวจดาราศาสตร์และคอลัมนิสต์สารคดีวิทยาศาสตร์', 'ratch@cosmos.in.th', 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100'),
(5, 'Donella Meadows', 'Pioneer in Systems Thinking and Environmental Dynamics', 'donella@systems.org', 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=100');

-- 4. เพิ่มข้อมูล categories
INSERT INTO categories (id, name, slug, description) VALUES
(1, 'นวนิยายและวรรณกรรม', 'literature', 'วรรณกรรมสร้างสรรค์ นิยายแฟนตาซี ไซไฟ และเรื่องสั้นร่วมสมัย'),
(2, 'เทคโนโลยีและคอมพิวเตอร์', 'technology', 'การเขียนโปรแกรม สถาปัตยกรรมระบบ ฐานข้อมูล และ AI สมัยใหม่'),
(3, 'ประวัติศาสตร์และสารคดี', 'documentary', 'สารคดีเจาะลึก ธรรมชาติ ดาราศาสตร์ และประวัติศาสตร์โลก'),
(4, 'ศิลปะและการออกแบบ', 'art-design', 'ทฤษฎีการออกแบบ UI/UX ศิลปะร่วมสมัย และความคิดสร้างสรรค์'),
(5, 'ไลฟ์สไตล์และอาหาร', 'lifestyle', 'คู่มือพัฒนาตนเอง การดูแลสุขภาพ จิตวิทยา และโภชนาการ');

-- 5. เพิ่มข้อมูล books
INSERT INTO books (id, title, author_id, category_id, price, cover_color, description, pages, isbn, is_active, file_url) VALUES
(1, 'แสงจันทร์บนป่าไผ่', 1, 1, 259.00, '#2F5D50', 'การเดินทางเพื่อค้นหาความหมายของชีวิตท่ามกลางธรรมชาติอันเงียบสงบ', 320, '978-616-01-0001-1', TRUE, '/downloads/sample_moonlight.pdf'),
(2, 'The Quiet Algorithm', 2, 2, 389.00, '#1E293B', 'เบื้องหลังการออกแบบอัลกอริทึมที่ทรงพลังและทำงานได้อย่างเงียบเชียบในระบบขนาดใหญ่', 450, '978-616-01-0002-8', TRUE, '/downloads/sample_algorithm.pdf'),
(3, 'Building Calm Software', 3, 2, 449.00, '#0F766E', 'คู่มือพัฒนาซอฟต์แวร์ที่ไม่สร้างความเครียดให้ทั้งนักพัฒนาและผู้ใช้งาน', 280, '978-616-01-0003-5', TRUE, '/downloads/sample_calm_soft.pdf'),
(4, 'ดาวพระศุกร์ก่อนรุ่งสาง', 4, 3, 264.00, '#4338CA', 'สารคดีดาราศาสตร์และการสังเกตการณ์ท้องฟ้าในมุมมองที่คุณไม่เคยสัมผัส', 240, '978-616-01-0004-2', TRUE, '/downloads/sample_venus.pdf'),
(5, 'Thinking in Systems', 5, 2, 399.00, '#B45309', 'มองโลกและปัญหาที่ซับซ้อนให้ทะลุปรุโปร่งด้วยการคิดเชิงระบบ', 310, '978-616-01-0005-9', TRUE, '/downloads/sample_systems.pdf'),
(6, 'สุนทรียศาสตร์แห่งการจัดวาง', 1, 4, 311.00, '#BE185D', 'การสร้างผลงานศิลปะผ่านการจัดองค์ประกอบและแสงเงา', 190, '978-616-01-0006-6', TRUE, '/downloads/sample_layout.pdf'),
(7, 'ความลับของเครื่องเทศ', 4, 5, 306.50, '#92400E', 'ศาสตร์และศิลป์แห่งการใช้เครื่องเทศในเมนูระดับโลก', 220, '978-616-01-0007-3', TRUE, '/downloads/sample_spices.pdf');

-- 6. เพิ่มข้อมูล orders (32 คำสั่งซื้อ ครอบคลุม 4 เดือนย้อนหลังตามรายงานวิเคราะห์)
INSERT INTO orders (id, user_id, checkout_email, checkout_name, total, status, created_at) VALUES
-- เดือน 2026-06 (8 คำสั่งซื้อ, รวม ฿3,599.00)
(1, 2, 'firts.zx99@gmail.com', 'KANNITI YASO', 449.00, 'Confirmed', '2026-06-05 10:15:00+07'),
(2, 3, 'peerat.dev@outlook.com', 'พีรณัฐ สายซอฟต์แวร์', 389.00, 'Confirmed', '2026-06-10 14:20:00+07'),
(3, 4, 'somchai.tech@gmail.com', 'สมชาย สายโค้ด', 259.00, 'Confirmed', '2026-06-15 09:30:00+07'),
(4, 5, 'tanawat.design@gmail.com', 'ธนวัฒน์ ศิลป์สว่าง', 311.00, 'Confirmed', '2026-06-18 16:45:00+07'),
(5, 6, 'wanida.read@hotmail.com', 'วนิดา นักอ่านตัวยง', 399.00, 'Confirmed', '2026-06-21 11:10:00+07'),
(6, 2, 'firts.zx99@gmail.com', 'KANNITI YASO', 778.00, 'Confirmed', '2026-06-25 13:00:00+07'),
(7, 3, 'peerat.dev@outlook.com', 'พีรณัฐ สายซอฟต์แวร์', 264.00, 'Confirmed', '2026-06-28 17:30:00+07'),
(8, 4, 'somchai.tech@gmail.com', 'สมชาย สายโค้ด', 750.00, 'Confirmed', '2026-06-30 19:15:00+07'),

-- เดือน 2026-07 (8 คำสั่งซื้อ, รวม ฿3,759.00)
(9, 5, 'tanawat.design@gmail.com', 'ธนวัฒน์ ศิลป์สว่าง', 389.00, 'Confirmed', '2026-07-04 10:00:00+07'),
(10, 6, 'wanida.read@hotmail.com', 'วนิดา นักอ่านตัวยง', 449.00, 'Confirmed', '2026-07-08 14:15:00+07'),
(11, 2, 'firts.zx99@gmail.com', 'KANNITI YASO', 259.00, 'Confirmed', '2026-07-12 11:20:00+07'),
(12, 3, 'peerat.dev@outlook.com', 'พีรณัฐ สายซอฟต์แวร์', 523.00, 'Confirmed', '2026-07-15 16:00:00+07'),
(13, 4, 'somchai.tech@gmail.com', 'สมชาย สายโค้ด', 399.00, 'Confirmed', '2026-07-19 12:45:00+07'),
(14, 5, 'tanawat.design@gmail.com', 'ธนวัฒน์ ศิลป์สว่าง', 622.00, 'Confirmed', '2026-07-22 15:30:00+07'),
(15, 6, 'wanida.read@hotmail.com', 'วนิดา นักอ่านตัวยง', 306.50, 'Confirmed', '2026-07-26 18:00:00+07'),
(16, 2, 'firts.zx99@gmail.com', 'KANNITI YASO', 811.50, 'Confirmed', '2026-07-29 20:10:00+07'),

-- เดือน 2026-08 (8 คำสั่งซื้อ, รวม ฿3,738.00)
(17, 3, 'peerat.dev@outlook.com', 'พีรณัฐ สายซอฟต์แวร์', 389.00, 'Confirmed', '2026-08-03 09:15:00+07'),
(18, 4, 'somchai.tech@gmail.com', 'สมชาย สายโค้ด', 449.00, 'Confirmed', '2026-08-07 13:40:00+07'),
(19, 5, 'tanawat.design@gmail.com', 'ธนวัฒน์ ศิลป์สว่าง', 259.00, 'Confirmed', '2026-08-11 11:00:00+07'),
(20, 6, 'wanida.read@hotmail.com', 'วนิดา นักอ่านตัวยง', 264.00, 'Confirmed', '2026-08-15 17:20:00+07'),
(21, 2, 'firts.zx99@gmail.com', 'KANNITI YASO', 399.00, 'Confirmed', '2026-08-19 14:50:00+07'),
(22, 3, 'peerat.dev@outlook.com', 'พีรณัฐ สายซอฟต์แวร์', 974.00, 'Confirmed', '2026-08-23 16:10:00+07'),
(23, 4, 'somchai.tech@gmail.com', 'สมชาย สายโค้ด', 698.00, 'Confirmed', '2026-08-27 10:30:00+07'),
(24, 2, 'firts.zx99@gmail.com', 'KANNITI YASO', 306.00, 'Confirmed', '2026-08-31 18:45:00+07'),

-- เดือน 2026-09 (8 คำสั่งซื้อ, รวม ฿2,791.00)
(25, 5, 'tanawat.design@gmail.com', 'ธนวัฒน์ ศิลป์สว่าง', 363.00, 'Confirmed', '2026-09-04 10:10:00+07'),
(26, 6, 'wanida.read@hotmail.com', 'วนิดา นักอ่านตัวยง', 259.00, 'Confirmed', '2026-09-08 14:00:00+07'),
(27, 2, 'firts.zx99@gmail.com', 'KANNITI YASO', 389.00, 'Confirmed', '2026-09-12 11:30:00+07'),
(28, 3, 'peerat.dev@outlook.com', 'พีรณัฐ สายซอฟต์แวร์', 449.00, 'Confirmed', '2026-09-16 15:45:00+07'),
(29, 4, 'somchai.tech@gmail.com', 'สมชาย สายโค้ด', 264.00, 'Confirmed', '2026-09-20 12:20:00+07'),
(30, 2, 'firts.zx99@gmail.com', 'KANNITI YASO', 518.00, 'Confirmed', '2026-09-24 16:50:00+07'),
(31, 6, 'wanida.read@hotmail.com', 'วนิดา นักอ่านตัวยง', 215.00, 'Pending', '2026-09-27 18:00:00+07'),
(32, 2, 'firts.zx99@gmail.com', 'KANNITI YASO', 334.00, 'Confirmed', '2026-09-30 21:00:00+07');

-- 7. เพิ่มข้อมูล order_items (ตัวอย่างสินค้าในแต่ละคำสั่งซื้อ)
INSERT INTO order_items (order_id, book_id, title, quantity, price_at_time) VALUES
(1, 3, 'Building Calm Software', 1, 449.00),
(2, 2, 'The Quiet Algorithm', 1, 389.00),
(3, 1, 'แสงจันทร์บนป่าไผ่', 1, 259.00),
(4, 6, 'สุนทรียศาสตร์แห่งการจัดวาง', 1, 311.00),
(5, 5, 'Thinking in Systems', 1, 399.00),
(6, 2, 'The Quiet Algorithm', 2, 389.00),
(7, 4, 'ดาวพระศุกร์ก่อนรุ่งสาง', 1, 264.00),
(8, 1, 'แสงจันทร์บนป่าไผ่', 2, 259.00),
(9, 2, 'The Quiet Algorithm', 1, 389.00),
(10, 3, 'Building Calm Software', 1, 449.00),
(11, 1, 'แสงจันทร์บนป่าไผ่', 1, 259.00),
(12, 4, 'ดาวพระศุกร์ก่อนรุ่งสาง', 1, 264.00),
(13, 5, 'Thinking in Systems', 1, 399.00),
(14, 6, 'สุนทรียศาสตร์แห่งการจัดวาง', 2, 311.00),
(15, 7, 'ความลับของเครื่องเทศ', 1, 306.50),
(16, 1, 'แสงจันทร์บนป่าไผ่', 3, 259.00),
(17, 2, 'The Quiet Algorithm', 1, 389.00),
(18, 3, 'Building Calm Software', 1, 449.00),
(19, 1, 'แสงจันทร์บนป่าไผ่', 1, 259.00),
(20, 4, 'ดาวพระศุกร์ก่อนรุ่งสาง', 1, 264.00),
(21, 5, 'Thinking in Systems', 1, 399.00),
(22, 3, 'Building Calm Software', 2, 449.00),
(23, 1, 'แสงจันทร์บนป่าไผ่', 2, 259.00),
(24, 7, 'ความลับของเครื่องเทศ', 1, 306.00),
(25, 6, 'สุนทรียศาสตร์แห่งการจัดวาง', 1, 311.00),
(26, 1, 'แสงจันทร์บนป่าไผ่', 1, 259.00),
(27, 2, 'The Quiet Algorithm', 1, 389.00),
(28, 3, 'Building Calm Software', 1, 449.00),
(29, 4, 'ดาวพระศุกร์ก่อนรุ่งสาง', 1, 264.00),
(30, 1, 'แสงจันทร์บนป่าไผ่', 2, 259.00),
(31, 7, 'ความลับของเครื่องเทศ', 1, 215.00),
(32, 2, 'The Quiet Algorithm', 1, 334.00);

-- 8. เพิ่มข้อมูล payments (การชำระเงินจำลอง)
INSERT INTO payments (order_id, payment_method, slip_url, amount, status, paid_at, verified_at)
SELECT id, 'PromptPay', '/static/uploads/slips/mock_slip_' || ((id % 5) + 1) || '.svg', total, 'Verified', created_at, created_at
FROM orders WHERE status = 'Confirmed';

-- 9. เพิ่มข้อมูล download_links (สิทธิ์ดาวน์โหลดสำหรับคำสั่งซื้อที่เสร็จสมบูรณ์)
INSERT INTO download_links (token, order_id, book_id, download_count, max_downloads, expires_at, created_at)
SELECT 
    md5(random()::text || clock_timestamp()::text),
    oi.order_id,
    oi.book_id,
    FLOOR(random() * 3)::INT,
    5,
    o.created_at + INTERVAL '1 year',
    o.created_at
FROM order_items oi
JOIN orders o ON oi.order_id = o.id
WHERE o.status = 'Confirmed';

-- รีเซ็ตค่า Sequence ID ของตารางทั้งหมดให้พร้อมใช้งานกับ Record ใหม่
SELECT setval('roles_id_seq', (SELECT MAX(id) FROM roles));
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));
SELECT setval('authors_id_seq', (SELECT MAX(id) FROM authors));
SELECT setval('categories_id_seq', (SELECT MAX(id) FROM categories));
SELECT setval('books_id_seq', (SELECT MAX(id) FROM books));
SELECT setval('orders_id_seq', (SELECT MAX(id) FROM orders));
SELECT setval('order_items_id_seq', (SELECT MAX(id) FROM order_items));
SELECT setval('payments_id_seq', (SELECT MAX(id) FROM payments));
SELECT setval('download_links_id_seq', (SELECT MAX(id) FROM download_links));

-- ====================================================================
-- ตรวจสอบความถูกต้อง (Verification Queries)
-- ====================================================================
-- ทดสอบดึงสรุปยอดขายแต่ละเดือน
SELECT 
    TO_CHAR(o.created_at, 'YYYY-MM') AS sale_month,
    COUNT(o.id) AS total_orders,
    SUM(o.total) AS total_sales,
    ROUND(AVG(o.total), 2) AS avg_order_value
FROM orders o
WHERE o.status IN ('Confirmed', 'Completed', 'Paid')
GROUP BY TO_CHAR(o.created_at, 'YYYY-MM')
ORDER BY sale_month DESC;
