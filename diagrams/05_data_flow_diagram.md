# ไดอะแกรมที่ 5: แผนภาพกระแสข้อมูล (Data Flow Diagram: DFD Level 0 & Level 1)
**โครงงาน:** Mini Project Database ร้านขาย E-Book  
**มาตรฐาน:** แผนภาพแสดงทิศทางการไหลของข้อมูลระหว่าง Entity, Process และ Data Store  

---

## 1. DFD Level 0 (Context Diagram - ภาพรวมระดับสูงสุด)

```mermaid
graph LR
    Customer["👤 ลูกค้า (Customer)"]
    Admin["👨‍💼 ผู้ดูแลร้าน (Admin)"]
    System(("0.0<br>ระบบร้านขาย E-Book<br>ออนไลน์"))

    Customer --> |ข้อมูลสมัคร/เข้าสู่ระบบ, รายการที่สั่งซื้อ, สลิปจำลอง| System
    System --> |สถานะคำสั่งซื้อ, ใบเสร็จจำลอง, ไฟล์ E-Book PDF| Customer

    Admin --> |จัดการหนังสือ/หมวดหมู่, อนุมัติ/ยกเลิกคำสั่งซื้อ| System
    System --> |รายการคำสั่งซื้อรอตรวจ, สถิติแดชบอร์ด, 4 รายงานวิเคราะห์ & CSV| Admin

    style System fill:#2563eb,color:#fff,stroke-width:3px
    style Customer fill:#f1f5f9,stroke:#3b82f6,stroke-width:2px
    style Admin fill:#f1f5f9,stroke:#ef4444,stroke-width:2px
```

---

## 2. DFD Level 1 (แผนภาพกระแสข้อมูลระดับกระบวนการย่อย)

```mermaid
graph TD
    Customer["👤 ลูกค้า (Customer)"]
    Admin["👨‍💼 ผู้ดูแลร้าน (Admin)"]

    subgraph Processes ["กระบวนการหลักในระบบ (Processes)"]
        P1(("1.0<br>จัดการบัญชีสมาชิก<br>& การเข้าสู่ระบบ"))
        P2(("2.0<br>ค้นหา & แคตตาล็อก<br>หนังสือ E-Book"))
        P3(("3.0<br>จัดการตะกร้าสินค้า<br>(Cart)"))
        P4(("4.0<br>สั่งซื้อ & ชำระเงินจำลอง<br>(Checkout)"))
        P5(("5.0<br>ตรวจสอบสลิป &<br>ส่งมอบไฟล์ E-Book"))
        P6(("6.0<br>วิเคราะห์ข้อมูล &<br>สร้างรายงาน"))
    end

    subgraph DataStores ["แหล่งเก็บข้อมูล (Data Stores)"]
        D1[("D1: users & roles")]
        D2[("D2: ebooks, authors, categories")]
        D3[("D3: carts & cart_items")]
        D4[("D4: orders & order_items")]
        D5[("D5: payments")]
        D6[("D6: download_links")]
    end

    %% Customer Flow
    Customer --> |สมัคร/Login| P1
    P1 <--> D1
    P1 --> |ยืนยันสิทธิ์สำเร็จ| Customer

    Customer --> |ค้นหา / กรองหมวด| P2
    P2 <-- อ่านแคตตาล็อก --> D2
    P2 --> |แสดงผลรายการหนังสือ| Customer

    Customer --> |หยิบใส่ตะกร้า / ปรับจำนวน| P3
    P3 <--> D3
    P3 <-- ดึงราคาปัจจุบัน --> D2
    P3 --> |ยอดรวมในตะกร้า| Customer

    Customer --> |ยืนยันสั่งซื้อ & แนบสลิป| P4
    P4 --> |ล้างตะกร้า| D3
    P4 --> |บันทึกบิล & Snapshot ราคา| D4
    P4 --> |บันทึกข้อมูลสลิป PENDING| D5
    P4 --> |แสดงเลขที่คำสั่งซื้อ| Customer

    %% Admin Flow
    Admin --> |เพิ่ม/แก้ไขหนังสือ & หมวด| P2
    Admin --> |ตรวจสลิป & อนุมัติ CONFIRMED| P5
    P5 <--> D4
    P5 <--> D5
    P5 --> |สร้าง Secure Token| D6
    
    %% Delivery Flow
    Customer --> |กดดาวน์โหลด PDF| P5
    P5 <-- ตรวจสอบ Token & สิทธิ์ --> D6
    P5 --> |ส่งมอบไฟล์ PDF| Customer

    %% Reporting Flow
    Admin --> |เปิดดู 4 รายงาน / Export CSV| P6
    P6 <-- รัน SQL คิวรีเชิงสถิติ --> D4
    P6 <-- ข้อมูลหนังสือ --> D2
    P6 <-- ข้อมูลลูกค้า --> D1
    P6 --> |ตารางรายงาน, กราฟ, ไฟล์ CSV| Admin
```
