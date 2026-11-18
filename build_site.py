"""Generates the static pages (python3 build_site.py). Data: downloads/bom.csv, modules.json."""
import csv, html, json, os
H = os.path.dirname(os.path.abspath(__file__))
E = html.escape
NAV = [('index.html', 'เครื่อง'), ('model.html', 'โมเดล 3 มิติ'), ('sim.html', 'จำลองการทำงาน'), ('how.html', 'การทำงาน'), ('build.html', 'สร้างเอง'), ('assembly.html', 'ประกอบ'), ('learn.html', 'งานวิจัย'), ('judges.html', 'สำหรับกรรมการ')]
def page(fn, title, body, desc='', extra_head='', script=''):
    links = ''.join(f'<a href="{h}">{t}</a>' for h, t in NAV)
    out = f'''<!doctype html><html lang="th"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}"><meta name="theme-color" content="#c2303f">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anuphan:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="site.css"><script src="site.js"></script>{extra_head}</head><body>
<nav><div class="wrap"><a class="brand" href="index.html"><span class="logo">🥩</span>Meat Inspection Station</a>
<div class="links" id="links">{links}<button class="tbtn" id="tbtn" aria-label="สลับโหมดมืด">◐</button></div><button class="mbtn" id="mbtn" aria-label="เมนู">☰</button></div></nav>
{body}
<footer><div class="wrap">โครงงานสถานีตรวจคุณภาพเนื้อวัวบนสายพาน · ออกแบบด้วย Fusion 360 · ภาพและโมเดล 3 มิติสร้างจากแบบ CAD ไม่ใช่ภาพถ่ายของจริง · ข้อมูลอัปเดต 18 พ.ย. 2569 · <a href="judges.html#limits" style="text-decoration:underline">ข้อจำกัด</a></div></footer>{script}</body></html>'''
    open(os.path.join(H, fn), 'w', encoding='utf-8').write(out)

IMP = '<script type="importmap">{"imports":{"three":"./vendor/three.module.min.js"}}</script>'
mods = json.load(open(os.path.join(H, 'modules.json'), encoding='utf-8'))

