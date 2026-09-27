import os

DOWNLOADS_DIR = os.path.join(os.path.dirname(__file__), 'static', 'downloads')
SLIPS_DIR = os.path.join(os.path.dirname(__file__), 'static', 'uploads', 'slips')

os.makedirs(DOWNLOADS_DIR, exist_ok=True)
os.makedirs(SLIPS_DIR, exist_ok=True)

sample_books = [
    ('sample_database_design.pdf', 'Mastering Database Design & SQL', 'Dr. Kittipong'),
    ('sample_fullstack_python.pdf', 'Full-Stack Web Development with Python', 'Aj. Pornchai'),
    ('sample_finance_invest.pdf', 'Personal Finance and Investment Guide', 'Chatchawal'),
    ('sample_focus_productivity.pdf', 'Focus & Productivity Psychology', 'Dr. Tidarat'),
    ('sample_growth_hacking.pdf', 'Modern Growth Hacking & Digital Ads', 'Anant'),
    ('sample_generative_ai.pdf', 'Practical Generative AI for Developers', 'Dr. Teerapat'),
    ('sample_scifi_eternity.pdf', 'Chronicles of Eternity', 'Kawee Srisiam'),
    ('sample_lean_startup.pdf', 'Lean Startup & Product Strategy', 'Nattaporn'),
    ('sample_clean_arch.pdf', 'Clean Architecture in Action', 'Dr. Kittipong'),
    ('sample_negotiation.pdf', 'The Art of Win-Win Negotiation', 'Dr. Tidarat'),
    ('sample_data_analytics.pdf', 'Data Analytics with SQL & BI', 'Dr. Teerapat'),
    ('sample_lost_in_cosmos.pdf', 'Lost in Cosmos: Space Chronicles', 'Kawee Srisiam')
]

def create_pdf(filename, title, author):
    path = os.path.join(DOWNLOADS_DIR, filename)
    # Generate standard valid PDF byte structure
    title_clean = "".join([c if ord(c) < 128 else '?' for c in title])
    author_clean = "".join([c if ord(c) < 128 else '?' for c in author])
    
    stream_content = f"BT\n/F1 20 Tf\n60 720 Td\n({title_clean}) Tj\n/F1 12 Tf\n0 -30 Td\n(Author: {author_clean}) Tj\n0 -25 Td\n(Licensed to: Official Customer - E-Book Store Database Project) Tj\n0 -25 Td\n(Verified Order - Download Authorized by System) Tj\nET"
    stream_len = len(stream_content.encode('utf-8'))
    
    pdf_text = f"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj
4 0 obj << /Length {stream_len} >> stream
{stream_content}
endstream
endobj
5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >> endobj
xref
0 6
0000000000 65535 f 
0000000010 00000 n 
0000000060 00000 n 
0000000117 00000 n 
0000000234 00000 n 
0000000350 00000 n 
trailer << /Size 6 /Root 1 0 R >>
startxref
430
%%EOF"""
    with open(path, 'wb') as f:
        f.write(pdf_text.encode('utf-8'))
    print(f"Created sample PDF: {path}")

for fn, t, a in sample_books:
    create_pdf(fn, t, a)

# Create 5 sample mock slips (SVGs that browser and preview can display)
for i in range(1, 6):
    slip_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="360" height="480" viewBox="0 0 360 480">
  <rect width="360" height="480" rx="16" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/>
  <rect width="360" height="80" rx="16" fill="#10b981"/>
  <text x="180" y="45" font-family="Arial, sans-serif" font-size="20" font-weight="bold" fill="#ffffff" text-anchor="middle">หลักฐานการชำระเงินจำลอง #{i}</text>
  <text x="180" y="65" font-family="Arial, sans-serif" font-size="12" fill="#ecfdf5" text-anchor="middle">MOCK PAYMENT SLIP (FOR DEMO ONLY)</text>
  
  <circle cx="180" cy="130" r="32" fill="#d1fae5"/>
  <path d="M168 130 l8 8 l16 -16" stroke="#059669" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  
  <text x="180" y="185" font-family="Arial, sans-serif" font-size="14" fill="#64748b" text-anchor="middle">โอนเงินสำเร็จ</text>
  <text x="180" y="215" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="#1e293b" text-anchor="middle">฿{350 + i*120}.00</text>
  
  <line x1="30" y1="240" x2="330" y2="240" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4"/>
  
  <text x="40" y="270" font-family="Arial, sans-serif" font-size="13" fill="#64748b">จากผู้โอน:</text>
  <text x="320" y="270" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="#334155" text-anchor="end">ลูกค้าจำลอง #{i}</text>
  
  <text x="40" y="305" font-family="Arial, sans-serif" font-size="13" fill="#64748b">ไปยังบัญชี:</text>
  <text x="320" y="305" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="#334155" text-anchor="end">ร้าน E-Book Store (PromptPay)</text>
  
  <text x="40" y="340" font-family="Arial, sans-serif" font-size="13" fill="#64748b">รหัสอ้างอิง:</text>
  <text x="320" y="340" font-family="Arial, sans-serif" font-size="13" fill="#334155" text-anchor="end">TXN-2026090{i}-987{i}</text>
  
  <text x="40" y="375" font-family="Arial, sans-serif" font-size="13" fill="#64748b">เวลาทำรายการ:</text>
  <text x="320" y="375" font-family="Arial, sans-serif" font-size="13" fill="#334155" text-anchor="end">2026-09-{10+i} 14:3{i}:00</text>
  
  <rect x="30" y="410" width="300" height="44" rx="8" fill="#fef3c7" stroke="#fde68a"/>
  <text x="180" y="437" font-family="Arial, sans-serif" font-size="12" fill="#92400e" text-anchor="middle">⚠️ ข้อมูลจำลองสำหรับทดสอบโครงงาน</text>
</svg>"""
    slip_file = os.path.join(SLIPS_DIR, f"mock_slip_{i}.svg")
    with open(slip_file, 'w', encoding='utf-8') as f:
        f.write(slip_svg)
    # Also save as .png extension for any template compatibility if needed
    with open(os.path.join(SLIPS_DIR, f"mock_slip_{i}.png"), 'w', encoding='utf-8') as f:
        f.write(slip_svg)

print("Generated sample PDFs and Mock Slips successfully.")
