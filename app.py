import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os, re
from datetime import date, timedelta

st.set_page_config(page_title="FDA & DBD Dashboard", page_icon="🏛️", layout="wide")

BASE     = os.path.dirname(__file__)
FDA_XLSX = os.path.join(BASE, "FDA.xlsx")
DBD_XLSX = os.path.join(BASE, "DBDALL.xlsx")

THAI_MONTHS = {
    'มกราคม':1,'กุมภาพันธ์':2,'มีนาคม':3,'เมษายน':4,
    'พฤษภาคม':5,'มิถุนายน':6,'กรกฎาคม':7,'สิงหาคม':8,
    'กันยายน':9,'ตุลาคม':10,'พฤศจิกายน':11,'ธันวาคม':12
}

# ── Global CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;600;700;800&family=IBM+Plex+Mono:wght@400;600&display=swap');
html,body,[class*="css"]{font-family:'Sarabun',sans-serif;}
#MainMenu,footer{visibility:hidden;}
.block-container{padding-top:1.5rem!important;}

/* ── dark KPI cards ── */
.dk-card{
    background:#163352;border-radius:12px;padding:18px 22px;
    border-left:4px solid #d4a017;margin-bottom:4px;
    box-shadow:0 2px 12px rgba(13,33,55,0.25);
}
.dk-card.green{border-left-color:#059669;}
.dk-card.red  {border-left-color:#dc2626;}
.dk-card.blue {border-left-color:#3b82f6;}
.dk-label{font-size:10px;font-weight:700;text-transform:uppercase;
          letter-spacing:.12em;color:#94a3b8;margin-bottom:6px;}
.dk-value{font-size:30px;font-weight:900;color:#f0f4ff;
          font-family:'IBM Plex Mono',monospace;line-height:1;}
.dk-sub{font-size:11px;font-weight:600;color:#64748b;margin-top:5px;}

/* ── light KPI cards ── */
.lt-card{
    background:#fff;border-radius:12px;padding:18px 22px;
    border-left:4px solid #00236f;margin-bottom:4px;
    box-shadow:0 1px 4px rgba(0,0,0,.08);
}
.lt-card.green{border-left-color:#006d30;}
.lt-card.red  {border-left-color:#dc2626;}
.lt-card.grey {border-left-color:#6b7280;}
.lt-label{font-size:10px;font-weight:700;text-transform:uppercase;
          letter-spacing:.1em;color:#444651;margin-bottom:4px;}
.lt-value{font-size:30px;font-weight:900;color:#0d1c2e;line-height:1;}
.lt-sub  {font-size:11px;font-weight:600;margin-top:5px;color:#444651;}

/* ── badges ── */
.badge{display:inline-block;padding:2px 10px;border-radius:99px;font-size:11px;font-weight:700;}
.b-ok  {background:#d0f0d8;color:#005323;}
.b-exp {background:#ffdad6;color:#93000a;}
.b-can {background:#f3f4f6;color:#374151;}
.b-run {background:#dce9ff;color:#00236f;}
.b-cls {background:#ffdad6;color:#93000a;}
.b-oth {background:#fef3c7;color:#92400e;}

/* ── data table ── */
.df-wrap{border-radius:10px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.08);}
.dataframe{width:100%;border-collapse:collapse;font-size:13px;}
.dataframe th{background:#0d2137;color:#d4a017;font-size:10px;font-weight:700;
              text-transform:uppercase;letter-spacing:.08em;padding:10px 14px;text-align:left;}
.dataframe td{padding:9px 14px;border-bottom:1px solid #e6eeff;vertical-align:top;background:#fff;}
.dataframe tr:hover td{background:#f0f7ff;}

div[data-testid="stTabs"] button{font-family:'Sarabun',sans-serif;font-weight:700;font-size:14px;}
div[data-testid="stTabs"] button[aria-selected="true"]{color:#d4a017!important;border-bottom-color:#d4a017!important;}
</style>
""", unsafe_allow_html=True)


# ── Thai date helpers ──────────────────────────────────────────
def parse_thai_date(s):
    if not s or str(s).strip() in ['-','','nan']: return None
    p = str(s).strip().split()
    if len(p) < 3: return None
    try:
        d, m_th, y_be = int(p[0]), p[1], int(p[-1])
        m = THAI_MONTHS.get(m_th)
        y = y_be - 543
        if m and 1 <= d <= 31 and 1900 < y < 2200:
            return date(y, m, d)
    except: pass
    return None

def extract_be_year(s):
    m = re.search(r'(\d{4})', str(s))
    return int(m.group(1)) if m else None


# ── Load & pre-process ─────────────────────────────────────────
@st.cache_data(show_spinner="⏳ โหลด FDA.xlsx...")
def load_fda():
    df = pd.read_excel(FDA_XLSX, dtype=str).fillna("")
    df["_สถานะ"]  = df["สถานะสินค้า"].apply(lambda s: "อนุมัติ" if s == "อนุมัติ" else "ยกเลิก")
    df["_year"]   = df["วันที่อนุญาต"].apply(extract_be_year)
    df["_expiry"] = df["วันหมดอายุ"].apply(parse_thai_date)
    return df

@st.cache_data(show_spinner="⏳ โหลด DBDALL.xlsx...")
def load_dbd():
    return pd.read_excel(DBD_XLSX, dtype=str).fillna("")


# ── Plotly dark helpers ────────────────────────────────────────
DARK_BG  = "#0d2137"
DARK_BG2 = "#163352"
GOLD     = "#d4a017"
GREEN    = "#059669"
RED      = "#dc2626"

def dark_fig(fig):
    fig.update_layout(
        paper_bgcolor=DARK_BG2, plot_bgcolor=DARK_BG2,
        font=dict(family="Sarabun", color="#cbd5e1"),
        margin=dict(l=10,r=10,t=30,b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(gridcolor="#1e3a5c", zerolinecolor="#1e3a5c")
    fig.update_yaxes(gridcolor="#1e3a5c", zerolinecolor="#1e3a5c")
    return fig

def card(label, value, sub, cls=""):
    v = f"{value:,}" if isinstance(value, int) else str(value)
    return f'<div class="dk-card {cls}"><div class="dk-label">{label}</div><div class="dk-value">{v}</div><div class="dk-sub">{sub}</div></div>'

def lt_card(label, value, sub, cls=""):
    v = f"{value:,}" if isinstance(value, int) else str(value)
    return f'<div class="lt-card {cls}"><div class="lt-label">{label}</div><div class="lt-value">{v}</div><div class="lt-sub">{sub}</div></div>'


# ══════════════════════════════════════════════════════════════
#  DASHBOARD TAB
# ══════════════════════════════════════════════════════════════
def tab_dashboard():
    # dark header
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0d2137,#1a3a5c);border-radius:14px;
                padding:20px 28px;margin-bottom:20px;">
        <div style="font-size:11px;color:#d4a017;font-weight:700;letter-spacing:.15em;
                    text-transform:uppercase;margin-bottom:4px;">Executive Dashboard</div>
        <div style="font-size:22px;font-weight:800;color:#f0f4ff;line-height:1.1;">
            FDA จดแจ้งผู้ประกอบการ
        </div>
        <div style="font-size:13px;color:#64748b;margin-top:4px;">
            ข้อมูลรวม FDA.xlsx และ DBDALL.xlsx
        </div>
    </div>""", unsafe_allow_html=True)

    fda = load_fda()
    dbd = load_dbd()

    # ── Year filter ──
    year_cols = st.columns([1,1,1,1,3])
    years = ["ทั้งหมด", "2566", "2567", "2568"]
    sel_year = st.radio("", years, horizontal=True, key="dash_yr", label_visibility="collapsed")

    prod_types = ["ทุกประเภทสินค้า"] + sorted(fda["ประเภทการผลิต"].unique().tolist())
    sel_type   = st.selectbox("", prod_types, key="dash_type", label_visibility="collapsed")

    # apply filters
    df = fda.copy()
    if sel_year != "ทั้งหมด":
        df = df[df["_year"] == int(sel_year)]
    if sel_type != "ทุกประเภทสินค้า":
        df = df[df["ประเภทการผลิต"] == sel_type]

    today = date.today()
    in90  = today + timedelta(days=90)

    # ── KPIs ──
    total_ops   = df["ผู้ประกอบการ"].replace("", pd.NA).dropna().nunique()
    dbd_total   = len(dbd)
    # simple match count
    dbd_names   = set(dbd["Account"].str.strip().tolist())
    fda_ops     = set(df["ผู้ประกอบการ"].str.strip().tolist())
    linked      = len(fda_ops & dbd_names)

    total_items = len(df)
    near_expiry = df[
        df["_expiry"].apply(lambda d: d is not None and today <= d <= in90)
        & (df["_สถานะ"] == "อนุมัติ")
    ]
    near_exp_ct = len(near_expiry)
    foreign_ct  = df[~df["ผู้ผลิตต่างประเทส"].isin(["-","","nan"])]["ผู้ประกอบการ"].nunique()

    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(card("ผู้ประกอบการทั้งหมด", total_ops, f"{linked} linked กับ DBD"), unsafe_allow_html=True)
    c2.markdown(card("รายการทั้งหมด", total_items, f"{df[df['_สถานะ']=='อนุมัติ']['ผู้ประกอบการ'].nunique():,} Active"), unsafe_allow_html=True)
    c3.markdown(card("ใกล้หมดอายุ (90 วัน)", near_exp_ct, "ต้องติดตาม", "red"), unsafe_allow_html=True)
    c4.markdown(card("ใช้ผู้ผลิตต่างประเทศ", foreign_ct, "ผู้ประกอบการ", "blue"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 2: Trend bar + Donut ──
    col_trend, col_donut = st.columns([6, 4])

    with col_trend:
        st.markdown('<div style="color:#94a3b8;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;margin-bottom:8px;">จดแจ้งใหม่รายปี — TREND</div>', unsafe_allow_html=True)
        year_counts = fda.groupby("_year").size().reset_index(name="จำนวน")
        year_counts = year_counts[year_counts["_year"].isin([2566,2567,2568])].copy()
        year_counts["ปี"] = year_counts["_year"].astype(str)
        colors = [GOLD if y != 2568 else GREEN for y in year_counts["_year"]]

        fig_trend = go.Figure(go.Bar(
            x=year_counts["ปี"], y=year_counts["จำนวน"],
            marker_color=colors,
            text=year_counts["จำนวน"].apply(lambda v: f"{v:,}"),
            textposition="outside", textfont=dict(color="#f0f4ff", size=11),
        ))
        if len(year_counts) >= 2:
            vals = year_counts["จำนวน"].tolist()
            chg  = ((vals[-1]-vals[-2])/vals[-2]*100) if vals[-2] else 0
            fig_trend.add_annotation(
                text=f"{'▲' if chg>=0 else '▼'} {abs(chg):.0f}%",
                xref="paper", yref="paper", x=1, y=1.08,
                showarrow=False, font=dict(color=GREEN if chg>=0 else RED, size=13, family="Sarabun")
            )
        fig_trend.update_layout(showlegend=False, height=260,
            bargap=0.35, yaxis=dict(visible=False), xaxis=dict(tickfont=dict(size=12)))
        dark_fig(fig_trend)
        st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar":False})

    with col_donut:
        st.markdown('<div style="color:#94a3b8;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;margin-bottom:8px;">สถานะสินค้าทั้งหมด</div>', unsafe_allow_html=True)
        status_counts = df["_สถานะ"].value_counts()
        ok_ct  = status_counts.get("อนุมัติ", 0)
        can_ct = status_counts.get("ยกเลิก", 0)
        tot    = ok_ct + can_ct if (ok_ct + can_ct) > 0 else 1
        ok_pct = round(ok_ct / tot * 100)

        fig_donut = go.Figure(go.Pie(
            labels=["Active", "ยกเลิก/สิ้นอายุ"],
            values=[ok_ct, can_ct],
            hole=0.62,
            marker=dict(colors=[GREEN, RED]),
            textinfo="percent",
            textfont=dict(size=12, color="#fff"),
        ))
        fig_donut.add_annotation(
            text=f"<b>{ok_pct}%</b><br>Active",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="#f0f4ff", family="Sarabun")
        )
        fig_donut.update_layout(
            showlegend=True, height=260,
            legend=dict(font=dict(color="#94a3b8",size=11), orientation="v", x=1, y=0.5),
        )
        dark_fig(fig_donut)
        st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar":False})

    # ── Row 3: Top operators + Compliance table ──
    col_top, col_tbl = st.columns([5, 5])

    with col_top:
        st.markdown('<div style="color:#94a3b8;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;margin-bottom:8px;">TOP 8 ผู้ประกอบการ (จำนวนสินค้า)</div>', unsafe_allow_html=True)
        top8 = (df[df["ผู้ประกอบการ"] != ""]
                .groupby("ผู้ประกอบการ").size()
                .sort_values(ascending=False).head(8).reset_index())
        top8.columns = ["ผู้ประกอบการ","จำนวน"]
        # shorten names
        top8["ชื่อ"] = top8["ผู้ประกอบการ"].apply(
            lambda s: s.replace("บริษัท ","").replace(" จำกัด","").replace("(มหาชน)","").strip()[:28])

        fig_top = go.Figure(go.Bar(
            y=top8["ชื่อ"][::-1], x=top8["จำนวน"][::-1],
            orientation="h",
            marker_color=GOLD,
            text=top8["จำนวน"][::-1],
            textposition="outside",
            textfont=dict(color="#f0f4ff", size=11),
        ))
        fig_top.update_layout(height=300, showlegend=False,
            xaxis=dict(visible=False), yaxis=dict(tickfont=dict(size=11, color="#cbd5e1")))
        dark_fig(fig_top)
        st.plotly_chart(fig_top, use_container_width=True, config={"displayModeBar":False})

    with col_tbl:
        st.markdown('<div style="color:#94a3b8;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;margin-bottom:8px;">สินค้าที่ต้องติดตาม — ใกล้หมดอายุ / ยกเลิก</div>', unsafe_allow_html=True)
        # products expiring soon OR cancelled with recent approval
        near_df = df[
            df["_expiry"].apply(lambda d: d is not None and today <= d <= in90)
        ].head(8)[["BrandsTH","ผู้ประกอบการ","วันหมดอายุ","_สถานะ"]].copy()
        if len(near_df) < 8:
            cancelled_df = df[df["_สถานะ"] == "ยกเลิก"].head(8 - len(near_df))[
                ["BrandsTH","ผู้ประกอบการ","วันหมดอายุ","_สถานะ"]].copy()
            near_df = pd.concat([near_df, cancelled_df], ignore_index=True)

        def tbl_badge(s):
            if s == "อนุมัติ": return '<span class="badge b-ok">อนุมัติ</span>'
            return '<span class="badge b-exp">ยกเลิก</span>'

        near_df["สถานะ"] = near_df["_สถานะ"].apply(tbl_badge)
        near_df["แบรนด์"] = near_df["BrandsTH"].apply(lambda s: s[:20] if s else "-")
        near_df["ผู้ประกอบการ"] = near_df["ผู้ประกอบการ"].apply(
            lambda s: s.replace("บริษัท ","").replace(" จำกัด","")[:22])
        disp = near_df[["แบรนด์","ผู้ประกอบการ","วันหมดอายุ","สถานะ"]]
        html = '<div class="df-wrap">' + disp.to_html(escape=False, index=False, classes="dataframe") + '</div>'
        st.write(html, unsafe_allow_html=True)

    # ── DBD Summary ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div style="color:#94a3b8;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;margin-bottom:12px;">DBD — กรมพัฒนาธุรกิจการค้า</div>', unsafe_allow_html=True)
    dbd_running = dbd["สถานะนิติบุคคล"].str.contains("ดำเนินกิจการ", na=False).sum()
    dbd_closed  = dbd["สถานะนิติบุคคล"].isin(["เลิก","เสร็จการชำระบัญชี"]).sum()
    dbd_other   = len(dbd) - dbd_running - dbd_closed

    d1,d2,d3,d4 = st.columns(4)
    d1.markdown(card("นิติบุคคลทั้งหมด",  len(dbd),    "ใน DBDALL.xlsx"),           unsafe_allow_html=True)
    d2.markdown(card("ดำเนินกิจการอยู่",   dbd_running, "✅ ยังเปิดดำเนินการ","green"), unsafe_allow_html=True)
    d3.markdown(card("เลิก / ชำระบัญชี",  dbd_closed,  "❌ ปิดกิจการแล้ว","red"),    unsafe_allow_html=True)
    d4.markdown(card("สถานะอื่นๆ",         dbd_other,   "ร้าง / แปรสภาพ ฯลฯ"),       unsafe_allow_html=True)

    # DBD biz group chart
    biz_counts = dbd["กลุ่มธุรกิจ"].replace("",pd.NA).dropna().value_counts().head(6).reset_index()
    biz_counts.columns = ["กลุ่ม","จำนวน"]
    fig_biz = px.bar(biz_counts, x="จำนวน", y="กลุ่ม", orientation="h",
                     color_discrete_sequence=[GOLD])
    fig_biz.update_layout(height=220, showlegend=False, title="กลุ่มธุรกิจ DBD",
        title_font=dict(color="#94a3b8",size=11),
        yaxis=dict(tickfont=dict(size=11, color="#cbd5e1")),
        xaxis=dict(visible=False))
    dark_fig(fig_biz)
    st.plotly_chart(fig_biz, use_container_width=True, config={"displayModeBar":False})


# ══════════════════════════════════════════════════════════════
#  FDA TAB
# ══════════════════════════════════════════════════════════════
def fda_badge(s):
    if s == "อนุมัติ": return '<span class="badge b-ok">อนุมัติ</span>'
    return '<span class="badge b-exp">ยกเลิก</span>'

def dbd_badge(s):
    s = str(s)
    if "ดำเนินกิจการ" in s:               return f'<span class="badge b-run">{s}</span>'
    if s in ("เลิก","เสร็จการชำระบัญชี"): return f'<span class="badge b-cls">{s}</span>'
    return                                        f'<span class="badge b-oth">{s}</span>'

def show_paginated(df_show, badge_fn, cols, key, page_size=100):
    total = len(df_show)
    pages = max(1, -(-total // page_size))
    page  = st.number_input(f"หน้า (จาก {pages} หน้า — {total:,} รายการ)",
                            min_value=1, max_value=pages, value=1, step=1, key=f"pg_{key}")
    chunk = df_show.iloc[(page-1)*page_size : page*page_size][cols].copy()
    chunk[cols[-1]] = chunk[cols[-1]].apply(badge_fn)
    html = '<div class="df-wrap">' + chunk.to_html(escape=False, index=False, classes="dataframe") + '</div>'
    st.write(html, unsafe_allow_html=True)

def tab_fda():
    st.markdown('<div style="font-size:20px;font-weight:800;color:#00236f;margin-bottom:2px">FDA — สำนักงานคณะกรรมการอาหารและยา (อย.)</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:13px;color:#444651;margin-bottom:16px">ข้อมูลผลิตภัณฑ์จดแจ้ง / ทะเบียนเครื่องสำอาง</div>', unsafe_allow_html=True)
    df = load_fda()

    total    = len(df)
    approved = (df["_สถานะ"] == "อนุมัติ").sum()
    cancelled= total - approved
    c1,c2,c3 = st.columns(3)
    c1.markdown(lt_card("ทั้งหมด",  total,     "รายการในฐานข้อมูล"),           unsafe_allow_html=True)
    c2.markdown(lt_card("อนุมัติ",  approved,  "✅ สินค้าที่อนุมัติแล้ว","green"), unsafe_allow_html=True)
    c3.markdown(lt_card("ยกเลิก",   cancelled, "❌ สิ้นอายุ / ยกเลิก","red"),    unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    f1,f2,f3,f4 = st.columns([2.5,1.2,1.5,1.5])
    with f1: q = st.text_input("🔍 ค้นหา (เลขจดแจ้ง / แบรนด์ TH-EN / ชื่อสินค้า TH-EN / ผู้ประกอบการ)", key="fda_q", placeholder="พิมพ์คำค้นหา...")
    with f2: sel_st = st.selectbox("สถานะสินค้า", ["ทั้งหมด","อนุมัติ","ยกเลิก"], key="fda_st")
    with f3:
        prod_list = ["ทั้งหมด"] + sorted(df["ประเภทการผลิต"].unique().tolist())
        sel_prod = st.selectbox("ประเภทการผลิต", prod_list, key="fda_prod")
    with f4:
        yr_list = ["ทั้งหมด"] + [str(y) for y in sorted(df["_year"].dropna().unique().astype(int), reverse=True)]
        sel_yr = st.selectbox("ปีจดแจ้ง (BE)", yr_list, key="fda_yr")

    filtered = df.copy()
    if q:
        mask = (
            filtered["เลขจดแจ้ง"].str.contains(q, case=False, na=False) |
            filtered["เลขจดแจ้งไม่มีขีด"].str.contains(q, case=False, na=False) |
            filtered["BrandsTH"].str.contains(q, case=False, na=False) |
            filtered["BrandsENG"].str.contains(q, case=False, na=False) |
            filtered["ProductnameTH"].str.contains(q, case=False, na=False) |
            filtered["ProductnameENG"].str.contains(q, case=False, na=False) |
            filtered["ผู้ประกอบการ"].str.contains(q, case=False, na=False)
        )
        filtered = filtered[mask]
    if sel_st   != "ทั้งหมด": filtered = filtered[filtered["_สถานะ"] == sel_st]
    if sel_prod != "ทั้งหมด": filtered = filtered[filtered["ประเภทการผลิต"] == sel_prod]
    if sel_yr   != "ทั้งหมด": filtered = filtered[filtered["_year"] == int(sel_yr)]

    st.caption(f"พบ **{len(filtered):,}** รายการ")
    if filtered.empty: st.info("ไม่พบข้อมูล"); return

    cols_show = ["เลขจดแจ้ง","BrandsTH","BrandsENG","ProductnameTH",
                 "ผู้ประกอบการ","ประเภทการผลิต","วันที่อนุญาต","วันหมดอายุ","_สถานะ"]
    show_paginated(filtered, fda_badge, cols_show, "fda")


# ══════════════════════════════════════════════════════════════
#  DBD TAB
# ══════════════════════════════════════════════════════════════
def tab_dbd():
    st.markdown('<div style="font-size:20px;font-weight:800;color:#b34600;margin-bottom:2px">DBD — กรมพัฒนาธุรกิจการค้า (พค.)</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:13px;color:#444651;margin-bottom:16px">ข้อมูลนิติบุคคลจดทะเบียน</div>', unsafe_allow_html=True)
    df = load_dbd()

    total   = len(df)
    running = df["สถานะนิติบุคคล"].str.contains("ดำเนินกิจการ", na=False).sum()
    closed  = df["สถานะนิติบุคคล"].isin(["เลิก","เสร็จการชำระบัญชี"]).sum()
    other   = total - running - closed

    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(lt_card("ทั้งหมด",            total,   "นิติบุคคลในฐานข้อมูล"),           unsafe_allow_html=True)
    c2.markdown(lt_card("ดำเนินกิจการอยู่",   running, "✅ ยังเปิดดำเนินการ","green"),   unsafe_allow_html=True)
    c3.markdown(lt_card("เลิก / ชำระบัญชี",  closed,  "❌ ปิดกิจการแล้ว","red"),         unsafe_allow_html=True)
    c4.markdown(lt_card("สถานะอื่นๆ",         other,   "ร้าง / แปรสภาพ ฯลฯ","grey"),    unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    f1,f2,f3 = st.columns([2.5,1.5,1.5])
    with f1: q = st.text_input("🔍 ค้นหา (ชื่อบริษัท / เลขทะเบียน)", key="dbd_q", placeholder="พิมพ์คำค้นหา...")
    with f2:
        st_list = ["ทั้งหมด"] + sorted(df["สถานะนิติบุคคล"].unique().tolist())
        sel_st = st.selectbox("สถานะ", st_list, key="dbd_st")
    with f3:
        biz_list = ["ทั้งหมด"] + sorted(df["กลุ่มธุรกิจ"].replace("",pd.NA).dropna().unique().tolist())
        sel_biz = st.selectbox("กลุ่มธุรกิจ", biz_list, key="dbd_biz")

    filtered = df.copy()
    if q:
        mask = (filtered["Account"].str.contains(q, case=False, na=False) |
                filtered["เลขทะเบียนนิติบุคคล"].str.contains(q, case=False, na=False))
        filtered = filtered[mask]
    if sel_st  != "ทั้งหมด": filtered = filtered[filtered["สถานะนิติบุคคล"] == sel_st]
    if sel_biz != "ทั้งหมด": filtered = filtered[filtered["กลุ่มธุรกิจ"] == sel_biz]

    st.caption(f"พบ **{len(filtered):,}** รายการ")
    if filtered.empty: st.info("ไม่พบข้อมูล"); return

    cols_show = ["Account","เลขทะเบียนนิติบุคคล","ประเภทนิติบุคคล",
                 "วันที่จดทะเบียนจัดตั้ง","ทุนจดทะเบียน",
                 "กลุ่มธุรกิจ","ที่ตั้งสำนักงานแห่งใหญ่","สถานะนิติบุคคล"]
    show_paginated(filtered, dbd_badge, cols_show, "dbd")


# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════
def main():
    st.markdown("""
    <div style="margin-bottom:4px">
        <span style="font-size:10px;font-weight:700;text-transform:uppercase;
                     letter-spacing:.15em;color:#757682;">Home /</span>
        <span style="font-size:10px;font-weight:700;text-transform:uppercase;
                     letter-spacing:.15em;color:#d4a017;"> Visit Information</span>
        <div style="font-size:24px;font-weight:800;color:#0d1c2e;margin-top:2px;">FDA & DBD Information System</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    tab0, tab1, tab2 = st.tabs([
        "📊  Executive Dashboard",
        "🏥  FDA — อย.",
        "🏢  DBD — กรมพัฒนาธุรกิจการค้า",
    ])
    with tab0: tab_dashboard()
    with tab1: tab_fda()
    with tab2: tab_dbd()

if __name__ == "__main__":
    main()