# ---------------------------------------------------------------- index
page('index.html', 'สถานีตรวจคุณภาพเนื้อวัวบนสายพาน', f'''
<header class="hero"><div class="wrap"><div>
<span class="kick">โครงงานสถานีตรวจเนื้อ · งบเป้าหมาย 4,500–6,000 บาท</span>
<h1>ตรวจคุณภาพเนื้อวัว<br>บนสายพานเล็ก ๆ</h1>
<p class="lead">แพ็กเนื้อเลื่อนเข้าอุโมงค์ปิดแสง หยุดถ่ายภาพ วัดไขมันแทรก สีเนื้อ และอ่านเซนเซอร์เสริม แล้วสรุปเป็นสถานะ ไม่ได้คัดแยกเนื้อ (โมดูลคัดแยกเป็นออปชัน)</p>
<div class="row"><a class="btn go" href="model.html">ดูโมเดล 3 มิติ →</a><a class="btn ghost" href="#demo">▶ คลิปแนะนำ</a><a class="btn ghost" href="build.html">สร้างเอง</a></div>
<div class="chips"><span class="chip">โปรไฟล์อะลูมิเนียม 2020</span><span class="chip">อะคริลิกตัดและเจาะเอง</span><span class="chip">พิมพ์ 3 มิติ PETG</span><span class="chip">ESP32 + กล้อง USB</span><span class="chip">มอเตอร์ DC + เอนโค้ดเดอร์</span></div>
</div><div class="v3d" id="hero3d"><div class="ld" id="ld">กำลังโหลดโมเดล 3 มิติ…</div><span class="hint">ลากเพื่อหมุน · ถ่างนิ้วเพื่อซูม</span></div></div></header>

<section id="demo"><div class="wrap"><h2>คลิปแนะนำ</h2><p class="sub">แนวตั้ง 53 วินาที พากย์ไทย (เสียงสังเคราะห์) ภาพในคลิปเป็นเรนเดอร์จากโมเดล</p>
<div class="vid"><video controls playsinline preload="metadata" poster="img/poster.jpg"><source src="demo.mp4" type="video/mp4"></video>
<div class="note"><b>หมายเหตุ</b> เครื่องนี้ยังเป็นแบบ CAD ที่ออกแบบให้ประกอบได้ ยังไม่ได้ประกอบและทดสอบกับมอเตอร์ กล้อง และเซนเซอร์จริง</div></div></div></section>

<section class="alt"><div class="wrap"><h2>จุดเด่น</h2><p class="sub">ออกแบบให้คนทั่วไปสร้างได้เอง ด้วยของที่หาซื้อในไทยและเครื่องพิมพ์ 3 มิติ</p>
<div class="grid">
<div class="card feat"><div class="ic">📸</div><h3>ถ่ายแบบควบคุมแสง</h3><p>อุโมงค์ปิดแสง ไฟขาว (และ NIR/UV ในชุด Plus) แผ่นอ้างอิงสีขาว/เทา 18% ในทุกภาพ</p></div>
<div class="card feat"><div class="ic">🥩</div><h3>วัด marbling และสีเนื้อ</h3><p>แยกไขมันจากกล้ามเนื้อด้วยสี Lab คำนวณ % ไขมันแทรก สี L*a*b* และอัตราส่วนสีน้ำตาล</p></div>
<div class="card feat"><div class="ic">🧪</div><h3>สัญญาณเสริม</h3><p>สเปกตรัมจุด AS7341 อุณหภูมิผิว MLX90614 แก๊ส MQ-137 และฟิล์มกะหล่ำม่วงบ่งชี้ความสด</p></div>
<div class="card feat"><div class="ic">🔧</div><h3>ถอดประกอบง่าย</h3><p>เสาร่องสอดแผ่นอะคริลิก ฝาแม่เหล็ก ตลับกล้องสไลด์ เสียบคอนเนคเตอร์ ไม่มีสายลอย</p></div>
<div class="card feat"><div class="ic">🎯</div><h3>หยุดแม่นด้วยเอนโค้ดเดอร์</h3><p>มอเตอร์ DC เกียร์ฉาก + BTS7960 (IBT-2) ลูปตำแหน่ง 1 kHz บน ESP32</p></div>
<div class="card feat"><div class="ic">💸</div><h3>งบประหยัด</h3><p>อะคริลิกแผ่นเต็มตัดเอง ชิ้นส่วนพิมพ์เอง ไม่กัด PCB ใช้บอร์ดสำเร็จรูป</p></div></div></div></section>

<section><div class="wrap"><h2>ภาพจากแบบ</h2><p class="sub">เรนเดอร์จาก Fusion 360</p><div class="grid">
<div class="card"><img src="img/cu_meatpack.jpg" alt="" loading="lazy"><div class="b"><h3>แพ็กเนื้อวัว</h3><p>ถาดโฟม 65×90 มม. แผ่นซับ สเต็ก ฟิล์ม สติกเกอร์ ขนาดตามมุมมองกล้อง</p></div></div>
<div class="card"><img src="img/cu_tunnel_open.jpg" alt="" loading="lazy"><div class="b"><h3>อุโมงค์ปิดแสง</h3><p>เสาพิมพ์มีร่องสอดแผ่นอะคริลิกดำ ตลับกล้องหางเหยี่ยว</p></div></div>
<div class="card"><img src="img/cu_drive.jpg" alt="" loading="lazy"><div class="b"><h3>ชุดขับ</h3><p>มอเตอร์ DC เกียร์ฉาก เอนโค้ดเดอร์ รางไวร์ดักท์ 20×20</p></div></div>
<div class="card"><img src="img/cu_controller.jpg" alt="" loading="lazy"><div class="b"><h3>กล่องควบคุม</h3><p>อะคริลิกใส เสาพิมพ์ แผงสอดร่อง ฝาแม่เหล็ก</p></div></div>
<div class="card"><img src="img/cu_mains.jpg" alt="" loading="lazy"><div class="b"><h3>ไฟเข้าเครื่อง</h3><p>ช่อง IEC C14 มีฟิวส์+สวิตช์ สาย AC ปลั๊กไทย</p></div></div>
<div class="card"><img src="img/cu_blocks.jpg" alt="" loading="lazy"><div class="b"><h3>ลูกกลิ้งและแท่นลูกปืน</h3><p>ลูกกลิ้งพิมพ์ 608ZZ ยึดบนรางด้วย M5 + T-nut</p></div></div></div></div></section>

<section class="alt"><div class="wrap"><h2>ตัวเลขหลักของแบบ</h2><p class="sub">จากแบบ CAD ปัจจุบัน (ค่าบางส่วนเป็นประมาณ ดูหน้า "สำหรับกรรมการ")</p><div class="kpi">
<div><b>485×162</b><span>มม. ขนาดโครง (โหมด COMPACT)</span></div><div><b>≈ 120</b><span>มม. ความสูงผิวสายพานจากโต๊ะ</span></div><div><b>≈ 0.84</b><span>กก. PETG · ≈ 45 ชม. พิมพ์</span></div><div><b>≈ 6,300</b><span>บาท งบแกนหลัก (ประมาณ)</span></div><div><b>≤ 65</b><span>มม. ขนาดชิ้นเนื้อตามแนวสายพาน</span></div></div></div></section>
''', 'แบบสถานีตรวจคุณภาพเนื้อวัวบนสายพานขนาดเล็ก พร้อมโมเดล 3 มิติ BOM และไฟล์พิมพ์',
 IMP, '<script type="module">import{mount}from"./viewer3d.js";mount(document.getElementById("hero3d"),{auto:true}).then(()=>document.getElementById("ld").remove()).catch(()=>{document.getElementById("ld").textContent="โหลดโมเดล 3 มิติไม่ได้ ลองรีเฟรช หรือดูภาพด้านล่าง"})</script>')

