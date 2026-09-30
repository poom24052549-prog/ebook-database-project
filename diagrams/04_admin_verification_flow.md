# ไดอะแกรมที่ 4: แผนผังกระบวนการตรวจสอบคำสั่งซื้อของผู้ดูแลร้าน (Admin Verification Flow)
**โครงงาน:** Mini Project Database ร้านขาย E-Book  
**หมวดหมู่:** เส้นทางการทำงานของผู้ดูแลร้าน (Admin Journey & Workflow) ตามข้อกำหนดหัวข้อ 3  

---

## 1. แผนผังกระบวนการทำงานของผู้ดูแลร้าน (Flowchart)

```mermaid
flowchart TD
    AdminStart(["ผู้ดูแลร้านเข้าสู่ระบบ (Login as Admin)"]) --> Dash["1. แดชบอร์ดภาพรวม (Dashboard)<br>- ตรวจดูยอดขายสะสม และคำสั่งซื้อใหม่<br>- ตรวจสอบกราฟยอดขายและหมวดหมู่"]
    
    Dash --> OrderList["2. เข้าสู่หน้ารายการคำสั่งซื้อ (/admin/orders)"]
    
    OrderList --> FilterPending["3. คลิกตัวกรอง 'รอตรวจสอบ (PENDING)'"]
    
    FilterPending --> ViewDetail["4. คลิกดูรายละเอียดคำสั่งซื้อ (/admin/orders/id)<br>- ตรวจชื่อลูกค้าและรายการหนังสือ<br>- ตรวจยอดเงินสุทธิที่ต้องชำระ<br>- ตรวจสอบภาพสลิปการโอนเงินจำลอง"]
    
    ViewDetail --> Decision{"การตรวจสอบสลิปและยอดเงิน"}
    
    Decision -- "สลิปถูกต้อง & ยอดเงินตรง" --> ActionConfirm["5ก. เลือกสถานะ: 'CONFIRMED' (ยืนยันแล้ว)<br>พิมพ์บันทึก: 'ยอดเงินโอนถูกต้อง เรียบร้อย'"]
    
    subgraph ConfirmProcess ["ระบบจัดการฐานข้อมูลอัตโนมัติ (Automated Database Process)"]
        UpdateOrderConf["UPDATE orders SET status = 'CONFIRMED'"]
        UpdatePayVer["UPDATE payments SET payment_status = 'VERIFIED'"]
        GenTokenLoop["วนลูปสร้าง Token UUID ใน download_links<br>(กำหนด is_active = 1)"]
        
        UpdateOrderConf --> UpdatePayVer --> GenTokenLoop
    end
    
    ActionConfirm --> ConfirmProcess
    ConfirmProcess --> ClientNotifyConfirm["✅ ลูกค้าได้รับสิทธิ์ดาวน์โหลดไฟล์ E-Book ทันที"]
    
    Decision -- "สลิปไม่ถูกต้อง / ลูกค้าขอยกเลิก" --> ActionCancel["5ข. เลือกสถานะ: 'CANCELLED' (ยกเลิก)<br>พิมพ์เหตุผลบันทึกร้านค้า"]
    
    subgraph CancelProcess ["ระบบเพิกถอนสิทธิ์"]
        UpdateOrderCanc["UPDATE orders SET status = 'CANCELLED'"]
        UpdatePayRej["UPDATE payments SET payment_status = 'REJECTED'"]
        RevokeToken["UPDATE download_links SET is_active = 0"]
        
        UpdateOrderCanc --> UpdatePayRej --> RevokeToken
    end
    
    ActionCancel --> CancelProcess
    CancelProcess --> ClientNotifyCancel["❌ ปิดการเข้าถึงไฟล์ถาวร"]
    
    Decision -- "สลิปไม่ชัดเจน / รอหลักฐานเพิ่ม" --> ActionPending["5ค. คงสถานะเป็น: 'PENDING'<br>พิมพ์บันทึกแจ้งลูกค้า"]
    
    ActionPending --> ClientNotifyPending["⚠️ ลูกค้ายังคงอยู่ในสถานะรอตรวจสอบ"]
    
    ClientNotifyConfirm --> Finish(["เสร็จสิ้นการจัดการคำสั่งซื้อ"])
    ClientNotifyCancel --> Finish
    ClientNotifyPending --> Finish

    style AdminStart fill:#dc2626,color:#fff,stroke-width:2px
    style Finish fill:#2563eb,color:#fff,stroke-width:2px
    style ActionConfirm fill:#dcfce7,stroke:#16a34a,stroke-width:2px,color:#166534
    style ActionCancel fill:#fee2e2,stroke:#dc2626,stroke-width:2px,color:#991b1b
    style ConfirmProcess fill:#f0fdf4,stroke:#86efac,stroke-dasharray: 4 4
```

---

## 2. ลำดับการเปลี่ยนสถานะ (State Machine Transitions)
* **PENDING $\rightarrow$ CONFIRMED:** ยอดเงินถูกต้อง $\rightarrow$ สร้างโทเค็นและเปิดการดาวน์โหลด
* **PENDING $\rightarrow$ CANCELLED:** สลิปปลอมหรือลูกค้าไม่ชำระ $\rightarrow$ ปิดบิลและระงับการดาวน์โหลด
* **CONFIRMED $\rightarrow$ CANCELLED:** กรณีขอคืนเงิน $\rightarrow$ เพิกถอนสิทธิ์ในตาราง `download_links` ทันที (`is_active = 0`)
