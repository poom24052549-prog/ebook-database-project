# คลังแผนผังและไดอะแกรมระบบ (System & Database Diagrams)
**โครงงาน:** Mini Project Database ร้านขาย E-Book ออนไลน์  
**รายวิชา:** Database Mini Project  

โฟลเดอร์นี้รวบรวมแผนภาพและไดอะแกรมทั้งหมดของโครงงาน เพื่อใช้ในการออกแบบ อ้างอิงสถาปัตยกรรมระบบ และประกอบการนำเสนอส่งงานอาจารย์ตามเกณฑ์ใบงานระยะที่ 1 และระยะที่ 2

---

## 📑 รายการไดอะแกรมในระบบ

| ลำดับ | ไฟล์เอกสาร | ชื่อไดอะแกรม | รายละเอียดและประโยชน์ |
|:---:|---|---|---|
| 🌐 | **[`view_diagrams.html`](view_diagrams.html)** | **Interactive Visual Viewer** | **หน้าเว็บสำหรับเปิดดูไดอะแกรมทั้งหมดแบบกราฟิกสวยงามในเบราว์เซอร์ (คลิกเปิดได้ทันที)** |
| 01 | **[`01_erd_database.md`](01_erd_database.md)** | **Entity-Relationship Diagram (ERD)** | แผนภาพความสัมพันธ์ฐานข้อมูลเชิงสัมพันธ์ 11 ตาราง (3NF, PK, FK, Cardinality) |
| 02 | **[`02_system_architecture.md`](02_system_architecture.md)** | **System Architecture Diagram** | สถาปัตยกรรมระบบ (Client Browser, Flask Web App, SQLite3 Engine, File Storage) |
| 03 | **[`03_purchase_and_download_flow.md`](03_purchase_and_download_flow.md)** | **Purchase & Download Flowchart** | แผนผังเส้นทางลูกค้า (Customer Flow) ตั้งแต่เลือกหนังสือ สั่งซื้อ ตรวจสอบสลิป จนถึงรับไฟล์ PDF |
| 04 | **[`04_admin_verification_flow.md`](04_admin_verification_flow.md)** | **Admin Order Verification Flowchart** | แผนผังกระบวนการของผู้ดูแลร้านในการตรวจสอบสลิปจำลอง และเปลี่ยนสถานะเพื่อปลดล็อกสิทธิ์ดาวน์โหลด |
| 05 | **[`05_data_flow_diagram.md`](05_data_flow_diagram.md)** | **Data Flow Diagram (DFD Level 0 & 1)** | แผนภาพกระแสข้อมูล แสดงการไหลของข้อมูลระหว่าง Entity, Process และ Data Stores ทั้ง 6 แหล่ง |

---

### 💡 วิธีเปิดดูไดอะแกรมแบบกราฟิก
* ดับเบิ้ลคลิกเปิดไฟล์ **[`view_diagrams.html`](view_diagrams.html)** ด้วย Google Chrome หรือ Microsoft Edge จะแสดงผลเป็นภาพกราฟิกชัดเจน พร้อมคำอธิบายทุกไดอะแกรม
