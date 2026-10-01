import unittest
import os
import json
from app import app, get_db

class EbookStoreTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_01_homepage_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('E-Book Store'.encode('utf-8'), response.data)

    def test_02_login_and_logout(self):
        # Test Admin Login
        res = self.client.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn('ผู้ดูแลระบบ'.encode('utf-8'), res.data)

        # Test Logout
        res_logout = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(res_logout.status_code, 200)

    def test_03_customer_login_and_cart(self):
        # Login customer1
        self.client.post('/login', data={'username': 'customer1', 'password': 'user123'})
        
        # View cart
        res_cart = self.client.get('/cart')
        self.assertEqual(res_cart.status_code, 200)

        # Add book #1 to cart
        res_add = self.client.post('/cart/add/1', follow_redirects=True)
        self.assertEqual(res_add.status_code, 200)

    def test_04_admin_dashboard_and_reports(self):
        # Login as Admin
        self.client.post('/login', data={'username': 'admin', 'password': 'admin123'})
        
        # Test Dashboard
        res_dash = self.client.get('/admin')
        self.assertEqual(res_dash.status_code, 200)
        self.assertIn('แดชบอร์ดภาพรวม'.encode('utf-8'), res_dash.data)

        # Test Reports
        res_rep = self.client.get('/admin/reports')
        self.assertEqual(res_rep.status_code, 200)
        self.assertIn('รายงานวิเคราะห์จากข้อมูลจริง'.encode('utf-8'), res_rep.data)

        # Test CSV Export
        res_csv1 = self.client.get('/admin/reports/export/1')
        self.assertEqual(res_csv1.status_code, 200)
        self.assertEqual(res_csv1.mimetype, 'text/csv')

        res_csv2 = self.client.get('/admin/reports/export/2')
        self.assertEqual(res_csv2.status_code, 200)

    def test_05_security_download_unconfirmed_rejected(self):
        # Find a PENDING order in database
        conn = get_db()
        pending_order = conn.execute("SELECT order_id, user_id FROM orders WHERE status = 'PENDING' LIMIT 1").fetchone()
        customer = conn.execute("SELECT username FROM users WHERE user_id = ?", (pending_order['user_id'],)).fetchone()
        conn.close()

        # Login as that customer
        self.client.post('/login', data={'username': customer['username'], 'password': 'user123'})

        # Attempt to download directly with endpoint
        res = self.client.get(f"/download/ebook/{pending_order['order_id']}/1", follow_redirects=True)
        # Should redirect with danger flash stating not allowed
        self.assertIn('ไม่สามารถดาวน์โหลดได้'.encode('utf-8'), res.data)

    def test_06_security_download_confirmed_allowed(self):
        # Find a CONFIRMED order with download link
        conn = get_db()
        link = conn.execute("""
            SELECT dl.download_token, dl.user_id, u.username
            FROM download_links dl
            JOIN users u ON dl.user_id = u.user_id
            WHERE dl.is_active = 1
            LIMIT 1
        """).fetchone()
        conn.close()

        # Login as owner
        self.client.post('/login', data={'username': link['username'], 'password': 'user123'})

        # Download by token
        res = self.client.get(f"/download/{link['download_token']}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.mimetype, 'application/pdf')

    def test_07_admin_sql_query_and_export(self):
        # Login as Admin
        self.client.post('/login', data={'username': 'admin', 'password': 'admin123'})

        # GET /admin/sql
        res_get = self.client.get('/admin/sql')
        self.assertEqual(res_get.status_code, 200)
        self.assertIn('เครื่องมือรัน SQL ดึงข้อมูลจากตาราง'.encode('utf-8'), res_get.data)

        # POST custom query
        res_post = self.client.post('/admin/sql', data={'query': 'SELECT * FROM categories ORDER BY category_id ASC;'})
        self.assertEqual(res_post.status_code, 200)
        self.assertIn('หมวดหมู่'.encode('utf-8'), res_post.data)

        # Export SQL query result to CSV
        res_export = self.client.post('/admin/sql/export', data={'query': 'SELECT * FROM categories;'})
        self.assertEqual(res_export.status_code, 200)
        self.assertEqual(res_export.mimetype, 'text/csv')

        # Test API JSON query for interactive console in reports page
        res_api = self.client.post('/admin/api/sql', json={'query': 'SELECT * FROM ebooks LIMIT 5;'})
        self.assertEqual(res_api.status_code, 200)
        data = res_api.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['rows']), 5)

if __name__ == '__main__':
    unittest.main()
