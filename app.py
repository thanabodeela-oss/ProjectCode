import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Visit Info — FDA & DBD",
    page_icon="🏛️",
    layout="wide",
)

# ── Paths ─────────────────────────────────────────────────────
DATA_DIR   = os.path.join(os.path.dirname(__file__), "data")
FDA_CSV    = os.path.join(DATA_DIR, "fda_visits.csv")
DBD_CSV    = os.path.join(DATA_DIR, "dbd_visits.csv")
COLS       = ["date", "purpose", "officer", "division", "docs", "status", "notes"]

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Sarabun', sans-serif; }

/* hide streamlit default top menu & footer */
#MainMenu, footer { visibility: hidden; }

/* ── KPI cards ── */
.kpi-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 20px 24px;
    box-shadow: 0 1px 4px rgba(0,0,0,.08);
    border-left: 4px solid #ccc;
}
.kpi-fda  { border-left-color: #00236f; }
.kpi-dbd  { border-left-color: #b34600; }
.kpi-green{ border-left-color: #006d30; }
.kpi-yellow{ border-left-color: #ca8a04; }
.kpi-red  { border-left-color: #dc2626; }

.kpi-label { font-size:10px; font-weight:700; text-transform:uppercase;
             letter-spacing:.1em; color:#444651; margin-bottom:4px; }
.kpi-value { font-size:32px; font-weight:900; color:#0d1c2e; line-height:1; }
.kpi-sub   { font-size:11px; font-weight:600; margin-top:6px; }

/* ── Status badges ── */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 99px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .05em;
}
.badge-completed  { background:#d0f0d8; color:#005323; }
.badge-pending    { background:#dce1ff; color:#264191; }
.badge-upcoming   { background:#fef3c7; color:#92400e; }
.badge-cancelled  { background:#ffdad6; color:#93000a; }

/* ── Section header ── */
.section-header {
    font-size: 20px;
    font-weight: 800;
    margin-bottom: 4px;
}
.section-sub { font-size: 13px; color: #444651; margin-bottom: 20px; }

/* ── Tab style override ── */
div[data-testid="stTabs"] button {
    font-family: 'Sarabun', sans-serif;
    font-weight: 700;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)


# ── Data helpers ──────────────────────────────────────────────
def load(path: str) -> pd.DataFrame:
    if os.path.exists(path):
        df = pd.read_csv(path, dtype=str).fillna("")
    else:
        df = pd.DataFrame(columns=COLS)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df


def save_df(df: pd.DataFrame, path: str):
    os.makedirs(DATA_DIR, exist_ok=True)
    df_save = df.copy()
    df_save["date"] = df_save["date"].dt.strftime("%Y-%m-%d")
    df_save.to_csv(path, index=False, encoding="utf-8-sig")


def status_badge(status: str) -> str:
    cls = {
        "Completed": "badge-completed",
        "Pending":   "badge-pending",
        "Upcoming":  "badge-upcoming",
        "Cancelled": "badge-cancelled",
    }.get(status, "badge-pending")
    return f'<span class="badge {cls}">{status}</span>'


def kpi_card(label: str, value: int, sub: str, color_cls: str) -> str:
    return f"""
    <div class="kpi-card {color_cls}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>"""


# ── KPI section ───────────────────────────────────────────────
def show_kpis(df: pd.DataFrame, color: str):
    today = pd.Timestamp(date.today())
    in30  = today + timedelta(days=30)
    total    = len(df)
    done     = (df["status"] == "Completed").sum()
    pending  = (df["status"] == "Pending").sum()
    upcoming = ((df["status"] == "Upcoming") & (df["date"] >= today) & (df["date"] <= in30)).sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi_card("Total Visits",    total,    f"{'FDA (อย.)' if color=='fda' else 'DBD (พค.)'}", f"kpi-{color}"), unsafe_allow_html=True)
    c2.markdown(kpi_card("Completed",       done,     "✅ เสร็จสิ้น",         "kpi-green"),  unsafe_allow_html=True)
    c3.markdown(kpi_card("Pending",         pending,  "⏳ รออนุมัติ",          "kpi-yellow"), unsafe_allow_html=True)
    c4.markdown(kpi_card("Upcoming (30d)",  upcoming, "📅 นัดหมายที่กำลังมาถึง","kpi-red"),    unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


# ── Table section ─────────────────────────────────────────────
def show_table(df: pd.DataFrame, key: str):
    col_search, col_filter, _ = st.columns([2, 1.5, 4])
    with col_search:
        q = st.text_input("🔍 ค้นหา", key=f"search_{key}", placeholder="พิมพ์คำค้นหา...")
    with col_filter:
        status_opts = ["ทั้งหมด", "Completed", "Pending", "Upcoming", "Cancelled"]
        sel = st.selectbox("สถานะ", status_opts, key=f"filter_{key}")

    filtered = df.copy()
    if q:
        mask = filtered.apply(lambda r: q.lower() in " ".join(r.astype(str)).lower(), axis=1)
        filtered = filtered[mask]
    if sel != "ทั้งหมด":
        filtered = filtered[filtered["status"] == sel]

    if filtered.empty:
        st.info("ไม่พบข้อมูล")
        return

    display = filtered.copy()
    display["date"] = display["date"].dt.strftime("%d %b %Y")
    display["สถานะ"] = display["status"].apply(status_badge)
    display = display.rename(columns={
        "date":     "วันที่",
        "purpose":  "หัวข้อ / Purpose",
        "officer":  "เจ้าหน้าที่",
        "division": "กอง / Division",
        "docs":     "เอกสาร",
        "notes":    "หมายเหตุ",
    })
    display = display[["วันที่", "หัวข้อ / Purpose", "เจ้าหน้าที่", "กอง / Division", "เอกสาร", "สถานะ", "หมายเหตุ"]]

    st.write(display.to_html(escape=False, index=False, border=0,
        classes="dataframe"), unsafe_allow_html=True)

    st.markdown("""
    <style>
    .dataframe { width:100%; border-collapse:collapse; font-size:13px; }
    .dataframe th { background:#eff4ff; color:#444651; font-size:10px; font-weight:700;
                    text-transform:uppercase; letter-spacing:.08em; padding:10px 14px; text-align:left; }
    .dataframe td { padding:10px 14px; border-bottom:1px solid #e6eeff; vertical-align:top; }
    .dataframe tr:hover td { background:#f5f8ff; }
    </style>""", unsafe_allow_html=True)


# ── Add / Edit form ───────────────────────────────────────────
def visit_form(df: pd.DataFrame, path: str, key: str, accent: str):
    with st.expander("➕ เพิ่ม / แก้ไข ข้อมูลการเข้าพบ", expanded=False):
        # pick row to edit
        labels = ["— เพิ่มใหม่ —"] + [
            f"{i+1}. {row['purpose']} ({row['date'].strftime('%d/%m/%y') if pd.notna(row['date']) else '-'})"
            for i, row in df.iterrows()
        ]
        chosen = st.selectbox("เลือกรายการที่ต้องการแก้ไข (หรือเพิ่มใหม่)", labels, key=f"edit_sel_{key}")
        idx = labels.index(chosen) - 1  # -1 = new

        prefill = df.iloc[idx] if idx >= 0 else None

        c1, c2 = st.columns(2)
        with c1:
            f_date = st.date_input("วันที่เข้าพบ *",
                value=prefill["date"].date() if prefill is not None and pd.notna(prefill["date"]) else date.today(),
                key=f"f_date_{key}")
        with c2:
            statuses = ["Upcoming", "Pending", "Completed", "Cancelled"]
            f_status = st.selectbox("สถานะ *", statuses,
                index=statuses.index(prefill["status"]) if prefill is not None and prefill["status"] in statuses else 0,
                key=f"f_status_{key}")

        f_purpose = st.text_input("หัวข้อ / Purpose *",
            value=prefill["purpose"] if prefill is not None else "",
            key=f"f_purpose_{key}")

        c3, c4 = st.columns(2)
        with c3:
            f_officer = st.text_input("เจ้าหน้าที่",
                value=prefill["officer"] if prefill is not None else "",
                key=f"f_officer_{key}")
        with c4:
            f_division = st.text_input("กอง / Division",
                value=prefill["division"] if prefill is not None else "",
                key=f"f_div_{key}")

        f_docs = st.text_input("เอกสาร",
            value=prefill["docs"] if prefill is not None else "",
            key=f"f_docs_{key}")
        f_notes = st.text_area("หมายเหตุ",
            value=prefill["notes"] if prefill is not None else "",
            key=f"f_notes_{key}", height=80)

        col_save, col_del = st.columns([1, 1])
        with col_save:
            if st.button("💾 บันทึก", key=f"save_{key}", type="primary", use_container_width=True):
                if not f_purpose.strip():
                    st.error("กรุณากรอกหัวข้อ")
                else:
                    new_row = {
                        "date":     pd.Timestamp(f_date),
                        "purpose":  f_purpose.strip(),
                        "officer":  f_officer.strip(),
                        "division": f_division.strip(),
                        "docs":     f_docs.strip(),
                        "status":   f_status,
                        "notes":    f_notes.strip(),
                    }
                    if idx >= 0:
                        for col, val in new_row.items():
                            df.at[idx, col] = val
                    else:
                        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    save_df(df, path)
                    st.success("✅ บันทึกเรียบร้อย")
                    st.rerun()

        with col_del:
            if idx >= 0:
                if st.button("🗑️ ลบรายการนี้", key=f"del_{key}", use_container_width=True):
                    df = df.drop(index=idx).reset_index(drop=True)
                    save_df(df, path)
                    st.success("ลบเรียบร้อย")
                    st.rerun()

    return df


# ── Main App ──────────────────────────────────────────────────
def main():
    # Header
    st.markdown("""
    <div style="margin-bottom:8px">
        <div style="font-size:11px;font-weight:700;text-transform:uppercase;
                    letter-spacing:.15em;color:#757682;margin-bottom:4px">
            Home / Visit Information
        </div>
        <div style="font-size:28px;font-weight:800;color:#0d1c2e;line-height:1">
            Visit Information
        </div>
        <div style="font-size:13px;color:#444651;margin-top:6px">
            ติดตามการเข้าพบ อย. และ DBD — FDA & Department of Business Development
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Load data
    fda_df = load(FDA_CSV)
    dbd_df = load(DBD_CSV)

    # Tabs
    tab_fda, tab_dbd = st.tabs(["🏥  FDA — สำนักงานคณะกรรมการอาหารและยา", "🏢  DBD — กรมพัฒนาธุรกิจการค้า"])

    # ── FDA ──
    with tab_fda:
        st.markdown('<div class="section-header" style="color:#00236f">FDA Visits</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">ประวัติการเข้าพบสำนักงานคณะกรรมการอาหารและยา (อย.)</div>', unsafe_allow_html=True)
        show_kpis(fda_df, "fda")
        show_table(fda_df, "fda")
        st.markdown("<br>", unsafe_allow_html=True)
        fda_df = visit_form(fda_df, FDA_CSV, "fda", "#00236f")

    # ── DBD ──
    with tab_dbd:
        st.markdown('<div class="section-header" style="color:#b34600">DBD Visits</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">ประวัติการเข้าพบกรมพัฒนาธุรกิจการค้า (พค.)</div>', unsafe_allow_html=True)
        show_kpis(dbd_df, "dbd")
        show_table(dbd_df, "dbd")
        st.markdown("<br>", unsafe_allow_html=True)
        dbd_df = visit_form(dbd_df, DBD_CSV, "dbd", "#b34600")


if __name__ == "__main__":
    main()
