import streamlit as st
import pandas as pd
import os

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Visit Info — FDA & DBD",
    page_icon="🏛️",
    layout="wide",
)

BASE = os.path.dirname(__file__)
FDA_XLSX = os.path.join(BASE, "FDA.xlsx")
DBD_XLSX = os.path.join(BASE, "DBDALL.xlsx")

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Sarabun', sans-serif; }
#MainMenu, footer { visibility: hidden; }

.kpi-card {
    background:#fff; border-radius:12px; padding:18px 22px;
    box-shadow:0 1px 4px rgba(0,0,0,.08); border-left:4px solid #ccc;
    margin-bottom:4px;
}
.kpi-fda   { border-left-color:#00236f; }
.kpi-dbd   { border-left-color:#b34600; }
.kpi-green { border-left-color:#006d30; }
.kpi-red   { border-left-color:#dc2626; }
.kpi-grey  { border-left-color:#6b7280; }
.kpi-label { font-size:10px;font-weight:700;text-transform:uppercase;
             letter-spacing:.1em;color:#444651;margin-bottom:4px; }
.kpi-value { font-size:30px;font-weight:900;color:#0d1c2e;line-height:1; }
.kpi-sub   { font-size:11px;font-weight:600;margin-top:5px;color:#444651; }

.badge { display:inline-block;padding:2px 10px;border-radius:99px;
         font-size:11px;font-weight:700;letter-spacing:.04em; }
.b-active   { background:#d0f0d8;color:#005323; }
.b-expired  { background:#ffdad6;color:#93000a; }
.b-cancel   { background:#f3f4f6;color:#374151; }
.b-running  { background:#dce9ff;color:#00236f; }
.b-closed   { background:#ffdad6;color:#93000a; }
.b-other    { background:#fef3c7;color:#92400e; }

.dataframe { width:100%;border-collapse:collapse;font-size:13px; }
.dataframe th { background:#eff4ff;color:#444651;font-size:10px;font-weight:700;
                text-transform:uppercase;letter-spacing:.08em;padding:10px 14px;text-align:left; }
.dataframe td { padding:9px 14px;border-bottom:1px solid #e6eeff;vertical-align:top; }
.dataframe tr:hover td { background:#f5f8ff; }

div[data-testid="stTabs"] button { font-family:'Sarabun',sans-serif;font-weight:700;font-size:14px; }
</style>
""", unsafe_allow_html=True)


# ── Load helpers (cached) ─────────────────────────────────────
@st.cache_data(show_spinner="⏳ กำลังโหลดข้อมูล FDA.xlsx ...")
def load_fda():
    df = pd.read_excel(FDA_XLSX, dtype=str).fillna("")
    return df

@st.cache_data(show_spinner="⏳ กำลังโหลดข้อมูล DBDALL.xlsx ...")
def load_dbd():
    df = pd.read_excel(DBD_XLSX, dtype=str).fillna("")
    return df


# ── KPI card html ─────────────────────────────────────────────
def kpi(label, value, sub, cls):
    return f"""<div class="kpi-card {cls}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value:,}</div>
        <div class="kpi-sub">{sub}</div>
    </div>"""


# ── FDA status badge ──────────────────────────────────────────
def fda_badge(s):
    s = str(s)
    if s == "อนุมัติ": return f'<span class="badge b-active">อนุมัติ</span>'
    return                    f'<span class="badge b-cancel">ยกเลิก</span>'

# map raw status → 2 buckets
def fda_status_bucket(s):
    return "อนุมัติ" if str(s) == "อนุมัติ" else "ยกเลิก"

# ── DBD status badge ──────────────────────────────────────────
def dbd_badge(s):
    s = str(s)
    if "ดำเนินกิจการ" in s:   return f'<span class="badge b-running">{s}</span>'
    if s in ("เลิก","เสร็จการชำระบัญชี"): return f'<span class="badge b-closed">{s}</span>'
    return                            f'<span class="badge b-other">{s}</span>'


# ── Paginated table renderer ───────────────────────────────────
def show_paginated(df_show: pd.DataFrame, badge_fn, cols_display: list, key: str, page_size=100):
    total = len(df_show)
    pages = max(1, -(-total // page_size))  # ceil division
    page  = st.number_input(f"หน้า (จาก {pages} หน้า — {total:,} รายการ)",
                            min_value=1, max_value=pages, value=1, step=1, key=f"page_{key}")
    start = (page - 1) * page_size
    chunk = df_show.iloc[start:start + page_size][cols_display].copy()

    # apply badge to last col (status)
    status_col = cols_display[-1]
    chunk[status_col] = chunk[status_col].apply(badge_fn)

    html = chunk.to_html(escape=False, index=False, border=0, classes="dataframe")
    st.write(html, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  FDA TAB
# ══════════════════════════════════════════════════════════════
def tab_fda():
    st.markdown('<div style="font-size:20px;font-weight:800;color:#00236f;margin-bottom:2px">FDA — สำนักงานคณะกรรมการอาหารและยา (อย.)</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:13px;color:#444651;margin-bottom:16px">ข้อมูลผลิตภัณฑ์จดแจ้ง / ทะเบียนเครื่องสำอางและผลิตภัณฑ์</div>', unsafe_allow_html=True)

    df = load_fda()

    # ── add bucket column ──
    df = df.copy()
    df["_สถานะ"] = df["สถานะสินค้า"].apply(fda_status_bucket)

    # ── KPIs ──
    total    = len(df)
    approved = (df["_สถานะ"] == "อนุมัติ").sum()
    cancelled= total - approved

    c1, c2, c3 = st.columns(3)
    c1.markdown(kpi("ทั้งหมด",  total,     "รายการในฐานข้อมูล",    "kpi-fda"),   unsafe_allow_html=True)
    c2.markdown(kpi("อนุมัติ",  approved,  "✅ สินค้าที่อนุมัติแล้ว","kpi-green"), unsafe_allow_html=True)
    c3.markdown(kpi("ยกเลิก",   cancelled, "❌ สิ้นอายุ / ยกเลิก",  "kpi-red"),   unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Filters ──
    f1, f2, f3, f4 = st.columns([2.5, 1.2, 1.5, 1.5])
    with f1:
        q = st.text_input(
            "🔍 ค้นหา (เลขจดแจ้ง / แบรนด์ TH-EN / ชื่อสินค้า TH-EN / ผู้ประกอบการ)",
            key="fda_q", placeholder="พิมพ์คำค้นหา...")
    with f2:
        sel_status = st.selectbox("สถานะสินค้า", ["ทั้งหมด", "อนุมัติ", "ยกเลิก"], key="fda_status")
    with f3:
        prod_list = ["ทั้งหมด"] + sorted(df["ประเภทการผลิต"].unique().tolist())
        sel_prod = st.selectbox("ประเภทการผลิต", prod_list, key="fda_prod")
    with f4:
        year_list = ["ทั้งหมด"] + sorted(df["ปีจดแจ้ง"].replace("", pd.NA).dropna().unique().tolist(), reverse=True)
        sel_year = st.selectbox("ปีจดแจ้ง", year_list, key="fda_year")

    # ── Apply filters ──
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
    if sel_status != "ทั้งหมด":
        filtered = filtered[filtered["_สถานะ"] == sel_status]
    if sel_prod != "ทั้งหมด":
        filtered = filtered[filtered["ประเภทการผลิต"] == sel_prod]
    if sel_year != "ทั้งหมด":
        filtered = filtered[filtered["ปีจดแจ้ง"] == sel_year]

    st.caption(f"พบ **{len(filtered):,}** รายการ")

    if filtered.empty:
        st.info("ไม่พบข้อมูลที่ตรงกัน")
        return

    cols_show = ["เลขจดแจ้ง", "BrandsTH", "BrandsENG", "ProductnameTH",
                 "ผู้ประกอบการ", "ประเภทการผลิต", "วันที่อนุญาต", "วันหมดอายุ", "_สถานะ"]
    show_paginated(filtered, fda_badge, cols_show, "fda")


# ══════════════════════════════════════════════════════════════
#  DBD TAB
# ══════════════════════════════════════════════════════════════
def tab_dbd():
    st.markdown('<div style="font-size:20px;font-weight:800;color:#b34600;margin-bottom:2px">DBD — กรมพัฒนาธุรกิจการค้า (พค.)</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:13px;color:#444651;margin-bottom:16px">ข้อมูลนิติบุคคลจดทะเบียน</div>', unsafe_allow_html=True)

    df = load_dbd()

    # ── KPIs ──
    total   = len(df)
    running = df["สถานะนิติบุคคล"].str.contains("ดำเนินกิจการ", na=False).sum()
    closed  = df["สถานะนิติบุคคล"].isin(["เลิก", "เสร็จการชำระบัญชี"]).sum()
    other   = total - running - closed

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("ทั้งหมด",            total,   "นิติบุคคลในฐานข้อมูล", "kpi-dbd"),   unsafe_allow_html=True)
    c2.markdown(kpi("ดำเนินกิจการอยู่",   running, "✅ ยังเปิดดำเนินการ",    "kpi-green"), unsafe_allow_html=True)
    c3.markdown(kpi("เลิก/ชำระบัญชี",     closed,  "❌ ปิดกิจการแล้ว",       "kpi-red"),   unsafe_allow_html=True)
    c4.markdown(kpi("สถานะอื่นๆ",         other,   "ร้าง / แปรสภาพ ฯลฯ",    "kpi-grey"),  unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Filters ──
    f1, f2, f3 = st.columns([2.5, 1.5, 1.5])
    with f1:
        q = st.text_input("🔍 ค้นหา (ชื่อบริษัท / เลขทะเบียน)",
                          key="dbd_q", placeholder="พิมพ์คำค้นหา...")
    with f2:
        status_list = ["ทั้งหมด"] + sorted(df["สถานะนิติบุคคล"].unique().tolist())
        sel_status = st.selectbox("สถานะ", status_list, key="dbd_status")
    with f3:
        biz_list = ["ทั้งหมด"] + sorted(df["กลุ่มธุรกิจ"].replace("", pd.NA).dropna().unique().tolist())
        sel_biz = st.selectbox("กลุ่มธุรกิจ", biz_list, key="dbd_biz")

    # ── Apply filters ──
    filtered = df.copy()
    if q:
        mask = (
            filtered["Account"].str.contains(q, case=False, na=False) |
            filtered["เลขทะเบียนนิติบุคคล"].str.contains(q, case=False, na=False)
        )
        filtered = filtered[mask]
    if sel_status != "ทั้งหมด":
        filtered = filtered[filtered["สถานะนิติบุคคล"] == sel_status]
    if sel_biz != "ทั้งหมด":
        filtered = filtered[filtered["กลุ่มธุรกิจ"] == sel_biz]

    st.caption(f"พบ **{len(filtered):,}** รายการ")

    if filtered.empty:
        st.info("ไม่พบข้อมูลที่ตรงกัน")
        return

    cols_show = ["Account", "เลขทะเบียนนิติบุคคล", "ประเภทนิติบุคคล",
                 "วันที่จดทะเบียนจัดตั้ง", "ทุนจดทะเบียน",
                 "กลุ่มธุรกิจ", "ที่ตั้งสำนักงานแห่งใหญ่", "สถานะนิติบุคคล"]
    show_paginated(filtered, dbd_badge, cols_show, "dbd")


# ══════════════════════════════════════════════════════════════
#  DASHBOARD TAB
# ══════════════════════════════════════════════════════════════
def tab_dashboard():
    st.markdown('<div style="font-size:20px;font-weight:800;color:#0d1c2e;margin-bottom:2px">Dashboard — ภาพรวม FDA & DBD</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:13px;color:#444651;margin-bottom:16px">สรุปข้อมูลรวมจากฐานข้อมูล FDA.xlsx และ DBDALL.xlsx</div>', unsafe_allow_html=True)

    fda = load_fda()
    dbd = load_dbd()

    fda["_สถานะ"] = fda["สถานะสินค้า"].apply(fda_status_bucket)

    # ── Summary KPIs row ──
    fda_total    = len(fda)
    fda_approved = (fda["_สถานะ"] == "อนุมัติ").sum()
    fda_cancel   = fda_total - fda_approved
    dbd_total    = len(dbd)
    dbd_running  = dbd["สถานะนิติบุคคล"].str.contains("ดำเนินกิจการ", na=False).sum()
    dbd_closed   = dbd["สถานะนิติบุคคล"].isin(["เลิก", "เสร็จการชำระบัญชี"]).sum()

    st.markdown("#### 🏥 FDA — สำนักงานคณะกรรมการอาหารและยา")
    c1, c2, c3 = st.columns(3)
    c1.markdown(kpi("ผลิตภัณฑ์ทั้งหมด", fda_total,    "รายการใน FDA.xlsx",     "kpi-fda"),   unsafe_allow_html=True)
    c2.markdown(kpi("อนุมัติ",           fda_approved, "✅ ได้รับการอนุมัติ",    "kpi-green"), unsafe_allow_html=True)
    c3.markdown(kpi("ยกเลิก / สิ้นอายุ", fda_cancel,   "❌ หมดอายุหรือยกเลิก",  "kpi-red"),   unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🏢 DBD — กรมพัฒนาธุรกิจการค้า")
    c4, c5, c6 = st.columns(3)
    c4.markdown(kpi("นิติบุคคลทั้งหมด",   dbd_total,   "รายการใน DBDALL.xlsx",  "kpi-dbd"),   unsafe_allow_html=True)
    c5.markdown(kpi("ดำเนินกิจการอยู่",   dbd_running, "✅ ยังเปิดดำเนินการ",    "kpi-green"), unsafe_allow_html=True)
    c6.markdown(kpi("เลิก / ชำระบัญชี",   dbd_closed,  "❌ ปิดกิจการแล้ว",       "kpi-red"),   unsafe_allow_html=True)

    st.divider()

    # ── Charts row ──
    ch1, ch2 = st.columns(2)

    with ch1:
        st.markdown("**สัดส่วนสถานะผลิตภัณฑ์ FDA**")
        fda_status_counts = fda["_สถานะ"].value_counts().reset_index()
        fda_status_counts.columns = ["สถานะ", "จำนวน"]
        st.bar_chart(fda_status_counts.set_index("สถานะ"), color="#00236f", height=280)

    with ch2:
        st.markdown("**สัดส่วนสถานะนิติบุคคล DBD**")
        dbd_status_counts = dbd["สถานะนิติบุคคล"].value_counts().reset_index()
        dbd_status_counts.columns = ["สถานะ", "จำนวน"]
        st.bar_chart(dbd_status_counts.set_index("สถานะ"), color="#b34600", height=280)

    st.markdown("<br>", unsafe_allow_html=True)

    ch3, ch4 = st.columns(2)

    with ch3:
        st.markdown("**ประเภทการผลิต FDA (Top 5)**")
        top_prod = fda["ประเภทการผลิต"].replace("", pd.NA).dropna().value_counts().head(5).reset_index()
        top_prod.columns = ["ประเภท", "จำนวน"]
        st.bar_chart(top_prod.set_index("ประเภท"), color="#264191", height=280)

    with ch4:
        st.markdown("**กลุ่มธุรกิจ DBD (Top 5)**")
        top_biz = dbd["กลุ่มธุรกิจ"].replace("", pd.NA).dropna().value_counts().head(5).reset_index()
        top_biz.columns = ["กลุ่ม", "จำนวน"]
        st.bar_chart(top_biz.set_index("กลุ่ม"), color="#b34600", height=280)


# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════
def main():
    st.markdown("""
    <div style="margin-bottom:8px">
        <div style="font-size:10px;font-weight:700;text-transform:uppercase;
                    letter-spacing:.15em;color:#757682;margin-bottom:4px">
            Home / ข้อมูลการเข้าพบ
        </div>
        <div style="font-size:26px;font-weight:800;color:#0d1c2e;line-height:1.1">
            Visit Information — FDA & DBD
        </div>
        <div style="font-size:13px;color:#444651;margin-top:6px">
            ข้อมูลจากฐานข้อมูล FDA.xlsx และ DBDALL.xlsx
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    tab0, tab1, tab2 = st.tabs([
        "📊  Dashboard — ภาพรวม",
        "🏥  FDA — อย. (เครื่องสำอาง/ผลิตภัณฑ์)",
        "🏢  DBD — กรมพัฒนาธุรกิจการค้า",
    ])
    with tab0:
        tab_dashboard()
    with tab1:
        tab_fda()
    with tab2:
        tab_dbd()


if __name__ == "__main__":
    main()