# ---------------------------------------------------------------- model
mlist = ''.join(f'<label><input type="checkbox" data-k="{m["key"]}" checked>{E(m["th"])}<small>{m["tris"]//1000}k</small></label>' for m in mods if m['tris'])
page('model.html', 'โมเดล 3 มิติ — สถานีตรวจเนื้อ', f'''
<section style="padding-top:30px"><div class="wrap"><h2>โมเดล 3 มิติ</h2><p class="sub">แปลงจากไฟล์ STEP ของ Fusion 360 ลากเพื่อหมุน เลื่อนล้อเมาส์เพื่อซูม ติ๊กเพื่อซ่อน/แสดงแต่ละส่วน</p>
<div class="split"><div class="mods" id="mods"><b style="padding:6px 10px;display:block">ส่วนประกอบ</b>{mlist}
<div style="padding:8px 10px;border-top:1px solid var(--line)"><b style="font-size:14px">โปร่งใส (มองทะลุ)</b>
<label style="padding:6px 0"><input type="checkbox" id="xt">อุโมงค์ปิดแสง</label><label style="padding:6px 0"><input type="checkbox" id="xc">กล่องควบคุม</label><label style="padding:6px 0"><input type="checkbox" id="xa">ทั้งหมด (X-ray)</label></div>
<div style="padding:8px 10px"><button class="btn ghost" id="solo" style="padding:8px 14px;font-size:14px">แสดงทั้งหมด</button></div>
<div style="padding:8px 10px;font-size:13px;color:var(--muted)">แผ่นอะคริลิกโปร่งใส · ชิ้นส่วนบางตัว (E-stop, ช่อง C14, PSU, ไดรเวอร์) เป็นรูปทรงทั่วไป ยังไม่ปรับตามสินค้าจริง</div></div>
<div class="v3d tall" id="v"><div class="ld" id="ld">กำลังโหลดโมเดล 3 มิติ (6.6 MB)…</div></div></div>
<p style="margin-top:14px"><a class="btn ghost" href="downloads/assembly.step" download>ดาวน์โหลด STEP (8 MB)</a></p></div></section>''',
 '', IMP, '''<script type="module">import{mount}from"./viewer3d.js";const ld=document.getElementById("ld");
mount(document.getElementById("v"),{auto:false,onProgress:p=>ld.textContent="กำลังโหลด "+Math.round(p*100)+"%"}).then(v=>{ld.remove();
document.querySelectorAll("#mods input").forEach(i=>i.onchange=()=>v.setVisible(i.dataset.k,i.checked));
const xr=(keys,on)=>keys.forEach(k=>v.setOpacity(k,on?0.14:1));
document.getElementById("xt").onchange=e=>xr(["tunnel"],e.target.checked);document.getElementById("xc").onchange=e=>xr(["control"],e.target.checked);
document.getElementById("xa").onchange=e=>{xr(["frame","conveyor","drive","tunnel","sensing","control"],e.target.checked);document.getElementById("xt").checked=document.getElementById("xc").checked=e.target.checked};
document.getElementById("solo").onclick=()=>document.querySelectorAll("#mods input").forEach(i=>{i.checked=true;v.setVisible(i.dataset.k,true)})}).catch(()=>ld.textContent="โหลดโมเดลไม่ได้ ลองรีเฟรช")</script>''')

# ---------------------------------------------------------------- how
page('how.html', 'หลักการทำงาน', '''
<section style="padding-top:30px"><div class="wrap"><h2>หลักการทำงาน (stop-and-capture)</h2><p class="sub">ESP32 คุมสายพานด้วยตำแหน่งจากเอนโค้ดเดอร์ ส่วนโปรแกรมบนคอมพิวเตอร์ถ่ายภาพและวิเคราะห์</p>
<ol class="steps">
<li><b>วางแพ็ก</b> โฟโต้เซนเซอร์ E18-D80NK ตรวจพบถาด</li>
<li><b>เดินเข้ากล้อง</b> สายพานเดินระยะที่ตั้งไว้ (ปรับด้วย <code>DIST</code>) จนถาดหยุดกลางภาพกล้องในอุโมงค์</li>
<li><b>ถ่ายภาพ</b> ไฟขาว (และ NIR 850 / UV 365 ในชุด Plus) ติดทีละแบบ กล้องถ่ายพร้อมแผ่นสีอ้างอิง</li>
<li><b>วิเคราะห์ภาพ</b> แปลงเป็นแสงเชิงเส้น ปรับด้วยการ์ดเทา 18% แยกเนื้อด้วย Lab แยกไขมันด้วย Otsu บนแกน a* คำนวณ % marbling สี L*a*b* อัตราส่วนสีน้ำตาล</li>
<li><b>อ่านเซนเซอร์</b> เลื่อนถาดไปใต้ AS7341 / MLX90614 / MQ-137 รอ 1.2 วินาที</li>
<li><b>สรุปผล</b> สถานะ ok / watch / alarm (กฎเริ่มต้น ต้องปรับเทียบ) บันทึก CSV และภาพ annotated แล้วปล่อยถาดออก</li></ol>
<h2 style="margin-top:44px">ฮาร์ดแวร์ → ขา ESP32</h2><div class="tw"><table>
<tr><th>ขา</th><th>ใช้ทำ</th><th>หมายเหตุ</th></tr>
<tr><td>26 / 27</td><td>BTS7960 RPWM / LPWM</td><td>PWM 20 kHz</td></tr><tr><td>13 / 14</td><td>Encoder A / B</td><td>จ่ายไฟ encoder 3.3 V</td></tr>
<tr><td>34</td><td>โฟโต้เซนเซอร์</td><td>NPN + pull-up 10k</td></tr><tr><td>32</td><td>ปุ่ม START</td><td>ต่อลง GND</td></tr><tr><td>33</td><td>ESTOP_OK</td><td>อ่านราง 12 V ผ่านตัวแบ่งแรงดัน</td></tr>
<tr><td>16 / 17 / 18</td><td>MOSFET ไฟ ขาว / NIR / UV</td><td>PWM 5 kHz</td></tr><tr><td>21 / 22</td><td>I²C: AS7341 + MLX90614</td><td></td></tr><tr><td>35</td><td>MQ-137 (AO)</td><td>ต้องมีตัวแบ่ง 10k/20k</td></tr></table></div>
<p class="sub" style="margin-top:14px">E-stop ตัดไฟ 12 V แบบฮาร์ดแวร์เท่านั้น ไม่ใช่ฟังก์ชันความปลอดภัยที่รับรอง ไฟบ้านอยู่ในกล่อง A เท่านั้น ให้ช่างไฟตรวจ</p>
<div class="note ok"><b>สถานะซอฟต์แวร์</b> firmware คอมไพล์ผ่านบน ESP32 core 3.3.12 (ใช้แฟลช 26%) และโปรแกรม Python ผ่าน unit test 5 ข้อบนภาพสังเคราะห์ <b>ยังไม่ได้ทดสอบกับฮาร์ดแวร์จริง</b></div></div></section>''', 'หลักการทำงานของสถานีตรวจเนื้อ')

