import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os, re
from datetime import date, timedelta

st.set_page_config(page_title="FDA & DBD System", page_icon="🏛️",
                   layout="wide", initial_sidebar_state="expanded")

BASE     = os.path.dirname(__file__)
FDA_XLSX = os.path.join(BASE, "FDA.xlsx")
DBD_XLSX = os.path.join(BASE, "DBDALL.xlsx")

THAI_MONTHS = {'มกราคม':1,'กุมภาพันธ์':2,'มีนาคม':3,'เมษายน':4,
               'พฤษภาคม':5,'มิถุนายน':6,'กรกฎาคม':7,'สิงหาคม':8,
               'กันยายน':9,'ตุลาคม':10,'พฤศจิกายน':11,'ธันวาคม':12}

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;600;700;800&family=IBM+Plex+Mono:wght@400;600&display=swap');
html,body,[class*="css"]{font-family:'Sarabun',sans-serif;}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding-top:1rem!important;padding-left:1.5rem!important;padding-right:1.5rem!important;}
section[data-testid="stSidebar"]{background:#0d2137!important;min-width:220px!important;max-width:220px!important;}
section[data-testid="stSidebar"] *{color:#cbd5e1;}
.sidebar-logo{padding:20px 16px 12px;border-bottom:1px solid rgba(255,255,255,0.08);margin-bottom:8px;}
.sidebar-logo .top{font-size:10px;color:#d4a017;font-weight:700;letter-spacing:2px;text-transform:uppercase;}
.sidebar-logo h2{font-size:16px;font-weight:800;color:#fff;line-height:1.25;margin:4px 0 2px;}
.sidebar-logo .sub{font-size:11px;color:rgba(255,255,255,0.4);}
.user-pill{margin:0 10px 10px;padding:8px 12px;background:rgba(255,255,255,0.06);
           border-radius:8px;border:1px solid rgba(255,255,255,0.1);}
.user-pill .uname{font-size:12px;color:#fff;font-weight:700;}
.user-pill .urole{font-size:11px;color:#d4a017;}
/* nav buttons */
div[data-testid="stSidebar"] .stButton>button{
    width:100%!important;text-align:left!important;padding:9px 16px!important;
    background:transparent!important;border:none!important;color:rgba(255,255,255,0.6)!important;
    font-size:13.5px!important;font-family:'Sarabun',sans-serif!important;font-weight:600!important;
    border-left:3px solid transparent!important;border-radius:0!important;margin:0!important;
    transition:all .15s!important;
}
div[data-testid="stSidebar"] .stButton>button:hover{
    color:#fff!important;background:rgba(255,255,255,0.05)!important;
}
/* active nav */
.nav-active div[data-testid="stSidebar"] .stButton>button{
    color:#fff!important;background:rgba(212,160,23,0.12)!important;
    border-left-color:#d4a017!important;
}
/* KPI dark */
.dk{background:#163352;border-radius:12px;padding:18px 22px;border-left:4px solid #d4a017;
    box-shadow:0 2px 12px rgba(13,33,55,.25);margin-bottom:2px;}
.dk.g{border-left-color:#059669;}.dk.r{border-left-color:#dc2626;}.dk.b{border-left-color:#3b82f6;}
.dk-lbl{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#64748b;margin-bottom:5px;}
.dk-val{font-size:28px;font-weight:900;color:#f0f4ff;font-family:'IBM Plex Mono',monospace;line-height:1;}
.dk-sub{font-size:11px;color:#475569;margin-top:4px;}
/* KPI light */
.lt{background:#fff;border-radius:12px;padding:16px 20px;border-left:4px solid #00236f;
    box-shadow:0 1px 4px rgba(0,0,0,.08);margin-bottom:2px;}
.lt.g{border-left-color:#006d30;}.lt.r{border-left-color:#dc2626;}.lt.grey{border-left-color:#6b7280;}.lt.o{border-left-color:#b34600;}
.lt-lbl{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:#444651;margin-bottom:4px;}
.lt-val{font-size:26px;font-weight:900;color:#0d1c2e;line-height:1;}
.lt-sub{font-size:11px;color:#444651;margin-top:4px;}
/* badge */
.badge{display:inline-block;padding:2px 10px;border-radius:99px;font-size:11px;font-weight:700;}
.b-ok{background:#d0f0d8;color:#005323;}.b-exp{background:#ffdad6;color:#93000a;}
.b-run{background:#dbeafe;color:#1e40af;}.b-cls{background:#ffdad6;color:#93000a;}
.b-oth{background:#fef3c7;color:#92400e;}.b-lo{background:#d1fae5;color:#065f46;}
.b-md{background:#fef3c7;color:#92400e;}.b-hi{background:#fee2e2;color:#991b1b;}
/* table */
.df-wrap{border-radius:10px;overflow:hidden;box-shadow:0 1px 6px rgba(0,0,0,.1);}
.dataframe{width:100%;border-collapse:collapse;font-size:12.5px;}
.dataframe th{background:#0d2137;color:#d4a017;font-size:10px;font-weight:700;text-transform:uppercase;
              letter-spacing:.08em;padding:9px 12px;text-align:left;white-space:nowrap;}
.dataframe td{padding:8px 12px;border-bottom:1px solid #e6eeff;background:#fff;vertical-align:top;}
.dataframe tr:hover td{background:#f0f7ff;}
/* risk bar */
.risk-bar{background:#fff;border-radius:10px;padding:12px 18px;display:flex;align-items:center;
          gap:14px;box-shadow:0 1px 4px rgba(0,0,0,.08);margin-bottom:16px;}
.risk-seg{display:inline-flex;align-items:center;gap:6px;padding:4px 14px;border-radius:20px;
          font-size:12px;font-weight:700;cursor:pointer;}
.r-lo{background:#d1fae5;color:#065f46;}.r-md{background:#fef3c7;color:#92400e;}.r-hi{background:#fee2e2;color:#991b1b;}
/* company detail */
.detail-sec h4{font-size:11px;font-weight:700;color:#0d2137;text-transform:uppercase;letter-spacing:.8px;
               padding-bottom:6px;border-bottom:2px solid #d4a017;margin:16px 0 10px;}
.info-row{display:flex;padding:6px 0;border-bottom:1px solid #f0f0f0;gap:8px;}
.info-lbl{color:#6b7280;font-size:12px;min-width:160px;flex-shrink:0;}
.info-val{font-size:13px;font-weight:500;word-break:break-word;}
</style>""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────
for k, v in [("page","dashboard"),("dbd_selected",None),("dbd_risk_filter","ALL"),("dbd_status_filter","ALL")]:
    if k not in st.session_state: st.session_state[k] = v

# ── Helpers ───────────────────────────────────────────────────
def parse_thai_date(s):
    if not s or str(s).strip() in ['-','','nan']: return None
    p = str(s).strip().split()
    if len(p) < 3: return None
    try:
        d, m_th, y_be = int(p[0]), p[1], int(p[-1])
        m = THAI_MONTHS.get(m_th)
        y = y_be - 543
        if m and 1 <= d <= 31 and 1900 < y < 2200: return date(y, m, d)
    except: pass
    return None

def extract_be_year(s):
    m = re.search(r'(\d{4})', str(s))
    return int(m.group(1)) if m else None

def parse_filed_years(s):
    return [int(y) for y in re.findall(r'\d{4}', str(s))]

def risk_level(row):
    status = str(row.get("สถานะนิติบุคคล",""))
    if status in ("เลิก","ร้าง","เสร็จการชำระบัญชี","แปรสภาพ"): return "HIGH"
    years = parse_filed_years(row.get("ปีที่ส่งงบการเงิน",""))
    if not years: return "MEDIUM"
    mx = max(years)
    if mx >= 2567: return "LOW"
    if mx >= 2565: return "MEDIUM"
    return "HIGH"

def dark_fig(fig, h=260):
    fig.update_layout(paper_bgcolor="#163352", plot_bgcolor="#163352",
        font=dict(family="Sarabun",color="#cbd5e1"), margin=dict(l=8,r=8,t=30,b=8), height=h,
        legend=dict(bgcolor="rgba(0,0,0,0)"))
    fig.update_xaxes(gridcolor="#1e3a5c", zerolinecolor="#1e3a5c")
    fig.update_yaxes(gridcolor="#1e3a5c", zerolinecolor="#1e3a5c")
    return fig

def dkcard(lbl, val, sub, cls=""):
    v = f"{val:,}" if isinstance(val,int) else str(val)
    return f'<div class="dk {cls}"><div class="dk-lbl">{lbl}</div><div class="dk-val">{v}</div><div class="dk-sub">{sub}</div></div>'

def ltcard(lbl, val, sub, cls=""):
    v = f"{val:,}" if isinstance(val,int) else str(val)
    return f'<div class="lt {cls}"><div class="lt-lbl">{lbl}</div><div class="lt-val">{v}</div><div class="lt-sub">{sub}</div></div>'

def show_table(df_chunk, badge_fn, cols, badge_col):
    chunk = df_chunk[cols].copy()
    chunk[badge_col] = chunk[badge_col].apply(badge_fn)
    html = '<div class="df-wrap">'+chunk.to_html(escape=False,index=False,classes="dataframe")+'</div>'
    st.write(html, unsafe_allow_html=True)

# ── Data loading ──────────────────────────────────────────────
@st.cache_data(show_spinner="⏳ โหลด FDA.xlsx...")
def load_fda():
    df = pd.read_excel(FDA_XLSX, dtype=str).fillna("")
    df["_สถานะ"]  = df["สถานะสินค้า"].apply(lambda s: "อนุมัติ" if s=="อนุมัติ" else "ยกเลิก")
    df["_year"]   = df["วันที่อนุญาต"].apply(extract_be_year)
    df["_expiry"] = df["วันหมดอายุ"].apply(parse_thai_date)
    return df

@st.cache_data(show_spinner="⏳ โหลด DBDALL.xlsx...")
def load_dbd():
    df = pd.read_excel(DBD_XLSX, dtype=str).fillna("")
    df["_risk"] = df.apply(risk_level, axis=1)
    return df

# ── PDF HTML generators ────────────────────────────────────────
def gen_dbd_pdf(row):
    name = row.get("Account","—"); reg = row.get("เลขทะเบียนนิติบุคคล","—")
    risk = row.get("_risk","—")
    risk_color = {"LOW":"#059669","MEDIUM":"#d97706","HIGH":"#dc2626"}.get(risk,"#6b7280")
    fields = [
        ("ประเภทนิติบุคคล",     row.get("ประเภทนิติบุคคล","")),
        ("สถานะ",               row.get("สถานะนิติบุคคล","")),
        ("วันที่จดทะเบียน",      row.get("วันที่จดทะเบียนจัดตั้ง","")),
        ("ทุนจดทะเบียน",        row.get("ทุนจดทะเบียน","")),
        ("ทุนชำระแล้ว",          row.get("ทุนชำระแล้ว","")),
        ("กลุ่มธุรกิจ",          row.get("กลุ่มธุรกิจ","")),
        ("ขนาดธุรกิจ",          row.get("ขนาดธุรกิจ","")),
        ("ปีที่ส่งงบการเงิน",    row.get("ปีที่ส่งงบการเงิน","")),
        ("Website",             row.get("Website","")),
        ("ที่ตั้ง",              row.get("ที่ตั้งสำนักงานแห่งใหญ่","")),
        ("รายชื่อกรรมการ",       row.get("รายชื่อกรรมการ","")),
        ("กรรมการลงชื่อผูกพัน",  row.get("กรรมการลงชื่อผูกพัน","")),
        ("วัตถุประสงค์",         row.get("วัตถุประสงค์ปีล่าสุด","") or row.get("วัตถุประสงค์ตอนจดทะเบียน","")),
    ]
    rows_html = "".join(f"<tr><td style='color:#6b7280;width:180px;padding:7px 12px;border-bottom:1px solid #f0f0f0;font-size:13px;'>{k}</td><td style='padding:7px 12px;border-bottom:1px solid #f0f0f0;font-size:13px;'>{v or '—'}</td></tr>" for k,v in fields)
    return f"""<!DOCTYPE html><html lang="th"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;600;700;800&display=swap" rel="stylesheet">
<title>Company Report — {name}</title>
<style>
  body{{font-family:'Sarabun',sans-serif;font-size:14px;color:#1a2332;margin:0;padding:32px;background:#f0f2f5;}}
  .card{{background:#fff;border-radius:12px;padding:24px;box-shadow:0 2px 16px rgba(0,0,0,.1);max-width:900px;margin:0 auto;}}
  .header{{background:linear-gradient(135deg,#0d2137,#1a3a5c);color:#fff;border-radius:10px;padding:20px 24px;margin-bottom:20px;}}
  .header h1{{font-size:20px;font-weight:800;margin:0 0 4px;}}
  .header p{{font-size:12px;opacity:.7;margin:0;}}
  .risk-badge{{display:inline-block;padding:3px 12px;border-radius:99px;font-size:12px;font-weight:700;margin-top:8px;background:{risk_color}22;color:{risk_color};border:1px solid {risk_color};}}
  h3{{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;
      color:#0d2137;padding-bottom:6px;border-bottom:2px solid #d4a017;margin:20px 0 10px;}}
  table{{width:100%;border-collapse:collapse;}}
  @media print{{body{{padding:0;background:#fff;}}.card{{box-shadow:none;padding:16px;}}}}
</style></head><body>
<div class="card">
  <div class="header">
    <h1>{name}</h1>
    <p>เลขทะเบียน: {reg}</p>
    <span class="risk-badge">Risk: {risk}</span>
  </div>
  <h3>ข้อมูลนิติบุคคล</h3>
  <table>{rows_html}</table>
  <p style="font-size:11px;color:#9ca3af;margin-top:24px;text-align:right;">
    สร้างเมื่อ: {date.today().strftime('%d/%m/%Y')} · DBD Report System
  </p>
</div></body></html>"""

def gen_fda_pdf(df_filtered):
    rows_html = ""
    for _, r in df_filtered.head(200).iterrows():
        st_badge = "#059669" if r["_สถานะ"]=="อนุมัติ" else "#dc2626"
        rows_html += f"<tr><td>{r['เลขจดแจ้ง']}</td><td>{r['BrandsTH']}</td><td>{r['ProductnameTH']}</td><td>{r['ผู้ประกอบการ'][:40]}</td><td>{r['วันที่อนุญาต']}</td><td>{r['วันหมดอายุ']}</td><td><span style='color:{st_badge};font-weight:700;'>{r['_สถานะ']}</span></td></tr>"
    return f"""<!DOCTYPE html><html lang="th"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;600;700&display=swap" rel="stylesheet">
<title>FDA Report</title>
<style>
  body{{font-family:'Sarabun',sans-serif;font-size:12px;color:#1a2332;margin:0;padding:24px;}}
  h1{{font-size:18px;color:#00236f;margin-bottom:4px;}}
  p{{color:#6b7280;font-size:11px;margin-bottom:16px;}}
  table{{width:100%;border-collapse:collapse;}}
  th{{background:#0d2137;color:#d4a017;font-size:10px;text-transform:uppercase;padding:8px 10px;text-align:left;}}
  td{{padding:7px 10px;border-bottom:1px solid #e5e7eb;}}
  tr:nth-child(even) td{{background:#f9fafb;}}
  @media print{{body{{padding:0;}}}}
</style></head><body>
<h1>FDA — รายงานผลิตภัณฑ์จดแจ้ง</h1>
<p>จำนวน {len(df_filtered):,} รายการ · สร้างเมื่อ {date.today().strftime('%d/%m/%Y')}</p>
<table><thead><tr><th>เลขจดแจ้ง</th><th>แบรนด์</th><th>ชื่อสินค้า</th><th>ผู้ประกอบการ</th><th>วันที่อนุญาต</th><th>วันหมดอายุ</th><th>สถานะ</th></tr></thead>
<tbody>{rows_html}</tbody></table></body></html>"""

# ══════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════
def sidebar():
    with st.sidebar:
        st.markdown("""<div class="sidebar-logo">
            <div class="top">EXECUTIVE</div>
            <h2>FDA & DBD<br>Report System</h2>
            <div class="sub">กรมพัฒนาธุรกิจการค้า / อย.</div>
        </div>""", unsafe_allow_html=True)
        st.markdown('<div class="user-pill"><div class="uname">Data</div><div class="urole">ตำแหน่ง: Data</div></div>', unsafe_allow_html=True)
        st.markdown("")

        nav = [("dashboard","📊","Dashboard"),("fda","🏥","FDA — จดแจ้งผลิตภัณฑ์"),("dbd","🏢","DBD — นิติบุคคล")]
        for pid, icon, label in nav:
            active = "🔸 " if st.session_state.page == pid else ""
            if st.button(f"{active}{icon}  {label}", key=f"nav_{pid}"):
                st.session_state.page = pid
                st.session_state.dbd_selected = None
                st.rerun()

        st.sidebar.markdown("---")
        st.sidebar.markdown(f'<div style="font-size:10px;color:rgba(255,255,255,0.3);">Last sync<br><span style="color:rgba(255,255,255,0.5);">{date.today().strftime("%d/%m/%Y")}</span></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════
def page_dashboard():
    st.markdown("""<div style="background:linear-gradient(135deg,#0d2137,#1a3a5c);border-radius:14px;
        padding:18px 24px;margin-bottom:16px;">
        <div style="font-size:10px;color:#d4a017;font-weight:700;letter-spacing:.15em;text-transform:uppercase;">Executive Dashboard</div>
        <div style="font-size:20px;font-weight:800;color:#f0f4ff;margin-top:2px;">FDA จดแจ้งผู้ประกอบการ</div>
        <div style="font-size:12px;color:#64748b;margin-top:2px;">ข้อมูลรวม FDA.xlsx และ DBDALL.xlsx</div>
    </div>""", unsafe_allow_html=True)

    fda = load_fda(); dbd = load_dbd()

    # year buttons
    all_years = sorted([int(y) for y in fda["_year"].dropna().unique()], reverse=True)
    yr_opts = ["ทั้งหมด"] + [str(y) for y in all_years]
    sel_yr = st.radio("", yr_opts, horizontal=True, key="dash_yr", label_visibility="collapsed")

    prod_types = ["ทุกประเภทสินค้า"] + sorted(fda["ประเภทการผลิต"].unique().tolist())
    sel_type = st.selectbox("", prod_types, key="dash_type", label_visibility="collapsed")

    df = fda.copy()
    if sel_yr != "ทั้งหมด": df = df[df["_year"] == int(sel_yr)]
    if sel_type != "ทุกประเภทสินค้า": df = df[df["ประเภทการผลิต"] == sel_type]

    today = date.today(); in90 = today + timedelta(days=90)
    total_ops = df["ผู้ประกอบการ"].replace("",pd.NA).dropna().nunique()
    dbd_names = set(dbd["Account"].str.strip()); fda_ops = set(df["ผู้ประกอบการ"].str.strip())
    linked    = len(fda_ops & dbd_names)
    near_exp  = len(df[df["_expiry"].apply(lambda d: d is not None and today <= d <= in90) & (df["_สถานะ"]=="อนุมัติ")])
    foreign   = df[~df["ผู้ผลิตต่างประเทส"].isin(["-","","nan"])]["ผู้ประกอบการ"].nunique()

    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(dkcard("ผู้ประกอบการทั้งหมด", total_ops, f"{linked} linked กับ DBD"), unsafe_allow_html=True)
    c2.markdown(dkcard("รายการทั้งหมด", len(df), f"{df[df['_สถานะ']=='อนุมัติ']['ผู้ประกอบการ'].nunique():,} Active"), unsafe_allow_html=True)
    c3.markdown(dkcard("ใกล้หมดอายุ (90 วัน)", near_exp, "ต้องติดตาม","r"), unsafe_allow_html=True)
    c4.markdown(dkcard("ใช้ผู้ผลิตต่างประเทศ", foreign, "ผู้ประกอบการ","b"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([6,4])
    with col1:
        st.markdown('<div style="color:#64748b;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;">จดแจ้งใหม่รายปี — TREND</div>', unsafe_allow_html=True)
        yr_cnt = fda.groupby("_year").size().reset_index(name="n")
        yr_cnt = yr_cnt[yr_cnt["_year"].between(2559,2580)].copy()
        yr_cnt["ปี"] = yr_cnt["_year"].astype(str)
        colors = ["#059669" if y == yr_cnt["_year"].max() else "#d4a017" for y in yr_cnt["_year"]]
        fig = go.Figure(go.Bar(x=yr_cnt["ปี"], y=yr_cnt["n"], marker_color=colors,
            text=yr_cnt["n"].apply(lambda v:f"{v:,}"), textposition="outside",
            textfont=dict(color="#f0f4ff",size=10)))
        if len(yr_cnt) >= 2:
            v = yr_cnt["n"].tolist()
            chg = (v[-1]-v[-2])/v[-2]*100 if v[-2] else 0
            fig.add_annotation(text=f"{'▲' if chg>=0 else '▼'} {abs(chg):.0f}%",
                xref="paper",yref="paper",x=1,y=1.1,showarrow=False,
                font=dict(color="#059669" if chg>=0 else "#dc2626",size=12))
        fig.update_layout(showlegend=False,bargap=0.3,yaxis=dict(visible=False))
        dark_fig(fig,260); st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

    with col2:
        st.markdown('<div style="color:#64748b;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;">สถานะสินค้าทั้งหมด</div>', unsafe_allow_html=True)
        sc = df["_สถานะ"].value_counts()
        ok_ct = int(sc.get("อนุมัติ",0)); can_ct = int(sc.get("ยกเลิก",0))
        tot = ok_ct+can_ct if ok_ct+can_ct else 1
        fig2 = go.Figure(go.Pie(labels=["Active","ยกเลิก/สิ้นอายุ"],values=[ok_ct,can_ct],
            hole=0.62, marker=dict(colors=["#059669","#dc2626"]),
            textinfo="percent", textfont=dict(size=11,color="#fff")))
        fig2.add_annotation(text=f"<b>{round(ok_ct/tot*100)}%</b><br>Active",
            x=0.5,y=0.5,showarrow=False,font=dict(size=13,color="#f0f4ff"))
        fig2.update_layout(showlegend=True,
            legend=dict(font=dict(color="#94a3b8",size=11),orientation="v",x=1.02,y=0.5))
        dark_fig(fig2,260); st.plotly_chart(fig2,use_container_width=True,config={"displayModeBar":False})

    col3, col4 = st.columns([5,5])
    with col3:
        st.markdown('<div style="color:#64748b;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;">TOP 8 ผู้ประกอบการ (จำนวนสินค้า)</div>', unsafe_allow_html=True)
        top8 = df[df["ผู้ประกอบการ"]!=""].groupby("ผู้ประกอบการ").size().sort_values(ascending=False).head(8).reset_index()
        top8.columns=["ผู้ประกอบการ","n"]
        top8["ชื่อ"] = top8["ผู้ประกอบการ"].apply(lambda s: s.replace("บริษัท ","").replace(" จำกัด","").replace("(มหาชน)","").strip()[:26])
        fig3 = go.Figure(go.Bar(y=top8["ชื่อ"][::-1],x=top8["n"][::-1],orientation="h",
            marker_color="#d4a017",text=top8["n"][::-1],textposition="outside",
            textfont=dict(color="#f0f4ff",size=10)))
        fig3.update_layout(showlegend=False,xaxis=dict(visible=False),
            yaxis=dict(tickfont=dict(size=10,color="#cbd5e1")))
        dark_fig(fig3,300); st.plotly_chart(fig3,use_container_width=True,config={"displayModeBar":False})

    with col4:
        st.markdown('<div style="color:#64748b;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;">สินค้าที่ต้องติดตาม — ใกล้หมดอายุ / ยกเลิก</div>', unsafe_allow_html=True)
        ndf = df[df["_expiry"].apply(lambda d: d is not None and today<=d<=in90)].head(8)
        if len(ndf) < 8:
            extra = df[df["_สถานะ"]=="ยกเลิก"].head(8-len(ndf))
            ndf = pd.concat([ndf,extra], ignore_index=True)
        def tb(s): return f'<span class="badge b-ok">อนุมัติ</span>' if s=="อนุมัติ" else '<span class="badge b-exp">ยกเลิก</span>'
        ndf2 = ndf[["BrandsTH","ผู้ประกอบการ","วันหมดอายุ","_สถานะ"]].copy()
        ndf2.columns=["แบรนด์","ผู้ประกอบการ","วันหมดอายุ","สถานะ"]
        ndf2["แบรนด์"] = ndf2["แบรนด์"].str[:20]
        ndf2["ผู้ประกอบการ"] = ndf2["ผู้ประกอบการ"].apply(lambda s:s.replace("บริษัท ","").replace(" จำกัด","")[:22])
        ndf2["สถานะ"] = ndf2["สถานะ"].apply(tb)
        st.write('<div class="df-wrap">'+ndf2.to_html(escape=False,index=False,classes="dataframe")+'</div>', unsafe_allow_html=True)

    # DBD summary
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div style="color:#64748b;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;margin-bottom:10px;">DBD — กรมพัฒนาธุรกิจการค้า</div>', unsafe_allow_html=True)
    dbd_run=dbd["สถานะนิติบุคคล"].str.contains("ดำเนินกิจการ",na=False).sum()
    dbd_cls=dbd["สถานะนิติบุคคล"].isin(["เลิก","เสร็จการชำระบัญชี"]).sum()
    dbd_risk_hi=(dbd["_risk"]=="HIGH").sum(); dbd_risk_md=(dbd["_risk"]=="MEDIUM").sum()
    d1,d2,d3,d4=st.columns(4)
    d1.markdown(dkcard("นิติบุคคลทั้งหมด",len(dbd),"ใน DBDALL.xlsx"),unsafe_allow_html=True)
    d2.markdown(dkcard("ดำเนินกิจการอยู่",dbd_run,"✅ ยังเปิดดำเนินการ","g"),unsafe_allow_html=True)
    d3.markdown(dkcard("ต้องติดตาม",dbd_risk_md+dbd_risk_hi,"MEDIUM + HIGH risk","r"),unsafe_allow_html=True)
    d4.markdown(dkcard("เลิก/ชำระบัญชี",dbd_cls,"❌ ปิดกิจการแล้ว"),unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  FDA PAGE
# ══════════════════════════════════════════════════════════════
def page_fda():
    st.markdown('<div style="font-size:20px;font-weight:800;color:#00236f;margin-bottom:2px">FDA — สำนักงานคณะกรรมการอาหารและยา (อย.)</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:13px;color:#444651;margin-bottom:14px">ข้อมูลผลิตภัณฑ์จดแจ้ง / ทะเบียนเครื่องสำอาง</div>', unsafe_allow_html=True)
    df = load_fda()

    total=len(df); approved=(df["_สถานะ"]=="อนุมัติ").sum(); cancelled=total-approved
    c1,c2,c3=st.columns(3)
    c1.markdown(ltcard("ทั้งหมด",total,"รายการในฐานข้อมูล"),unsafe_allow_html=True)
    c2.markdown(ltcard("อนุมัติ",approved,"✅ สินค้าที่อนุมัติแล้ว","g"),unsafe_allow_html=True)
    c3.markdown(ltcard("ยกเลิก",cancelled,"❌ สิ้นอายุ / ยกเลิก","r"),unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)

    f1,f2,f3,f4=st.columns([2.5,1.2,1.5,1.5])
    with f1: q=st.text_input("🔍 ค้นหา (เลขจดแจ้ง / แบรนด์ TH-EN / ชื่อสินค้า / ผู้ประกอบการ)",key="fda_q",placeholder="พิมพ์คำค้นหา...")
    with f2: sel_st=st.selectbox("สถานะ",["ทั้งหมด","อนุมัติ","ยกเลิก"],key="fda_st")
    with f3:
        prod_list=["ทั้งหมด"]+sorted(df["ประเภทการผลิต"].unique().tolist())
        sel_prod=st.selectbox("ประเภทการผลิต",prod_list,key="fda_prod")
    with f4:
        yr_list=["ทั้งหมด"]+[str(y) for y in sorted(df["_year"].dropna().unique().astype(int),reverse=True)]
        sel_yr=st.selectbox("ปีจดแจ้ง (BE)",yr_list,key="fda_yr")

    filtered=df.copy()
    if q:
        mask=(filtered["เลขจดแจ้ง"].str.contains(q,case=False,na=False)|
              filtered["เลขจดแจ้งไม่มีขีด"].str.contains(q,case=False,na=False)|
              filtered["BrandsTH"].str.contains(q,case=False,na=False)|
              filtered["BrandsENG"].str.contains(q,case=False,na=False)|
              filtered["ProductnameTH"].str.contains(q,case=False,na=False)|
              filtered["ProductnameENG"].str.contains(q,case=False,na=False)|
              filtered["ผู้ประกอบการ"].str.contains(q,case=False,na=False))
        filtered=filtered[mask]
    if sel_st!="ทั้งหมด":   filtered=filtered[filtered["_สถานะ"]==sel_st]
    if sel_prod!="ทั้งหมด": filtered=filtered[filtered["ประเภทการผลิต"]==sel_prod]
    if sel_yr!="ทั้งหมด":   filtered=filtered[filtered["_year"]==int(sel_yr)]

    st.caption(f"พบ **{len(filtered):,}** รายการ")

    # PDF download
    if len(filtered) > 0:
        pdf_html = gen_fda_pdf(filtered)
        st.download_button("📥 ดาวน์โหลด Report (HTML→Print PDF)",
            data=pdf_html.encode("utf-8"), file_name="FDA_Report.html",
            mime="text/html", key="fda_dl")

    if filtered.empty: st.info("ไม่พบข้อมูล"); return

    cols_show=["เลขจดแจ้ง","BrandsTH","BrandsENG","ProductnameTH","ผู้ประกอบการ","ประเภทการผลิต","วันที่อนุญาต","วันหมดอายุ","_สถานะ"]
    total2=len(filtered); pages=max(1,-(-total2//100))
    page_no=st.number_input(f"หน้า (จาก {pages} หน้า — {total2:,} รายการ)",min_value=1,max_value=pages,value=1,step=1,key="fda_pg")
    chunk=filtered.iloc[(page_no-1)*100:page_no*100][cols_show].copy()
    def fda_b(s): return '<span class="badge b-ok">อนุมัติ</span>' if s=="อนุมัติ" else '<span class="badge b-exp">ยกเลิก</span>'
    chunk["_สถานะ"]=chunk["_สถานะ"].apply(fda_b)
    st.write('<div class="df-wrap">'+chunk.to_html(escape=False,index=False,classes="dataframe")+'</div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  DBD LIST
# ══════════════════════════════════════════════════════════════
def page_dbd_list():
    st.markdown('<div style="font-size:20px;font-weight:800;color:#0d2137;margin-bottom:2px">DBD — ภาพรวมทั้งหมด</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:13px;color:#444651;margin-bottom:14px">สรุปข้อมูลสำหรับผู้บริหาร</div>', unsafe_allow_html=True)
    df = load_dbd()

    total=len(df); running=df["สถานะนิติบุคคล"].str.contains("ดำเนินกิจการ",na=False).sum()
    risk_lo=(df["_risk"]=="LOW").sum(); risk_md=(df["_risk"]=="MEDIUM").sum(); risk_hi=(df["_risk"]=="HIGH").sum()
    c1,c2,c3,c4=st.columns(4)
    c1.markdown(ltcard("บริษัททั้งหมด",total,"ในระบบ","o"),unsafe_allow_html=True)
    c2.markdown(ltcard("ดำเนินกิจการอยู่",running,f"{round(running/total*100)}% ของทั้งหมด","g"),unsafe_allow_html=True)
    c3.markdown(ltcard("ปกติ (LOW Risk)",risk_lo,f"{round(risk_lo/total*100)}% ของทั้งหมด","g"),unsafe_allow_html=True)
    c4.markdown(ltcard("ต้องติดตาม",risk_md+risk_hi,"MEDIUM + HIGH risk","r"),unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)

    # Risk bar
    st.markdown(f"""<div class="risk-bar">
        <div style="font-size:11px;font-weight:700;color:#6b7280;text-transform:uppercase;letter-spacing:1px;min-width:80px;">⚡ Risk Level</div>
        <span class="risk-seg r-lo">{risk_lo} ปกติ</span>
        <span class="risk-seg r-md">{risk_md} ต้องติดตาม</span>
        <span class="risk-seg r-hi">{risk_hi} ความเสี่ยงสูง</span>
    </div>""", unsafe_allow_html=True)

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
        risk_opts=["ทั้งหมด","LOW","MEDIUM","HIGH"]
        sel_risk=st.selectbox("Risk Level",risk_opts,key="dbd_risk")

    filtered=df.copy()
    if q:
        mask=(filtered["Account"].str.contains(q,case=False,na=False)|
              filtered["เลขทะเบียนนิติบุคคล"].str.contains(q,case=False,na=False))
        filtered=filtered[mask]
    if sf!="ทั้งหมด":       filtered=filtered[filtered["สถานะนิติบุคคล"]==sf]
    if sel_biz!="ทั้งหมด": filtered=filtered[filtered["กลุ่มธุรกิจ"]==sel_biz]
    if sel_risk!="ทั้งหมด":filtered=filtered[filtered["_risk"]==sel_risk]

    st.caption(f"แสดง {len(filtered):,} จาก {total:,} บริษัท")

    # Paginate
    page_size=25; total_f=len(filtered); pages=max(1,-(-total_f//page_size))
    page_no=st.number_input(f"หน้า (จาก {pages})",min_value=1,max_value=pages,value=1,step=1,key="dbd_pg")
    page_df=filtered.iloc[(page_no-1)*page_size:page_no*page_size].reset_index(drop=True)

    def risk_b(r):
        return {"LOW":'<span class="badge b-lo">ปกติ</span>',
                "MEDIUM":'<span class="badge b-md">ติดตาม</span>',
                "HIGH":'<span class="badge b-hi">เสี่ยงสูง</span>'}.get(r,'<span class="badge b-oth">-</span>')
    def status_b(s):
        if "ดำเนินกิจการ" in str(s): return f'<span class="badge b-run">{s}</span>'
        if str(s) in ("เลิก","เสร็จการชำระบัญชี"): return f'<span class="badge b-cls">{s}</span>'
        return f'<span class="badge b-oth">{s}</span>'

    # Table header
    st.markdown("""<div style="background:#fff;border-radius:10px 10px 0 0;padding:12px 16px;
        border-bottom:1px solid #e5e7eb;display:flex;justify-content:space-between;align-items:center;">
        <div style="font-size:14px;font-weight:700;color:#0d2137;">รายชื่อบริษัท</div>
    </div>""", unsafe_allow_html=True)

    # Render rows with detail buttons
    for i, row in page_df.iterrows():
        cols = st.columns([3.5,1.2,1,1,0.8,0.8])
        with cols[0]:
            st.markdown(f"""<div style="padding:4px 0;">
                <div style="font-weight:700;color:#0d2137;font-size:13px;">{row['Account']}</div>
                <div style="font-size:11px;color:#6b7280;font-family:'IBM Plex Mono';">{row['เลขทะเบียนนิติบุคคล']}</div>
            </div>""", unsafe_allow_html=True)
        with cols[1]: st.markdown(status_b(row["สถานะนิติบุคคล"]), unsafe_allow_html=True)
        with cols[2]: st.markdown(f'<div style="font-size:12px;color:#6b7280;">{row["กลุ่มธุรกิจ"] or "-"}</div>', unsafe_allow_html=True)
        with cols[3]: st.markdown(f'<div style="font-size:11px;color:#6b7280;">{row["ทุนจดทะเบียน"] or "-"}</div>', unsafe_allow_html=True)
        with cols[4]: st.markdown(risk_b(row["_risk"]), unsafe_allow_html=True)
        with cols[5]:
            if st.button("ดูข้อมูล", key=f"detail_{page_no}_{i}", use_container_width=True):
                st.session_state.dbd_selected = row.to_dict()
                st.rerun()
        st.markdown('<hr style="margin:2px 0;border-color:#f0f0f0;">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  DBD COMPANY DETAIL
# ══════════════════════════════════════════════════════════════
def page_dbd_detail():
    row = st.session_state.dbd_selected
    name = row.get("Account","—"); reg = row.get("เลขทะเบียนนิติบุคคล","—")
    status = row.get("สถานะนิติบุคคล","—"); risk = row.get("_risk","—")
    risk_color = {"LOW":"#059669","MEDIUM":"#d97706","HIGH":"#dc2626"}.get(risk,"#6b7280")

    # Header
    st.markdown(f"""<div style="background:linear-gradient(135deg,#0d2137,#1a3a5c);border-radius:12px;
        padding:18px 24px;margin-bottom:16px;display:flex;justify-content:space-between;align-items:flex-start;">
        <div>
            <div style="font-size:18px;font-weight:800;color:#fff;">{name}</div>
            <div style="font-size:12px;color:rgba(255,255,255,0.5);margin-top:3px;">เลขทะเบียน: {reg} · {status}</div>
            <span style="display:inline-block;margin-top:8px;padding:3px 12px;border-radius:99px;
                font-size:11px;font-weight:700;background:{risk_color}22;color:{risk_color};
                border:1px solid {risk_color};">Risk: {risk}</span>
        </div>
    </div>""", unsafe_allow_html=True)

    btn1, btn2, _ = st.columns([1.5, 1.5, 5])
    with btn1:
        if st.button("← กลับรายการ", use_container_width=True):
            st.session_state.dbd_selected = None; st.rerun()
    with btn2:
        pdf_html = gen_dbd_pdf(row)
        st.download_button("📄 ออก PDF Report", data=pdf_html.encode("utf-8"),
            file_name=f"DBD_{reg}.html", mime="text/html",
            use_container_width=True, key="dbd_pdf_dl")

    st.markdown('<div style="font-size:11px;color:#6b7280;margin-bottom:16px;">💡 หลังดาวน์โหลด HTML ให้เปิดในเบราว์เซอร์ แล้วกด Ctrl+P เพื่อ Print as PDF</div>', unsafe_allow_html=True)

    tab_info, tab_dir, tab_biz = st.tabs(["📋 ข้อมูลนิติบุคคล","👥 กรรมการ","🏭 วัตถุประสงค์"])

    def info_row(label, value):
        v = value if value and value not in ["-",""] else "—"
        return f'<div class="info-row"><div class="info-lbl">{label}</div><div class="info-val">{v}</div></div>'

    with tab_info:
        html = '<div class="detail-sec"><h4>ข้อมูลพื้นฐาน</h4>'
        for k,v in [("ประเภทนิติบุคคล",row.get("ประเภทนิติบุคคล","")),
                    ("สถานะนิติบุคคล",row.get("สถานะนิติบุคคล","")),
                    ("วันที่จดทะเบียนจัดตั้ง",row.get("วันที่จดทะเบียนจัดตั้ง","")),
                    ("ทุนจดทะเบียน",row.get("ทุนจดทะเบียน","")),
                    ("ทุนชำระแล้ว",row.get("ทุนชำระแล้ว","")),
                    ("กลุ่มธุรกิจ",row.get("กลุ่มธุรกิจ","")),
                    ("ขนาดธุรกิจ",row.get("ขนาดธุรกิจ","")),
                    ("ปีที่ส่งงบการเงิน",row.get("ปีที่ส่งงบการเงิน","")),
                    ("Website",row.get("Website","")),
                    ("ที่ตั้งสำนักงาน",row.get("ที่ตั้งสำนักงานแห่งใหญ่","")),
                    ]:
            html += info_row(k,v)
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)

    with tab_dir:
        dirs = row.get("รายชื่อกรรมการ","")
        sign = row.get("กรรมการลงชื่อผูกพัน","")
        st.markdown(f'<div class="detail-sec"><h4>รายชื่อกรรมการ</h4><div style="font-size:13px;line-height:1.8;">{dirs or "—"}</div>', unsafe_allow_html=True)
        st.markdown(f'<h4 style="margin-top:16px;">อำนาจลงนาม</h4><div style="font-size:13px;line-height:1.8;">{sign or "—"}</div></div>', unsafe_allow_html=True)

    with tab_biz:
        biz_reg = row.get("ประเภทธุรกิจตอนจดทะเบียน","")
        biz_new = row.get("ประเภทธุรกิจที่ส่งงบการเงินปีล่าสุด","")
        obj_reg = row.get("วัตถุประสงค์ตอนจดทะเบียน","")
        obj_new = row.get("วัตถุประสงค์ปีล่าสุด","")
        st.markdown(f"""<div class="detail-sec">
            <h4>ประเภทธุรกิจตอนจดทะเบียน</h4><div style="font-size:13px;line-height:1.8;">{biz_reg or "—"}</div>
            <h4 style="margin-top:16px;">ประเภทธุรกิจปีล่าสุด</h4><div style="font-size:13px;line-height:1.8;">{biz_new or "—"}</div>
            <h4 style="margin-top:16px;">วัตถุประสงค์ตอนจดทะเบียน</h4><div style="font-size:13px;line-height:1.8;">{obj_reg or "—"}</div>
            <h4 style="margin-top:16px;">วัตถุประสงค์ปีล่าสุด</h4><div style="font-size:13px;line-height:1.8;">{obj_new or "—"}</div>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════
def main():
    sidebar()
    page = st.session_state.page
    if page == "dashboard":
        page_dashboard()
    elif page == "fda":
        page_fda()
    elif page == "dbd":
        if st.session_state.dbd_selected:
            page_dbd_detail()
        else:
            page_dbd_list()

main()
