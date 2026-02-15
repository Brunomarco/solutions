import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import io
import re
import warnings
warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Marken Solutions Pipeline",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# MARKEN DESIGN SYSTEM
# ──────────────────────────────────────────────────────────────────────────────
MARKEN = {
    "navy":       "#003B5C",
    "dark_navy":  "#00263A",
    "teal":       "#0091DA",
    "teal_light": "#5CB8B2",
    "pale_teal":  "#A7D6D4",
    "bg_light":   "#E8F4F8",
    "gold":       "#D4A843",
    "green":      "#2E8B57",
    "red":        "#C0392B",
    "orange":     "#E67E22",
    "white":      "#FFFFFF",
    "gray_50":    "#FAFBFD",
    "gray_100":   "#F0F4F8",
    "gray_200":   "#E2E8F0",
    "gray_400":   "#94A3B8",
    "gray_600":   "#64748B",
    "gray_800":   "#1E293B",
    "text":       "#1A2332",
}

PALETTE_SEQ = [
    MARKEN["navy"], MARKEN["teal"], MARKEN["teal_light"],
    MARKEN["gold"], MARKEN["green"], MARKEN["orange"],
    MARKEN["pale_teal"], MARKEN["red"], MARKEN["gray_600"],
]

# ──────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;600;700&display=swap');

    /* ── Global ─────────────────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'Source Sans Pro', 'Segoe UI', 'Helvetica Neue', sans-serif;
        color: #1A2332;
    }
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; max-width: 1280px; }
    h1, h2, h3, h4, h5, h6 { font-family: 'Source Sans Pro', sans-serif; }

    /* ── Sidebar ────────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #00263A 0%, #003B5C 100%);
    }
    [data-testid="stSidebar"] * {
        color: #E8F4F8 !important;
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stSlider label,
    [data-testid="stSidebar"] .stDateInput label {
        color: #A7D6D4 !important;
        font-weight: 600;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* ── KPI Cards ──────────────────────────────────────────── */
    .kpi-card {
        background: linear-gradient(135deg, #003B5C 0%, #00263A 100%);
        border-radius: 10px;
        padding: 1.25rem 1.5rem;
        color: white;
        position: relative;
        overflow: hidden;
        min-height: 120px;
    }
    .kpi-card::after {
        content: '';
        position: absolute;
        top: -30px; right: -30px;
        width: 100px; height: 100px;
        background: rgba(0,145,218,0.12);
        border-radius: 50%;
    }
    .kpi-label {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #A7D6D4;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: white;
        line-height: 1.1;
        margin-bottom: 4px;
    }
    .kpi-sub {
        font-size: 0.75rem;
        color: #5CB8B2;
        font-weight: 400;
    }

    /* ── Accent KPI ─────────────────────────────────────────── */
    .kpi-accent {
        background: linear-gradient(135deg, #0091DA 0%, #003B5C 100%);
    }

    /* ── Section Headers ────────────────────────────────────── */
    .section-header {
        border-left: 4px solid #0091DA;
        padding-left: 14px;
        margin: 2.5rem 0 1rem 0;
    }
    .section-header h2 {
        font-size: 1.3rem;
        font-weight: 700;
        color: #003B5C;
        margin: 0;
        line-height: 1.2;
    }
    .section-header p {
        font-size: 0.82rem;
        color: #64748B;
        margin: 3px 0 0 0;
    }

    /* ── Insight Box ─────────────────────────────────────────── */
    .insight-box {
        background: #E8F4F8;
        border-left: 3px solid #0091DA;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin: 10px 0;
        font-size: 0.85rem;
        color: #003B5C;
        line-height: 1.5;
    }
    .insight-box strong { color: #00263A; }

    /* ── Status Badges ──────────────────────────────────────── */
    .status-working {
        background: #E8F4F8; color: #0091DA;
        padding: 3px 10px; border-radius: 12px;
        font-size: 0.75rem; font-weight: 600;
        display: inline-block;
    }
    .status-pending {
        background: #FDF2E0; color: #D4A843;
        padding: 3px 10px; border-radius: 12px;
        font-size: 0.75rem; font-weight: 600;
        display: inline-block;
    }
    .status-unassigned {
        background: #F0F4F8; color: #94A3B8;
        padding: 3px 10px; border-radius: 12px;
        font-size: 0.75rem; font-weight: 600;
        display: inline-block;
    }

    /* ── Header Bar ──────────────────────────────────────────── */
    .header-bar {
        background: linear-gradient(135deg, #003B5C 0%, #00263A 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }
    .header-bar::before {
        content: '';
        position: absolute;
        top: 0; right: 0;
        width: 300px; height: 100%;
        background: linear-gradient(135deg, transparent 0%, rgba(0,145,218,0.08) 100%);
    }
    .header-bar h1 {
        color: white;
        font-size: 1.6rem;
        font-weight: 700;
        margin: 0 0 2px 0;
        letter-spacing: -0.01em;
    }
    .header-bar .subtitle {
        color: #A7D6D4;
        font-size: 0.85rem;
        font-weight: 400;
    }
    .header-bar .marken-label {
        color: #5CB8B2;
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-weight: 600;
        margin-bottom: 4px;
    }

    /* ── Table styling ───────────────────────────────────────── */
    .stDataFrame { border-radius: 8px; overflow: hidden; }

    /* ── Tab styling ─────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] { gap: 0; }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }

    /* ── Divider ─────────────────────────────────────────────── */
    .subtle-divider {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #E2E8F0, transparent);
        margin: 2rem 0;
    }

    /* ── Hide Streamlit branding ─────────────────────────────── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────
def parse_par(value):
    """Parse Opportunity PAR values that can be int, float, or 'USD X,XXX' strings."""
    if pd.isna(value):
        return np.nan
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    s = re.sub(r'[^\d.]', '', s.replace(',', ''))
    try:
        return float(s)
    except ValueError:
        return np.nan


def parse_mixed_date(value):
    """Parse dates from mixed formats (datetime objects and various string formats)."""
    if pd.isna(value):
        return pd.NaT
    if isinstance(value, datetime):
        return value
    s = str(value).strip()
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%m/%d/%y', '%d/%m/%y'):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    try:
        return pd.to_datetime(s, dayfirst=True)
    except Exception:
        return pd.NaT


def fmt_currency(val, prefix="$"):
    """Format number as currency."""
    if pd.isna(val):
        return "—"
    if val >= 1_000_000:
        return f"{prefix}{val/1_000_000:,.1f}M"
    if val >= 1_000:
        return f"{prefix}{val/1_000:,.0f}K"
    return f"{prefix}{val:,.0f}"


def fmt_number(val):
    if pd.isna(val):
        return "—"
    return f"{val:,.0f}"


def section_header(title, subtitle=""):
    st.markdown(f"""
    <div class="section-header">
        <h2>{title}</h2>
        {"<p>" + subtitle + "</p>" if subtitle else ""}
    </div>
    """, unsafe_allow_html=True)


def insight(text):
    st.markdown(f'<div class="insight-box">{text}</div>', unsafe_allow_html=True)


def kpi_card(label, value, sub="", accent=False):
    cls = "kpi-card kpi-accent" if accent else "kpi-card"
    return f"""
    <div class="{cls}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>
    """


def plotly_layout(fig, height=400, margin=None):
    """Apply consistent Marken styling to all Plotly figures."""
    if margin is None:
        margin = dict(l=40, r=20, t=50, b=40)
    fig.update_layout(
        height=height,
        margin=margin,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Source Sans Pro, Segoe UI, sans-serif", color=MARKEN["text"], size=12),
        title_font=dict(size=15, color=MARKEN["navy"], family="Source Sans Pro, sans-serif"),
        legend=dict(
            font=dict(size=11),
            bgcolor="rgba(255,255,255,0.7)",
            bordercolor=MARKEN["gray_200"],
            borderwidth=1,
        ),
        hoverlabel=dict(
            bgcolor=MARKEN["navy"],
            font_size=12,
            font_color="white",
            font_family="Source Sans Pro, sans-serif",
        ),
    )
    fig.update_xaxes(
        gridcolor=MARKEN["gray_200"], gridwidth=0.5,
        linecolor=MARKEN["gray_200"], zeroline=False,
        tickfont=dict(size=11, color=MARKEN["gray_600"]),
    )
    fig.update_yaxes(
        gridcolor=MARKEN["gray_200"], gridwidth=0.5,
        linecolor=MARKEN["gray_200"], zeroline=False,
        tickfont=dict(size=11, color=MARKEN["gray_600"]),
    )
    return fig


# ──────────────────────────────────────────────────────────────────────────────
# DATA LOADING & CLEANING
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_and_clean(file):
    df = pd.read_excel(file)
    # Strip whitespace from column names
    df.columns = [c.strip() for c in df.columns]

    # Parse PAR
    if "Opportunity PAR" in df.columns:
        df["PAR_clean"] = df["Opportunity PAR"].apply(parse_par)

    # Parse dates
    for dcol in ["Close Date", "Received by Solutions", "Closed by Solutions"]:
        if dcol in df.columns:
            df[dcol + "_dt"] = df[dcol].apply(parse_mixed_date)

    # Stage Duration as numeric
    if "Stage Duration" in df.columns:
        df["Stage Duration"] = pd.to_numeric(df["Stage Duration"], errors="coerce")

    # Fill status for display
    if "Status" in df.columns:
        df["Status_display"] = df["Status"].fillna("Not Assigned")

    # Fill Product for display
    if "Product" in df.columns:
        df["Product_display"] = df["Product"].fillna("Not Specified")

    return df


# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────
def render_sidebar(df):
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding: 0.8rem 0 1.2rem 0;">
            <div style="font-size:1.4rem; font-weight:700; color:white; letter-spacing:0.15em;">MARKEN</div>
            <div style="font-size:0.65rem; color:#5CB8B2; text-transform:uppercase; letter-spacing:0.1em; margin-top:2px;">
                A UPS Healthcare Company
            </div>
        </div>
        <hr style="border:none; height:1px; background:rgba(255,255,255,0.15); margin:0 0 1rem 0;">
        """, unsafe_allow_html=True)

        st.markdown('<p style="font-size:0.72rem; color:#A7D6D4; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:8px;">Global Filters</p>', unsafe_allow_html=True)

        filters = {}

        # Region
        if "Owner Role" in df.columns:
            opts = sorted(df["Owner Role"].dropna().unique())
            filters["region"] = st.multiselect("Region", opts, default=opts, key="f_region")

        # Solution Resource
        if "Solution Resource" in df.columns:
            opts = sorted(df["Solution Resource"].dropna().unique())
            filters["resource"] = st.multiselect("Solution Resource", opts, default=opts, key="f_resource")

        # Service
        if "Main Primary Service" in df.columns:
            opts = sorted(df["Main Primary Service"].dropna().unique())
            filters["service"] = st.multiselect("Primary Service", opts, default=opts, key="f_service")

        # Status
        if "Status_display" in df.columns:
            opts = sorted(df["Status_display"].unique())
            filters["status"] = st.multiselect("Status", opts, default=opts, key="f_status")

        # Product
        if "Product_display" in df.columns:
            opts = sorted(df["Product_display"].unique())
            filters["product"] = st.multiselect("Product", opts, default=opts, key="f_product")

        # Opportunity Owner
        if "Opportunity Owner" in df.columns:
            opts = sorted(df["Opportunity Owner"].dropna().unique())
            filters["owner"] = st.multiselect("Opportunity Owner", opts, default=opts, key="f_owner")

        # PAR Range
        if "PAR_clean" in df.columns:
            par_min = float(df["PAR_clean"].min()) if not df["PAR_clean"].isna().all() else 0
            par_max = float(df["PAR_clean"].max()) if not df["PAR_clean"].isna().all() else 1000000
            if par_min < par_max:
                filters["par_range"] = st.slider(
                    "Pipeline Value Range (USD)",
                    min_value=par_min, max_value=par_max,
                    value=(par_min, par_max),
                    format="$%,.0f",
                    key="f_par",
                )

        st.markdown("<hr style='border:none; height:1px; background:rgba(255,255,255,0.15); margin:1rem 0;'>", unsafe_allow_html=True)

        if st.button("↻  Reset All Filters", use_container_width=True):
            st.rerun()

        st.markdown("""
        <div style="position:fixed; bottom:16px; left:16px; font-size:0.62rem; color:rgba(255,255,255,0.35);">
            Solutions Pipeline Dashboard v1.0
        </div>
        """, unsafe_allow_html=True)

    return filters


def apply_filters(df, filters):
    mask = pd.Series(True, index=df.index)
    if "region" in filters and "Owner Role" in df.columns:
        mask &= df["Owner Role"].isin(filters["region"])
    if "resource" in filters and "Solution Resource" in df.columns:
        mask &= df["Solution Resource"].isin(filters["resource"])
    if "service" in filters and "Main Primary Service" in df.columns:
        mask &= df["Main Primary Service"].fillna("Unknown").isin(filters["service"])
    if "status" in filters and "Status_display" in df.columns:
        mask &= df["Status_display"].isin(filters["status"])
    if "product" in filters and "Product_display" in df.columns:
        mask &= df["Product_display"].isin(filters["product"])
    if "owner" in filters and "Opportunity Owner" in df.columns:
        mask &= df["Opportunity Owner"].isin(filters["owner"])
    if "par_range" in filters and "PAR_clean" in df.columns:
        lo, hi = filters["par_range"]
        mask &= (df["PAR_clean"].fillna(0) >= lo) & (df["PAR_clean"].fillna(0) <= hi)
    return df[mask].copy()


# ──────────────────────────────────────────────────────────────────────────────
# MAIN DASHBOARD SECTIONS
# ──────────────────────────────────────────────────────────────────────────────
def render_header(df):
    today = datetime.now().strftime("%B %d, %Y")
    total_val = df["PAR_clean"].sum() if "PAR_clean" in df.columns else 0
    st.markdown(f"""
    <div class="header-bar">
        <div class="marken-label">Solutions Team — Global Pipeline Dashboard</div>
        <h1>Opportunity Pipeline Overview</h1>
        <div class="subtitle">{len(df)} active opportunities · {fmt_currency(total_val)} total pipeline · Report date: {today}</div>
    </div>
    """, unsafe_allow_html=True)


def render_kpis(df):
    total_opps = len(df)
    total_val = df["PAR_clean"].sum() if "PAR_clean" in df.columns else 0
    avg_val = df["PAR_clean"].mean() if "PAR_clean" in df.columns else 0
    median_val = df["PAR_clean"].median() if "PAR_clean" in df.columns else 0
    unique_accts = df["Account Name"].nunique() if "Account Name" in df.columns else 0
    avg_duration = df["Stage Duration"].mean() if "Stage Duration" in df.columns else 0

    # Status counts
    working = len(df[df.get("Status_display", pd.Series()) == "Working"]) if "Status_display" in df.columns else 0
    pending = len(df[df.get("Status_display", pd.Series()) == "Pending"]) if "Status_display" in df.columns else 0
    not_assigned = len(df[df.get("Status_display", pd.Series()) == "Not Assigned"]) if "Status_display" in df.columns else 0

    # Regions
    emea = len(df[df["Owner Role"] == "EMEA BD"]) if "Owner Role" in df.columns else 0
    noram = len(df[df["Owner Role"] == "NORAM BD"]) if "Owner Role" in df.columns else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(kpi_card("Total Pipeline Value", fmt_currency(total_val),
                             f"Avg {fmt_currency(avg_val)} · Med {fmt_currency(median_val)}", accent=True), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("Opportunities", fmt_number(total_opps),
                             f"EMEA {emea} · NORAM {noram}"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("Unique Accounts", fmt_number(unique_accts),
                             f"{total_opps/max(unique_accts,1):.1f} opps per account"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card("Avg Stage Duration", f"{avg_duration:.0f} days",
                             f"Max {df['Stage Duration'].max():.0f}d" if "Stage Duration" in df.columns and not df["Stage Duration"].isna().all() else ""), unsafe_allow_html=True)
    with c5:
        st.markdown(kpi_card("Status Breakdown",
                             f"{working}W · {pending}P",
                             f"{not_assigned} not yet assigned"), unsafe_allow_html=True)


def render_executive_summary(df):
    section_header("Executive Summary", "High-level pipeline health and composition at a glance")

    col1, col2 = st.columns([1.1, 1])

    with col1:
        # Pipeline by Region — donut
        if "Owner Role" in df.columns and "PAR_clean" in df.columns:
            region_data = df.groupby("Owner Role")["PAR_clean"].agg(["sum", "count"]).reset_index()
            region_data.columns = ["Region", "Value", "Count"]

            fig = go.Figure(data=[go.Pie(
                labels=region_data["Region"],
                values=region_data["Value"],
                hole=0.55,
                marker=dict(colors=[MARKEN["navy"], MARKEN["teal"]]),
                textinfo="label+percent",
                textfont=dict(size=12, color="white"),
                hovertemplate="<b>%{label}</b><br>Value: $%{value:,.0f}<br>Share: %{percent}<extra></extra>",
            )])
            fig.update_layout(
                title=dict(text="Pipeline Value by Region", font=dict(size=14, color=MARKEN["navy"])),
                annotations=[dict(text=fmt_currency(region_data["Value"].sum()), x=0.5, y=0.5,
                                  font_size=18, font_color=MARKEN["navy"], showarrow=False, font_family="Source Sans Pro")],
                showlegend=False,
            )
            plotly_layout(fig, height=340, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Status breakdown — horizontal bar
        if "Status_display" in df.columns and "PAR_clean" in df.columns:
            status_data = df.groupby("Status_display").agg(
                Count=("Status_display", "size"),
                Value=("PAR_clean", "sum")
            ).reset_index().sort_values("Value", ascending=True)

            color_map = {"Working": MARKEN["teal"], "Pending": MARKEN["gold"], "Not Assigned": MARKEN["gray_400"]}

            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=status_data["Status_display"],
                x=status_data["Value"],
                orientation="h",
                marker_color=[color_map.get(s, MARKEN["gray_400"]) for s in status_data["Status_display"]],
                text=[f"{fmt_currency(v)}  ({c} opps)" for v, c in zip(status_data["Value"], status_data["Count"])],
                textposition="auto",
                textfont=dict(size=11, color="white"),
                hovertemplate="<b>%{y}</b><br>Value: $%{x:,.0f}<extra></extra>",
            ))
            fig.update_layout(title=dict(text="Pipeline by Solutions Status", font=dict(size=14, color=MARKEN["navy"])))
            plotly_layout(fig, height=340, margin=dict(l=100, r=20, t=50, b=30))
            fig.update_xaxes(title="", tickformat="$,.0s")
            fig.update_yaxes(title="")
            st.plotly_chart(fig, use_container_width=True)

    # Auto-generated narrative
    top_service = df["Main Primary Service"].value_counts().idxmax() if "Main Primary Service" in df.columns else "N/A"
    top_service_pct = df["Main Primary Service"].value_counts(normalize=True).iloc[0] * 100 if "Main Primary Service" in df.columns else 0
    top_account = df.groupby("Account Name")["PAR_clean"].sum().idxmax() if "Account Name" in df.columns and "PAR_clean" in df.columns else "N/A"
    top_account_val = df.groupby("Account Name")["PAR_clean"].sum().max() if "Account Name" in df.columns and "PAR_clean" in df.columns else 0

    total_val = df["PAR_clean"].sum() if "PAR_clean" in df.columns else 0
    insight(
        f"The Solutions team currently manages <strong>{len(df)} opportunities</strong> across "
        f"<strong>{df['Account Name'].nunique() if 'Account Name' in df.columns else 0} accounts</strong>, "
        f"with a combined pipeline of <strong>{fmt_currency(total_val)}</strong>. "
        f"<strong>{top_service}</strong> is the dominant service line, representing {top_service_pct:.0f}% of all opportunities. "
        f"The largest account by pipeline value is <strong>{top_account}</strong> ({fmt_currency(top_account_val)})."
    )


def render_pipeline_analysis(df):
    section_header("Pipeline Deep-Dive", "Service mix, value distribution, and timeline analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Pipeline by Service — horizontal bars
        if "Main Primary Service" in df.columns and "PAR_clean" in df.columns:
            svc = df.groupby("Main Primary Service").agg(
                Value=("PAR_clean", "sum"),
                Count=("Main Primary Service", "size"),
                Avg=("PAR_clean", "mean"),
            ).reset_index().sort_values("Value", ascending=True)

            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=svc["Main Primary Service"], x=svc["Value"],
                orientation="h",
                marker=dict(color=svc["Value"], colorscale=[[0, MARKEN["pale_teal"]], [1, MARKEN["navy"]]]),
                text=[f"{fmt_currency(v)} ({c})" for v, c in zip(svc["Value"], svc["Count"])],
                textposition="auto", textfont=dict(size=11, color="white"),
                hovertemplate="<b>%{y}</b><br>Total: $%{x:,.0f}<extra></extra>",
            ))
            fig.update_layout(title=dict(text="Pipeline Value by Primary Service", font=dict(size=14, color=MARKEN["navy"])))
            plotly_layout(fig, height=380, margin=dict(l=140, r=20, t=50, b=30))
            fig.update_xaxes(title="", tickformat="$,.0s")
            fig.update_yaxes(title="")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Value distribution — histogram
        if "PAR_clean" in df.columns:
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=df["PAR_clean"].dropna(),
                nbinsx=12,
                marker_color=MARKEN["teal"],
                marker_line=dict(color=MARKEN["navy"], width=1),
                hovertemplate="Range: $%{x:,.0f}<br>Count: %{y}<extra></extra>",
            ))
            fig.update_layout(title=dict(text="Opportunity Value Distribution", font=dict(size=14, color=MARKEN["navy"])))
            plotly_layout(fig, height=380, margin=dict(l=50, r=20, t=50, b=40))
            fig.update_xaxes(title="Opportunity PAR (USD)", tickformat="$,.0s")
            fig.update_yaxes(title="Frequency")
            st.plotly_chart(fig, use_container_width=True)

    # Second row
    col3, col4 = st.columns(2)

    with col3:
        # Close Date timeline
        if "Close Date_dt" in df.columns and "PAR_clean" in df.columns:
            timeline = df.dropna(subset=["Close Date_dt"]).copy()
            if len(timeline) > 0:
                timeline["Month"] = timeline["Close Date_dt"].dt.to_period("M").astype(str)
                monthly = timeline.groupby("Month").agg(
                    Value=("PAR_clean", "sum"),
                    Count=("Month", "size"),
                ).reset_index().sort_values("Month")

                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=monthly["Month"], y=monthly["Value"],
                    marker_color=MARKEN["teal"],
                    text=[fmt_currency(v) for v in monthly["Value"]],
                    textposition="outside", textfont=dict(size=10, color=MARKEN["navy"]),
                    hovertemplate="<b>%{x}</b><br>Value: $%{y:,.0f}<extra></extra>",
                    name="Value",
                ))
                fig.add_trace(go.Scatter(
                    x=monthly["Month"], y=monthly["Count"],
                    mode="lines+markers+text",
                    yaxis="y2",
                    line=dict(color=MARKEN["gold"], width=2.5),
                    marker=dict(size=8, color=MARKEN["gold"]),
                    text=monthly["Count"].astype(str),
                    textposition="top center", textfont=dict(size=10, color=MARKEN["gold"]),
                    hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>",
                    name="# Opps",
                ))
                fig.update_layout(
                    title=dict(text="Expected Close Timeline", font=dict(size=14, color=MARKEN["navy"])),
                    yaxis2=dict(overlaying="y", side="right", showgrid=False,
                                tickfont=dict(color=MARKEN["gold"], size=11)),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02),
                )
                plotly_layout(fig, height=380, margin=dict(l=50, r=50, t=60, b=40))
                fig.update_xaxes(title="")
                fig.update_yaxes(title="Value (USD)", tickformat="$,.0s")
                st.plotly_chart(fig, use_container_width=True)

    with col4:
        # Stage Duration scatter
        if "Stage Duration" in df.columns and "PAR_clean" in df.columns:
            scatter_df = df.dropna(subset=["Stage Duration", "PAR_clean"]).copy()
            if len(scatter_df) > 0:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=scatter_df["Stage Duration"],
                    y=scatter_df["PAR_clean"],
                    mode="markers",
                    marker=dict(
                        size=10,
                        color=scatter_df["Stage Duration"],
                        colorscale=[[0, MARKEN["teal"]], [0.5, MARKEN["gold"]], [1, MARKEN["red"]]],
                        line=dict(width=1, color="white"),
                        opacity=0.85,
                    ),
                    text=scatter_df["Account Name"] if "Account Name" in scatter_df.columns else None,
                    hovertemplate="<b>%{text}</b><br>Duration: %{x} days<br>Value: $%{y:,.0f}<extra></extra>",
                ))
                # Add median lines
                med_dur = scatter_df["Stage Duration"].median()
                med_val = scatter_df["PAR_clean"].median()
                fig.add_hline(y=med_val, line_dash="dot", line_color=MARKEN["gray_400"], opacity=0.5,
                              annotation_text=f"Median Value: {fmt_currency(med_val)}", annotation_font_size=10)
                fig.add_vline(x=med_dur, line_dash="dot", line_color=MARKEN["gray_400"], opacity=0.5,
                              annotation_text=f"Median: {med_dur:.0f}d", annotation_font_size=10)

                fig.update_layout(title=dict(text="Value vs. Stage Duration", font=dict(size=14, color=MARKEN["navy"])))
                plotly_layout(fig, height=380, margin=dict(l=60, r=20, t=50, b=50))
                fig.update_xaxes(title="Days in Stage")
                fig.update_yaxes(title="Opportunity PAR (USD)", tickformat="$,.0s")
                st.plotly_chart(fig, use_container_width=True)


def render_solutions_status(df):
    """New section for Status, Received/Closed by Solutions, Product columns."""
    section_header("Solutions Workflow Tracker", "Status progression, cycle time, and product classification")

    col1, col2, col3 = st.columns(3)

    # KPI mini-cards for Solutions-specific metrics
    if "Status_display" in df.columns:
        working = len(df[df["Status_display"] == "Working"])
        pending = len(df[df["Status_display"] == "Pending"])
        not_assigned = len(df[df["Status_display"] == "Not Assigned"])
    else:
        working = pending = not_assigned = 0

    received_count = df["Received by Solutions_dt"].notna().sum() if "Received by Solutions_dt" in df.columns else 0
    closed_count = df["Closed by Solutions_dt"].notna().sum() if "Closed by Solutions_dt" in df.columns else 0
    product_count = df["Product"].notna().sum() if "Product" in df.columns else 0

    with col1:
        st.markdown(kpi_card("Assigned to Solutions", str(working + pending),
                             f"Working: {working} · Pending: {pending}", accent=True), unsafe_allow_html=True)
    with col2:
        st.markdown(kpi_card("Received / Closed", f"{received_count} / {closed_count}",
                             f"{not_assigned} awaiting assignment"), unsafe_allow_html=True)
    with col3:
        st.markdown(kpi_card("Product Classified", str(product_count),
                             f"{len(df) - product_count} unclassified"), unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        # Status donut
        if "Status_display" in df.columns and "PAR_clean" in df.columns:
            status_agg = df.groupby("Status_display").agg(
                Value=("PAR_clean", "sum"), Count=("Status_display", "size")
            ).reset_index()
            color_map = {"Working": MARKEN["teal"], "Pending": MARKEN["gold"], "Not Assigned": MARKEN["gray_400"]}

            fig = go.Figure(data=[go.Pie(
                labels=status_agg["Status_display"],
                values=status_agg["Count"],
                hole=0.5,
                marker=dict(colors=[color_map.get(s, MARKEN["gray_400"]) for s in status_agg["Status_display"]]),
                textinfo="label+value",
                textfont=dict(size=12),
                hovertemplate="<b>%{label}</b><br>Opportunities: %{value}<br>Pipeline: $%{customdata:,.0f}<extra></extra>",
                customdata=status_agg["Value"],
            )])
            fig.update_layout(title=dict(text="Opportunities by Solutions Status", font=dict(size=14, color=MARKEN["navy"])))
            plotly_layout(fig, height=340, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig, use_container_width=True)

    with col_b:
        # Product breakdown
        if "Product_display" in df.columns and "PAR_clean" in df.columns:
            prod_agg = df.groupby("Product_display").agg(
                Value=("PAR_clean", "sum"), Count=("Product_display", "size")
            ).reset_index().sort_values("Value", ascending=True)

            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=prod_agg["Product_display"], x=prod_agg["Value"],
                orientation="h",
                marker_color=[MARKEN["navy"] if p != "Not Specified" else MARKEN["gray_400"] for p in prod_agg["Product_display"]],
                text=[f"{fmt_currency(v)} ({c})" for v, c in zip(prod_agg["Value"], prod_agg["Count"])],
                textposition="auto", textfont=dict(size=11, color="white"),
                hovertemplate="<b>%{y}</b><br>Value: $%{x:,.0f}<extra></extra>",
            ))
            fig.update_layout(title=dict(text="Pipeline Value by Product", font=dict(size=14, color=MARKEN["navy"])))
            plotly_layout(fig, height=340, margin=dict(l=120, r=20, t=50, b=30))
            fig.update_xaxes(title="", tickformat="$,.0s")
            fig.update_yaxes(title="")
            st.plotly_chart(fig, use_container_width=True)

    # Solutions intake timeline
    if "Received by Solutions_dt" in df.columns:
        received_df = df.dropna(subset=["Received by Solutions_dt"]).copy()
        if len(received_df) > 0:
            received_df["Received_Week"] = received_df["Received by Solutions_dt"].dt.to_period("W").astype(str)
            weekly = received_df.groupby("Received_Week").size().reset_index(name="Count").sort_values("Received_Week")

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=weekly["Received_Week"], y=weekly["Count"],
                marker_color=MARKEN["teal"],
                text=weekly["Count"].astype(str),
                textposition="outside", textfont=dict(size=11, color=MARKEN["navy"]),
                hovertemplate="<b>%{x}</b><br>Received: %{y}<extra></extra>",
            ))
            fig.update_layout(title=dict(text="Opportunities Received by Solutions (by Week)", font=dict(size=14, color=MARKEN["navy"])))
            plotly_layout(fig, height=300, margin=dict(l=40, r=20, t=50, b=60))
            fig.update_xaxes(title="", tickangle=-45)
            fig.update_yaxes(title="# Opportunities")
            st.plotly_chart(fig, use_container_width=True)

    # Detailed status table
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    status_cols = ["Account Name", "Opportunity Name", "Status_display", "Product_display",
                   "Received by Solutions", "Closed by Solutions", "PAR_clean", "Solution Resource"]
    avail_cols = [c for c in status_cols if c in df.columns]

    if avail_cols:
        display_df = df[avail_cols].copy()
        display_df = display_df.rename(columns={
            "Status_display": "Status",
            "Product_display": "Product",
            "PAR_clean": "Value (USD)",
        })
        st.dataframe(display_df, use_container_width=True, height=280,
                     column_config={
                         "Value (USD)": st.column_config.NumberColumn(format="$%,.0f"),
                     })


def render_customer_analysis(df):
    section_header("Customer Intelligence", "Account concentration, top accounts, and customer-service mapping")

    col1, col2 = st.columns(2)

    with col1:
        # Top accounts bar
        if "Account Name" in df.columns and "PAR_clean" in df.columns:
            top = df.groupby("Account Name")["PAR_clean"].sum().reset_index()
            top.columns = ["Account", "Value"]
            top = top.sort_values("Value", ascending=True).tail(10)

            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=top["Account"], x=top["Value"],
                orientation="h",
                marker=dict(color=top["Value"],
                            colorscale=[[0, MARKEN["pale_teal"]], [0.5, MARKEN["teal"]], [1, MARKEN["navy"]]]),
                text=[fmt_currency(v) for v in top["Value"]],
                textposition="auto", textfont=dict(size=11, color="white"),
                hovertemplate="<b>%{y}</b><br>Pipeline: $%{x:,.0f}<extra></extra>",
            ))
            fig.update_layout(title=dict(text="Top 10 Accounts by Pipeline Value", font=dict(size=14, color=MARKEN["navy"])))
            plotly_layout(fig, height=420, margin=dict(l=180, r=20, t=50, b=30))
            fig.update_xaxes(title="", tickformat="$,.0s")
            fig.update_yaxes(title="")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Customer concentration — Pareto
        if "Account Name" in df.columns and "PAR_clean" in df.columns:
            conc = df.groupby("Account Name")["PAR_clean"].sum().reset_index()
            conc.columns = ["Account", "Value"]
            conc = conc.sort_values("Value", ascending=False).reset_index(drop=True)
            conc["Cumulative"] = conc["Value"].cumsum()
            conc["Cum_Pct"] = conc["Cumulative"] / conc["Value"].sum() * 100
            conc["Rank"] = range(1, len(conc) + 1)

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=conc["Rank"], y=conc["Value"],
                marker_color=MARKEN["teal"], name="Account Value",
                hovertemplate="<b>#%{x}: %{customdata}</b><br>$%{y:,.0f}<extra></extra>",
                customdata=conc["Account"],
            ))
            fig.add_trace(go.Scatter(
                x=conc["Rank"], y=conc["Cum_Pct"],
                mode="lines+markers", yaxis="y2",
                line=dict(color=MARKEN["navy"], width=2.5),
                marker=dict(size=6, color=MARKEN["navy"]),
                name="Cumulative %",
                hovertemplate="Top %{x} accounts = %{y:.0f}%<extra></extra>",
            ))
            fig.add_hline(y=80, yref="y2", line_dash="dot", line_color=MARKEN["gold"], opacity=0.7,
                          annotation_text="80% threshold", annotation_font_size=10, annotation_font_color=MARKEN["gold"])
            fig.update_layout(
                title=dict(text="Customer Concentration (Pareto)", font=dict(size=14, color=MARKEN["navy"])),
                yaxis2=dict(overlaying="y", side="right", range=[0, 105], showgrid=False,
                            ticksuffix="%", tickfont=dict(color=MARKEN["navy"])),
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
            )
            plotly_layout(fig, height=420, margin=dict(l=60, r=60, t=60, b=40))
            fig.update_xaxes(title="Account Rank")
            fig.update_yaxes(title="Value (USD)", tickformat="$,.0s")
            st.plotly_chart(fig, use_container_width=True)

    # Customer-Service heatmap
    if "Account Name" in df.columns and "Main Primary Service" in df.columns and "PAR_clean" in df.columns:
        top_accts = df.groupby("Account Name")["PAR_clean"].sum().nlargest(10).index.tolist()
        heat_df = df[df["Account Name"].isin(top_accts)].copy()
        pivot = heat_df.pivot_table(values="PAR_clean", index="Account Name",
                                    columns="Main Primary Service", aggfunc="sum", fill_value=0)

        fig = go.Figure(data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale=[[0, "#F0F4F8"], [0.3, MARKEN["pale_teal"]], [0.7, MARKEN["teal"]], [1, MARKEN["navy"]]],
            text=[[fmt_currency(v) if v > 0 else "" for v in row] for row in pivot.values],
            texttemplate="%{text}",
            textfont=dict(size=10),
            hovertemplate="<b>%{y}</b><br>Service: %{x}<br>Value: $%{z:,.0f}<extra></extra>",
            showscale=False,
        ))
        fig.update_layout(title=dict(text="Top 10 Accounts × Service Matrix", font=dict(size=14, color=MARKEN["navy"])))
        plotly_layout(fig, height=380, margin=dict(l=180, r=20, t=50, b=80))
        fig.update_xaxes(tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

    # Concentration insight
    if "Account Name" in df.columns and "PAR_clean" in df.columns:
        total = df["PAR_clean"].sum()
        top3 = df.groupby("Account Name")["PAR_clean"].sum().nlargest(3)
        top3_pct = top3.sum() / total * 100 if total > 0 else 0
        top3_names = ", ".join(top3.index.tolist())
        insight(f"<strong>Concentration risk:</strong> The top 3 accounts ({top3_names}) represent "
                f"<strong>{top3_pct:.0f}%</strong> of total pipeline value. "
                f"{'Consider diversification strategies.' if top3_pct > 50 else 'Pipeline is well-diversified across accounts.'}")


def render_team_analysis(df):
    section_header("Team Performance", "Solution resource allocation, opportunity distribution, and workload balance")

    col1, col2 = st.columns(2)

    with col1:
        # Solution Resource — bar chart with value + count
        if "Solution Resource" in df.columns and "PAR_clean" in df.columns:
            team = df.groupby("Solution Resource").agg(
                Value=("PAR_clean", "sum"),
                Count=("Solution Resource", "size"),
                Avg_Duration=("Stage Duration", "mean"),
            ).reset_index().sort_values("Value", ascending=True)

            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=team["Solution Resource"], x=team["Value"],
                orientation="h",
                marker_color=MARKEN["navy"],
                text=[f"{fmt_currency(v)} ({c} opps)" for v, c in zip(team["Value"], team["Count"])],
                textposition="auto", textfont=dict(size=11, color="white"),
                hovertemplate="<b>%{y}</b><br>Total: $%{x:,.0f}<extra></extra>",
            ))
            fig.update_layout(title=dict(text="Pipeline by Solution Resource", font=dict(size=14, color=MARKEN["navy"])))
            plotly_layout(fig, height=380, margin=dict(l=150, r=20, t=50, b=30))
            fig.update_xaxes(title="", tickformat="$,.0s")
            fig.update_yaxes(title="")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Opportunity Owner — bar
        if "Opportunity Owner" in df.columns and "PAR_clean" in df.columns:
            owner = df.groupby("Opportunity Owner").agg(
                Value=("PAR_clean", "sum"),
                Count=("Opportunity Owner", "size"),
            ).reset_index().sort_values("Value", ascending=True)

            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=owner["Opportunity Owner"], x=owner["Value"],
                orientation="h",
                marker_color=MARKEN["teal"],
                text=[f"{fmt_currency(v)} ({c})" for v, c in zip(owner["Value"], owner["Count"])],
                textposition="auto", textfont=dict(size=11, color="white"),
                hovertemplate="<b>%{y}</b><br>Total: $%{x:,.0f}<extra></extra>",
            ))
            fig.update_layout(title=dict(text="Pipeline by Opportunity Owner (BD)", font=dict(size=14, color=MARKEN["navy"])))
            plotly_layout(fig, height=380, margin=dict(l=150, r=20, t=50, b=30))
            fig.update_xaxes(title="", tickformat="$,.0s")
            fig.update_yaxes(title="")
            st.plotly_chart(fig, use_container_width=True)

    # Workload balance — treemap
    if "Solution Resource" in df.columns and "PAR_clean" in df.columns and "Main Primary Service" in df.columns:
        tree_df = df.dropna(subset=["PAR_clean"]).copy()
        tree_df["Service"] = tree_df["Main Primary Service"].fillna("Other")
        tree_data = tree_df.groupby(["Solution Resource", "Service"]).agg(
            Value=("PAR_clean", "sum"), Count=("PAR_clean", "size")
        ).reset_index()

        if len(tree_data) > 0:
            fig = px.treemap(
                tree_data,
                path=["Solution Resource", "Service"],
                values="Value",
                color="Value",
                color_continuous_scale=[[0, MARKEN["pale_teal"]], [0.5, MARKEN["teal"]], [1, MARKEN["navy"]]],
                hover_data={"Count": True, "Value": ":$,.0f"},
            )
            fig.update_layout(
                title=dict(text="Resource × Service Treemap (sized by value)", font=dict(size=14, color=MARKEN["navy"])),
                coloraxis_showscale=False,
            )
            fig.update_traces(textinfo="label+value", texttemplate="%{label}<br>%{value:$,.0s}")
            plotly_layout(fig, height=400, margin=dict(l=10, r=10, t=50, b=10))
            st.plotly_chart(fig, use_container_width=True)


def render_aging_risk(df):
    section_header("Aging & Risk Analysis", "Stage duration distribution and at-risk opportunities")

    col1, col2 = st.columns(2)

    with col1:
        if "Stage Duration" in df.columns:
            dur = df.dropna(subset=["Stage Duration"]).copy()
            if len(dur) > 0:
                # Duration buckets
                bins = [0, 14, 30, 60, 90, float("inf")]
                labels = ["0-14d", "15-30d", "31-60d", "61-90d", "90d+"]
                dur["Bucket"] = pd.cut(dur["Stage Duration"], bins=bins, labels=labels, right=True)
                bucket_agg = dur.groupby("Bucket", observed=True).agg(
                    Count=("Bucket", "size"),
                    Value=("PAR_clean", "sum"),
                ).reset_index()

                colors = [MARKEN["green"], MARKEN["teal"], MARKEN["teal_light"], MARKEN["gold"], MARKEN["red"]]

                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=bucket_agg["Bucket"].astype(str), y=bucket_agg["Count"],
                    marker_color=colors[:len(bucket_agg)],
                    text=[f"{c} opps\n{fmt_currency(v)}" for c, v in zip(bucket_agg["Count"], bucket_agg["Value"])],
                    textposition="outside", textfont=dict(size=10),
                    hovertemplate="<b>%{x}</b><br>Count: %{y}<br>Value: $%{customdata:,.0f}<extra></extra>",
                    customdata=bucket_agg["Value"],
                ))
                fig.update_layout(title=dict(text="Stage Duration Distribution", font=dict(size=14, color=MARKEN["navy"])))
                plotly_layout(fig, height=380, margin=dict(l=40, r=20, t=50, b=40))
                fig.update_xaxes(title="Duration Bucket")
                fig.update_yaxes(title="# Opportunities")
                st.plotly_chart(fig, use_container_width=True)

    with col2:
        # At-risk table — long stage duration
        if "Stage Duration" in df.columns and "PAR_clean" in df.columns:
            at_risk = df.dropna(subset=["Stage Duration"]).nlargest(8, "Stage Duration")
            cols = ["Account Name", "Opportunity Name", "Stage Duration", "PAR_clean", "Solution Resource"]
            avail = [c for c in cols if c in at_risk.columns]

            st.markdown("""
            <div style="background:#FDF2E0; border-left:3px solid #D4A843; border-radius:0 8px 8px 0;
                        padding:10px 14px; margin:0 0 10px 0;">
                <strong style="color:#8B6914; font-size:0.85rem;">⚠ Longest Duration Opportunities</strong>
                <div style="color:#8B6914; font-size:0.78rem; margin-top:2px;">
                    These opportunities may require escalation or review
                </div>
            </div>
            """, unsafe_allow_html=True)

            disp = at_risk[avail].copy()
            disp = disp.rename(columns={"PAR_clean": "Value (USD)", "Stage Duration": "Days"})
            st.dataframe(disp, use_container_width=True, height=300,
                         column_config={"Value (USD)": st.column_config.NumberColumn(format="$%,.0f")})


def render_notes_explorer(df):
    section_header("Notes & Activity Log", "Team commentary and latest updates across the pipeline")

    if "Notes" in df.columns:
        search = st.text_input("🔍  Search notes, accounts, or opportunity names", "", key="notes_search")

        display = df.copy()
        if search:
            mask = pd.Series(False, index=display.index)
            for col in ["Notes", "Account Name", "Opportunity Name", "Solution Resource"]:
                if col in display.columns:
                    mask |= display[col].astype(str).str.contains(search, case=False, na=False)
            display = display[mask]

        st.markdown(f"<p style='color:{MARKEN['gray_600']}; font-size:0.8rem;'>{len(display)} results</p>",
                    unsafe_allow_html=True)

        show_cols = ["Account Name", "Opportunity Name", "Solution Resource", "Status_display",
                     "PAR_clean", "Stage Duration", "Notes"]
        avail = [c for c in show_cols if c in display.columns]
        disp = display[avail].copy()
        disp = disp.rename(columns={"Status_display": "Status", "PAR_clean": "Value (USD)"})
        st.dataframe(disp, use_container_width=True, height=450,
                     column_config={
                         "Value (USD)": st.column_config.NumberColumn(format="$%,.0f"),
                         "Notes": st.column_config.TextColumn(width="large"),
                     })


def render_export(df):
    section_header("Export & Report", "Download filtered data or a formatted executive summary")

    col1, col2 = st.columns(2)

    with col1:
        # Excel export
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            export_df = df.copy()
            # Clean up for export
            drop_cols = [c for c in export_df.columns if c.endswith("_dt") or c.endswith("_display") or c == "PAR_clean"]
            export_df = export_df.drop(columns=[c for c in drop_cols if c in export_df.columns], errors="ignore")
            export_df.to_excel(writer, sheet_name="Pipeline Data", index=False)

            # Summary sheet
            summary_data = {
                "Metric": ["Total Opportunities", "Total Pipeline Value", "Average Deal Size",
                           "Unique Accounts", "Avg Stage Duration (days)"],
                "Value": [
                    len(df),
                    f"${df['PAR_clean'].sum():,.0f}" if "PAR_clean" in df.columns else "N/A",
                    f"${df['PAR_clean'].mean():,.0f}" if "PAR_clean" in df.columns else "N/A",
                    df["Account Name"].nunique() if "Account Name" in df.columns else "N/A",
                    f"{df['Stage Duration'].mean():.0f}" if "Stage Duration" in df.columns else "N/A",
                ],
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name="Summary", index=False)

            # Format workbook
            wb = writer.book
            header_fmt = wb.add_format({
                "bold": True, "bg_color": "#003B5C", "font_color": "white",
                "border": 1, "font_name": "Segoe UI", "font_size": 11,
            })
            for sheet_name in writer.sheets:
                ws = writer.sheets[sheet_name]
                for col_idx, col_name in enumerate(export_df.columns if sheet_name == "Pipeline Data" else summary_data.keys()):
                    ws.write(0, col_idx, col_name, header_fmt)
                    ws.set_column(col_idx, col_idx, 20)

        st.download_button(
            label="📥  Download Filtered Data (Excel)",
            data=buffer.getvalue(),
            file_name=f"Marken_Solutions_Pipeline_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    with col2:
        # CSV quick export
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥  Download as CSV",
            data=csv,
            file_name=f"Marken_Solutions_Pipeline_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )


# ──────────────────────────────────────────────────────────────────────────────
# MAIN APP
# ──────────────────────────────────────────────────────────────────────────────
def main():
    # Upload state
    uploaded = st.sidebar.file_uploader(
        "Upload Masterfile (.xlsx)",
        type=["xlsx", "xls"],
        help="Upload the Solutions Masterfile exported from Salesforce with team annotations.",
    )

    if uploaded is None:
        # Landing page
        st.markdown("""
        <div class="header-bar">
            <div class="marken-label">Solutions Team — Global Pipeline Dashboard</div>
            <h1>Welcome</h1>
            <div class="subtitle">Upload your Solutions Masterfile to get started</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="text-align:center; padding:4rem 2rem;">
            <div style="font-size:3rem; margin-bottom:1rem;">📊</div>
            <h3 style="color:#003B5C; margin-bottom:0.5rem;">Upload Your Masterfile</h3>
            <p style="color:#64748B; max-width:500px; margin:0 auto; line-height:1.6;">
                Use the file uploader in the sidebar to load your Solutions team Masterfile.
                The dashboard will automatically generate a full executive overview with interactive
                charts, KPIs, and exportable reports.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    # Load data
    df = load_and_clean(uploaded)

    # Sidebar filters
    filters = render_sidebar(df)
    fdf = apply_filters(df, filters)

    # Filtered count notice
    if len(fdf) < len(df):
        st.sidebar.markdown(
            f"<div style='text-align:center; padding:8px; background:rgba(0,145,218,0.15); border-radius:6px; margin-top:8px;'>"
            f"<span style='font-size:0.78rem; color:#0091DA; font-weight:600;'>"
            f"Showing {len(fdf)} of {len(df)} opportunities</span></div>",
            unsafe_allow_html=True
        )

    # ── Render all sections ─────────────────────────────────────
    render_header(fdf)
    render_kpis(fdf)

    st.markdown('<hr class="subtle-divider">', unsafe_allow_html=True)

    # Navigation tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📋 Executive Summary",
        "📊 Pipeline Analysis",
        "🔄 Solutions Tracker",
        "🏢 Customers",
        "👥 Team",
        "⏱ Aging & Risk",
        "📝 Notes & Export",
    ])

    with tab1:
        render_executive_summary(fdf)
    with tab2:
        render_pipeline_analysis(fdf)
    with tab3:
        render_solutions_status(fdf)
    with tab4:
        render_customer_analysis(fdf)
    with tab5:
        render_team_analysis(fdf)
    with tab6:
        render_aging_risk(fdf)
    with tab7:
        render_notes_explorer(fdf)
        st.markdown('<hr class="subtle-divider">', unsafe_allow_html=True)
        render_export(fdf)


if __name__ == "__main__":
    main()