# ---------------------------------------------------------------- build (BOM)
rows = list(csv.DictReader(open(os.path.join(H, 'downloads', 'bom.csv'), encoding='utf-8-sig')))
tot = {}
trs = ''
for r in rows:
    t = r['Tier']; v = float(r['Total THB'] or 0); tot[t] = tot.get(t, 0) + v
    pill = {'core': 'g', 'plus': 'y', 'sort': 'r'}.get(t, '')
    lnk = f' <a href="{E(r["Shopee"])}" target="_blank" rel="noopener" style="color:var(--sky)">Shopee</a>' if r['Shopee'] else ''
    trs += f'<tr><td>{r["#"]}</td><td><span class="pill {pill}">{t}</span></td><td>{E(r["Group"])}</td><td><b>{E(r["Item"])}</b><br><span style="color:var(--muted);font-size:13px">{E(r["Spec"])}</span></td><td>{E(r["Qty"])}</td><td>{E(r["Unit THB (est.)"])}</td><td>{E(r["Total THB"])}</td><td>{lnk}</td></tr>'
page('build.html', 'สร้างเอง — BOM และไฟล์', f'''
<section style="padding-top:30px"><div class="wrap"><h2>ไฟล์สำหรับสร้างเอง</h2><p class="sub">ไฟล์พิมพ์ 3 มิติ แบบตัดอะคริลิก STEP โปรแกรมและเฟิร์มแวร์</p>
<div class="dl"><a href="downloads/print_stl_petg.zip"><b>⬇ STL พิมพ์ PETG</b><span>84 ชิ้น · 4.5 MB · รวมคู่มือพิมพ์</span></a>
<a href="downloads/acrylic_dxf.zip"><b>⬇ DXF แผ่นอะคริลิก</b><span>18 ชิ้น + ใบรายการตัด/เจาะด้วยมือ</span></a>
<a href="downloads/assembly.step"><b>⬇ STEP ทั้งชุด</b><span>8 MB</span></a>
<a href="downloads/bom.csv"><b>⬇ BOM (CSV)</b><span>52 รายการ</span></a>
<a href="downloads/meat_station.ino"><b>⬇ Firmware ESP32</b><span>Arduino · meat_station.ino</span></a>
<a href="downloads/host_python.zip"><b>⬇ โปรแกรมวิเคราะห์ภาพ</b><span>Python + OpenCV + unit test</span></a></div>
<h2 style="margin-top:46px">วิธีสร้างโดยย่อ</h2>
<ol class="steps"><li>ตัดโปรไฟล์ 2020 ตามรายการ (ขา 86×4, ราง 445×4, คาน 122×3 มม.) ประกอบด้วยฉากมุมหล่อและ T-nut</li>
<li>พิมพ์ชิ้นส่วน PETG ฝังเกลียวทองเหลืองด้วยหัวแร้ง (เฉพาะในชิ้นพิมพ์)</li>
<li>ซื้ออะคริลิกแผ่นเต็ม ตัดและเจาะเองตามใบรายการ (ขีดด้วยคัตเตอร์อะคริลิกแล้วหัก เจาะด้วยดอกสำหรับพลาสติก) ทาบชิ้นพิมพ์แล้วเจาะรูที่ต้องตรงกัน</li>
<li>ประกอบสายพาน ลูกกลิ้ง ตุ๊กตาลูกปืน 608ZZ และชุดมอเตอร์ ตั้งแรงตึงสายพาน</li>
<li>ประกอบอุโมงค์ ตลับกล้อง ไฟ และกล่องควบคุม ต่อสายตามขาที่ระบุ ให้ช่างไฟตรวจงานไฟบ้าน</li>
<li>อัปโหลด firmware ปรับเทียบ counts/มม. จูน PID ตั้งโฟกัสกล้อง และเก็บภาพเนื้อจริงเพื่อตั้งเกณฑ์</li></ol>
<h2 style="margin-top:46px">รายการอุปกรณ์ (BOM)</h2><p class="sub">ราคาเป็นราคาประมาณ ไม่ใช่ใบเสนอราคา (ยืนยันแล้วเฉพาะเว็บแคม C270 และเส้นพลาสติก 350 บาท/ม้วน) ลิงก์เป็นหน้าค้นหา</p>
<div class="kpi" style="margin-bottom:16px"><div><b>≈ {tot.get("core",0):,.0f}</b><span>บาท แกนหลัก (core) · ≈ 6,070 ถ้ามีเครื่องมือตัดเจาะแล้ว</span></div><div><b>+ {tot.get("plus",0):,.0f}</b><span>บาท ชุด Plus</span></div><div><b>+ {tot.get("sort",0):,.0f}</b><span>บาท โมดูลคัดแยก (ออปชัน)</span></div></div>
<div class="tw"><table><tr><th>#</th><th>ชุด</th><th>กลุ่ม</th><th>รายการ</th><th>จำนวน</th><th>ราคา/หน่วย</th><th>รวม</th><th></th></tr>{trs}</table></div>
<p class="sub" style="margin-top:12px">ตารางนี้เป็นราคาประมาณตอนออกแบบ ส่วนที่สั่งจริง ณ 17 พ.ย. 2569 รวมประมาณ 6,400–6,700 บาท (รวมเซนเซอร์ Plus ≈ 1,100) ดูรายการจริงใน <a href="downloads/lists_buy_and_print.pdf">PDF รายการอุปกรณ์และพาร์ทพิมพ์</a> · ที่ซื้อต่างจากแบบ: ขาโปรไฟล์ตัดจาก 100 เหลือ 86 มม. · LED 4000 K · heat-set M4 ยาว 6 มม.</p></div></section>''', 'BOM ไฟล์พิมพ์ DXF และวิธีสร้างสถานีตรวจเนื้อ')

