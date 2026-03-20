import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io, os, re
from datetime import date, timedelta

st.set_page_config(page_title="FDA & DBD System", page_icon="🏛️",
                   layout="wide", initial_sidebar_state="expanded")

BASE     = os.path.dirname(__file__)
FDA_XLSX = os.path.join(BASE, "FDA.xlsx")
DBD_XLSX = os.path.join(BASE, "DBDALL.xlsx")

THAI_MONTHS = {'มกราคม':1,'กุมภาพันธ์':2,'มีนาคม':3,'เมษายน':4,
               'พฤษภาคม':5,'มิถุนายน':6,'กรกฎาคม':7,'สิงหาคม':8,
               'กันยายน':9,'ตุลาคม':10,'พฤศจิกายน':11,'ธันวาคม':12}

# ── PALETTE ──────────────────────────────────────────────────
# Navy: #0d2137  Gold: #d4a017  Green: #059669  Red: #dc2626
# Amber: #d97706  BG: #f0f2f5   White: #fff    Text: #1a2332

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;600;700;800&family=IBM+Plex+Mono:wght@400;600&display=swap');

/* ── Global ── */
html,body,[class*="css"]{font-family:'Sarabun',sans-serif;background:#f0f2f5;}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding:1rem 1.5rem 2rem!important;background:#f0f2f5;}

/* ── Hide sidebar collapse button (keep nav buttons visible) ── */
[data-testid="collapsedControl"]{display:none!important;}
[data-testid="stSidebarCollapseButton"]{display:none!important;}
button[data-testid="baseButton-headerNoPadding"]{display:none!important;}
.stSidebarCollapsedControl{display:none!important;}
/* Force sidebar open, no toggle arrow */
section[data-testid="stSidebar"]{transform:none!important;width:230px!important;}

/* ── Nav links in sidebar ── */
.sb-nav a{
    display:block;padding:10px 18px;
    color:rgba(255,255,255,0.55);text-decoration:none;
    font-size:13px;font-weight:600;font-family:'Sarabun',sans-serif;
    border-left:3px solid transparent;margin:1px 0;
    transition:all .15s;
}
.sb-nav a:hover{color:#fff;background:rgba(255,255,255,0.06);}
.sb-nav a.active{color:#fff;background:rgba(212,160,23,0.15);border-left-color:#d4a017;}

/* ── Sidebar ── */
section[data-testid="stSidebar"]{
    background:#0d2137!important;
    min-width:230px!important;max-width:230px!important;
}
section[data-testid="stSidebar"] > div{padding-top:0!important;}
section[data-testid="stSidebar"] *{color:#cbd5e1;}

.sb-logo{padding:22px 18px 14px;border-bottom:1px solid rgba(255,255,255,0.08);}
.sb-logo .acc{font-size:10px;color:#d4a017;font-weight:700;letter-spacing:2px;text-transform:uppercase;}
.sb-logo h2{font-size:16px;font-weight:800;color:#fff;line-height:1.25;margin:4px 0 2px;}
.sb-logo .sub{font-size:11px;color:rgba(255,255,255,0.35);}
.sb-pill{margin:10px 12px;padding:9px 13px;background:rgba(255,255,255,0.06);
         border-radius:8px;border:1px solid rgba(255,255,255,0.1);}
.sb-pill .uname{font-size:12px;color:#fff;font-weight:700;}
.sb-pill .urole{font-size:11px;color:#d4a017;margin-top:2px;}
.sb-section{font-size:10px;color:rgba(255,255,255,0.3);font-weight:700;
            text-transform:uppercase;letter-spacing:1.5px;padding:12px 18px 4px;}
.sb-sync{padding:14px 18px 20px;border-top:1px solid rgba(255,255,255,0.08);
         font-size:10px;color:rgba(255,255,255,0.3);}

/* Nav buttons — force visible, override any hide rule */
section[data-testid="stSidebar"] .stButton>button{
    display:block!important;
    width:100%!important;text-align:left!important;padding:10px 18px!important;
    background:transparent!important;border:none!important;
    color:rgba(255,255,255,0.65)!important;
    font-size:13px!important;font-family:'Sarabun',sans-serif!important;font-weight:600!important;
    border-left:3px solid transparent!important;border-radius:0!important;
    margin:1px 0!important;transition:all .15s!important;
    box-shadow:none!important;
}
section[data-testid="stSidebar"] .stButton>button:hover{
    color:#fff!important;background:rgba(255,255,255,0.08)!important;
}
/* ── Nav links in sidebar (HTML fallback style) ── */
.sb-nav a{
    display:block;padding:10px 18px;
    color:rgba(255,255,255,0.55);text-decoration:none;
    font-size:13px;font-weight:600;border-left:3px solid transparent;margin:1px 0;
}
.sb-nav a:hover{color:#fff;background:rgba(255,255,255,0.06);}
.sb-nav a.active{color:#fff;background:rgba(212,160,23,0.15);border-left-color:#d4a017;}

/* ── Page banner ── */
.page-banner{
    background:linear-gradient(135deg,#0d2137 0%,#163352 100%);
    border-radius:12px;padding:18px 24px;margin-bottom:18px;
    box-shadow:0 4px 20px rgba(13,33,55,0.2);
}
.page-banner .acc{font-size:10px;color:#d4a017;font-weight:700;letter-spacing:.15em;text-transform:uppercase;}
.page-banner h1{font-size:20px;font-weight:800;color:#f0f4ff;margin:3px 0 2px;line-height:1.2;}
.page-banner p{font-size:12px;color:rgba(255,255,255,0.4);margin:0;}

/* ── KPI card ── */
.kpi{background:#fff;border-radius:10px;padding:18px 20px;
     border-left:4px solid #d4a017;
     box-shadow:0 2px 8px rgba(0,0,0,0.07);margin-bottom:4px;}
.kpi.g{border-left-color:#059669;}.kpi.r{border-left-color:#dc2626;}
.kpi.b{border-left-color:#3b82f6;}.kpi.o{border-left-color:#d97706;}
.kpi .lbl{font-size:10px;font-weight:700;text-transform:uppercase;
           letter-spacing:.1em;color:#6b7280;margin-bottom:5px;}
.kpi .val{font-size:26px;font-weight:900;color:#0d2137;
          font-family:'IBM Plex Mono',monospace;line-height:1;}
.kpi .sub{font-size:11px;color:#9ca3af;margin-top:4px;}

/* ── Risk bar ── */
.risk-bar{background:#fff;border-radius:10px;padding:12px 18px;
          display:flex;align-items:center;gap:12px;
          box-shadow:0 2px 8px rgba(0,0,0,0.07);margin-bottom:16px;}
.risk-seg{display:inline-flex;align-items:center;gap:6px;
          padding:5px 14px;border-radius:20px;font-size:12px;font-weight:700;}
.rs-lo{background:#d1fae5;color:#065f46;}
.rs-md{background:#fef3c7;color:#92400e;}
.rs-hi{background:#fee2e2;color:#991b1b;}

/* ── Badges ── */
.badge{display:inline-block;padding:2px 10px;border-radius:99px;font-size:11px;font-weight:700;}
.b-ok {background:#d1fae5;color:#065f46;}
.b-exp{background:#fee2e2;color:#991b1b;}
.b-run{background:#dbeafe;color:#1e40af;}
.b-cls{background:#fee2e2;color:#991b1b;}
.b-oth{background:#fef3c7;color:#92400e;}
.b-lo {background:#d1fae5;color:#065f46;}
.b-md {background:#fef3c7;color:#92400e;}
.b-hi {background:#fee2e2;color:#991b1b;}

/* ── Table ── */
.df-wrap{border-radius:10px;overflow:hidden;
         box-shadow:0 2px 8px rgba(0,0,0,0.08);background:#fff;}
.dataframe{width:100%;border-collapse:collapse;font-size:12.5px;}
.dataframe th{background:#0d2137;color:#d4a017;font-size:10px;font-weight:700;
              text-transform:uppercase;letter-spacing:.08em;padding:10px 13px;
              text-align:left;white-space:nowrap;}
.dataframe td{padding:9px 13px;border-bottom:1px solid #f0f2f5;
              background:#fff;vertical-align:top;}
.dataframe tr:hover td{background:#f0f7ff;}

/* ── Section title ── */
.sec-title{font-size:11px;font-weight:700;text-transform:uppercase;
           letter-spacing:.12em;color:#6b7280;margin-bottom:10px;}

/* ── Detail info ── */
.detail-sec h4{font-size:11px;font-weight:700;color:#0d2137;text-transform:uppercase;
               letter-spacing:.8px;padding-bottom:6px;
               border-bottom:2px solid #d4a017;margin:18px 0 10px;}
.info-row{display:flex;padding:7px 0;border-bottom:1px solid #f5f5f5;gap:8px;}
.info-lbl{color:#9ca3af;font-size:12px;min-width:160px;flex-shrink:0;}
.info-val{font-size:13px;font-weight:500;color:#1a2332;word-break:break-word;}

/* ── Export row ── */
.export-bar{background:#fff;border-radius:10px;padding:12px 18px;
            display:flex;align-items:center;gap:12px;
            box-shadow:0 2px 8px rgba(0,0,0,0.07);margin-bottom:16px;}

/* Streamlit tab tweaks */
div[data-testid="stTabs"] button{
    font-family:'Sarabun',sans-serif;font-weight:700;font-size:13px;}
div[data-testid="stTabs"] button[aria-selected="true"]{
    color:#0d2137!important;border-bottom-color:#d4a017!important;}

/* Download buttons */
div[data-testid="stSidebar"] .stDownloadButton>button,
.stDownloadButton>button{
    background:#0d2137!important;color:#d4a017!important;
    border:1px solid #d4a017!important;font-weight:700!important;
    font-size:12px!important;
}
</style>""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────
for k,v in [("page","dashboard"),("dbd_selected",None)]:
    if k not in st.session_state: st.session_state[k]=v

# ── Helpers ───────────────────────────────────────────────────
def parse_thai_date(s):
    if not s or str(s).strip() in ['-','','nan']: return None
    p=str(s).strip().split()
    if len(p)<3: return None
    try:
        d,m_th,y_be=int(p[0]),p[1],int(p[-1])
        m=THAI_MONTHS.get(m_th); y=y_be-543
        if m and 1<=d<=31 and 1900<y<2200: return date(y,m,d)
    except: pass
    return None

def extract_be_year(s):
    m=re.search(r'(\d{4})',str(s)); return int(m.group(1)) if m else None

def risk_level(row):
    status=str(row.get("สถานะนิติบุคคล",""))
    if status in ("เลิก","ร้าง","เสร็จการชำระบัญชี","แปรสภาพ"): return "HIGH"
    years=[int(y) for y in re.findall(r'\d{4}',str(row.get("ปีที่ส่งงบการเงิน","")))]
    if not years: return "MEDIUM"
    mx=max(years)
    if mx>=2567: return "LOW"
    if mx>=2565: return "MEDIUM"
    return "HIGH"

def dark_fig(fig,h=260):
    fig.update_layout(paper_bgcolor="#fff",plot_bgcolor="#fff",
        font=dict(family="Sarabun",color="#1a2332"),
        margin=dict(l=8,r=8,t=30,b=8),height=h,
        legend=dict(bgcolor="rgba(0,0,0,0)"))
    fig.update_xaxes(gridcolor="#f0f2f5",zerolinecolor="#f0f2f5")
    fig.update_yaxes(gridcolor="#f0f2f5",zerolinecolor="#f0f2f5")
    return fig

# ── KPI card HTML ─────────────────────────────────────────────
def kcard(lbl,val,sub,cls=""):
    v=f"{val:,}" if isinstance(val,int) else str(val)
    return f'<div class="kpi {cls}"><div class="lbl">{lbl}</div><div class="val">{v}</div><div class="sub">{sub}</div></div>'

# ── Data loading (cached) ─────────────────────────────────────
@st.cache_data(show_spinner="⏳ โหลด FDA.xlsx...")
def load_fda():
    df=pd.read_excel(FDA_XLSX,dtype=str).fillna("")
    df["_สถานะ"] =df["สถานะสินค้า"].apply(lambda s:"อนุมัติ" if s=="อนุมัติ" else "ยกเลิก")
    df["_year"]  =df["วันที่อนุญาต"].apply(extract_be_year)
    df["_expiry"]=df["วันหมดอายุ"].apply(parse_thai_date)
    return df

@st.cache_data(show_spinner="⏳ โหลด DBDALL.xlsx...")
def load_dbd():
    df=pd.read_excel(DBD_XLSX,dtype=str).fillna("")
    df["_risk"]=df.apply(risk_level,axis=1)
    return df

# ── Excel export ──────────────────────────────────────────────
def to_excel_bytes(df, sheet="Data"):
    buf=io.BytesIO()
    with pd.ExcelWriter(buf,engine="openpyxl") as w:
        df.to_excel(w,index=False,sheet_name=sheet)
    return buf.getvalue()

# ── PDF (HTML summary) generators ────────────────────────────
def _pdf_base():
    return """<!DOCTYPE html><html lang="th"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;600;700;800&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:'Sarabun',sans-serif;font-size:13px;color:#1a2332;background:#f0f2f5;padding:32px;}
.card{background:#fff;border-radius:12px;padding:24px;box-shadow:0 2px 16px rgba(0,0,0,.1);margin-bottom:16px;max-width:1100px;margin-left:auto;margin-right:auto;}
.hdr{background:linear-gradient(135deg,#0d2137,#163352);color:#fff;border-radius:10px;padding:20px 24px;margin-bottom:20px;max-width:1100px;margin-left:auto;margin-right:auto;}
.hdr h1{font-size:20px;font-weight:800;margin-bottom:4px;}
.hdr p{font-size:12px;opacity:.6;}
.kpi-row{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px;}
.kpi-box{background:#f8fafc;border-radius:8px;padding:14px;border-left:4px solid #d4a017;text-align:left;}
.kpi-box.g{border-left-color:#059669;}.kpi-box.r{border-left-color:#dc2626;}.kpi-box.b{border-left-color:#3b82f6;}
.kpi-box .lbl{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:#6b7280;margin-bottom:4px;}
.kpi-box .val{font-size:22px;font-weight:900;color:#0d2137;font-family:'IBM Plex Mono',monospace;}
.kpi-box .sub{font-size:11px;color:#9ca3af;margin-top:3px;}
h3{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:#0d2137;
   padding-bottom:6px;border-bottom:2px solid #d4a017;margin:0 0 12px;}
table{width:100%;border-collapse:collapse;font-size:12px;}
th{background:#0d2137;color:#d4a017;font-size:10px;font-weight:700;text-transform:uppercase;
   letter-spacing:.06em;padding:9px 12px;text-align:left;}
td{padding:8px 12px;border-bottom:1px solid #f0f2f5;vertical-align:top;}
tr:nth-child(even) td{background:#f8fafc;}
.badge{display:inline-block;padding:2px 8px;border-radius:99px;font-size:10px;font-weight:700;}
.b-ok{background:#d1fae5;color:#065f46;}.b-exp{background:#fee2e2;color:#991b1b;}
.b-lo{background:#d1fae5;color:#065f46;}.b-md{background:#fef3c7;color:#92400e;}.b-hi{background:#fee2e2;color:#991b1b;}
.b-run{background:#dbeafe;color:#1e40af;}
.footer{text-align:right;font-size:11px;color:#9ca3af;margin-top:8px;}
@media print{body{padding:0;background:#fff;}.card,.hdr{box-shadow:none;border-radius:0;}
  @page{margin:1.5cm;size:A4;}}
</style></head><body>"""

def gen_fda_pdf_summary(df, kpis):
    today=date.today(); tot,appr,canc,near=kpis
    # top 10 operators
    top10=df[df["ผู้ประกอบการ"]!=""].groupby("ผู้ประกอบการ").size().sort_values(ascending=False).head(10)
    top_rows="".join(f"<tr><td>{i+1}</td><td>{op[:50]}</td><td style='font-weight:700;'>{ct:,}</td></tr>"
                     for i,(op,ct) in enumerate(top10.items()))
    # status by year
    yr_data=df.groupby(["_year","_สถานะ"]).size().unstack(fill_value=0).reset_index()
    yr_rows=""
    for _,r in yr_data.iterrows():
        ok=int(r.get("อนุมัติ",0)); canc2=int(r.get("ยกเลิก",0)); tot2=ok+canc2
        yr_rows+=f"<tr><td>{int(r['_year'])}</td><td>{ok:,}</td><td>{canc2:,}</td><td>{tot2:,}</td><td><div style='height:8px;background:#e5e7eb;border-radius:4px;overflow:hidden;'><div style='width:{round(ok/tot2*100) if tot2 else 0}%;height:100%;background:#059669;'></div></div></td></tr>"
    return _pdf_base()+f"""
<div class="hdr">
  <h1>FDA — สรุปผลิตภัณฑ์จดแจ้ง</h1>
  <p>สร้างเมื่อ {today.strftime('%d/%m/%Y')} · ข้อมูลจาก FDA.xlsx</p>
</div>
<div class="card">
  <div class="kpi-row">
    <div class="kpi-box"><div class="lbl">ผลิตภัณฑ์ทั้งหมด</div><div class="val">{tot:,}</div><div class="sub">รายการ</div></div>
    <div class="kpi-box g"><div class="lbl">อนุมัติ</div><div class="val">{appr:,}</div><div class="sub">✅ Active</div></div>
    <div class="kpi-box r"><div class="lbl">ยกเลิก/สิ้นอายุ</div><div class="val">{canc:,}</div><div class="sub">❌ Inactive</div></div>
    <div class="kpi-box b"><div class="lbl">ใกล้หมดอายุ (90วัน)</div><div class="val">{near:,}</div><div class="sub">⚠️ ต้องติดตาม</div></div>
  </div>
  <h3>สัดส่วนตามปีจดแจ้ง</h3>
  <table><thead><tr><th>ปี (BE)</th><th>อนุมัติ</th><th>ยกเลิก</th><th>รวม</th><th>% Active</th></tr></thead>
  <tbody>{yr_rows}</tbody></table>
</div>
<div class="card">
  <h3>TOP 10 ผู้ประกอบการ (จำนวนสินค้า)</h3>
  <table><thead><tr><th>#</th><th>ผู้ประกอบการ</th><th>จำนวนสินค้า</th></tr></thead>
  <tbody>{top_rows}</tbody></table>
</div>
<div class="card">
  <h3>รายการสินค้า (200 รายการแรก)</h3>
  <table><thead><tr><th>เลขจดแจ้ง</th><th>แบรนด์ TH</th><th>ชื่อสินค้า</th><th>ผู้ประกอบการ</th><th>วันที่อนุญาต</th><th>วันหมดอายุ</th><th>สถานะ</th></tr></thead>
  <tbody>{"".join(f"<tr><td style='font-family:monospace;'>{r['เลขจดแจ้ง']}</td><td>{r['BrandsTH'][:30]}</td><td>{r['ProductnameTH'][:30]}</td><td>{r['ผู้ประกอบการ'][:35]}</td><td>{r['วันที่อนุญาต']}</td><td>{r['วันหมดอายุ']}</td><td><span class='badge {'b-ok' if r['_สถานะ']=='อนุมัติ' else 'b-exp'}'>{r['_สถานะ']}</span></td></tr>" for _,r in df.head(200).iterrows())}</tbody></table>
  <div class="footer">แสดง 200 รายการแรกจาก {len(df):,} รายการ · พิมพ์ PDF: Ctrl+P</div>
</div>
</body></html>"""

def gen_dbd_pdf_summary(df):
    today=date.today()
    total=len(df); run=df["สถานะนิติบุคคล"].str.contains("ดำเนินกิจการ",na=False).sum()
    lo=(df["_risk"]=="LOW").sum(); md=(df["_risk"]=="MEDIUM").sum(); hi=(df["_risk"]=="HIGH").sum()
    biz_rows="".join(f"<tr><td>{r['Account'][:50]}</td><td style='font-family:monospace;font-size:11px;'>{r['เลขทะเบียนนิติบุคคล']}</td><td>{r['ประเภทนิติบุคคล']}</td><td>{r['กลุ่มธุรกิจ']}</td><td>{r['ทุนจดทะเบียน'][:20]}</td><td>{r['ปีที่ส่งงบการเงิน'][:20]}</td><td><span class='badge {'b-run' if 'ดำเนินกิจการ' in str(r['สถานะนิติบุคคล']) else 'b-exp'}'>{r['สถานะนิติบุคคล']}</span></td><td><span class='badge b-{'lo' if r['_risk']=='LOW' else 'md' if r['_risk']=='MEDIUM' else 'hi'}'>{r['_risk']}</span></td></tr>"
              for _,r in df.head(500).iterrows())
    return _pdf_base()+f"""
<div class="hdr">
  <h1>DBD — สรุปข้อมูลนิติบุคคล</h1>
  <p>สร้างเมื่อ {today.strftime('%d/%m/%Y')} · ข้อมูลจาก DBDALL.xlsx</p>
</div>
<div class="card">
  <div class="kpi-row">
    <div class="kpi-box"><div class="lbl">นิติบุคคลทั้งหมด</div><div class="val">{total:,}</div><div class="sub">รายการ</div></div>
    <div class="kpi-box g"><div class="lbl">ดำเนินกิจการ</div><div class="val">{run:,}</div><div class="sub">✅ Active</div></div>
    <div class="kpi-box"><div class="lbl">Low Risk</div><div class="val">{lo:,}</div><div class="sub">ปกติ</div></div>
    <div class="kpi-box r"><div class="lbl">Medium+High Risk</div><div class="val">{md+hi:,}</div><div class="sub">⚠️ ต้องติดตาม</div></div>
  </div>
</div>
<div class="card">
  <h3>รายชื่อนิติบุคคล (สูงสุด 500 รายการ)</h3>
  <table><thead><tr><th>ชื่อบริษัท</th><th>เลขทะเบียน</th><th>ประเภท</th><th>กลุ่มธุรกิจ</th><th>ทุนจดทะเบียน</th><th>ส่งงบปี</th><th>สถานะ</th><th>Risk</th></tr></thead>
  <tbody>{biz_rows}</tbody></table>
  <div class="footer">แสดง {min(500,len(df))} รายการจาก {len(df):,} รายการ · พิมพ์ PDF: Ctrl+P</div>
</div>
</body></html>"""

def gen_dbd_company_pdf(row):
    name=row.get("Account","—"); reg=row.get("เลขทะเบียนนิติบุคคล","—")
    risk=row.get("_risk","—"); rc={"LOW":"#059669","MEDIUM":"#d97706","HIGH":"#dc2626"}.get(risk,"#6b7280")
    fields=[("ประเภทนิติบุคคล",row.get("ประเภทนิติบุคคล","")),("สถานะ",row.get("สถานะนิติบุคคล","")),
            ("วันที่จดทะเบียน",row.get("วันที่จดทะเบียนจัดตั้ง","")),("ทุนจดทะเบียน",row.get("ทุนจดทะเบียน","")),
            ("ทุนชำระแล้ว",row.get("ทุนชำระแล้ว","")),("กลุ่มธุรกิจ",row.get("กลุ่มธุรกิจ","")),
            ("ขนาดธุรกิจ",row.get("ขนาดธุรกิจ","")),("ปีที่ส่งงบ",row.get("ปีที่ส่งงบการเงิน","")),
            ("ที่ตั้ง",row.get("ที่ตั้งสำนักงานแห่งใหญ่","")),("Website",row.get("Website","")),
            ("กรรมการ",row.get("รายชื่อกรรมการ","")),("อำนาจลงนาม",row.get("กรรมการลงชื่อผูกพัน","")),
            ("วัตถุประสงค์",row.get("วัตถุประสงค์ปีล่าสุด","") or row.get("วัตถุประสงค์ตอนจดทะเบียน",""))]
    rows_h="".join(f"<tr><td style='color:#9ca3af;width:170px;padding:7px 12px;border-bottom:1px solid #f5f5f5;'>{k}</td><td style='padding:7px 12px;border-bottom:1px solid #f5f5f5;font-weight:500;'>{v or '—'}</td></tr>" for k,v in fields)
    return _pdf_base()+f"""
<div class="hdr">
  <h1>{name}</h1>
  <p>เลขทะเบียน: {reg} · สร้างเมื่อ {date.today().strftime('%d/%m/%Y')}</p>
  <span style="display:inline-block;margin-top:8px;padding:3px 12px;border-radius:99px;font-size:11px;
    font-weight:700;background:{rc}22;color:{rc};border:1px solid {rc};">Risk: {risk}</span>
</div>
<div class="card">
  <h3>ข้อมูลนิติบุคคล</h3>
  <table>{rows_h}</table>
  <div class="footer">พิมพ์ PDF: Ctrl+P → Save as PDF</div>
</div>
</body></html>"""

# ══════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════
def sidebar():
    with st.sidebar:
        st.markdown("""<div class="sb-logo">
            <div class="acc">EXECUTIVE</div>
            <h2>FDA & DBD<br>Report System</h2>
            <div class="sub">กรมพัฒนาธุรกิจการค้า / อย.</div>
        </div>""", unsafe_allow_html=True)
        st.markdown('<div class="sb-pill"><div class="uname">Data</div><div class="urole">ตำแหน่ง: Data</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="sb-section">เมนูหลัก</div>', unsafe_allow_html=True)

        nav=[("dashboard","📊  Dashboard"),
             ("fda",      "🏥  FDA"),
             ("dbd",      "🏢  DBD")]
        for pid, label in nav:
            active = "🔸 " if st.session_state.page==pid else "    "
            if st.button(f"{active}{label}", key=f"nav_{pid}"):
                st.session_state.page=pid; st.session_state.dbd_selected=None; st.rerun()

        st.sidebar.markdown("")
        st.markdown(f'<div class="sb-sync">Last sync<br><span style="color:rgba(255,255,255,0.5);">{date.today().strftime("%d/%m/%Y")}</span></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  DASHBOARD PAGE
# ══════════════════════════════════════════════════════════════
def page_dashboard():
    st.markdown("""<div class="page-banner">
        <div class="acc">Executive Dashboard</div>
        <h1>FDA จดแจ้งผู้ประกอบการ</h1>
        <p>ข้อมูลรวม FDA.xlsx และ DBDALL.xlsx</p>
    </div>""", unsafe_allow_html=True)

    fda=load_fda(); dbd=load_dbd()

    all_years=sorted([int(y) for y in fda["_year"].dropna().unique() if int(y)>=2561],reverse=True)
    yr_opts=["ทั้งหมด"]+[str(y) for y in all_years]
    col_r,col_s=st.columns([5,2])
    with col_r: sel_yr=st.radio("ปี",yr_opts,horizontal=True,key="d_yr",label_visibility="collapsed")
    with col_s:
        prod_types=["ทุกประเภท"]+sorted(fda["ประเภทการผลิต"].unique().tolist())
        sel_type=st.selectbox("ประเภท",prod_types,key="d_type",label_visibility="collapsed")

    df=fda.copy()
    if sel_yr!="ทั้งหมด": df=df[df["_year"]==int(sel_yr)]
    if sel_type!="ทุกประเภท": df=df[df["ประเภทการผลิต"]==sel_type]

    today=date.today(); in90=today+timedelta(days=90)
    total_ops=df["ผู้ประกอบการ"].replace("",pd.NA).dropna().nunique()
    linked=len(set(df["ผู้ประกอบการ"].str.strip())&set(dbd["Account"].str.strip()))
    near_exp=len(df[df["_expiry"].apply(lambda d:d is not None and today<=d<=in90)&(df["_สถานะ"]=="อนุมัติ")])
    foreign=df[~df["ผู้ผลิตต่างประเทส"].isin(["-","","nan"])]["ผู้ประกอบการ"].nunique()

    c1,c2,c3,c4=st.columns(4)
    c1.markdown(kcard("ผู้ประกอบการทั้งหมด",total_ops,f"{linked} linked กับ DBD","b"),unsafe_allow_html=True)
    c2.markdown(kcard("รายการทั้งหมด",len(df),f"{df[df['_สถานะ']=='อนุมัติ']['ผู้ประกอบการ'].nunique():,} Active"),unsafe_allow_html=True)
    c3.markdown(kcard("ใกล้หมดอายุ (90 วัน)",near_exp,"ต้องติดตาม","r"),unsafe_allow_html=True)
    c4.markdown(kcard("ใช้ผู้ผลิตต่างประเทศ",foreign,"ผู้ประกอบการ","o"),unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)

    col1,col2=st.columns([6,4])
    with col1:
        st.markdown('<div class="sec-title">จดแจ้งใหม่รายปี — TREND</div>',unsafe_allow_html=True)
        yr_cnt=fda.groupby("_year").size().reset_index(name="n")
        yr_cnt=yr_cnt[yr_cnt["_year"].between(2561,2580)].copy()
        yr_cnt["ปี"]=yr_cnt["_year"].astype(str)
        gold="#d4a017"; green="#059669"
        colors=[green if y==yr_cnt["_year"].max() else gold for y in yr_cnt["_year"]]

        # คำนวณ % growth เทียบปีก่อน
        yr_cnt["pct"]=yr_cnt["n"].pct_change()*100
        yr_cnt["pct_label"]=yr_cnt["pct"].apply(lambda v: f"+{v:.1f}%" if v>=0 else f"{v:.1f}%" if pd.notna(v) else "")
        pct_colors=["#059669" if (pd.notna(v) and v>=0) else "#dc2626" for v in yr_cnt["pct"]]

        fig=go.Figure()
        # Bar
        fig.add_trace(go.Bar(
            x=yr_cnt["ปี"],y=yr_cnt["n"],marker_color=colors,
            text=yr_cnt["n"].apply(lambda v:f"{v:,}"),textposition="outside",
            textfont=dict(color="#0d2137",size=10),
            name="จำนวนจดแจ้ง",yaxis="y"))
        # Line % growth (secondary y-axis)
        fig.add_trace(go.Scatter(
            x=yr_cnt["ปี"],y=yr_cnt["pct"],mode="lines+markers+text",
            line=dict(color="#3b82f6",width=2,dash="dot"),
            marker=dict(size=7,color=pct_colors,line=dict(color="#fff",width=1)),
            text=yr_cnt["pct_label"],textposition="top center",
            textfont=dict(size=9,color="#3b82f6"),
            name="% เติบโต",yaxis="y2"))

        if len(yr_cnt)>=2:
            v=yr_cnt["n"].tolist(); chg=(v[-1]-v[-2])/v[-2]*100 if v[-2] else 0
            fig.add_annotation(text=f"{'▲' if chg>=0 else '▼'} {abs(chg):.0f}%",
                xref="paper",yref="paper",x=1,y=1.08,showarrow=False,
                font=dict(color=green if chg>=0 else "#dc2626",size=12))

        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="h",x=0,y=-0.15,font=dict(size=10,color="#6b7280")),
            bargap=0.3,
            yaxis=dict(
                showgrid=True,gridcolor="rgba(0,0,0,0.07)",gridwidth=1,
                tickfont=dict(color="#6b7280",size=9),
                tickformat=",",zeroline=False),
            yaxis2=dict(
                overlaying="y",side="right",
                showgrid=False,zeroline=True,zerolinecolor="rgba(0,0,0,0.1)",
                ticksuffix="%",tickfont=dict(color="#3b82f6",size=9)),
            xaxis=dict(tickfont=dict(color="#6b7280",size=10)),
        )
        dark_fig(fig,280)
        # restore visible grid after dark_fig override
        fig.update_yaxes(showgrid=True,gridcolor="rgba(0,0,0,0.08)",gridwidth=1)
        st.plotly_chart(fig,width="stretch",config={"displayModeBar":False})

    with col2:
        st.markdown('<div class="sec-title">สถานะสินค้าทั้งหมด</div>',unsafe_allow_html=True)
        sc=df["_สถานะ"].value_counts()
        ok_ct=int(sc.get("อนุมัติ",0)); can_ct=int(sc.get("ยกเลิก",0))
        tot2=ok_ct+can_ct if ok_ct+can_ct else 1
        fig2=go.Figure(go.Pie(labels=["Active","ยกเลิก/สิ้นอายุ"],values=[ok_ct,can_ct],
            hole=0.62,marker=dict(colors=["#059669","#dc2626"]),
            textinfo="percent",textfont=dict(size=11,color="#fff")))
        fig2.add_annotation(text=f"<b>{round(ok_ct/tot2*100)}%</b><br>Active",
            x=0.5,y=0.5,showarrow=False,font=dict(size=13,color="#0d2137"))
        fig2.update_layout(showlegend=True,legend=dict(font=dict(color="#6b7280",size=11),x=1.02,y=0.5))
        dark_fig(fig2,260); st.plotly_chart(fig2,width="stretch",config={"displayModeBar":False})

    col3,col4=st.columns([5,5])
    with col3:
        st.markdown('<div class="sec-title">TOP 8 ผู้ประกอบการ (จำนวนสินค้า)</div>',unsafe_allow_html=True)
        top8=df[df["ผู้ประกอบการ"]!=""].groupby("ผู้ประกอบการ").size().sort_values(ascending=False).head(8).reset_index()
        top8.columns=["ผู้ประกอบการ","n"]
        top8["ชื่อ"]=top8["ผู้ประกอบการ"].apply(lambda s:s.replace("บริษัท ","").replace(" จำกัด","").replace("(มหาชน)","").strip()[:26])
        fig3=go.Figure(go.Bar(y=top8["ชื่อ"][::-1],x=top8["n"][::-1],orientation="h",
            marker_color="#0d2137",text=top8["n"][::-1],textposition="outside",
            textfont=dict(color="#0d2137",size=10)))
        fig3.update_layout(showlegend=False,xaxis=dict(visible=False),yaxis=dict(tickfont=dict(size=10,color="#6b7280")))
        dark_fig(fig3,300); st.plotly_chart(fig3,width="stretch",config={"displayModeBar":False})

    with col4:
        st.markdown('<div class="sec-title">สินค้าที่ต้องติดตาม — ใกล้หมดอายุ / ยกเลิก</div>',unsafe_allow_html=True)
        ndf=df[df["_expiry"].apply(lambda d:d is not None and today<=d<=in90)].head(8)
        if len(ndf)<8:
            ndf=pd.concat([ndf,df[df["_สถานะ"]=="ยกเลิก"].head(8-len(ndf))],ignore_index=True)
        def tb(s): return '<span class="badge b-ok">อนุมัติ</span>' if s=="อนุมัติ" else '<span class="badge b-exp">ยกเลิก</span>'
        ndf2=ndf[["BrandsTH","ผู้ประกอบการ","วันหมดอายุ","_สถานะ"]].copy()
        ndf2.columns=["แบรนด์","ผู้ประกอบการ","วันหมดอายุ","สถานะ"]
        ndf2["แบรนด์"]=ndf2["แบรนด์"].str[:20]
        ndf2["ผู้ประกอบการ"]=ndf2["ผู้ประกอบการ"].apply(lambda s:s.replace("บริษัท ","").replace(" จำกัด","")[:22])
        ndf2["สถานะ"]=ndf2["สถานะ"].apply(tb)
        st.write('<div class="df-wrap">'+ndf2.to_html(escape=False,index=False,classes="dataframe")+'</div>',unsafe_allow_html=True)

    # DBD summary
    st.markdown("<br>",unsafe_allow_html=True)
    st.markdown('<div class="sec-title">DBD — กรมพัฒนาธุรกิจการค้า</div>',unsafe_allow_html=True)
    dbd_run=dbd["สถานะนิติบุคคล"].str.contains("ดำเนินกิจการ",na=False).sum()
    dbd_hi=(dbd["_risk"]=="HIGH").sum(); dbd_md=(dbd["_risk"]=="MEDIUM").sum()
    d1,d2,d3,d4=st.columns(4)
    d1.markdown(kcard("นิติบุคคลทั้งหมด",len(dbd),"ใน DBDALL.xlsx"),unsafe_allow_html=True)
    d2.markdown(kcard("ดำเนินกิจการอยู่",dbd_run,"✅ ยังเปิดดำเนินการ","g"),unsafe_allow_html=True)
    d3.markdown(kcard("ต้องติดตาม",dbd_md+dbd_hi,"MEDIUM+HIGH risk","r"),unsafe_allow_html=True)
    d4.markdown(kcard("LOW Risk",len(dbd)-dbd_md-dbd_hi,"ปกติ","o"),unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  FDA PAGE
# ══════════════════════════════════════════════════════════════
def page_fda():
    st.markdown("""<div class="page-banner">
        <div class="acc">สำนักงานคณะกรรมการอาหารและยา</div>
        <h1>FDA — จดแจ้งผลิตภัณฑ์</h1>
        <p>ข้อมูลผลิตภัณฑ์จดแจ้ง / ทะเบียนเครื่องสำอาง</p>
    </div>""", unsafe_allow_html=True)
    df=load_fda()

    total=len(df); appr=(df["_สถานะ"]=="อนุมัติ").sum(); canc=total-appr
    today=date.today(); in90=today+timedelta(days=90)
    near=len(df[df["_expiry"].apply(lambda d:d is not None and today<=d<=in90)&(df["_สถานะ"]=="อนุมัติ")])

    c1,c2,c3,c4=st.columns(4)
    c1.markdown(kcard("ทั้งหมด",total,"รายการในฐานข้อมูล"),unsafe_allow_html=True)
    c2.markdown(kcard("อนุมัติ",appr,"✅ สินค้าที่อนุมัติแล้ว","g"),unsafe_allow_html=True)
    c3.markdown(kcard("ยกเลิก",canc,"❌ สิ้นอายุ / ยกเลิก","r"),unsafe_allow_html=True)
    c4.markdown(kcard("ใกล้หมดอายุ (90วัน)",near,"⚠️ ต้องติดตาม","o"),unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)

    # Filters
    f1,f2,f3,f4=st.columns([2.5,1.2,1.5,1.5])
    with f1: q=st.text_input("🔍 ค้นหา",key="fda_q",placeholder="เลขจดแจ้ง / แบรนด์ TH-EN / ชื่อสินค้า / ผู้ประกอบการ")
    with f2: sel_st=st.selectbox("สถานะ",["ทั้งหมด","อนุมัติ","ยกเลิก"],key="fda_st")
    with f3:
        pl=["ทั้งหมด"]+sorted(df["ประเภทการผลิต"].unique().tolist())
        sel_prod=st.selectbox("ประเภทการผลิต",pl,key="fda_prod")
    with f4:
        yl=["ทั้งหมด"]+[str(y) for y in sorted(df["_year"].dropna().unique().astype(int),reverse=True)]
        sel_yr=st.selectbox("ปีจดแจ้ง (BE)",yl,key="fda_yr")

    filtered=df.copy()
    if q:
        m=(filtered["เลขจดแจ้ง"].str.contains(q,case=False,na=False)|
           filtered["เลขจดแจ้งไม่มีขีด"].str.contains(q,case=False,na=False)|
           filtered["BrandsTH"].str.contains(q,case=False,na=False)|
           filtered["BrandsENG"].str.contains(q,case=False,na=False)|
           filtered["ProductnameTH"].str.contains(q,case=False,na=False)|
           filtered["ProductnameENG"].str.contains(q,case=False,na=False)|
           filtered["ผู้ประกอบการ"].str.contains(q,case=False,na=False))
        filtered=filtered[m]
    if sel_st!="ทั้งหมด":   filtered=filtered[filtered["_สถานะ"]==sel_st]
    if sel_prod!="ทั้งหมด": filtered=filtered[filtered["ประเภทการผลิต"]==sel_prod]
    if sel_yr!="ทั้งหมด":   filtered=filtered[filtered["_year"]==int(sel_yr)]

    st.caption(f"พบ **{len(filtered):,}** รายการ")

    # Export bar
    if len(filtered)>0:
        st.markdown('<div class="export-bar">📤 <strong>Export ข้อมูล</strong>', unsafe_allow_html=True)
        e1,e2,_=st.columns([1.5,1.5,5])
        with e1:
            xlsx=to_excel_bytes(filtered.drop(columns=["_สถานะ","_year","_expiry"],errors="ignore"))
            st.download_button("📊 Excel (.xlsx)", data=xlsx,
                file_name=f"FDA_Export_{date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width="stretch")
        with e2:
            pdf_h=gen_fda_pdf_summary(filtered,(len(filtered),int(appr),int(canc),near))
            st.download_button("📄 PDF Summary (.html)", data=pdf_h.encode("utf-8"),
                file_name=f"FDA_Summary_{date.today()}.html", mime="text/html",
                width="stretch")
        st.markdown('</div>', unsafe_allow_html=True)

    if filtered.empty: st.info("ไม่พบข้อมูล"); return

    cols_s=["เลขจดแจ้ง","BrandsTH","BrandsENG","ProductnameTH","ผู้ประกอบการ","ประเภทการผลิต","วันที่อนุญาต","วันหมดอายุ","_สถานะ"]
    tot2=len(filtered); pages=max(1,-(-tot2//100))
    pg=st.number_input(f"หน้า (จาก {pages} หน้า — {tot2:,} รายการ)",min_value=1,max_value=pages,value=1,step=1,key="fda_pg")
    chunk=filtered.iloc[(pg-1)*100:pg*100][cols_s].copy()
    def fb(s): return '<span class="badge b-ok">อนุมัติ</span>' if s=="อนุมัติ" else '<span class="badge b-exp">ยกเลิก</span>'
    chunk["_สถานะ"]=chunk["_สถานะ"].apply(fb)
    st.write('<div class="df-wrap">'+chunk.to_html(escape=False,index=False,classes="dataframe")+'</div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  DBD LIST PAGE
# ══════════════════════════════════════════════════════════════
def page_dbd_list():
    st.markdown("""<div class="page-banner">
        <div class="acc">กรมพัฒนาธุรกิจการค้า</div>
        <h1>DBD — ภาพรวมนิติบุคคล</h1>
        <p>สรุปข้อมูลสำหรับผู้บริหาร</p>
    </div>""", unsafe_allow_html=True)
    df=load_dbd()

    total=len(df); run=df["สถานะนิติบุคคล"].str.contains("ดำเนินกิจการ",na=False).sum()
    lo=(df["_risk"]=="LOW").sum(); md=(df["_risk"]=="MEDIUM").sum(); hi=(df["_risk"]=="HIGH").sum()
    c1,c2,c3,c4=st.columns(4)
    c1.markdown(kcard("บริษัททั้งหมด",total,"ในระบบ"),unsafe_allow_html=True)
    c2.markdown(kcard("ดำเนินกิจการอยู่",run,f"{round(run/total*100)}% ของทั้งหมด","g"),unsafe_allow_html=True)
    c3.markdown(kcard("ปกติ (LOW Risk)",lo,f"{round(lo/total*100)}%","g"),unsafe_allow_html=True)
    c4.markdown(kcard("ต้องติดตาม",md+hi,f"MEDIUM {md} · HIGH {hi}","r"),unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)

    # Risk bar
    st.markdown(f"""<div class="risk-bar">
        <div style="font-size:11px;font-weight:700;color:#6b7280;text-transform:uppercase;letter-spacing:1px;min-width:90px;">⚡ Risk Level</div>
        <span class="risk-seg rs-lo">{lo} ปกติ</span>
        <span class="risk-seg rs-md">{md} ต้องติดตาม</span>
        <span class="risk-seg rs-hi">{hi} ความเสี่ยงสูง</span>
    </div>""", unsafe_allow_html=True)

    # Export bar
    e1,e2,_=st.columns([1.5,1.5,5])
    with e1:
        xlsx=to_excel_bytes(df.drop(columns=["_risk"],errors="ignore"))
        st.download_button("📊 Export Excel (.xlsx)", data=xlsx,
            file_name=f"DBD_Export_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch")
    with e2:
        pdf_h=gen_dbd_pdf_summary(df)
        st.download_button("📄 PDF Summary (.html)", data=pdf_h.encode("utf-8"),
            file_name=f"DBD_Summary_{date.today()}.html", mime="text/html",
            width="stretch")
    st.markdown("<br>",unsafe_allow_html=True)

    # Filters
    f1,f2,f3,f4=st.columns([2.5,1.2,1.5,1.5])
    with f1: q=st.text_input("🔍 ค้นหาชื่อบริษัท / เลขทะเบียน",key="dbd_q",placeholder="พิมพ์คำค้นหา...")
    with f2:
        sf_opts=["ทั้งหมด","ยังดำเนินกิจการอยู่","เลิก","ร้าง"]
        sf=st.selectbox("สถานะ",sf_opts,key="dbd_sf")
    with f3:
        biz=["ทั้งหมด"]+sorted(df["กลุ่มธุรกิจ"].replace("",pd.NA).dropna().unique().tolist())
        sel_biz=st.selectbox("กลุ่มธุรกิจ",biz,key="dbd_biz")
    with f4:
        sel_risk=st.selectbox("Risk Level",["ทั้งหมด","LOW","MEDIUM","HIGH"],key="dbd_risk")

    filtered=df.copy()
    if q:
        m=(filtered["Account"].str.contains(q,case=False,na=False)|
           filtered["เลขทะเบียนนิติบุคคล"].str.contains(q,case=False,na=False))
        filtered=filtered[m]
    if sf!="ทั้งหมด":         filtered=filtered[filtered["สถานะนิติบุคคล"]==sf]
    if sel_biz!="ทั้งหมด":   filtered=filtered[filtered["กลุ่มธุรกิจ"]==sel_biz]
    if sel_risk!="ทั้งหมด":  filtered=filtered[filtered["_risk"]==sel_risk]

    st.caption(f"แสดง **{len(filtered):,}** จาก {total:,} บริษัท")

    # Table header row
    hd=st.columns([3.5,1.5,1,1.5,0.8,0.8])
    for c,t in zip(hd,["ชื่อบริษัท","สถานะ","กลุ่มธุรกิจ","ทุนจดทะเบียน","Risk",""]):
        c.markdown(f'<div style="font-size:10px;font-weight:700;color:#6b7280;text-transform:uppercase;letter-spacing:.06em;padding:6px 0;border-bottom:2px solid #e5e7eb;">{t}</div>',unsafe_allow_html=True)

    def rb(r): return {"LOW":'<span class="badge b-lo">ปกติ</span>',"MEDIUM":'<span class="badge b-md">ติดตาม</span>',"HIGH":'<span class="badge b-hi">เสี่ยงสูง</span>'}.get(r,'<span class="badge b-oth">-</span>')
    def sb(s):
        if "ดำเนินกิจการ" in str(s): return f'<span class="badge b-run">{s}</span>'
        if str(s) in ("เลิก","เสร็จการชำระบัญชี"): return f'<span class="badge b-cls">{s}</span>'
        return f'<span class="badge b-oth">{s}</span>'

    page_size=25; tot_f=len(filtered); pages=max(1,-(-tot_f//page_size))
    pg=st.number_input(f"หน้า (จาก {pages} หน้า)",min_value=1,max_value=pages,value=1,step=1,key="dbd_pg")
    page_df=filtered.iloc[(pg-1)*page_size:pg*page_size].reset_index(drop=True)

    for i,row in page_df.iterrows():
        cols=st.columns([3.5,1.5,1,1.5,0.8,0.8])
        with cols[0]:
            st.markdown(f'<div style="padding:4px 0;"><div style="font-weight:700;color:#0d2137;font-size:13px;">{row["Account"]}</div><div style="font-size:11px;color:#9ca3af;font-family:monospace;">{row["เลขทะเบียนนิติบุคคล"]}</div></div>',unsafe_allow_html=True)
        with cols[1]: st.markdown(sb(row["สถานะนิติบุคคล"]),unsafe_allow_html=True)
        with cols[2]: st.markdown(f'<div style="font-size:12px;color:#6b7280;">{row["กลุ่มธุรกิจ"] or "-"}</div>',unsafe_allow_html=True)
        with cols[3]: st.markdown(f'<div style="font-size:11px;color:#6b7280;">{(row["ทุนจดทะเบียน"] or "-")[:22]}</div>',unsafe_allow_html=True)
        with cols[4]: st.markdown(rb(row["_risk"]),unsafe_allow_html=True)
        with cols[5]:
            if st.button("ดูข้อมูล",key=f"d_{pg}_{i}",width="stretch"):
                st.session_state.dbd_selected=row.to_dict(); st.rerun()
        st.markdown('<hr style="margin:3px 0;border:none;border-top:1px solid #f0f2f5;">',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  DBD DETAIL PAGE
# ══════════════════════════════════════════════════════════════
def page_dbd_detail():
    row=st.session_state.dbd_selected
    name=row.get("Account","—"); reg=row.get("เลขทะเบียนนิติบุคคล","—")
    status=row.get("สถานะนิติบุคคล","—"); risk=row.get("_risk","—")
    rc={"LOW":"#059669","MEDIUM":"#d97706","HIGH":"#dc2626"}.get(risk,"#6b7280")

    st.markdown(f"""<div class="page-banner" style="display:flex;justify-content:space-between;align-items:flex-start;">
        <div>
            <div class="acc">รายละเอียดบริษัท</div>
            <h1>{name}</h1>
            <p>เลขทะเบียน: {reg} · {status}</p>
            <span style="display:inline-block;margin-top:6px;padding:3px 12px;border-radius:99px;
                font-size:11px;font-weight:700;background:{rc}33;color:{rc};border:1px solid {rc};">Risk: {risk}</span>
        </div>
    </div>""", unsafe_allow_html=True)

    b1,b2,b3,_=st.columns([1.2,1.6,1.8,4])
    with b1:
        if st.button("← กลับรายการ",width="stretch"):
            st.session_state.dbd_selected=None; st.rerun()
    with b2:
        xlsx=to_excel_bytes(pd.DataFrame([row]).drop(columns=["_risk"],errors="ignore"))
        st.download_button("📊 Export Excel",data=xlsx,
            file_name=f"DBD_{reg}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch")
    with b3:
        pdf_h=gen_dbd_company_pdf(row)
        st.download_button("📄 PDF Report (.html)",data=pdf_h.encode("utf-8"),
            file_name=f"DBD_{reg}.html",mime="text/html",width="stretch")

    st.markdown('<div style="font-size:11px;color:#9ca3af;margin:6px 0 16px;">💡 หลังดาวน์โหลด HTML → เปิดในเบราว์เซอร์ → Ctrl+P → Save as PDF</div>',unsafe_allow_html=True)

    tab1,tab2,tab3=st.tabs(["📋 ข้อมูลนิติบุคคล","👥 กรรมการ","🏭 วัตถุประสงค์"])

    def ir(label,value):
        v=value if value and value not in ["-",""] else "—"
        return f'<div class="info-row"><div class="info-lbl">{label}</div><div class="info-val">{v}</div></div>'

    with tab1:
        html='<div class="detail-sec"><h4>ข้อมูลพื้นฐาน</h4>'
        for k,v in [("ประเภทนิติบุคคล",row.get("ประเภทนิติบุคคล","")),
                    ("สถานะนิติบุคคล",row.get("สถานะนิติบุคคล","")),
                    ("วันที่จดทะเบียนจัดตั้ง",row.get("วันที่จดทะเบียนจัดตั้ง","")),
                    ("ทุนจดทะเบียน",row.get("ทุนจดทะเบียน","")),
                    ("ทุนชำระแล้ว",row.get("ทุนชำระแล้ว","")),
                    ("กลุ่มธุรกิจ",row.get("กลุ่มธุรกิจ","")),
                    ("ขนาดธุรกิจ",row.get("ขนาดธุรกิจ","")),
                    ("ปีที่ส่งงบการเงิน",row.get("ปีที่ส่งงบการเงิน","")),
                    ("Website",row.get("Website","")),
                    ("ที่ตั้งสำนักงาน",row.get("ที่ตั้งสำนักงานแห่งใหญ่",""))]:
            html+=ir(k,v)
        html+='</div>'
        st.markdown(html,unsafe_allow_html=True)

    with tab2:
        st.markdown(f'<div class="detail-sec"><h4>รายชื่อกรรมการ</h4><div style="font-size:13px;line-height:1.8;color:#1a2332;">{row.get("รายชื่อกรรมการ","") or "—"}</div><h4>อำนาจลงนาม</h4><div style="font-size:13px;line-height:1.8;color:#1a2332;">{row.get("กรรมการลงชื่อผูกพัน","") or "—"}</div></div>',unsafe_allow_html=True)

    with tab3:
        st.markdown(f"""<div class="detail-sec">
            <h4>ประเภทธุรกิจ (ตอนจดทะเบียน)</h4><div style="font-size:13px;line-height:1.8;">{row.get("ประเภทธุรกิจตอนจดทะเบียน","") or "—"}</div>
            <h4>ประเภทธุรกิจ (ปีล่าสุด)</h4><div style="font-size:13px;line-height:1.8;">{row.get("ประเภทธุรกิจที่ส่งงบการเงินปีล่าสุด","") or "—"}</div>
            <h4>วัตถุประสงค์ (ตอนจดทะเบียน)</h4><div style="font-size:13px;line-height:1.8;">{row.get("วัตถุประสงค์ตอนจดทะเบียน","") or "—"}</div>
            <h4>วัตถุประสงค์ (ปีล่าสุด)</h4><div style="font-size:13px;line-height:1.8;">{row.get("วัตถุประสงค์ปีล่าสุด","") or "—"}</div>
        </div>""",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════
def main():
    sidebar()
    page=st.session_state.page
    if page=="dashboard":    page_dashboard()
    elif page=="fda":        page_fda()
    elif page=="dbd":
        if st.session_state.dbd_selected: page_dbd_detail()
        else:                             page_dbd_list()

main()
