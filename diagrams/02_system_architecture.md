# ไดอะแกรมที่ 2: สถาปัตยกรรมระบบ (System Architecture Diagram)
**โครงงาน:** Mini Project Database ร้านขาย E-Book  
**รูปแบบ:** Multi-Tier Web Application Architecture  

---

## 1. แผนภาพสถาปัตยกรรมระบบ (System Architecture)

```mermaid
graph TD
    subgraph ClientTier ["1. ส่วนติดต่อผู้ใช้ (Client Tier)"]
        BrowserCustomer["🌐 ลูกค้าทั่วไป (Customer Browser)<br>- ค้นหา/เลือกดู E-Book<br>- จัดการตะกร้าสินค้า<br>- ชำระเงินจำลอง & รับไฟล์ PDF"]
        BrowserAdmin["💻 ผู้ดูแลระบบ (Admin Browser)<br>- จัดการ E-Book & หมวดหมู่<br>- ตรวจสอบสลิป & อนุมัติออเดอร์<br>- ดู 4 รายงานวิเคราะห์ & กราฟ"]
    end

    subgraph AppTier ["2. เซิร์ฟเวอร์แอปพลิเคชัน (Application Tier - Python Flask)"]
        Router["HTTP Router & Middleware<br>- Session Management<br>- Auth Decorators (@login_required, @admin_required)"]
        
        subgraph Controllers ["Controllers & Modules"]
            AuthModule["Module 1: Authentication<br>(Register, Login, Scrypt Hash)"]
            StoreModule["Module 2: Storefront & Cart<br>(Catalog, Search, Cart CRUD)"]
            OrderModule["Module 3: Checkout & Orders<br>(Order Transaction, Slip Upload)"]
            DownloadModule["Module 4: Secure Delivery<br>(4-Tier Token & PDF Serving)"]
            AdminModule["Module 5: Admin Panel<br>(CRUD Books, Status Workflow)"]
            ReportModule["Module 6: Business Intelligence<br>(4 Analytical Queries, CSV Export)"]
        end
        
        Templates["Jinja2 Template Engine<br>- Bootstrap 5 UI & Responsive Design<br>- Chart.js Interactive Dashboards"]
    end

    subgraph DataTier ["3. ส่วนจัดการข้อมูล (Database & Storage Tier)"]
        DBEngine["🗄️ SQLite3 Database Engine<br>- Foreign Keys Enforcement (PRAGMA foreign_keys = ON)<br>- Constraints (NOT NULL, UNIQUE, CHECK, DEFAULT)<br>- 11 Relational Tables (3NF)"]
        
        subgraph FileStorage ["Local / Cloud File Storage"]
            PDFStore["📁 static/downloads/<br>ไฟล์หนังสือดิจิทัลตัวอย่าง (PDF)"]
            SlipStore["📁 static/uploads/slips/<br>หลักฐานการชำระเงินจำลอง (PNG/SVG)"]
            CSSStore["📁 static/css/ & js/<br>ไฟล์สไตล์ชีตและสคริปต์หน้าเว็บ"]
        end
    end

    BrowserCustomer <==> |HTTP / HTTPS| Router
    BrowserAdmin <==> |HTTP / HTTPS| Router

    Router --> AuthModule
    Router --> StoreModule
    Router --> OrderModule
    Router --> DownloadModule
    Router --> AdminModule
    Router --> ReportModule

    Controllers <--> DBEngine
    Controllers --> Templates
    DownloadModule --> PDFStore
    OrderModule --> SlipStore
    Templates --> BrowserCustomer
    Templates --> BrowserAdmin
```

---

## 2. อธิบายองค์ประกอบของสถาปัตยกรรม (Architecture Layers)
1. **Client Tier:** รองรับทั้งอุปกรณ์เดสก์ท็อปและสมาร์ตโฟนผ่าน Responsive Web Design (Bootstrap 5)
2. **Application Tier:** พัฒนาด้วย Python Flask ทำหน้าที่ตรวจสอบความปลอดภัย (Session Authentication), ควบคุมเงื่อนไขทางธุรกิจ (Business Rules) และคำนวณราคา
3. **Database Tier:** จัดการด้วย SQLite3 Relational Database ที่ปฏิบัติตามมาตรฐานฐานข้อมูล มีดัชนี (Indexes) ช่วยเร่งความเร็ว และมีการใช้ Constraints ควบคุมความถูกต้อง
4. **File Storage:** แยกพื้นที่เก็บไฟล์สลิป (`uploads/slips`) และไฟล์หนังสือ (`downloads`) ออกจากตัวฐานข้อมูล เพื่อให้สอดคล้องกับหลักการออกแบบฐานข้อมูลที่ดี