# ---------------------------------------------------------------- learn
page('learn.html', 'งานวิจัยที่ใช้ — ตรวจคุณภาพเนื้อ', '''
<section style="padding-top:30px"><div class="wrap"><h2>วิธีตรวจคุณภาพเนื้อแบบใหม่ ๆ ที่ค้นมา</h2><p class="sub">ค้นเมื่อ 4 พ.ย. 2569 อ่านจากบทคัดย่อและหน้าสรุปเท่านั้น ยังไม่ได้อ่านฉบับเต็ม ตัวเลขความแม่นยำมาจากคนละชุดข้อมูล เทียบกันตรง ๆ ไม่ได้ และยังไม่ได้ทดสอบกับเนื้อของโครงงานนี้</p>
<div class="tw"><table><tr><th>วิธี</th><th>ต้นทุน</th><th>การตัดสินใจ</th></tr>
<tr><td>Multi-waveband LED + กล้องธรรมดา (Applied Sciences 2019)</td><td>ต่ำ</td><td><span class="pill g">เลือก</span> ไฟขาว + NIR 850 + UV 365</td></tr>
<tr><td>เซนเซอร์สเปกตรัม AS7341 (Biosensors 2022 เนื้อหมู)</td><td>ต่ำ</td><td><span class="pill g">เลือก</span> เก็บเป็น feature ต้องสร้าง calibration เอง</td></tr>
<tr><td>ฟิล์ม/อาร์เรย์สี (colorimetric) อ่านด้วยกล้อง</td><td>ต่ำมาก</td><td><span class="pill g">เลือก</span> ฟิล์มกะหล่ำม่วง ให้ค่าสีเท่านั้น</td></tr>
<tr><td>Computer vision สี + marbling (MSENet, SegFormer, YOLOv8)</td><td>ต่ำ</td><td><span class="pill g">เลือก</span> ใช้วิธีดั้งเดิม (Lab + Otsu) ก่อน แล้วค่อยต่อยอด</td></tr>
<tr><td>Thermal IR จุดเดียว MLX90614</td><td>ต่ำ</td><td><span class="pill g">เลือก</span> อุณหภูมิผิว</td></tr>
<tr><td>แก๊ส MQ-137 / e-nose</td><td>ต่ำ</td><td><span class="pill y">ทดลอง</span> ไวต่อชื้นและอุณหภูมิ ต้องปรับเทียบ</td></tr>
<tr><td>Structured-illumination (SIRI)</td><td>กลาง</td><td><span class="pill y">ต่อยอด</span> เกินงบ</td></tr>
<tr><td>Electrical impedance (EIS)</td><td>กลาง</td><td><span class="pill y">ต่อยอด</span> ต้องแตะเนื้อ</td></tr>
<tr><td>Hyperspectral imaging (HSI)</td><td>สูงมาก</td><td><span class="pill r">ไม่ใช้</span> เกินงบ</td></tr>
<tr><td>Raman / NIRS / Terahertz</td><td>สูง</td><td><span class="pill r">ไม่ใช้</span> เกินงบ</td></tr></table></div>
<h2 style="margin-top:44px">ตัวชี้วัดต่อแพ็กที่เครื่องรายงาน</h2><ol class="steps"><li><b>Marbling %</b> พื้นที่ไขมัน ÷ พื้นที่กล้ามเนื้อ และเกรด 3 ระดับ (ยังไม่ validate)</li><li><b>สีเนื้อ L*a*b*</b> จากภาพโพลาไรซ์ไขว้และแผ่นอ้างอิง</li><li><b>ดัชนีสีฟิล์มกะหล่ำ</b> ตารางสี→สถานะต้องปรับเทียบเอง</li><li><b>สเปกตรัม 11 ช่อง + ภาพ NIR/UV</b> เก็บเป็น feature สำหรับโมเดล</li><li><b>อุณหภูมิผิว + แนวโน้มแก๊ส NH₃</b></li><li><b>สถานะรวม</b> ok / watch / alarm ไม่ใช่การรับรองความปลอดภัยอาหาร</li></ol>
<div class="note" style="margin-top:20px"><b>ข้อควรระวังจากงานวิจัย</b> Computer vision ทำนาย pH ได้ไม่ดี (R² ≈ 0.32) จึงไม่รายงาน pH ตัวเลขของ HSI/สเปกตรัมมาจากเครื่องห้องแล็บที่ปรับเทียบกับ TVB-N เซนเซอร์ราคาถูกของโครงงานต้องสร้างการปรับเทียบเอง</div>
<h2 style="margin-top:44px">แหล่งอ้างอิง</h2><p class="sub">บทคัดย่อ/หน้าสรุป</p><ul style="color:var(--muted)">
<li><a style="text-decoration:underline" href="https://pmc.ncbi.nlm.nih.gov/articles/PMC12681067/" target="_blank" rel="noopener">รีวิว HSI (PMC12681067)</a></li>
<li><a style="text-decoration:underline" href="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9688451/" target="_blank" rel="noopener">AS7341 ความสดเนื้อหมู (Biosensors 2022)</a></li>
<li><a style="text-decoration:underline" href="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11731488/" target="_blank" rel="noopener">Colorimetric/fluorescent arrays</a></li>
<li><a style="text-decoration:underline" href="https://agris.fao.org/search/zh/records/64747d4b2d3f560f80afa255" target="_blank" rel="noopener">Multi-waveband LED (Applied Sciences 2019)</a></li></ul>
</div></section>''', 'งานวิจัยวิธีตรวจคุณภาพเนื้อแบบใหม่ที่ใช้กับโครงงาน')

