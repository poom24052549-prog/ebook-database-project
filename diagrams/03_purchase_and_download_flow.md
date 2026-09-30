# ไดอะแกรมที่ 3: แผนผังกระบวนการสั่งซื้อและดาวน์โหลด (Customer Purchase & Download Flow)
**โครงงาน:** Mini Project Database ร้านขาย E-Book  
**หมวดหมู่:** เส้นทางการทำงานของลูกค้า (Customer Journey & Flowchart) ตามข้อกำหนดหัวข้อ 2.1 และ 2.2  

---

## 1. แผนผังกระบวนการสั่งซื้อและรับไฟล์ E-Book (Flowchart)

```mermaid
flowchart TD
    Start(["เริ่มต้น: ลูกค้าเข้าสู่เว็บไซต์"]) --> Browse["1. ค้นหา / เลือกดูหนังสือ E-Book<br>(กรองหมวดหมู่, ดูรายละเอียดราคา)"]
    
    Browse --> AddCart["2. กดปุ่ม 'ใส่ตะกร้า'"]
    AddCart --> CheckLogin{"เข้าสู่ระบบหรือยัง?"}
    
    CheckLogin -- "ยังไม่ได้เข้าสู่ระบบ" --> LoginScreen["นำทางไปหน้าเข้าสู่ระบบ / สมัครสมาชิก"]
    LoginScreen --> AddCart
    
    CheckLogin -- "เข้าสู่ระบบแล้ว" --> CartPage["3. หน้าตะกร้าสินค้า (Cart)<br>- ปรับเพิ่ม/ลดจำนวนเล่ม<br>- คำนวณยอดเงินรวมสุทธิ"]
    
    CartPage --> Checkout["4. ไปที่ขั้นตอนชำระเงิน (Checkout)"]
    
    Checkout --> PaySim["5. เลือกช่องทางชำระเงินจำลอง<br>- PromptPay QR Code จำลอง<br>- โอนผ่านบัญชีธนาคาร<br>- บัตรเครดิตจำลอง (Mock Sandbox)"]
    
    PaySim --> UploadSlip["6. แนบหลักฐานสลิปจำลอง<br>(หรือใช้สลิปทดสอบเริ่มต้น)"]
    
    UploadSlip --> SubmitOrder["7. กดยืนยันคำสั่งซื้อ"]
    
    subgraph Transaction ["ธุรกรรมในฐานข้อมูล (Database Transaction)"]
        GenOrderNum["สร้างเลขที่คำสั่งซื้อ ORD-YYYYMMDD-XXXX"]
        InsertOrder["บันทึกตาราง orders (สถานะ PENDING)"]
        InsertItems["บันทึกตาราง order_items (Snapshot ราคา)"]
        InsertPayment["บันทึกตาราง payments (สถานะ PENDING)"]
        ClearCart["ล้างสินค้าในตาราง cart_items"]
        
        GenOrderNum --> InsertOrder --> InsertItems --> InsertPayment --> ClearCart
    end
    
    SubmitOrder --> Transaction
    Transaction --> MyOrders["8. ไปยังหน้าประวัติคำสั่งซื้อ (/my-orders)"]
    
    MyOrders --> OrderState{"ตรวจสอบสถานะคำสั่งซื้อในระบบ"}
    
    OrderState -- "สถานะ = PENDING (รอตรวจสอบ)" --> LockDownload["⛔ ปุ่มดาวน์โหลดถูกล็อก (Disabled)<br>ไม่อนุญาตให้เปิดไฟล์ (กฎข้อ 2.2)<br>หากพยายามเจาะ URL ตอบกลับ 403 Forbidden"]
    
    LockDownload --> WaitForAdmin["รอผู้ดูแลระบบ (Admin) ตรวจสอบสลิป"]
    
    WaitForAdmin --> AdminAction{"ผลการตรวจสลิปโดย Admin"}
    
    AdminAction -- "ไม่อนุมัติ / ยกเลิก" --> OrderCancelled["สถานะ = CANCELLED<br>ปิดการเข้าถึงไฟล์ถาวร"]
    
    AdminAction -- "อนุมัติเรียบร้อย" --> OrderConfirmed["สถานะ = CONFIRMED (ยืนยันแล้ว)<br>ระบบเจน Secure UUID Token ใน download_links"]
    
    OrderConfirmed --> UnlockDownload["✅ ปุ่มดาวน์โหลดสีเขียวเปิดใช้งาน"]
    
    UnlockDownload --> ClickDownload["9. ลูกค้าคลิกปุ่ม 'ดาวน์โหลด PDF'"]
    
    ClickDownload --> DeliverFile["10. เซิร์ฟเวอร์ส่งไฟล์ PDF ลงเครื่อง<br>พร้อมบันทึก download_count + 1"]
    
    DeliverFile --> Finish(["เสร็จสิ้นกระบวนการ"])

    style Start fill:#2563eb,color:#fff,stroke-width:2px
    style Finish fill:#10b981,color:#fff,stroke-width:2px
    style LockDownload fill:#fee2e2,stroke:#ef4444,stroke-width:2px,color:#991b1b
    style UnlockDownload fill:#dcfce7,stroke:#22c55e,stroke-width:2px,color:#166534
    style Transaction fill:#f8fafc,stroke:#94a3b8,stroke-dasharray: 5 5
```

---

## 2. จุดเด่นและกติกาสำคัญในกระบวนการ (Key Business Rules)
1. **การจำลองการชำระเงินที่ปลอดภัย (Simulation):** ไม่มีการเก็บข้อมูลบัตรเครดิตหรือข้อมูลบัญชีจริง เพื่อให้สอดคล้องกับข้อกำหนดวิชา
2. **การ Snapshot ราคาประวัติ (`unit_price`):** ข้อมูลราคาที่ซื้อจะถูกบันทึกแยกต่างหากจากตารางหนังสือ เพื่อไม่ให้ประวัติยอดขายคลาดเคลื่อนหากมีการปรับราคาในอนาคต
3. **การบังคับใช้กฎข้อ 2.2 อย่างเข้มงวด:** ระบบควบคุมสิทธิ์ทั้งในระดับ UI (ปุ่มล็อก) และระดับเซิร์ฟเวอร์ (ปฏิเสธ HTTP 403) ทำให้ผู้ใช้ไม่สามารถแอบเปิดไฟล์ได้ก่อนแอดมินยืนยัน
