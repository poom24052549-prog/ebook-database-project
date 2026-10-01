import os
import sqlite3
import uuid
import time
from datetime import datetime
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, send_from_directory, Response, abort, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'ebook_store.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads', 'slips')
DOWNLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'downloads')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Auto-initialize database if not present (useful for cloud deploys)
if not os.path.exists(DB_PATH):
    try:
        from database.init_db import init_database
        init_database()
        import create_sample_files
    except Exception as e:
        print(f"Auto-init db notice: {e}")

app = Flask(__name__)
app.secret_key = 'super-secret-ebook-database-mini-project-key-2026'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# -------------------------------------------------------------
# Context Processors & Decorators
# -------------------------------------------------------------
@app.context_processor
def inject_global_data():
    cart_count = 0
    categories = []
    current_user = None
    try:
        conn = get_db()
        # Categories for navbar dropdown
        categories = conn.execute("SELECT * FROM categories ORDER BY category_name ASC").fetchall()
        
        # User & Cart count
        if 'user_id' in session:
            current_user = conn.execute(
                "SELECT u.*, r.role_name FROM users u JOIN roles r ON u.role_id = r.role_id WHERE u.user_id = ?",
                (session['user_id'],)
            ).fetchone()
            
            cart_row = conn.execute("SELECT cart_id FROM carts WHERE user_id = ?", (session['user_id'],)).fetchone()
            if cart_row:
                item_sum = conn.execute(
                    "SELECT COALESCE(SUM(quantity), 0) as total FROM cart_items WHERE cart_id = ?",
                    (cart_row['cart_id'],)
                ).fetchone()
                cart_count = item_sum['total'] if item_sum else 0
        conn.close()
    except Exception as e:
        print(f"Context processor error: {e}")
    
    return dict(cart_count=cart_count, global_categories=categories, current_user=current_user)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('กรุณาเข้าสู่ระบบก่อนดำเนินการ', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role_name') != 'admin':
            flash('หน้านี้สำหรับผู้ดูแลระบบ (Admin) เท่านั้น', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# -------------------------------------------------------------
# Frontend Routes (Customers & Public)
# -------------------------------------------------------------
@app.route('/')
def index():
    category_id = request.args.get('category', type=int)
    search_query = request.args.get('q', '').strip()
    sort_by = request.args.get('sort', 'newest')

    conn = get_db()
    sql = """
        SELECT b.*, a.author_name, c.category_name 
        FROM ebooks b
        JOIN authors a ON b.author_id = a.author_id
        JOIN categories c ON b.category_id = c.category_id
        WHERE b.is_active = 1
    """
    params = []

    if category_id:
        sql += " AND b.category_id = ?"
        params.append(category_id)
    if search_query:
        sql += " AND (b.title LIKE ? OR b.description LIKE ? OR a.author_name LIKE ?)"
        like_term = f"%{search_query}%"
        params.extend([like_term, like_term, like_term])

    if sort_by == 'price_asc':
        sql += " ORDER BY b.price ASC"
    elif sort_by == 'price_desc':
        sql += " ORDER BY b.price DESC"
    elif sort_by == 'title':
        sql += " ORDER BY b.title ASC"
    else:
        sql += " ORDER BY b.ebook_id DESC"

    ebooks = conn.execute(sql, params).fetchall()
    
    selected_category = None
    if category_id:
        selected_category = conn.execute("SELECT * FROM categories WHERE category_id = ?", (category_id,)).fetchone()

    conn.close()
    return render_template('index.html', ebooks=ebooks, selected_category=selected_category, search_query=search_query, sort_by=sort_by)

@app.route('/ebook/<int:ebook_id>')
def ebook_detail(ebook_id):
    conn = get_db()
    ebook = conn.execute("""
        SELECT b.*, a.author_name, a.bio as author_bio, c.category_name 
        FROM ebooks b
        JOIN authors a ON b.author_id = a.author_id
        JOIN categories c ON b.category_id = c.category_id
        WHERE b.ebook_id = ?
    """, (ebook_id,)).fetchone()

    if not ebook:
        conn.close()
        flash('ไม่พบหนังสือที่ท่านต้องการ', 'warning')
        return redirect(url_for('index'))

    # Check if logged in user already purchased and confirmed
    has_purchased = False
    download_token = None
    if 'user_id' in session:
        dl_row = conn.execute("""
            SELECT dl.download_token 
            FROM download_links dl
            JOIN orders o ON dl.order_id = o.order_id
            WHERE dl.user_id = ? AND dl.ebook_id = ? AND o.status = 'CONFIRMED' AND dl.is_active = 1
            LIMIT 1
        """, (session['user_id'], ebook_id)).fetchone()
        if dl_row:
            has_purchased = True
            download_token = dl_row['download_token']

    # Related books in same category
    related = conn.execute("""
        SELECT b.*, a.author_name 
        FROM ebooks b
        JOIN authors a ON b.author_id = a.author_id
        WHERE b.category_id = ? AND b.ebook_id != ? AND b.is_active = 1
        LIMIT 4
    """, (ebook['category_id'], ebook_id)).fetchall()

    conn.close()
    return render_template('ebook_detail.html', ebook=ebook, has_purchased=has_purchased, download_token=download_token, related=related)

# -------------------------------------------------------------
# User Authentication & Profile
# -------------------------------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not full_name or not username or not email or not password:
            flash('กรุณากรอกข้อมูลที่จำเป็นให้ครบถ้วน', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('รหัสผ่านและการยืนยันรหัสผ่านไม่ตรงกัน', 'danger')
            return render_template('register.html')

        conn = get_db()
        existing = conn.execute("SELECT user_id FROM users WHERE username = ? OR email = ?", (username, email)).fetchone()
        if existing:
            conn.close()
            flash('ชื่อผู้ใช้หรืออีเมลนี้มีในระบบแล้ว กรุณาใช้ข้อมูลอื่น', 'danger')
            return render_template('register.html')

        # Insert new customer
        hashed = generate_password_hash(password)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (role_id, username, email, password_hash, full_name, phone)
                VALUES (1, ?, ?, ?, ?, ?)
            """, (username, email, hashed, full_name, phone))
            new_uid = cursor.lastrowid
            # Create cart
            cursor.execute("INSERT INTO carts (user_id) VALUES (?)", (new_uid,))
            conn.commit()
            conn.close()

            flash('สมัครสมาชิกสำเร็จแล้ว! กรุณาเข้าสู่ระบบ', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            conn.rollback()
            conn.close()
            flash(f'เกิดข้อผิดพลาดในการลงทะเบียน: {e}', 'danger')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        next_url = request.args.get('next')

        conn = get_db()
        user = conn.execute("""
            SELECT u.*, r.role_name 
            FROM users u
            JOIN roles r ON u.role_id = r.role_id
            WHERE u.username = ? OR u.email = ?
        """, (username, username)).fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['role_name'] = user['role_name']

            flash(f'ยินดีต้อนรับคุณ {user["full_name"]}!', 'success')
            if user['role_name'] == 'admin':
                return redirect(next_url or url_for('admin_dashboard'))
            return redirect(next_url or url_for('index'))
        else:
            flash('ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('ออกจากระบบเรียบร้อยแล้ว', 'info')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    conn = get_db()
    user_id = session['user_id']

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        new_password = request.form.get('new_password', '').strip()

        if full_name:
            if new_password:
                hashed = generate_password_hash(new_password)
                conn.execute("UPDATE users SET full_name = ?, phone = ?, password_hash = ? WHERE user_id = ?",
                             (full_name, phone, hashed, user_id))
            else:
                conn.execute("UPDATE users SET full_name = ?, phone = ? WHERE user_id = ?",
                             (full_name, phone, user_id))
            conn.commit()
            session['full_name'] = full_name
            flash('บันทึกการแก้ไขข้อมูลส่วนตัวเรียบร้อยแล้ว', 'success')

    user = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    # Order history count
    order_summary = conn.execute("""
        SELECT 
            COUNT(*) as total_orders,
            SUM(CASE WHEN status = 'CONFIRMED' THEN 1 ELSE 0 END) as confirmed_orders,
            COALESCE(SUM(CASE WHEN status = 'CONFIRMED' THEN total_amount ELSE 0 END), 0) as total_spent
        FROM orders WHERE user_id = ?
    """, (user_id,)).fetchone()

    conn.close()
    return render_template('profile.html', user=user, order_summary=order_summary)

# -------------------------------------------------------------
# Cart & Checkout Flow
# -------------------------------------------------------------
@app.route('/cart')
@login_required
def view_cart():
    conn = get_db()
    cart = conn.execute("SELECT cart_id FROM carts WHERE user_id = ?", (session['user_id'],)).fetchone()
    items = []
    total = 0.0
    if cart:
        items = conn.execute("""
            SELECT ci.*, b.title, b.price, b.cover_url, a.author_name, (ci.quantity * b.price) as item_total
            FROM cart_items ci
            JOIN ebooks b ON ci.ebook_id = b.ebook_id
            JOIN authors a ON b.author_id = a.author_id
            WHERE ci.cart_id = ?
            ORDER BY ci.added_at DESC
        """, (cart['cart_id'],)).fetchall()
        total = sum(item['item_total'] for item in items)
    conn.close()
    return render_template('cart.html', items=items, total=total)

@app.route('/cart/add/<int:ebook_id>', methods=['POST'])
@login_required
def add_to_cart(ebook_id):
    conn = get_db()
    # Ensure ebook is valid and active
    ebook = conn.execute("SELECT * FROM ebooks WHERE ebook_id = ? AND is_active = 1", (ebook_id,)).fetchone()
    if not ebook:
        conn.close()
        flash('หนังสือเล่มนี้ไม่พร้อมจำหน่าย', 'warning')
        return redirect(url_for('index'))

    # Ensure user has a cart
    cart = conn.execute("SELECT cart_id FROM carts WHERE user_id = ?", (session['user_id'],)).fetchone()
    if not cart:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO carts (user_id) VALUES (?)", (session['user_id'],))
        cart_id = cursor.lastrowid
    else:
        cart_id = cart['cart_id']

    # Check if already in cart
    existing = conn.execute("SELECT cart_item_id, quantity FROM cart_items WHERE cart_id = ? AND ebook_id = ?",
                            (cart_id, ebook_id)).fetchone()
    if existing:
        conn.execute("UPDATE cart_items SET quantity = quantity + 1 WHERE cart_item_id = ?", (existing['cart_item_id'],))
    else:
        conn.execute("INSERT INTO cart_items (cart_id, ebook_id, quantity) VALUES (?, ?, 1)", (cart_id, ebook_id))

    conn.commit()
    conn.close()
    flash(f'เพิ่ม "{ebook["title"]}" ลงในตะกร้าเรียบร้อยแล้ว', 'success')
    return redirect(request.referrer or url_for('view_cart'))

@app.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    action = request.form.get('action') # 'increase', 'decrease' or direct quantity
    qty = request.form.get('quantity', type=int)

    conn = get_db()
    item = conn.execute("""
        SELECT ci.* FROM cart_items ci
        JOIN carts c ON ci.cart_id = c.cart_id
        WHERE ci.cart_item_id = ? AND c.user_id = ?
    """, (item_id, session['user_id'])).fetchone()

    if item:
        if action == 'increase':
            new_qty = item['quantity'] + 1
            conn.execute("UPDATE cart_items SET quantity = ? WHERE cart_item_id = ?", (new_qty, item_id))
        elif action == 'decrease':
            new_qty = item['quantity'] - 1
            if new_qty > 0:
                conn.execute("UPDATE cart_items SET quantity = ? WHERE cart_item_id = ?", (new_qty, item_id))
            else:
                conn.execute("DELETE FROM cart_items WHERE cart_item_id = ?", (item_id,))
        elif qty is not None:
            if qty > 0:
                conn.execute("UPDATE cart_items SET quantity = ? WHERE cart_item_id = ?", (qty, item_id))
            else:
                conn.execute("DELETE FROM cart_items WHERE cart_item_id = ?", (item_id,))
        conn.commit()

    conn.close()
    return redirect(url_for('view_cart'))

@app.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    conn = get_db()
    conn.execute("""
        DELETE FROM cart_items 
        WHERE cart_item_id = ? AND cart_id IN (SELECT cart_id FROM carts WHERE user_id = ?)
    """, (item_id, session['user_id']))
    conn.commit()
    conn.close()
    flash('ลบรายการออกจากตะกร้าเรียบร้อยแล้ว', 'info')
    return redirect(url_for('view_cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    conn = get_db()
    cart = conn.execute("SELECT cart_id FROM carts WHERE user_id = ?", (session['user_id'],)).fetchone()
    if not cart:
        conn.close()
        flash('ตะกร้าสินค้าว่างเปล่า', 'warning')
        return redirect(url_for('index'))

    items = conn.execute("""
        SELECT ci.*, b.title, b.price, (ci.quantity * b.price) as item_total
        FROM cart_items ci
        JOIN ebooks b ON ci.ebook_id = b.ebook_id
        WHERE ci.cart_id = ?
    """, (cart['cart_id'],)).fetchall()

    if not items:
        conn.close()
        flash('ไม่มีสินค้าในตะกร้าสำหรับการชำระเงิน', 'warning')
        return redirect(url_for('index'))

    total_amount = sum(item['item_total'] for item in items)

    if request.method == 'POST':
        payment_method = request.form.get('payment_method', 'PROMPTPAY_QR')
        notes = request.form.get('notes', '').strip()
        slip_ref = request.form.get('slip_ref', '').strip()

        # Handle mock slip upload if provided
        slip_path = None
        if 'slip_file' in request.files:
            file = request.files['slip_file']
            if file and file.filename != '':
                ext = file.filename.rsplit('.', 1)[-1].lower()
                if ext in ['png', 'jpg', 'jpeg', 'webp', 'pdf', 'svg']:
                    filename = f"slip_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}.{ext}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    slip_path = f"/static/uploads/slips/{filename}"

        if not slip_path:
            # Default to simulated slip if user didn't upload
            slip_path = f"/static/uploads/slips/mock_slip_1.svg"

        # Generate unique order number
        order_num = f"ORD-{datetime.now().strftime('%Y%m%d')}-{random_order_suffix()}"

        try:
            cursor = conn.cursor()
            # 1. Create order
            cursor.execute("""
                INSERT INTO orders (order_number, user_id, total_amount, status, notes)
                VALUES (?, ?, ?, 'PENDING', ?)
            """, (order_num, session['user_id'], total_amount, notes or f"ชำระแบบจำลอง ({payment_method})"))
            order_id = cursor.lastrowid

            # 2. Create order items
            for it in items:
                cursor.execute("""
                    INSERT INTO order_items (order_id, ebook_id, unit_price, quantity, subtotal)
                    VALUES (?, ?, ?, ?, ?)
                """, (order_id, it['ebook_id'], it['price'], it['quantity'], it['item_total']))

            # 3. Create payment record
            cursor.execute("""
                INSERT INTO payments (order_id, payment_method, amount, slip_image, payment_status, admin_notes)
                VALUES (?, ?, ?, ?, 'PENDING', ?)
            """, (order_id, payment_method, total_amount, slip_path, f"รหัสอ้างอิง: {slip_ref or 'SIMULATED-PAYMENT'}"))

            # 4. Clear cart items
            cursor.execute("DELETE FROM cart_items WHERE cart_id = ?", (cart['cart_id'],))

            conn.commit()
            conn.close()

            flash('สั่งซื้อและส่งหลักฐานจำลองสำเร็จ! คำสั่งซื้อของคุณอยู่ระหว่างรอผู้ดูแลระบบตรวจสอบยืนยัน', 'success')
            return redirect(url_for('my_orders'))
        except Exception as e:
            conn.rollback()
            conn.close()
            flash(f'เกิดข้อผิดพลาดในการสั่งซื้อ: {e}', 'danger')

    conn.close()
    return render_template('checkout.html', items=items, total_amount=total_amount)

def random_order_suffix():
    import random
    return f"{random.randint(2000, 9999)}"

# -------------------------------------------------------------
# Customer Orders & Secure Download Logic
# -------------------------------------------------------------
@app.route('/my-orders')
@login_required
def my_orders():
    conn = get_db()
    orders = conn.execute("""
        SELECT o.*, p.payment_method, p.payment_status, p.slip_image,
               COUNT(oi.order_item_id) as total_items
        FROM orders o
        LEFT JOIN payments p ON o.order_id = p.order_id
        LEFT JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.user_id = ?
        GROUP BY o.order_id
        ORDER BY o.order_date DESC
    """, (session['user_id'],)).fetchall()

    conn.close()
    return render_template('my_orders.html', orders=orders)

@app.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    conn = get_db()
    # Check ownership or admin
    order = conn.execute("""
        SELECT o.*, u.full_name, u.email, u.phone, p.payment_method, p.payment_status, p.slip_image, p.payment_date, p.admin_notes
        FROM orders o
        JOIN users u ON o.user_id = u.user_id
        LEFT JOIN payments p ON o.order_id = p.order_id
        WHERE o.order_id = ?
    """, (order_id,)).fetchone()

    if not order:
        conn.close()
        flash('ไม่พบคำสั่งซื้อนี้', 'warning')
        return redirect(url_for('my_orders'))

    # Security check: must be owner or admin
    if order['user_id'] != session['user_id'] and session.get('role_name') != 'admin':
        conn.close()
        flash('คุณไม่มีสิทธิ์เข้าถึงคำสั่งซื้อนี้', 'danger')
        return redirect(url_for('index'))

    items = conn.execute("""
        SELECT oi.*, b.title, b.cover_url, b.download_file_url, a.author_name,
               dl.download_token, dl.download_count, dl.is_active as link_active
        FROM order_items oi
        JOIN ebooks b ON oi.ebook_id = b.ebook_id
        JOIN authors a ON b.author_id = a.author_id
        LEFT JOIN download_links dl ON dl.order_id = oi.order_id AND dl.ebook_id = oi.ebook_id
        WHERE oi.order_id = ?
    """, (order_id,)).fetchall()

    conn.close()
    return render_template('order_detail.html', order=order, items=items)

# CRITICAL SECURITY REQUIREMENT:
# "ระบบต้องไม่เปิดลิงก์ของหนังสือที่ลูกค้ายังไม่ได้ซื้อหรือคำสั่งซื้อยังไม่ยืนยัน"
@app.route('/download/<token>')
@login_required
def download_by_token(token):
    conn = get_db()
    link = conn.execute("""
        SELECT dl.*, o.status as order_status, b.title, b.download_file_url
        FROM download_links dl
        JOIN orders o ON dl.order_id = o.order_id
        JOIN ebooks b ON dl.ebook_id = b.ebook_id
        WHERE dl.download_token = ?
    """, (token,)).fetchone()

    if not link:
        conn.close()
        abort(404, description="ลิงก์ดาวน์โหลดไม่ถูกต้อง หรือถูกเพิกถอน")

    # Verify order status is strictly CONFIRMED
    if link['order_status'] != 'CONFIRMED':
        conn.close()
        abort(403, description="ไม่อนุญาต: คำสั่งซื้อนี้ยังไม่ได้รับการยืนยันการชำระเงิน")

    # Verify ownership (or admin)
    if link['user_id'] != session['user_id'] and session.get('role_name') != 'admin':
        conn.close()
        abort(403, description="ไม่อนุญาต: ลิงก์นี้เป็นสิทธิ์ของลูกค้ารายอื่น")

    if link['is_active'] != 1:
        conn.close()
        abort(403, description="ลิงก์ดาวน์โหลดนี้หมดอายุหรือถูกปิดใช้งานแล้ว")

    # Increment download counter
    conn.execute("UPDATE download_links SET download_count = download_count + 1 WHERE download_id = ?",
                 (link['download_id'],))
    conn.commit()
    conn.close()

    # Serve file
    filename = os.path.basename(link['download_file_url'])
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)
    if not os.path.exists(filepath):
        # Fallback to any valid sample pdf
        sample_files = [f for f in os.listdir(DOWNLOAD_FOLDER) if f.endswith('.pdf')]
        if sample_files:
            filename = sample_files[0]
        else:
            abort(404, description="ไม่พบไฟล์เอกสารบนเซิร์ฟเวอร์")

    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True, download_name=f"{link['title']}.pdf")

# Direct download route with full validation check
@app.route('/download/ebook/<int:order_id>/<int:ebook_id>')
@login_required
def download_ebook_order(order_id, ebook_id):
    conn = get_db()
    link = conn.execute("""
        SELECT dl.download_token
        FROM download_links dl
        JOIN orders o ON dl.order_id = o.order_id
        WHERE dl.order_id = ? AND dl.ebook_id = ? AND dl.user_id = ? AND o.status = 'CONFIRMED'
    """, (order_id, ebook_id, session['user_id'])).fetchone()
    conn.close()

    if not link:
        flash('ไม่สามารถดาวน์โหลดได้: คำสั่งซื้อยังไม่ได้รับการยืนยัน หรือท่านไม่ได้ซื้อหนังสือเล่มนี้', 'danger')
        return redirect(url_for('order_detail', order_id=order_id))

    return redirect(url_for('download_by_token', token=link['download_token']))

# -------------------------------------------------------------
# Admin Management Routes
# -------------------------------------------------------------
@app.route('/admin')
@admin_required
def admin_dashboard():
    conn = get_db()

    # KPI Statistics
    total_sales = conn.execute(
        "SELECT COALESCE(SUM(total_amount), 0) as s FROM orders WHERE status = 'CONFIRMED'"
    ).fetchone()['s']
    
    total_orders = conn.execute("SELECT COUNT(*) as c FROM orders").fetchone()['c']
    confirmed_orders = conn.execute("SELECT COUNT(*) as c FROM orders WHERE status = 'CONFIRMED'").fetchone()['c']
    pending_orders = conn.execute("SELECT COUNT(*) as c FROM orders WHERE status = 'PENDING'").fetchone()['c']
    cancelled_orders = conn.execute("SELECT COUNT(*) as c FROM orders WHERE status = 'CANCELLED'").fetchone()['c']

    total_ebooks = conn.execute("SELECT COUNT(*) as c FROM ebooks").fetchone()['c']
    total_users = conn.execute("SELECT COUNT(*) as c FROM users WHERE role_id = 1").fetchone()['c']

    # Monthly revenue for chart
    monthly_sales = conn.execute("""
        SELECT strftime('%Y-%m', order_date) as month, SUM(total_amount) as total
        FROM orders
        WHERE status = 'CONFIRMED'
        GROUP BY strftime('%Y-%m', order_date)
        ORDER BY month ASC
    """).fetchall()

    # Category revenue for chart
    cat_sales = conn.execute("""
        SELECT c.category_name, SUM(oi.subtotal) as total
        FROM categories c
        JOIN ebooks b ON c.category_id = b.category_id
        JOIN order_items oi ON b.ebook_id = oi.ebook_id
        JOIN orders o ON oi.order_id = o.order_id
        WHERE o.status = 'CONFIRMED'
        GROUP BY c.category_name
        ORDER BY total DESC
    """).fetchall()

    # Recent orders
    recent_orders = conn.execute("""
        SELECT o.*, u.full_name, u.username, p.payment_method
        FROM orders o
        JOIN users u ON o.user_id = u.user_id
        LEFT JOIN payments p ON o.order_id = p.order_id
        ORDER BY o.order_date DESC
        LIMIT 7
    """).fetchall()

    conn.close()
    return render_template(
        'admin/dashboard.html',
        total_sales=total_sales,
        total_orders=total_orders,
        confirmed_orders=confirmed_orders,
        pending_orders=pending_orders,
        cancelled_orders=cancelled_orders,
        total_ebooks=total_ebooks,
        total_users=total_users,
        monthly_sales=monthly_sales,
        cat_sales=cat_sales,
        recent_orders=recent_orders
    )

# Admin Ebooks CRUD
@app.route('/admin/ebooks')
@admin_required
def admin_ebooks():
    conn = get_db()
    ebooks = conn.execute("""
        SELECT b.*, a.author_name, c.category_name,
               (SELECT COUNT(*) FROM order_items oi JOIN orders o ON oi.order_id = o.order_id WHERE oi.ebook_id = b.ebook_id AND o.status = 'CONFIRMED') as sales_count
        FROM ebooks b
        JOIN authors a ON b.author_id = a.author_id
        JOIN categories c ON b.category_id = c.category_id
        ORDER BY b.ebook_id DESC
    """).fetchall()
    conn.close()
    return render_template('admin/ebooks.html', ebooks=ebooks)

@app.route('/admin/ebooks/add', methods=['GET', 'POST'])
@admin_required
def admin_ebook_add():
    conn = get_db()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author_id = request.form.get('author_id', type=int)
        category_id = request.form.get('category_id', type=int)
        price = request.form.get('price', type=float)
        description = request.form.get('description', '').strip()
        cover_url = request.form.get('cover_url', '').strip() or 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400&q=80'
        download_file_url = request.form.get('download_file_url', '').strip() or '/downloads/sample_database_design.pdf'
        is_active = 1 if request.form.get('is_active') == 'on' else 0

        if not title or not author_id or not category_id or price is None:
            flash('กรุณากรอกข้อมูลที่จำเป็นให้ครบถ้วน', 'danger')
        else:
            conn.execute("""
                INSERT INTO ebooks (title, author_id, category_id, price, description, cover_url, download_file_url, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, author_id, category_id, price, description, cover_url, download_file_url, is_active))
            conn.commit()
            conn.close()
            flash(f'เพิ่มหนังสือ "{title}" เรียบร้อยแล้ว', 'success')
            return redirect(url_for('admin_ebooks'))

    authors = conn.execute("SELECT * FROM authors ORDER BY author_name ASC").fetchall()
    categories = conn.execute("SELECT * FROM categories ORDER BY category_name ASC").fetchall()
    conn.close()
    return render_template('admin/ebook_form.html', ebook=None, authors=authors, categories=categories)

@app.route('/admin/ebooks/edit/<int:ebook_id>', methods=['GET', 'POST'])
@admin_required
def admin_ebook_edit(ebook_id):
    conn = get_db()
    ebook = conn.execute("SELECT * FROM ebooks WHERE ebook_id = ?", (ebook_id,)).fetchone()
    if not ebook:
        conn.close()
        flash('ไม่พบหนังสือที่ระบุ', 'warning')
        return redirect(url_for('admin_ebooks'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author_id = request.form.get('author_id', type=int)
        category_id = request.form.get('category_id', type=int)
        price = request.form.get('price', type=float)
        description = request.form.get('description', '').strip()
        cover_url = request.form.get('cover_url', '').strip() or ebook['cover_url']
        download_file_url = request.form.get('download_file_url', '').strip() or ebook['download_file_url']
        is_active = 1 if request.form.get('is_active') == 'on' else 0

        conn.execute("""
            UPDATE ebooks
            SET title = ?, author_id = ?, category_id = ?, price = ?, description = ?,
                cover_url = ?, download_file_url = ?, is_active = ?
            WHERE ebook_id = ?
        """, (title, author_id, category_id, price, description, cover_url, download_file_url, is_active, ebook_id))
        conn.commit()
        conn.close()
        flash('บันทึกการแก้ไขข้อมูลหนังสือเรียบร้อยแล้ว', 'success')
        return redirect(url_for('admin_ebooks'))

    authors = conn.execute("SELECT * FROM authors ORDER BY author_name ASC").fetchall()
    categories = conn.execute("SELECT * FROM categories ORDER BY category_name ASC").fetchall()
    conn.close()
    return render_template('admin/ebook_form.html', ebook=ebook, authors=authors, categories=categories)

@app.route('/admin/ebooks/toggle/<int:ebook_id>', methods=['POST'])
@admin_required
def admin_ebook_toggle(ebook_id):
    conn = get_db()
    ebook = conn.execute("SELECT is_active, title FROM ebooks WHERE ebook_id = ?", (ebook_id,)).fetchone()
    if ebook:
        new_status = 0 if ebook['is_active'] == 1 else 1
        conn.execute("UPDATE ebooks SET is_active = ? WHERE ebook_id = ?", (new_status, ebook_id))
        conn.commit()
        status_text = "เปิดขาย" if new_status == 1 else "ปิดการขาย"
        flash(f'เปลี่ยนสถานะหนังสือ "{ebook["title"]}" เป็น {status_text} แล้ว', 'info')
    conn.close()
    return redirect(url_for('admin_ebooks'))

# Admin Categories CRUD
@app.route('/admin/categories', methods=['GET', 'POST'])
@admin_required
def admin_categories():
    conn = get_db()
    if request.method == 'POST':
        category_name = request.form.get('category_name', '').strip()
        description = request.form.get('description', '').strip()
        edit_id = request.form.get('category_id', type=int)

        if not category_name:
            flash('กรุณาระบุชื่อหมวดหมู่', 'danger')
        else:
            if edit_id:
                conn.execute("UPDATE categories SET category_name = ?, description = ? WHERE category_id = ?",
                             (category_name, description, edit_id))
                flash('อัปเดตหมวดหมู่เรียบร้อยแล้ว', 'success')
            else:
                conn.execute("INSERT INTO categories (category_name, description) VALUES (?, ?)",
                             (category_name, description))
                flash('เพิ่มหมวดหมู่ใหม่เรียบร้อยแล้ว', 'success')
            conn.commit()

    categories = conn.execute("""
        SELECT c.*, COUNT(b.ebook_id) as ebook_count
        FROM categories c
        LEFT JOIN ebooks b ON c.category_id = b.category_id
        GROUP BY c.category_id
        ORDER BY c.category_id ASC
    """).fetchall()
    conn.close()
    return render_template('admin/categories.html', categories=categories)

# Admin Orders & Slip Verification
@app.route('/admin/orders')
@admin_required
def admin_orders():
    status_filter = request.args.get('status', 'all')
    conn = get_db()
    
    sql = """
        SELECT o.*, u.full_name, u.username, u.email,
               p.payment_method, p.payment_status, p.slip_image, p.payment_id
        FROM orders o
        JOIN users u ON o.user_id = u.user_id
        LEFT JOIN payments p ON o.order_id = p.order_id
    """
    params = []
    if status_filter != 'all':
        sql += " WHERE o.status = ?"
        params.append(status_filter)

    sql += " ORDER BY o.order_date DESC"
    orders = conn.execute(sql, params).fetchall()
    conn.close()
    return render_template('admin/orders.html', orders=orders, current_filter=status_filter)

@app.route('/admin/orders/<int:order_id>')
@admin_required
def admin_order_view(order_id):
    conn = get_db()
    order = conn.execute("""
        SELECT o.*, u.full_name, u.username, u.email, u.phone,
               p.payment_id, p.payment_method, p.payment_status, p.slip_image, p.payment_date, p.admin_notes
        FROM orders o
        JOIN users u ON o.user_id = u.user_id
        LEFT JOIN payments p ON o.order_id = p.order_id
        WHERE o.order_id = ?
    """, (order_id,)).fetchone()

    if not order:
        conn.close()
        flash('ไม่พบคำสั่งซื้อนี้', 'warning')
        return redirect(url_for('admin_orders'))

    items = conn.execute("""
        SELECT oi.*, b.title, b.cover_url, b.price as current_price, a.author_name
        FROM order_items oi
        JOIN ebooks b ON oi.ebook_id = b.ebook_id
        JOIN authors a ON b.author_id = a.author_id
        WHERE oi.order_id = ?
    """, (order_id,)).fetchall()

    conn.close()
    return render_template('admin/order_detail.html', order=order, items=items)

@app.route('/admin/orders/update-status/<int:order_id>', methods=['POST'])
@admin_required
def admin_order_update_status(order_id):
    new_status = request.form.get('status')
    admin_notes = request.form.get('admin_notes', '').strip()

    if new_status not in ['PENDING', 'CONFIRMED', 'CANCELLED']:
        flash('สถานะไม่ถูกต้อง', 'danger')
        return redirect(url_for('admin_orders'))

    conn = get_db()
    cursor = conn.cursor()

    # Update order status
    cursor.execute("UPDATE orders SET status = ? WHERE order_id = ?", (new_status, order_id))

    # Update payment status
    pay_status = 'VERIFIED' if new_status == 'CONFIRMED' else ('REJECTED' if new_status == 'CANCELLED' else 'PENDING')
    cursor.execute("""
        UPDATE payments
        SET payment_status = ?, admin_notes = COALESCE(?, admin_notes)
        WHERE order_id = ?
    """, (pay_status, admin_notes or None, order_id))

    # If CONFIRMED, ensure download links exist and are active!
    if new_status == 'CONFIRMED':
        order = cursor.execute("SELECT user_id, order_date FROM orders WHERE order_id = ?", (order_id,)).fetchone()
        items = cursor.execute("SELECT ebook_id FROM order_items WHERE order_id = ?", (order_id,)).fetchall()

        for it in items:
            existing = cursor.execute(
                "SELECT download_id FROM download_links WHERE order_id = ? AND ebook_id = ?",
                (order_id, it['ebook_id'])
            ).fetchone()
            if not existing:
                token = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO download_links (order_id, ebook_id, user_id, download_token, is_active)
                    VALUES (?, ?, ?, ?, 1)
                """, (order_id, it['ebook_id'], order['user_id'], token))
            else:
                cursor.execute("UPDATE download_links SET is_active = 1 WHERE download_id = ?", (existing['download_id'],))
    elif new_status == 'CANCELLED':
        # Deactivate download links if cancelled
        cursor.execute("UPDATE download_links SET is_active = 0 WHERE order_id = ?", (order_id,))

    conn.commit()
    conn.close()

    flash(f'อัปเดตสถานะคำสั่งซื้อ #{order_id} เป็น "{new_status}" เรียบร้อยแล้ว', 'success')
    return redirect(request.referrer or url_for('admin_orders'))

# Admin Users Management
@app.route('/admin/users')
@admin_required
def admin_users():
    conn = get_db()
    users = conn.execute("""
        SELECT u.*, r.role_name,
               (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.user_id) as total_orders,
               (SELECT COALESCE(SUM(total_amount), 0) FROM orders o WHERE o.user_id = u.user_id AND o.status = 'CONFIRMED') as total_spent
        FROM users u
        JOIN roles r ON u.role_id = r.role_id
        ORDER BY u.user_id ASC
    """).fetchall()
    roles = conn.execute("SELECT * FROM roles").fetchall()
    conn.close()
    return render_template('admin/users.html', users=users, roles=roles)

@app.route('/admin/users/role/<int:user_id>', methods=['POST'])
@admin_required
def admin_change_role(user_id):
    new_role_id = request.form.get('role_id', type=int)
    if user_id == session['user_id']:
        flash('ไม่สามารถเปลี่ยนบทบาทของบัญชีตนเองที่กำลังใช้งานอยู่ได้', 'warning')
        return redirect(url_for('admin_users'))

    conn = get_db()
    conn.execute("UPDATE users SET role_id = ? WHERE user_id = ?", (new_role_id, user_id))
    conn.commit()
    conn.close()
    flash('เปลี่ยนบทบาทผู้ใช้งานเรียบร้อยแล้ว', 'success')
    return redirect(url_for('admin_users'))

# -------------------------------------------------------------
# Admin Analytical Reports (4 Required Reports)
# -------------------------------------------------------------
@app.route('/admin/reports')
@admin_required
def admin_reports():
    conn = get_db()

    # Report 1: Sales by Time Period (Monthly + Daily)
    report1_monthly = conn.execute("""
        SELECT 
            strftime('%Y-%m', o.order_date) AS period_month,
            COUNT(o.order_id) AS total_orders,
            ROUND(SUM(o.total_amount), 2) AS total_sales,
            ROUND(AVG(o.total_amount), 2) AS average_order_value,
            MIN(o.total_amount) AS min_order_value,
            MAX(o.total_amount) AS max_order_value
        FROM orders o
        WHERE o.status = 'CONFIRMED'
        GROUP BY strftime('%Y-%m', o.order_date)
        ORDER BY period_month ASC
    """).fetchall()

    report1_daily = conn.execute("""
        SELECT 
            date(o.order_date) AS sale_date,
            COUNT(o.order_id) AS daily_orders,
            ROUND(SUM(o.total_amount), 2) AS daily_sales,
            ROUND(AVG(o.total_amount), 2) AS daily_avg_order
        FROM orders o
        WHERE o.status = 'CONFIRMED'
        GROUP BY date(o.order_date)
        ORDER BY sale_date DESC
        LIMIT 15
    """).fetchall()

    # Report 2: Best Selling E-Books
    report2_top_ebooks = conn.execute("""
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
        LIMIT 10
    """).fetchall()

    # Report 3: Sales by Category
    report3_categories = conn.execute("""
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
        ORDER BY category_revenue DESC
    """).fetchall()

    # Report 4A: Top Customers (HAVING clause)
    report4_customers = conn.execute("""
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
        LIMIT 10
    """).fetchall()

    # Report 4B: Order Status Distribution
    report4_status = conn.execute("""
        SELECT 
            o.status AS order_status,
            COUNT(o.order_id) AS order_count,
            ROUND(SUM(o.total_amount), 2) AS total_amount,
            ROUND(AVG(o.total_amount), 2) AS avg_amount,
            ROUND(COUNT(o.order_id) * 100.0 / (SELECT COUNT(*) FROM orders), 2) AS percentage_of_total_orders
        FROM orders o
        GROUP BY o.status
        ORDER BY order_count DESC
    """).fetchall()

    # Tables metadata for custom SQL runner inside reports page
    tables_meta = []
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name ASC")
    for r in cursor.fetchall():
        t = r['name']
        c_res = conn.execute(f"SELECT COUNT(*) as cnt FROM {t}").fetchone()
        row_count = c_res['cnt'] if c_res else 0
        cols_info = conn.execute(f"PRAGMA table_info({t})").fetchall()
        tables_meta.append({
            'name': t,
            'count': row_count,
            'columns': cols_info
        })

    conn.close()
    return render_template(
        'admin/reports.html',
        report1_monthly=report1_monthly,
        report1_daily=report1_daily,
        report2_top_ebooks=report2_top_ebooks,
        report3_categories=report3_categories,
        report4_customers=report4_customers,
        report4_status=report4_status,
        tables_meta=tables_meta
    )

# Export Reports to CSV
@app.route('/admin/reports/export/<int:report_id>')
@admin_required
def export_report_csv(report_id):
    conn = get_db()
    csv_rows = []
    filename = f"report_{report_id}_{datetime.now().strftime('%Y%m%d')}.csv"

    if report_id == 1:
        filename = f"report1_sales_by_time_{datetime.now().strftime('%Y%m%d')}.csv"
        csv_rows.append(["เดือน/งวดเวลา", "จำนวนคำสั่งซื้อ", "ยอดขายรวม (บาท)", "ค่าเฉลี่ยต่อบิล (บาท)", "ยอดบิลต่ำสุด (บาท)", "ยอดบิลสูงสุด (บาท)"])
        rows = conn.execute("""
            SELECT strftime('%Y-%m', o.order_date) AS m, COUNT(o.order_id), ROUND(SUM(o.total_amount), 2),
                   ROUND(AVG(o.total_amount), 2), MIN(o.total_amount), MAX(o.total_amount)
            FROM orders o WHERE o.status = 'CONFIRMED' GROUP BY strftime('%Y-%m', o.order_date) ORDER BY m ASC
        """).fetchall()
        for r in rows:
            csv_rows.append([str(col) for col in r])

    elif report_id == 2:
        filename = f"report2_best_selling_ebooks_{datetime.now().strftime('%Y%m%d')}.csv"
        csv_rows.append(["รหัสหนังสือ", "ชื่อ E-Book", "หมวดหมู่", "ผู้แต่ง", "ราคา (บาท)", "จำนวนเล่มที่ขายได้", "ยอดขายรวม (บาท)"])
        rows = conn.execute("""
            SELECT b.ebook_id, b.title, c.category_name, a.author_name, b.price, SUM(oi.quantity), ROUND(SUM(oi.subtotal), 2)
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            JOIN ebooks b ON oi.ebook_id = b.ebook_id
            JOIN categories c ON b.category_id = c.category_id
            JOIN authors a ON b.author_id = a.author_id
            WHERE o.status = 'CONFIRMED'
            GROUP BY b.ebook_id, b.title, c.category_name, a.author_name, b.price
            ORDER BY SUM(oi.quantity) DESC, SUM(oi.subtotal) DESC
        """).fetchall()
        for r in rows:
            csv_rows.append([str(col) for col in r])

    elif report_id == 3:
        filename = f"report3_sales_by_category_{datetime.now().strftime('%Y%m%d')}.csv"
        csv_rows.append(["รหัสหมวดหมู่", "ชื่อหมวดหมู่", "จำนวนคำสั่งซื้อที่มีรายการ", "จำนวนเล่มที่ขายได้", "ยอดขายรวม (บาท)", "สัดส่วนรายได้ (%)"])
        rows = conn.execute("""
            SELECT c.category_id, c.category_name, COUNT(DISTINCT o.order_id), SUM(oi.quantity), ROUND(SUM(oi.subtotal), 2),
                   ROUND(SUM(oi.subtotal) * 100.0 / (SELECT SUM(subtotal) FROM order_items oi2 JOIN orders o2 ON oi2.order_id = o2.order_id WHERE o2.status = 'CONFIRMED'), 2)
            FROM categories c
            JOIN ebooks b ON c.category_id = b.category_id
            JOIN order_items oi ON b.ebook_id = oi.ebook_id
            JOIN orders o ON oi.order_id = o.order_id
            WHERE o.status = 'CONFIRMED'
            GROUP BY c.category_id, c.category_name
            ORDER BY SUM(oi.subtotal) DESC
        """).fetchall()
        for r in rows:
            csv_rows.append([str(col) for col in r])

    elif report_id == 4:
        filename = f"report4_customer_and_orders_{datetime.now().strftime('%Y%m%d')}.csv"
        csv_rows.append(["รหัสลูกค้า", "ชื่อผู้ใช้", "ชื่อ-นามสกุล", "อีเมล", "จำนวนคำสั่งซื้อยืนยันแล้ว", "ยอดซื้อสะสมรวม (บาท)", "ยอดเฉลี่ยต่อบิล (บาท)"])
        rows = conn.execute("""
            SELECT u.user_id, u.username, u.full_name, u.email, COUNT(o.order_id), ROUND(SUM(o.total_amount), 2), ROUND(AVG(o.total_amount), 2)
            FROM users u
            JOIN orders o ON u.user_id = o.user_id
            WHERE o.status = 'CONFIRMED'
            GROUP BY u.user_id, u.username, u.full_name, u.email
            HAVING COUNT(o.order_id) >= 1
            ORDER BY SUM(o.total_amount) DESC
        """).fetchall()
        for r in rows:
            csv_rows.append([str(col) for col in r])

    conn.close()

    # Create CSV content with UTF-8 BOM for Thai Excel compatibility
    csv_content = "\ufeff" + "\n".join([",".join([f'"{c}"' for c in row]) for row in csv_rows])
    return Response(
        csv_content,
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# -------------------------------------------------------------
# Admin Direct SQL Query Console & Table Inspector
# -------------------------------------------------------------
@app.route('/admin/api/sql', methods=['POST'])
@admin_required
def admin_api_sql():
    data = request.get_json(silent=True) or request.form
    query = (data.get('query') or '').strip()
    if not query:
        return jsonify({'success': False, 'error': 'กรุณาระบุคำสั่ง SQL'})

    conn = get_db()
    start_time = time.time()
    try:
        res = conn.execute(query)
        exec_time_ms = round((time.time() - start_time) * 1000, 2)
        if res.description:
            columns = [col[0] for col in res.description]
            db_rows = res.fetchall()
            rows = []
            for r in db_rows:
                rows.append([r[col] for col in columns])
            conn.close()
            return jsonify({
                'success': True,
                'is_select': True,
                'columns': columns,
                'rows': rows,
                'row_count': len(rows),
                'exec_time_ms': exec_time_ms
            })
        else:
            row_count = res.rowcount
            conn.commit()
            conn.close()
            return jsonify({
                'success': True,
                'is_select': False,
                'row_count': row_count,
                'exec_time_ms': exec_time_ms
            })
    except Exception as e:
        conn.close()
        exec_time_ms = round((time.time() - start_time) * 1000, 2)
        return jsonify({
            'success': False,
            'error': str(e),
            'exec_time_ms': exec_time_ms
        })

@app.route('/admin/sql', methods=['GET', 'POST'])
@admin_required
def admin_sql():
    conn = get_db()
    
    # 1. Fetch metadata for all tables in database
    tables_meta = []
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name ASC")
    table_names = [r['name'] for r in cursor.fetchall()]
    
    for t in table_names:
        c_res = conn.execute(f"SELECT COUNT(*) as cnt FROM {t}").fetchone()
        row_count = c_res['cnt'] if c_res else 0
        cols_info = conn.execute(f"PRAGMA table_info({t})").fetchall()
        tables_meta.append({
            'name': t,
            'count': row_count,
            'columns': cols_info
        })

    # 2. Determine query to execute
    table_param = request.args.get('table')
    default_query = "SELECT * FROM ebooks LIMIT 20;"
    if table_param and table_param in table_names:
        default_query = f"SELECT * FROM {table_param} LIMIT 50;"

    query = request.form.get('query') or request.args.get('query') or default_query
    query = query.strip()

    columns = []
    rows = []
    error_message = None
    exec_time_ms = 0.0
    row_count = 0
    is_select = True

    if query:
        start_time = time.time()
        try:
            res = conn.execute(query)
            exec_time_ms = round((time.time() - start_time) * 1000, 2)
            
            if res.description:
                columns = [col[0] for col in res.description]
                rows = res.fetchall()
                row_count = len(rows)
            else:
                is_select = False
                row_count = res.rowcount
                conn.commit()
                flash(f'ดำเนินการคำสั่งเรียบร้อยแล้ว: มีผลกระทบ {row_count} แถว', 'success')
        except Exception as e:
            error_message = str(e)
            exec_time_ms = round((time.time() - start_time) * 1000, 2)

    conn.close()
    return render_template(
        'admin/sql_runner.html',
        query=query,
        columns=columns,
        rows=rows,
        error_message=error_message,
        exec_time_ms=exec_time_ms,
        row_count=row_count,
        tables_meta=tables_meta,
        is_select=is_select
    )

@app.route('/admin/sql/export', methods=['POST'])
@admin_required
def admin_sql_export():
    query = request.form.get('query', '').strip()
    if not query:
        flash('กรุณาระบุคำสั่ง SQL สำหรับส่งออกข้อมูล', 'warning')
        return redirect(url_for('admin_sql'))
        
    conn = get_db()
    try:
        res = conn.execute(query)
        if not res.description:
            conn.close()
            flash('คำสั่ง SQL นี้ไม่มีชุดผลลัพธ์ข้อมูลสำหรับสร้าง CSV', 'warning')
            return redirect(url_for('admin_sql', query=query))
            
        columns = [col[0] for col in res.description]
        rows = res.fetchall()
        conn.close()
        
        csv_rows = [columns]
        for row in rows:
            csv_rows.append([str(item) if item is not None else "" for item in row])
            
        filename = f"sql_query_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        csv_content = "\ufeff" + "\n".join([",".join([f'"{str(c).replace(chr(34), chr(34)+chr(34))}"' for c in r]) for r in csv_rows])
        return Response(
            csv_content,
            mimetype="text/csv; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        conn.close()
        flash(f'เกิดข้อผิดพลาดในการส่งออก CSV: {e}', 'danger')
        return redirect(url_for('admin_sql', query=query))



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("Starting E-Book Store Web Application...")
    print(f"Customer URL: http://127.0.0.1:{port}/")
    print(f"Admin URL:    http://127.0.0.1:{port}/admin")
    print("Default Test Accounts:")
    print(" - Admin:    Username: admin     / Password: admin123")
    print(" - Customer: Username: customer1 / Password: user123")
    app.run(host='0.0.0.0', port=port, debug=True)