# ---------------------------------------------------------------- judges
page('judges.html', 'สำหรับกรรมการ', '''
<section style="padding-top:30px"><div class="wrap"><h2>สำหรับกรรมการ</h2><p class="sub">สรุปว่าโครงงานทำอะไร อะไรทำเสร็จแล้ว และอะไรยังไม่ได้พิสูจน์</p>
<div class="kpi"><div><b>ออกแบบแล้ว</b><span>CAD ครบ 120 รายการยึด ชนกัน 4 จุดจิ๋ว ≤ 22 มม.³</span></div><div><b>เขียนแล้ว</b><span>firmware + โปรแกรมภาพ ผ่านการทดสอบเชิงโค้ด</span></div><div><b>ยังไม่ได้</b><span>ประกอบ ทดสอบกับของจริง และ validate เกรด</span></div></div>
<h2 style="margin-top:40px">คำถามที่คาดว่าจะถูกถาม</h2>
<details><summary>ต่างจากเครื่องคัดเกรดเนื้อทั่วไปอย่างไร</summary><p>เป็นสถานีตรวจราคาประหยัดที่สร้างเองได้ (เป้า 4,500–6,000 บาท) ใช้กล้องธรรมดา ไฟหลายช่วงคลื่น และเซนเซอร์ราคาถูกร่วมกัน ไม่ได้อ้างว่าแม่นเท่าเครื่องอุตสาหกรรม</p></details>
<details><summary>ความแม่นยำเท่าไร</summary><p>ยังไม่มีตัวเลข เกณฑ์ marbling และสถานะเป็นค่าตั้งต้น (USER_UNVALIDATED) ต้องเก็บภาพเนื้อจริงอย่างน้อย 100 ถาดต่อเกรดพร้อมค่าอ้างอิงจากผู้เชี่ยวชาญก่อน การทดสอบที่ทำแล้วใช้ภาพสังเคราะห์ที่รู้ค่าจริง ซึ่งตรวจได้แค่ว่าโค้ดทำงาน</p></details>
<details><summary>ตรวจความสดหรือความปลอดภัยของอาหารได้ไหม</summary><p>ไม่รับรอง เครื่องรายงานสัญญาณช่วยคัดกรอง (สี อุณหภูมิผิว ก๊าซ ฟิล์มสี) งานวิจัยชี้ว่าการทำนาย pH จากภาพทำได้ไม่ดี จึงไม่รายงาน pH</p></details>
<details><summary>ทำไมขนาดแพ็กเล็ก</summary><p>มุมมองกล้อง 16:9 ตามแนวสายพานราว 74 มม. ชิ้นเนื้อควรไม่เกิน ~65 มม. ถ้าใหญ่กว่า โปรแกรมจะติดธง clipped_by_frame</p></details>
<details><summary>ความปลอดภัยทางไฟฟ้า</summary><p>ไฟบ้านเข้าทางช่อง C14 ที่มีฟิวส์และสวิตช์ อยู่ในกล่อง A เท่านั้น ส่วนอื่นเป็น 12 V และ 5 V ต้องให้ช่างไฟตรวจงานเดินสาย E-stop เป็นการตัดไฟฮาร์ดแวร์ ไม่ใช่ระบบความปลอดภัยที่รับรอง</p></details>
<details><summary>งบประมาณจริงเท่าไร</summary><p>ที่สั่งจริงรวมประมาณ 6,400–6,700 บาท (รวมเซนเซอร์ Plus ≈ 1,100 บาท) ไม่รวมค่าสายพานสั่งทำและค่าตัดเลเซอร์ที่ยังไม่ทราบราคาจริง เป็นราคาในตะกร้า ไม่ใช่ใบเสร็จ ดูหน้า "สร้างเอง"</p></details>
<h2 id="limits" style="margin-top:40px">ข้อจำกัดที่ต้องรู้</h2>
<div class="note"><p><b>ภาพและโมเดล 3 มิติ</b> สร้างจากแบบ CAD ไม่ใช่เครื่องจริง</p><p><b>ส่วนประกอบทั่วไป</b> E-stop ช่อง C14 PSU ไดรเวอร์ มอเตอร์ ใช้ขนาดจากข้อมูลผู้ขายหรือรูปทรงมาตรฐาน ต้องวัดของจริงก่อนพิมพ์ขายึดและเจาะ</p><p><b>ยังไม่ได้ทดสอบ</b> PID ต้องจูน ปรับเทียบ counts/มม. ตั้งโฟกัสกล้องที่ ~15 ซม. เว็บแคมส่วนใหญ่มีฟิลเตอร์ตัด IR ทำให้แถบ NIR 850 มืด ต้องใช้กล้องที่ไม่มี IR-cut</p><p><b>เสียงพากย์ในคลิป</b> เป็นเสียงสังเคราะห์</p></div>
</div></section>''', 'สรุปโครงงานสำหรับกรรมการ: สิ่งที่ทำแล้ว ความแม่นยำ และข้อจำกัด')

