import sqlite3
import os
import uuid
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ebook_store.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')
SEED_SQL_PATH = os.path.join(os.path.dirname(__file__), 'seed.sql')

def init_database():
    print(f"Initializing database at: {DB_PATH}")
    
    # Remove existing database file if exists to rebuild clean
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print("Removed old database file.")
        except Exception as e:
            print(f"Note: Could not remove old db: {e}")

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    # Read and execute schema
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)
    print("Schema applied successfully.")

    # List of SQL statements to dump into seed.sql
    sql_dump_statements = []

    def record_insert(table, data_dict):
        cols = list(data_dict.keys())
        placeholders = [":" + c for c in cols]
        sql = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join(placeholders)});"
        cursor.execute(sql, data_dict)
        
        # Build SQL dump representation
        val_strs = []
        for c in cols:
            val = data_dict[c]
            if val is None:
                val_strs.append("NULL")
            elif isinstance(val, (int, float)):
                val_strs.append(str(val))
            else:
                escaped = str(val).replace("'", "''")
                val_strs.append(f"'{escaped}'")
        sql_dump_statements.append(f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join(val_strs)});")
        return cursor.lastrowid

    # 1. Insert Roles
    role_customer_id = record_insert('roles', {'role_name': 'customer', 'description': 'ลูกค้าทั่วไป สามารถเลือกซื้อและดาวน์โหลด E-Book'})
    role_admin_id = record_insert('roles', {'role_name': 'admin', 'description': 'ผู้ดูแลระบบ สามารถจัดการหนังสือ หมวดหมู่ คำสั่งซื้อ และดูรายงาน'})

    # 2. Insert Users
    hashed_admin = generate_password_hash('admin123')
    hashed_user = generate_password_hash('user123')

    users_data = [
        {'role_id': role_admin_id, 'username': 'admin', 'email': 'admin@ebookstore.local', 'password_hash': hashed_admin, 'full_name': 'ผู้ดูแลระบบ (Admin Store)', 'phone': '0812345678'},
        {'role_id': role_customer_id, 'username': 'customer1', 'email': 'customer1@test.com', 'password_hash': hashed_user, 'full_name': 'สมชาย ใจดี (บัญชีทดสอบ)', 'phone': '0891112222'},
        {'role_id': role_customer_id, 'username': 'suda', 'email': 'suda.k@gmail.com', 'password_hash': hashed_user, 'full_name': 'สุดา เกียรติสกุล', 'phone': '0842223333'},
        {'role_id': role_customer_id, 'username': 'anant', 'email': 'anant.dev@hotmail.com', 'password_hash': hashed_user, 'full_name': 'อนันต์ พัฒนกิจ', 'phone': '0853334444'},
        {'role_id': role_customer_id, 'username': 'wichai', 'email': 'wichai.c@outlook.com', 'password_hash': hashed_user, 'full_name': 'วิชัย ชาญวิทย์', 'phone': '0864445555'},
        {'role_id': role_customer_id, 'username': 'kanya', 'email': 'kanya.p@gmail.com', 'password_hash': hashed_user, 'full_name': 'กัญญา ประเสริฐผล', 'phone': '0875556666'},
        {'role_id': role_customer_id, 'username': 'thanakorn', 'email': 'thanakorn.t@gmail.com', 'password_hash': hashed_user, 'full_name': 'ธนากร ตั้งมั่น', 'phone': '0886667777'},
        {'role_id': role_customer_id, 'username': 'ploy', 'email': 'ploy.pailin@gmail.com', 'password_hash': hashed_user, 'full_name': 'พลอยไพลิน รัตนศิริ', 'phone': '0897778888'},
        {'role_id': role_customer_id, 'username': 'nattapong', 'email': 'natta.p@gmail.com', 'password_hash': hashed_user, 'full_name': 'ณัฐพงษ์ วิทยากร', 'phone': '0818889999'},
        {'role_id': role_customer_id, 'username': 'waraporn', 'email': 'wara.porn@yahoo.com', 'password_hash': hashed_user, 'full_name': 'วราภรณ์ สุวรรณโชติ', 'phone': '0829990000'}
    ]

    user_ids = []
    for u in users_data:
        uid = record_insert('users', u)
        user_ids.append(uid)
        # Create empty cart for each user
        record_insert('carts', {'user_id': uid})

    # 3. Categories
    categories_data = [
        {'category_name': 'เทคโนโลยี & การเขียนโปรแกรม', 'description': 'คู่มือและเทคโนโลยีการพัฒนาซอฟต์แวร์ เว็บไซต์ และฐานข้อมูล'},
        {'category_name': 'การเงิน & การลงทุน', 'description': 'ศาสตร์การบริหารการเงินส่วนบุคคล หุ้น อสังหาริมทรัพย์ และการลงทุน'},
        {'category_name': 'พัฒนาตนเอง & จิตวิทยา', 'description': 'เคล็ดลับเพิ่มผลผลิต การจัดการอารมณ์ และสร้างนิสัยสู่ความสำเร็จ'},
        {'category_name': 'ธุรกิจ & การตลาด', 'description': 'กลยุทธ์การสร้างธุรกิจ สตาร์ทอัป และการตลาดออนไลน์ยุคใหม่'},
        {'category_name': 'วิทยาศาสตร์ข้อมูล & AI', 'description': 'Machine Learning, Deep Learning และการนำ Generative AI มาประยุกต์ใช้'},
        {'category_name': 'วรรณกรรม & นวนิยาย', 'description': 'วรรณกรรมสร้างสรรค์ นิยายวิทยาศาสตร์ และสารคดีเรื่องเล่า'}
    ]
    category_ids = []
    for c in categories_data:
        cid = record_insert('categories', c)
        category_ids.append(cid)

    # 4. Authors
    authors_data = [
        {'author_name': 'ดร. กิตติพงษ์ วิริยะกุล', 'bio': 'ผู้เชี่ยวชาญด้านสถาปัตยกรรมระบบและฐานข้อมูล ประสบการณ์กว่า 15 ปี', 'email': 'kittipong@techauthor.com'},
        {'author_name': 'อาจารย์ พรชัย เทคโนโลยี', 'bio': 'นักพัฒนาซอฟต์แวร์ฟูลสแตกและอาจารย์พิเศษด้าน Web Engineering', 'email': 'pornchai@devhub.in.th'},
        {'author_name': 'ชัชวาล เศรษฐศาสตร์', 'bio': 'นักวางแผนการเงิน CFP และที่ปรึกษาการลงทุนพอร์ตระดับสากล', 'email': 'chatchawal@wealthcoach.com'},
        {'author_name': 'พญ. ธิดารัตน์ สุขภาพจิต', 'bio': 'จิตแพทย์และนักเขียนหนังสือ Best Seller ด้านการบริหารพลังชีวิต', 'email': 'tidarat@mindfuldr.com'},
        {'author_name': 'อนันต์ การตลาดดิจิทัล', 'bio': 'ผู้บริหารเอเจนซีโฆษณาชั้นนำ ผู้เชี่ยวชาญ Growth Hacking', 'email': 'anant@growthexpert.co'},
        {'author_name': 'ดร. ธีรภัทร ปัญญาประดิษฐ์', 'bio': 'นักวิจัย AI และอาจารย์ภาควิชาวิศวกรรมคอมพิวเตอร์', 'email': 'teerapat@airules.org'},
        {'author_name': 'กวี ศรีสยาม', 'bio': 'นักเขียนนวนิยายแฟนตาซีและไซไฟรางวัลวรรณกรรมสร้างสรรค์', 'email': 'kawee@novelworld.net'},
        {'author_name': 'ณัฐพร นวัตกรรม', 'bio': 'ผู้ก่อตั้งสตาร์ทอัปและวิทยากรด้านนวัตกรรมการบริหารงานสมัยใหม่', 'email': 'nattaporn@innovator.io'}
    ]
    author_ids = []
    for a in authors_data:
        aid = record_insert('authors', a)
        author_ids.append(aid)

    # 5. E-Books
    ebooks_data = [
        {
            'title': 'Mastering Database Design & SQL',
            'author_id': author_ids[0],
            'category_id': category_ids[0],
            'price': 350.00,
            'description': 'เจาะลึกการออกแบบฐานข้อมูลเชิงสัมพันธ์ตั้งแต่ระดับพื้นฐาน Normalization 3NF จนถึงการ Optimize Query ประสิทธิภาพสูง',
            'cover_url': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400&q=80',
            'download_file_url': '/downloads/sample_database_design.pdf',
            'is_active': 1
        },
        {
            'title': 'Full-Stack Web Development with Python',
            'author_id': author_ids[1],
            'category_id': category_ids[0],
            'price': 420.00,
            'description': 'สร้างเว็บแอปพลิเคชันระดับโปรดักชันด้วย Flask, RESTful API และฐานข้อมูล พร้อม Workshop ใช้งานได้จริง',
            'cover_url': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=400&q=80',
            'download_file_url': '/downloads/sample_fullstack_python.pdf',
            'is_active': 1
        },
        {
            'title': 'คู่มือวางแผนภาษีและการลงทุนฉบับประชาชน',
            'author_id': author_ids[2],
            'category_id': category_ids[1],
            'price': 290.00,
            'description': 'เข้าใจการลดหย่อนภาษีอย่างถูกต้อง พร้อมกลยุทธ์สร้างอิสรภาพทางการเงินผ่านกองทุนรวมและหุ้นปันผล',
            'cover_url': 'https://images.unsplash.com/photo-1579532537598-459ecdaf39cc?w=400&q=80',
            'download_file_url': '/downloads/sample_finance_invest.pdf',
            'is_active': 1
        },
        {
            'title': 'จิตวิทยาการบริหารเวลา Focus & Productivity',
            'author_id': author_ids[3],
            'category_id': category_ids[2],
            'price': 250.00,
            'description': 'เคล็ดลับทางประสาทวิทยาในการกำจัดนิสัยผลัดวันประกันพรุ่งและโฟกัสกับงานสำคัญอย่างเต็มศักยภาพ',
            'cover_url': 'https://images.unsplash.com/photo-1506784983877-45594efa4cbe?w=400&q=80',
            'download_file_url': '/downloads/sample_focus_productivity.pdf',
            'is_active': 1
        },
        {
            'title': 'The Modern Growth Hacking & Digital Ads',
            'author_id': author_ids[4],
            'category_id': category_ids[3],
            'price': 390.00,
            'description': 'กลยุทธ์ยิงแอดและสร้าง Funnel ปิดการขายอัตโนมัติ สำหรับธุรกิจออนไลน์ที่ต้องการสเกลยอดขาย 10X',
            'cover_url': 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&q=80',
            'download_file_url': '/downloads/sample_growth_hacking.pdf',
            'is_active': 1
        },
        {
            'title': 'Practical Generative AI for Developers',
            'author_id': author_ids[5],
            'category_id': category_ids[4],
            'price': 490.00,
            'description': 'คู่มือนักพัฒนาในการเชื่อมต่อ LLM APIs, Prompt Engineering, RAG Architecture และ AI Agents',
            'cover_url': 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=400&q=80',
            'download_file_url': '/downloads/sample_generative_ai.pdf',
            'is_active': 1
        },
        {
            'title': 'กำเนิดจักรกลนิรันดร์ (Chronicles of Eternity)',
            'author_id': author_ids[6],
            'category_id': category_ids[5],
            'price': 195.00,
            'description': 'นวนิยายไซไฟแฟนตาซี การเดินทางข้ามห้วงกาลเวลาเพื่อกอบกู้ดวงดาวที่สาบสูญ',
            'cover_url': 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&q=80',
            'download_file_url': '/downloads/sample_scifi_eternity.pdf',
            'is_active': 1
        },
        {
            'title': 'Lean Startup & Product Strategy',
            'author_id': author_ids[7],
            'category_id': category_ids[3],
            'price': 320.00,
            'description': 'คู่มือทดสอบไอเดียธุรกิจ สร้าง MVP และปรับเปลี่ยนทิศทางอย่างรวดเร็วโดยไม่เผางบประมาณทิ้ง',
            'cover_url': 'https://images.unsplash.com/photo-1553729459-efe14ef6055d?w=400&q=80',
            'download_file_url': '/downloads/sample_lean_startup.pdf',
            'is_active': 1
        },
        {
            'title': 'Clean Architecture & Design Patterns in Action',
            'author_id': author_ids[0],
            'category_id': category_ids[0],
            'price': 450.00,
            'description': 'การวางสถาปัตยกรรมโค้ดให้อ่านง่าย ขยายต่อได้ และทดสอบได้ตามหลัก SOLID & Clean Architecture',
            'cover_url': 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=400&q=80',
            'download_file_url': '/downloads/sample_clean_arch.pdf',
            'is_active': 1
        },
        {
            'title': 'จิตวิทยาการเจรจาต่อรองให้ชนะทุกสถานการณ์',
            'author_id': author_ids[3],
            'category_id': category_ids[2],
            'price': 280.00,
            'description': 'ศิลปะการสื่อสารโน้มน้าวใจ การอ่านภาษากาย และการสร้างข้อตกลงแบบ Win-Win ในชีวิตและการงาน',
            'cover_url': 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=400&q=80',
            'download_file_url': '/downloads/sample_negotiation.pdf',
            'is_active': 1
        },
        {
            'title': 'Data Analytics with SQL & Business Intelligence',
            'author_id': author_ids[5],
            'category_id': category_ids[4],
            'price': 380.00,
            'description': 'การสกัดข้อมูลเชิงลึกด้วยคำสั่ง SQL วิเคราะห์แนวโน้มธุรกิจ และสร้าง Dashboard สื่อสารกับผู้บริหาร',
            'cover_url': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&q=80',
            'download_file_url': '/downloads/sample_data_analytics.pdf',
            'is_active': 1
        },
        {
            'title': 'ถอดรหัสจิตวิญญาณแห่งดวงดาว (Lost in Cosmos)',
            'author_id': author_ids[6],
            'category_id': category_ids[5],
            'price': 220.00,
            'description': 'การผจญภัยของนักบินอวกาศผู้โดดเดี่ยว และความลับของอารยธรรมโบราณสุดขอบจักรวาล',
            'cover_url': 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400&q=80',
            'download_file_url': '/downloads/sample_lost_in_cosmos.pdf',
            'is_active': 1
        }
    ]

    ebook_ids = []
    ebook_price_map = {}
    for eb in ebooks_data:
        eid = record_insert('ebooks', eb)
        ebook_ids.append(eid)
        ebook_price_map[eid] = eb['price']

    # 6. Generate 36 realistic orders with dates spanning the last 90 days!
    # Requirement: "อย่างน้อย 30 คำสั่งซื้อ"
    random.seed(42)
    start_date = datetime.now() - timedelta(days=75)
    
    order_statuses = ['CONFIRMED'] * 27 + ['PENDING'] * 5 + ['CANCELLED'] * 4
    random.shuffle(order_statuses)

    customer_uids = user_ids[1:] # Exclude admin

    order_counter = 1001

    for status in order_statuses:
        customer_id = random.choice(customer_uids)
        # Random order date between start_date and now
        random_days_offset = random.uniform(0, 75)
        ord_datetime = start_date + timedelta(days=random_days_offset, hours=random.randint(8, 22), minutes=random.randint(0, 59))
        ord_datetime_str = ord_datetime.strftime('%Y-%m-%d %H:%M:%S')

        order_num = f"ORD-{ord_datetime.strftime('%Y%m%d')}-{order_counter}"
        order_counter += 1

        # Select 1 to 3 distinct ebooks
        num_items = random.choices([1, 2, 3], weights=[50, 35, 15])[0]
        selected_ebook_ids = random.sample(ebook_ids, num_items)

        order_items_to_insert = []
        total_order_amount = 0.0

        for eid in selected_ebook_ids:
            price = ebook_price_map[eid]
            qty = 1 # E-books are typically qty 1 per order
            subtotal = price * qty
            total_order_amount += subtotal
            order_items_to_insert.append({
                'ebook_id': eid,
                'unit_price': price,
                'quantity': qty,
                'subtotal': subtotal
            })

        # Insert order
        ord_id = record_insert('orders', {
            'order_number': order_num,
            'user_id': customer_id,
            'total_amount': total_order_amount,
            'status': status,
            'order_date': ord_datetime_str,
            'notes': f'คำสั่งซื้อผ่านระบบออนไลน์ #{order_num}'
        })

        # Insert order items
        for item in order_items_to_insert:
            item_data = dict(item)
            item_data['order_id'] = ord_id
            record_insert('order_items', item_data)

        # Payment records
        payment_methods = ['PROMPTPAY_QR', 'BANK_TRANSFER', 'MOCK_CREDIT']
        method = random.choice(payment_methods)
        
        if status == 'CONFIRMED':
            pay_status = 'VERIFIED'
            slip_note = f'/static/uploads/slips/mock_slip_{random.randint(1, 5)}.png'
            admin_note = 'ตรวจสอบยอดเงินและสลิปการโอนเรียบร้อยแล้ว'
        elif status == 'PENDING':
            pay_status = 'PENDING'
            slip_note = f'/static/uploads/slips/mock_slip_{random.randint(1, 5)}.png'
            admin_note = 'รอผู้ดูแลระบบตรวจสอบหลักฐานการชำระเงิน'
        else: # CANCELLED
            pay_status = 'REJECTED'
            slip_note = None
            admin_note = 'ลูกค้ายกเลิกคำสั่งซื้อ หรือสลิปไม่ถูกต้อง'

        record_insert('payments', {
            'order_id': ord_id,
            'payment_method': method,
            'amount': total_order_amount,
            'slip_image': slip_note,
            'payment_date': ord_datetime_str,
            'payment_status': pay_status,
            'admin_notes': admin_note
        })

        # If order is CONFIRMED, create download links!
        # Requirement: "ระบบต้องไม่เปิดลิงก์ของหนังสือที่ลูกค้ายังไม่ได้ซื้อหรือคำสั่งซื้อยังไม่ยืนยัน"
        if status == 'CONFIRMED':
            for item in order_items_to_insert:
                token = str(uuid.uuid4())
                record_insert('download_links', {
                    'order_id': ord_id,
                    'ebook_id': item['ebook_id'],
                    'user_id': customer_id,
                    'download_token': token,
                    'expiry_date': (ord_datetime + timedelta(days=365)).strftime('%Y-%m-%d %H:%M:%S'),
                    'download_count': random.randint(0, 3),
                    'is_active': 1,
                    'created_at': ord_datetime_str
                })

    conn.commit()
    conn.close()
    print("Database committed successfully.")

    # Write seed.sql for portability
    with open(SEED_SQL_PATH, 'w', encoding='utf-8') as f:
        f.write("-- ====================================================================\n")
        f.write("-- E-Book Store Seed Data (DML)\n")
        f.write("-- At least 30 orders, realistic customers, ebooks, categories, payments\n")
        f.write("-- ====================================================================\n\n")
        for st in sql_dump_statements:
            f.write(st + "\n")
    print(f"Exported seed SQL to: {SEED_SQL_PATH}")

if __name__ == '__main__':
    init_database()