# ---------------------------------------------------------------- sim
page('sim.html', 'จำลองการทำงาน — สถานีตรวจเนื้อ', """
<section style="padding-top:30px"><div class="wrap"><h2>จำลองการทำงาน</h2><p class="sub">แพ็กเนื้อวิ่งเข้าอุโมงค์ หยุดใต้กล้อง หยุดใต้เซนเซอร์ แล้วออกจากสายพาน ตามลำดับที่ firmware ตั้งไว้ (FEED → TO_CAM → AT_CAM → TO_SEN → AT_SEN → CLEAR)</p>
<div class="split" style="grid-template-columns:1fr 300px">
<div class="v3d tall" id="v"><div class="ld" id="ld">กำลังโหลดโมเดล 3 มิติ…</div>
<div id="hud" style="position:absolute;right:10px;top:10px;background:color-mix(in srgb,var(--panel) 90%,transparent);border:1px solid var(--line);border-radius:14px;padding:10px 14px;font-size:13px;min-width:190px;display:none"></div></div>
<div class="mods"><b style="padding:6px 10px;display:block">ขั้นตอน</b><div id="stp"></div>
<div style="padding:8px 10px;display:flex;gap:8px;flex-wrap:wrap"><button class="btn go" id="pp" style="padding:8px 16px;font-size:14px">⏸ หยุด</button><button class="btn ghost" id="sp" style="padding:8px 16px;font-size:14px">เร็ว ×1</button></div>
<div style="padding:4px 10px"><label style="padding:4px 0"><input type="checkbox" id="xt" checked>มองทะลุอุโมงค์</label><label style="padding:4px 0"><input type="checkbox" id="xc">มองทะลุกล่องควบคุม</label></div>
<div style="padding:8px 10px;font-size:12.5px;color:var(--muted)">ค่าที่แสดงเป็น <b>ตัวอย่างจำลอง</b> ไม่ใช่ผลวัดจริง การเคลื่อนที่จำลองจากลำดับในเฟิร์มแวร์ ไม่ใช่ข้อมูลจากเครื่องจริง</div></div></div></div></section>""",
 '', IMP, r"""<script type="module">import{mount}from"./viewer3d.js";
const ld=document.getElementById("ld"),hud=document.getElementById("hud"),stp=document.getElementById("stp");
const PH=[["FEED","สายพานวิ่งช้า ตรวจพบถาด (IR)",2.0],["AT_CAM","หยุดใต้กล้อง ถ่ายภาพ ขาว / NIR / UV",3.2],["TO_SEN","เลื่อนไปใต้เซนเซอร์",1.3],["AT_SEN","อ่าน AS7341 / MLX90614 / MQ-137",2.2],["CLEAR","ปล่อยถาดออกจากสายพาน",2.4]];
stp.innerHTML=PH.map((p,i)=>`<div class="sl" data-i="${i}" style="padding:7px 10px;border-radius:10px;font-size:14px"><b>${p[0]}</b><br><span style="color:var(--muted)">${p[1]}</span></div>`).join("");
const DEMO=[{m:11.8,L:43.1,a:22.4,b:11.0,t:3.8,s:"ok"},{m:19.5,L:40.2,a:24.9,b:12.3,t:4.1,s:"ok"},{m:6.4,L:37.6,a:18.2,b:10.1,t:8.9,s:"watch"}];
mount(document.getElementById("v"),{auto:false,onProgress:p=>ld.textContent="กำลังโหลด "+Math.round(p*100)+"%"}).then(v=>{ld.remove();
const U=v.unit,pack=v.nodesOf("meat"),base=pack.map(n=>n.position.x);const X0=175;
const setX=x=>pack.forEach((n,i)=>n.position.x=base[i]+(x-X0)*U);
const flash=k=>v.nodesOf("meat").forEach(n=>n.traverse(e=>{if(e.isMesh&&e.material.emissive){e.material.emissive.setRGB(k,k,k)}}));
v.setOpacity("tunnel",.14);
document.getElementById("xt").onchange=e=>v.setOpacity("tunnel",e.target.checked?.14:1);document.getElementById("xc").onchange=e=>v.setOpacity("control",e.target.checked?.14:1);
v.ctl.autoRotate=false;v.ctl.target.set(0,-.16,0);v.cam.position.set(1.15,.4,1.45);
let play=true,spd=1,t=0,idx=0,last=performance.now(),cyc=0;
const pp=document.getElementById("pp"),sp=document.getElementById("sp");
pp.onclick=()=>{play=!play;pp.textContent=play?"⏸ หยุด":"▶ เล่น"};sp.onclick=()=>{spd=spd===1?2:spd===2?.5:1;sp.textContent="เร็ว ×"+spd};
const ease=k=>k<0?0:k>1?1:k*k*(3-2*k);
function hudHtml(ph,k){const d=DEMO[cyc%3];let h=`<b>แพ็ก #${cyc+1}</b> <span class="pill">ตัวอย่างจำลอง</span><br>`;
if(ph===1){h+=k<.45?"แสงขาว…":k<.7?"NIR 850…":k<.9?"UV 365…":"วิเคราะห์ภาพ…";if(k>.9)h+=`<br>marbling ≈ ${d.m}% · L* ${d.L} a* ${d.a} b* ${d.b}`}
else if(ph===3){h+=k<.6?"กำลังอ่านเซนเซอร์…":`อุณหภูมิผิว ${d.t} °C`;}
else if(ph===4){h+=`marbling ≈ ${d.m}% · สถานะ <span class="pill ${d.s==="ok"?"g":"y"}">${d.s}</span>`}
else h+="รอตรวจ…";return h}
function step(now){requestAnimationFrame(step);const dt=Math.min(.1,(now-last)/1000);last=now;if(play)t+=dt*spd;
let a=t,ph=0;for(;ph<PH.length;ph++){if(a<PH[ph][2])break;a-=PH[ph][2]}
if(ph>=PH.length){t=0;cyc++;ph=0;a=0}
const k=a/PH[ph][2];let x;
if(ph===0)x=95+80*ease(k);else if(ph===1)x=175;else if(ph===2)x=175+65*ease(k);else if(ph===3)x=240;else x=240+170*ease(k);
setX(x);flash(ph===1?(.12+.1*Math.sin(now/90)):0);
hud.style.display="block";hud.innerHTML=hudHtml(ph,k);
stp.querySelectorAll(".sl").forEach((e,i)=>{e.style.background=i===ph?"var(--panel2)":"";e.style.outline=i===ph?"2px solid var(--accent)":""});}
requestAnimationFrame(step);}).catch(()=>ld.textContent="โหลดโมเดลไม่ได้ ลองรีเฟรช")</script>""")

print('pages ok')


# ---------------------------------------------------------------- assembly guide page (from 10_manual/assembly/assembly_guide.md)
import re
md = open(os.path.join(H, '..', '10_manual', 'assembly', 'assembly_guide.md'), encoding='utf-8').read()
steps_html = ''
for m in re.finditer(r'### ขั้นที่ (\d+) (.+?)\n\n!\[[^\]]*\]\(img/s(\d+)\.png\)\n\n(.*?)(?=\n### ขั้นที่|\n---|\Z)', md, re.S):
    n, title, im, rest = m.groups()
    items = re.findall(r'^\d+\. (.+)$', rest, re.M); chk = re.search(r'\*\*ตรวจ:\*\* (.+)', rest)
    conv = lambda t: re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', E(t).replace('&#x27;', "'")).replace('`', '')
    li = ''.join(f'<li>{conv(i)}</li>' for i in items)
    steps_html += f'<div class="card acard" style="margin:0 0 18px"><img src="img/assembly/s{im}.jpg" alt="ขั้นที่ {n}" loading="lazy"><div class="b"><h3>ขั้นที่ {n} {E(title)}</h3><ol class="steps">{li}</ol>' + (f'<p class="note"><b>ตรวจ:</b> {conv(chk.group(1))}</p>' if chk else '') + '</div></div>'
page('assembly.html', 'คู่มือประกอบ — สถานีตรวจเนื้อ', f'''
<style>.acard{{display:grid;grid-template-columns:1.1fr 1fr;align-items:center}}.acard img{{width:100%;height:100%;max-height:360px;object-fit:contain;background:#fff}}@media(max-width:760px){{.acard{{grid-template-columns:1fr}}}}</style>
<section style="padding-top:30px"><div class="wrap"><h2>คู่มือประกอบ 12 ขั้นตอน</h2>
<p class="sub">ภาพส้ม = ชิ้นที่เพิ่มในขั้นนั้น ภาพเป็นเรนเดอร์จากไฟล์ STEP (ผนังอุโมงค์/กล่องในภาพเป็นอะคริลิกใส แต่ของจริงพิมพ์ทึบ) ลำดับนี้ร่างจากแบบ <b>ยังไม่เคยประกอบจริง</b></p>
<div class="note" style="margin-bottom:18px"><b>ความปลอดภัย</b> หัวแร้งฝังเกลียวใช้เมื่อมีครูดูแล · ไฟบ้านเข้าช่อง C14 กล่องซ้ายเท่านั้น ให้ครูหรือช่างไฟตรวจก่อนเสียบปลั๊ก (ยังไม่มีแผนผังสายไฟที่ช่างไฟตรวจแล้ว) · ห้ามเสียบ/ถอดสายมอเตอร์ตอนมีไฟ · ห้ามมองไฟ IR/UV ตรง ๆ</div>
<div class="row" style="margin-bottom:18px"><a class="btn go" href="downloads/assembly_guide.pdf">⬇ คู่มือประกอบ (PDF)</a><a class="btn ghost" href="downloads/cad_parts_sheet.pdf">⬇ ภาพ CAD ชิ้นพิมพ์ (A4 1 หน้า)</a><a class="btn ghost" href="downloads/lists_buy_and_print.pdf">⬇ รายการอุปกรณ์ + พาร์ทพิมพ์ (PDF)</a></div>
<div class="vid" style="margin:0 auto 24px;max-width:340px"><video controls playsinline preload="metadata" poster="img/assembly/poster.jpg"><source src="assembly_clip.mp4" type="video/mp4"></video></div>
{steps_html}
<p class="sub">ทีมผู้จัดทำ: นายก้องภพ วาทปราชญ์ · นายปรัชกรณ์ ภิมุกภักดี · นายประกฤษฎิ์ ศรีเบญจบุตร (ม.5/2) · ครูที่ปรึกษา ครูสายสุดา เรืองซา</p></div></section>''', 'คู่มือประกอบสถานีตรวจคุณภาพเนื้อ 12 ขั้นตอน พร้อมภาพและคลิป')
