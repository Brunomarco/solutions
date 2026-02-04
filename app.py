import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import BytesIO
from datetime import datetime
import numpy as np

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Solutions Pipeline Report | Marken",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Marken / UPS Healthcare Brand Palette ────────────────────────────────────
MARKEN_TEAL = "#00857C"
MARKEN_TEAL_LIGHT = "#E6F4F3"
MARKEN_DARK = "#1B2A4A"
MARKEN_NAVY = "#0F1D35"
UPS_BROWN = "#351C15"
UPS_GOLD = "#FCB900"
ACCENT_CORAL = "#E8604C"
NEUTRAL_50 = "#F8F9FA"
NEUTRAL_100 = "#F1F3F5"
NEUTRAL_200 = "#E9ECEF"
NEUTRAL_400 = "#ADB5BD"
NEUTRAL_600 = "#6C757D"
NEUTRAL_800 = "#343A40"
WHITE = "#FFFFFF"

STAGE_COLORS = {
    "Solutions Design": MARKEN_TEAL,
    "Proposal/Price Quote": "#2E86AB",
    "Proposal Price/Quote": "#2E86AB",
    "Negotiations": UPS_GOLD,
    "Closed/Won": "#2ECC71",
    "Closed/Lost": ACCENT_CORAL,
}

CHART_PALETTE = [MARKEN_TEAL, "#2E86AB", UPS_GOLD, ACCENT_CORAL, "#6C5B7B", "#355C7D", "#C06C84", "#F67280", "#F8B500", "#00B4D8"]

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    /* Global */
    .stApp {{
        background-color: {NEUTRAL_50};
        font-family: 'Plus Jakarta Sans', sans-serif;
    }}
    
    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {MARKEN_NAVY} 0%, {MARKEN_DARK} 100%);
    }}
    section[data-testid="stSidebar"] * {{
        color: {WHITE} !important;
    }}
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stRadio label {{
        color: {NEUTRAL_200} !important;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 500;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }}
    
    /* Header Bar */
    .marken-header {{
        background: linear-gradient(135deg, {MARKEN_NAVY} 0%, {MARKEN_DARK} 60%, {MARKEN_TEAL} 100%);
        padding: 2rem 2.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }}
    .marken-header::before {{
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(0,133,124,0.25) 0%, transparent 70%);
        border-radius: 50%;
    }}
    .marken-header h1 {{
        color: {WHITE};
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 800;
        font-size: 1.75rem;
        margin: 0;
        letter-spacing: -0.02em;
    }}
    .marken-header p {{
        color: rgba(255,255,255,0.7);
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.9rem;
        margin: 0.3rem 0 0 0;
        font-weight: 400;
    }}
    .marken-brand {{
        color: {UPS_GOLD};
        font-weight: 700;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-bottom: 0.4rem;
        display: block;
    }}

    /* KPI Cards */
    .kpi-container {{
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }}
    .kpi-card {{
        background: {WHITE};
        border: 1px solid {NEUTRAL_200};
        border-radius: 10px;
        padding: 1.25rem 1.5rem;
        flex: 1;
        position: relative;
        transition: box-shadow 0.2s ease;
    }}
    .kpi-card:hover {{
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    }}
    .kpi-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        border-radius: 10px 10px 0 0;
    }}
    .kpi-card:nth-child(1)::before {{ background: {MARKEN_TEAL}; }}
    .kpi-card:nth-child(2)::before {{ background: {UPS_GOLD}; }}
    .kpi-card:nth-child(3)::before {{ background: #2E86AB; }}
    .kpi-card:nth-child(4)::before {{ background: {ACCENT_CORAL}; }}
    .kpi-card:nth-child(5)::before {{ background: #6C5B7B; }}
    .kpi-label {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: {NEUTRAL_600};
        margin-bottom: 0.4rem;
    }}
    .kpi-value {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.75rem;
        font-weight: 800;
        color: {MARKEN_DARK};
        letter-spacing: -0.03em;
        line-height: 1;
    }}
    .kpi-sub {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.75rem;
        color: {NEUTRAL_400};
        margin-top: 0.3rem;
    }}

    /* Section Headers */
    .section-header {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1rem;
        font-weight: 700;
        color: {MARKEN_DARK};
        margin: 1.5rem 0 0.75rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid {MARKEN_TEAL};
        display: inline-block;
    }}

    /* Chart containers */
    .chart-container {{
        background: {WHITE};
        border: 1px solid {NEUTRAL_200};
        border-radius: 10px;
        padding: 1.25rem;
    }}

    /* Tables */
    .dataframe {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.8rem !important;
    }}
    
    /* Stage badges */
    .stage-badge {{
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }}

    /* Data editor */
    [data-testid="stDataFrame"], [data-testid="data-grid"] {{
        font-family: 'Plus Jakarta Sans', sans-serif;
    }}

    /* Upload area */
    .upload-zone {{
        background: {WHITE};
        border: 2px dashed {NEUTRAL_200};
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        margin-bottom: 1rem;
    }}

    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.5rem;
    }}
    .stTabs [data-baseweb="tab"] {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 600;
        font-size: 0.85rem;
        padding: 0.5rem 1.25rem;
        border-radius: 8px 8px 0 0;
    }}
    
    /* Metric overrides */
    [data-testid="stMetricValue"] {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 800;
    }}
    
    div[data-testid="stFileUploader"] label p {{
        font-family: 'Plus Jakarta Sans', sans-serif;
    }}
</style>
""", unsafe_allow_html=True)


# ── Helper Functions ─────────────────────────────────────────────────────────

SALESFORCE_COLS = [
    "Stage", "Solution Resource", "Account Name", "Owner Role",
    "Opportunity Name", "Opportunity Owner", "Main Primary Service",
    "Opportunity PAR", "Stage Duration", "Close Date", "Notes"
]

TEAM_COLS = ["Solutions Notes", "Tasks", "Action Items", "Comments / Results"]

ALL_COLS = SALESFORCE_COLS + TEAM_COLS


def clean_sf_upload(df: pd.DataFrame) -> pd.DataFrame:
    """Clean a raw Salesforce export into standard format."""
    # Drop fully-empty unnamed columns
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
    # Standardise column names
    rename_map = {}
    for col in df.columns:
        for std in SALESFORCE_COLS:
            if col.strip().lower().replace(" ", "") == std.lower().replace(" ", ""):
                rename_map[col] = std
    df = df.rename(columns=rename_map)
    # Keep only known SF columns
    keep = [c for c in SALESFORCE_COLS if c in df.columns]
    df = df[keep].copy()
    # Coerce types
    if "Opportunity PAR" in df.columns:
        df["Opportunity PAR"] = pd.to_numeric(df["Opportunity PAR"], errors="coerce").fillna(0)
    if "Stage Duration" in df.columns:
        df["Stage Duration"] = pd.to_numeric(df["Stage Duration"], errors="coerce").fillna(0).astype(int)
    if "Close Date" in df.columns:
        df["Close Date"] = pd.to_datetime(df["Close Date"], errors="coerce", dayfirst=False).dt.strftime("%m/%d/%Y")
    return df.reset_index(drop=True)


def merge_masterfile(master: pd.DataFrame, new_sf: pd.DataFrame) -> pd.DataFrame:
    """Merge new Salesforce export into existing masterfile, preserving team columns."""
    # Ensure team columns exist in master
    for col in TEAM_COLS:
        if col not in master.columns:
            master[col] = ""

    # Identify rows by Opportunity Name
    existing_opps = set(master["Opportunity Name"].dropna().unique())
    new_opps = set(new_sf["Opportunity Name"].dropna().unique())

    # Update existing rows (refresh SF data, keep team notes)
    for idx, row in master.iterrows():
        opp = row.get("Opportunity Name")
        if opp in new_opps:
            match = new_sf[new_sf["Opportunity Name"] == opp].iloc[0]
            for col in SALESFORCE_COLS:
                if col in new_sf.columns:
                    master.at[idx, col] = match[col]

    # Add brand-new opportunities
    new_only = new_sf[~new_sf["Opportunity Name"].isin(existing_opps)].copy()
    for col in TEAM_COLS:
        new_only[col] = ""
    master = pd.concat([master, new_only], ignore_index=True)

    # Flag removed opportunities (in master but not in new SF)
    removed = existing_opps - new_opps
    if removed:
        master.loc[master["Opportunity Name"].isin(removed), "Solutions Notes"] = (
            master.loc[master["Opportunity Name"].isin(removed), "Solutions Notes"].fillna("").astype(str)
            + " [Removed from SF]"
        )
    return master[ALL_COLS].reset_index(drop=True)


def format_currency(val):
    """Format number as currency string."""
    if val >= 1_000_000:
        return f"${val / 1_000_000:,.1f}M"
    elif val >= 1_000:
        return f"${val / 1_000:,.0f}K"
    return f"${val:,.0f}"


def make_chart_layout(fig, title="", height=380):
    """Apply Marken-branded layout to Plotly figure."""
    fig.update_layout(
        title=dict(text=title, font=dict(family="Plus Jakarta Sans", size=14, color=MARKEN_DARK), x=0, xanchor="left"),
        font=dict(family="Plus Jakarta Sans", size=11, color=NEUTRAL_800),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(font=dict(size=10), orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
    )
    fig.update_xaxes(gridcolor=NEUTRAL_200, zerolinecolor=NEUTRAL_200)
    fig.update_yaxes(gridcolor=NEUTRAL_200, zerolinecolor=NEUTRAL_200)
    return fig


def to_excel_download(df: pd.DataFrame) -> bytes:
    """Export dataframe to styled Excel bytes."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Masterfile")
        ws = writer.sheets["Masterfile"]
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

        header_fill = PatternFill("solid", fgColor="1B2A4A")
        header_font = Font(name="Arial", bold=True, color="FFFFFF", size=10)
        team_fill = PatternFill("solid", fgColor="E6F4F3")
        thin_border = Border(
            left=Side(style="thin", color="E9ECEF"),
            right=Side(style="thin", color="E9ECEF"),
            top=Side(style="thin", color="E9ECEF"),
            bottom=Side(style="thin", color="E9ECEF"),
        )
        for col_idx, col_name in enumerate(df.columns, 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = thin_border
            # Highlight team columns
            if col_name in TEAM_COLS:
                for row_idx in range(2, len(df) + 2):
                    ws.cell(row=row_idx, column=col_idx).fill = team_fill
            # Set column widths
            max_len = max(len(str(col_name)), df[col_name].astype(str).str.len().max() if len(df) > 0 else 0)
            ws.column_dimensions[ws.cell(row=1, column=col_idx).column_letter].width = min(max_len + 4, 40)
        # Format data rows
        data_font = Font(name="Arial", size=10)
        for row_idx in range(2, len(df) + 2):
            for col_idx in range(1, len(df.columns) + 1):
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.font = data_font
                cell.border = thin_border
                cell.alignment = Alignment(vertical="center", wrap_text=True)
    return output.getvalue()


# ── Session State Init ───────────────────────────────────────────────────────

if "masterfile" not in st.session_state:
    st.session_state.masterfile = None
if "last_upload_name" not in st.session_state:
    st.session_state.last_upload_name = None


# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding: 1rem 0 1.5rem 0;">
        <div style="font-size:0.65rem; font-weight:700; letter-spacing:0.2em; color:{UPS_GOLD}; text-transform:uppercase; margin-bottom:0.2rem;">
            Marken · UPS Healthcare
        </div>
        <div style="font-size:1.1rem; font-weight:800; color:{WHITE}; letter-spacing:-0.02em;">
            Solutions Pipeline
        </div>
        <div style="font-size:0.7rem; color:rgba(255,255,255,0.5); margin-top:0.2rem;">
            Precision Logistics
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    nav = st.radio("Navigation", ["📊 Dashboard", "📋 Masterfile Manager", "📈 Detailed Analysis"], label_visibility="collapsed")

    st.markdown("---")
    st.markdown(f"""
    <div style="font-size:0.65rem; color:rgba(255,255,255,0.4); text-align:center; padding-top:1rem;">
        Solutions Team Report<br>
        Generated {datetime.now().strftime('%B %d, %Y')}
    </div>
    """, unsafe_allow_html=True)


# ── Header ───────────────────────────────────────────────────────────────────

st.markdown(f"""
<div class="marken-header">
    <span class="marken-brand">Marken · UPS Healthcare Precision Logistics</span>
    <h1>Solutions Team — Pipeline Report</h1>
    <p>Global opportunity overview · Salesforce-integrated masterfile · Updated {datetime.now().strftime('%B %d, %Y')}</p>
</div>
""", unsafe_allow_html=True)


# ── Data Loading ─────────────────────────────────────────────────────────────

# Always show upload option at top if no data loaded
if st.session_state.masterfile is None:
    st.info("👋 **Welcome!** Upload your Salesforce export or existing Masterfile to get started.")
    upload = st.file_uploader(
        "Upload Salesforce Export (.xlsx)",
        type=["xlsx", "xls", "csv"],
        key="initial_upload",
        help="Upload the Salesforce Stage 2 Opportunities export. The app will add team columns automatically."
    )
    if upload is not None:
        if upload.name.endswith(".csv"):
            raw = pd.read_csv(upload)
        else:
            raw = pd.read_excel(upload)
        # Check if this is already a masterfile (has team columns)
        if any(tc in raw.columns for tc in TEAM_COLS):
            # Existing masterfile — load as-is
            for col in TEAM_COLS:
                if col not in raw.columns:
                    raw[col] = ""
            raw = raw.loc[:, ~raw.columns.str.startswith("Unnamed")]
            st.session_state.masterfile = raw
        else:
            cleaned = clean_sf_upload(raw)
            for col in TEAM_COLS:
                cleaned[col] = ""
            st.session_state.masterfile = cleaned
        st.session_state.last_upload_name = upload.name
        st.rerun()

if st.session_state.masterfile is None:
    st.stop()

df = st.session_state.masterfile.copy()

# Ensure numeric types
df["Opportunity PAR"] = pd.to_numeric(df.get("Opportunity PAR", 0), errors="coerce").fillna(0)
df["Stage Duration"] = pd.to_numeric(df.get("Stage Duration", 0), errors="coerce").fillna(0).astype(int)


# ═══════════════════════════════════════════════════════════════════════════════
# 📊 DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

if nav == "📊 Dashboard":

    # ── Filters ──────────────────────────────────────────────────────────────
    with st.expander("🔍 **Filters**", expanded=False):
        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            stages = st.multiselect("Stage", options=sorted(df["Stage"].dropna().unique()), default=sorted(df["Stage"].dropna().unique()))
        with fc2:
            services = st.multiselect("Service", options=sorted(df["Main Primary Service"].dropna().unique()), default=sorted(df["Main Primary Service"].dropna().unique()))
        with fc3:
            regions = st.multiselect("Region", options=sorted(df["Owner Role"].dropna().unique()), default=sorted(df["Owner Role"].dropna().unique()))
        with fc4:
            resources = st.multiselect("Solution Resource", options=sorted(df["Solution Resource"].dropna().unique()), default=sorted(df["Solution Resource"].dropna().unique()))

    fdf = df[
        df["Stage"].isin(stages) &
        df["Main Primary Service"].isin(services) &
        df["Owner Role"].isin(regions) &
        df["Solution Resource"].isin(resources)
    ]

    # ── KPI Strip ────────────────────────────────────────────────────────────
    total_par = fdf["Opportunity PAR"].sum()
    n_opps = len(fdf)
    avg_par = fdf["Opportunity PAR"].mean() if n_opps > 0 else 0
    avg_duration = fdf["Stage Duration"].mean() if n_opps > 0 else 0
    n_customers = fdf["Account Name"].nunique()

    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-card">
            <div class="kpi-label">Total Pipeline Value</div>
            <div class="kpi-value">{format_currency(total_par)}</div>
            <div class="kpi-sub">{n_opps} opportunities</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Unique Customers</div>
            <div class="kpi-value">{n_customers}</div>
            <div class="kpi-sub">Across all regions</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Avg. Deal Size</div>
            <div class="kpi-value">{format_currency(avg_par)}</div>
            <div class="kpi-sub">Per opportunity</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Avg. Stage Duration</div>
            <div class="kpi-value">{avg_duration:.0f}</div>
            <div class="kpi-sub">Days in current stage</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Services in Scope</div>
            <div class="kpi-value">{fdf['Main Primary Service'].nunique()}</div>
            <div class="kpi-sub">Product categories</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Row 1: Stage Breakdown + Service Mix ─────────────────────────────────
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="section-header">Pipeline by Stage</div>', unsafe_allow_html=True)
        stage_df = fdf.groupby("Stage").agg(
            Count=("Opportunity Name", "count"),
            Value=("Opportunity PAR", "sum")
        ).reset_index().sort_values("Value", ascending=True)

        fig_stage = go.Figure()
        fig_stage.add_trace(go.Bar(
            y=stage_df["Stage"], x=stage_df["Value"],
            orientation="h",
            marker_color=[STAGE_COLORS.get(s, MARKEN_TEAL) for s in stage_df["Stage"]],
            text=[f"{format_currency(v)}  ({c})" for v, c in zip(stage_df["Value"], stage_df["Count"])],
            textposition="auto",
            textfont=dict(family="Plus Jakarta Sans", size=11, color=WHITE),
        ))
        make_chart_layout(fig_stage, height=320)
        fig_stage.update_layout(showlegend=False, yaxis=dict(tickfont=dict(size=11)))
        st.plotly_chart(fig_stage, use_container_width=True)

    with c2:
        st.markdown('<div class="section-header">Service Mix (by Value)</div>', unsafe_allow_html=True)
        svc_df = fdf.groupby("Main Primary Service")["Opportunity PAR"].sum().reset_index()
        svc_df = svc_df.sort_values("Opportunity PAR", ascending=False)

        fig_svc = go.Figure(go.Pie(
            labels=svc_df["Main Primary Service"],
            values=svc_df["Opportunity PAR"],
            hole=0.55,
            marker=dict(colors=CHART_PALETTE[:len(svc_df)]),
            textinfo="label+percent",
            textfont=dict(family="Plus Jakarta Sans", size=10),
            hovertemplate="<b>%{label}</b><br>Value: $%{value:,.0f}<br>Share: %{percent}<extra></extra>",
        ))
        make_chart_layout(fig_svc, height=320)
        fig_svc.update_layout(showlegend=False)
        st.plotly_chart(fig_svc, use_container_width=True)

    # ── Row 2: Top Customers + Regional Split ────────────────────────────────
    c3, c4 = st.columns(2)

    with c3:
        st.markdown('<div class="section-header">Top 10 Customers by Pipeline Value</div>', unsafe_allow_html=True)
        cust_df = fdf.groupby("Account Name").agg(
            Value=("Opportunity PAR", "sum"),
            Opps=("Opportunity Name", "count")
        ).reset_index().sort_values("Value", ascending=True).tail(10)

        fig_cust = go.Figure()
        fig_cust.add_trace(go.Bar(
            y=cust_df["Account Name"], x=cust_df["Value"],
            orientation="h",
            marker=dict(color=cust_df["Value"], colorscale=[[0, "#B2DFDB"], [1, MARKEN_TEAL]]),
            text=[f"{format_currency(v)}" for v in cust_df["Value"]],
            textposition="auto",
            textfont=dict(family="Plus Jakarta Sans", size=10, color=WHITE),
        ))
        make_chart_layout(fig_cust, height=380)
        fig_cust.update_layout(showlegend=False, yaxis=dict(tickfont=dict(size=10)))
        st.plotly_chart(fig_cust, use_container_width=True)

    with c4:
        st.markdown('<div class="section-header">Pipeline by Region</div>', unsafe_allow_html=True)
        region_df = fdf.groupby("Owner Role").agg(
            Value=("Opportunity PAR", "sum"),
            Count=("Opportunity Name", "count")
        ).reset_index().sort_values("Value", ascending=False)

        fig_region = go.Figure()
        fig_region.add_trace(go.Bar(
            x=region_df["Owner Role"], y=region_df["Value"],
            marker_color=CHART_PALETTE[:len(region_df)],
            text=[f"{format_currency(v)}<br>({c} opps)" for v, c in zip(region_df["Value"], region_df["Count"])],
            textposition="auto",
            textfont=dict(family="Plus Jakarta Sans", size=11),
        ))
        make_chart_layout(fig_region, height=380)
        fig_region.update_layout(showlegend=False, xaxis=dict(tickfont=dict(size=10)))
        st.plotly_chart(fig_region, use_container_width=True)

    # ── Row 3: Solution Resource Workload + Stage Duration ───────────────────
    c5, c6 = st.columns(2)

    with c5:
        st.markdown('<div class="section-header">Solution Resource Workload</div>', unsafe_allow_html=True)
        res_df = fdf.groupby("Solution Resource").agg(
            Value=("Opportunity PAR", "sum"),
            Count=("Opportunity Name", "count"),
            AvgDuration=("Stage Duration", "mean")
        ).reset_index().sort_values("Value", ascending=False)

        fig_res = go.Figure()
        fig_res.add_trace(go.Bar(
            x=res_df["Solution Resource"], y=res_df["Count"],
            name="# Opportunities",
            marker_color=MARKEN_TEAL,
            yaxis="y",
        ))
        fig_res.add_trace(go.Scatter(
            x=res_df["Solution Resource"], y=res_df["Value"],
            name="Total Value",
            mode="markers+lines",
            marker=dict(color=UPS_GOLD, size=10),
            line=dict(color=UPS_GOLD, width=2),
            yaxis="y2",
        ))
        make_chart_layout(fig_res, height=380)
        fig_res.update_layout(
            yaxis=dict(title="# Opportunities", titlefont=dict(size=10), side="left"),
            yaxis2=dict(title="Pipeline Value ($)", titlefont=dict(size=10), side="right", overlaying="y", showgrid=False),
            xaxis=dict(tickfont=dict(size=9), tickangle=30),
            legend=dict(font=dict(size=9)),
        )
        st.plotly_chart(fig_res, use_container_width=True)

    with c6:
        st.markdown('<div class="section-header">Stage Duration Distribution</div>', unsafe_allow_html=True)
        fig_dur = go.Figure()
        fig_dur.add_trace(go.Box(
            x=fdf["Stage"], y=fdf["Stage Duration"],
            marker_color=MARKEN_TEAL,
            boxmean=True,
            fillcolor=MARKEN_TEAL_LIGHT,
            line=dict(color=MARKEN_TEAL),
        ))
        make_chart_layout(fig_dur, height=380)
        fig_dur.update_layout(
            xaxis=dict(tickfont=dict(size=10)),
            yaxis=dict(title="Days", titlefont=dict(size=10)),
        )
        st.plotly_chart(fig_dur, use_container_width=True)

    # ── Pipeline Summary Table ───────────────────────────────────────────────
    st.markdown('<div class="section-header">Full Pipeline Overview</div>', unsafe_allow_html=True)

    display_df = fdf[["Stage", "Account Name", "Opportunity Name", "Solution Resource",
                       "Opportunity Owner", "Main Primary Service", "Opportunity PAR",
                       "Stage Duration", "Close Date", "Notes"]].copy()
    display_df["Opportunity PAR"] = display_df["Opportunity PAR"].apply(lambda x: f"${x:,.0f}")
    display_df = display_df.sort_values("Stage")

    st.dataframe(
        display_df,
        use_container_width=True,
        height=min(400, 35 * len(display_df) + 38),
        column_config={
            "Stage": st.column_config.TextColumn("Stage", width="medium"),
            "Account Name": st.column_config.TextColumn("Customer", width="medium"),
            "Opportunity Name": st.column_config.TextColumn("Opportunity", width="large"),
            "Opportunity PAR": st.column_config.TextColumn("PAR Value", width="small"),
            "Stage Duration": st.column_config.NumberColumn("Days", width="small"),
        },
        hide_index=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 📋 MASTERFILE MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

elif nav == "📋 Masterfile Manager":

    st.markdown('<div class="section-header">Masterfile Management</div>', unsafe_allow_html=True)
    st.markdown("""
    **Workflow:** Download fresh Salesforce data → Upload here → App merges with existing masterfile  
    (preserving your team's Notes, Tasks, Action Items & Comments) → Edit inline → Download updated Masterfile.
    """)

    # ── Upload new SF data to merge ──────────────────────────────────────────
    with st.expander("📤 **Upload New Salesforce Export (Merge)**", expanded=False):
        st.caption("Upload a new Salesforce export to merge into the current Masterfile. Team-added columns will be preserved.")
        new_upload = st.file_uploader("New Salesforce Export", type=["xlsx", "xls", "csv"], key="merge_upload")
        if new_upload is not None:
            if new_upload.name.endswith(".csv"):
                new_raw = pd.read_csv(new_upload)
            else:
                new_raw = pd.read_excel(new_upload)
            new_cleaned = clean_sf_upload(new_raw)
            merged = merge_masterfile(st.session_state.masterfile.copy(), new_cleaned)
            st.session_state.masterfile = merged
            st.success(f"✅ Merged {len(new_cleaned)} rows from Salesforce. Masterfile now has {len(merged)} opportunities.")
            st.rerun()

    # ── Editable Data Table ──────────────────────────────────────────────────
    st.markdown('<div class="section-header">Edit Masterfile</div>', unsafe_allow_html=True)
    st.caption("Edit team columns directly. Changes are saved in-session. Download when done.")

    edit_df = st.session_state.masterfile.copy()
    for col in TEAM_COLS:
        if col not in edit_df.columns:
            edit_df[col] = ""

    edited = st.data_editor(
        edit_df,
        use_container_width=True,
        height=min(600, 35 * len(edit_df) + 38),
        num_rows="dynamic",
        column_config={
            "Stage": st.column_config.TextColumn("Stage", width="medium", disabled=True),
            "Account Name": st.column_config.TextColumn("Customer", width="medium", disabled=True),
            "Opportunity Name": st.column_config.TextColumn("Opportunity", width="large", disabled=True),
            "Opportunity PAR": st.column_config.NumberColumn("PAR ($)", format="$%d", disabled=True),
            "Stage Duration": st.column_config.NumberColumn("Days", disabled=True),
            "Close Date": st.column_config.TextColumn("Close Date", disabled=True),
            "Owner Role": st.column_config.TextColumn("Region", disabled=True),
            "Opportunity Owner": st.column_config.TextColumn("Opp. Owner", disabled=True),
            "Solution Resource": st.column_config.TextColumn("Solution Res.", disabled=True),
            "Main Primary Service": st.column_config.TextColumn("Service", disabled=True),
            "Notes": st.column_config.TextColumn("SF Notes", disabled=True),
            "Solutions Notes": st.column_config.TextColumn("Solutions Notes", width="large"),
            "Tasks": st.column_config.TextColumn("Tasks", width="large"),
            "Action Items": st.column_config.TextColumn("Action Items", width="large"),
            "Comments / Results": st.column_config.TextColumn("Comments / Results", width="large"),
        },
        key="master_editor",
        hide_index=True,
    )

    # Save edits
    if st.button("💾 Save Changes", type="primary"):
        st.session_state.masterfile = edited.copy()
        st.success("Changes saved to session.")

    # ── Downloads ────────────────────────────────────────────────────────────
    st.markdown("---")
    dc1, dc2 = st.columns(2)
    with dc1:
        xlsx_bytes = to_excel_download(st.session_state.masterfile)
        st.download_button(
            "📥 Download Masterfile (.xlsx)",
            data=xlsx_bytes,
            file_name=f"Solutions_Masterfile_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
        )
    with dc2:
        csv_bytes = st.session_state.masterfile.to_csv(index=False).encode()
        st.download_button(
            "📥 Download Masterfile (.csv)",
            data=csv_bytes,
            file_name=f"Solutions_Masterfile_{datetime.now().strftime('%Y-%m-%d')}.csv",
            mime="text/csv",
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 📈 DETAILED ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

elif nav == "📈 Detailed Analysis":

    st.markdown('<div class="section-header">Detailed Opportunity Analysis</div>', unsafe_allow_html=True)

    # ── Opportunity Owner Analysis ───────────────────────────────────────────
    st.markdown('<div class="section-header">Opportunity Owner Performance</div>', unsafe_allow_html=True)

    owner_df = df.groupby("Opportunity Owner").agg(
        TotalValue=("Opportunity PAR", "sum"),
        Count=("Opportunity Name", "count"),
        AvgDuration=("Stage Duration", "mean"),
        AvgDeal=("Opportunity PAR", "mean"),
    ).reset_index().sort_values("TotalValue", ascending=False)

    oc1, oc2 = st.columns(2)
    with oc1:
        fig_owner = go.Figure()
        fig_owner.add_trace(go.Bar(
            x=owner_df["Opportunity Owner"].head(10),
            y=owner_df["TotalValue"].head(10),
            marker_color=MARKEN_TEAL,
            text=[format_currency(v) for v in owner_df["TotalValue"].head(10)],
            textposition="auto",
            textfont=dict(family="Plus Jakarta Sans", size=10, color=WHITE),
        ))
        make_chart_layout(fig_owner, title="Top 10 Owners by Pipeline Value", height=380)
        fig_owner.update_layout(showlegend=False, xaxis=dict(tickangle=30, tickfont=dict(size=9)))
        st.plotly_chart(fig_owner, use_container_width=True)

    with oc2:
        st.dataframe(
            owner_df.rename(columns={
                "Opportunity Owner": "Owner",
                "TotalValue": "Total Value",
                "Count": "# Opps",
                "AvgDuration": "Avg Duration (d)",
                "AvgDeal": "Avg Deal Size",
            }).style.format({
                "Total Value": "${:,.0f}",
                "Avg Duration (d)": "{:.0f}",
                "Avg Deal Size": "${:,.0f}",
            }),
            use_container_width=True,
            height=380,
            hide_index=True,
        )

    # ── Stage Transition Heatmap ─────────────────────────────────────────────
    st.markdown('<div class="section-header">Service × Stage Heatmap (Value $)</div>', unsafe_allow_html=True)

    heat_df = df.groupby(["Main Primary Service", "Stage"])["Opportunity PAR"].sum().reset_index()
    heat_pivot = heat_df.pivot_table(index="Main Primary Service", columns="Stage", values="Opportunity PAR", fill_value=0)

    fig_heat = go.Figure(go.Heatmap(
        z=heat_pivot.values,
        x=heat_pivot.columns.tolist(),
        y=heat_pivot.index.tolist(),
        colorscale=[[0, WHITE], [0.5, MARKEN_TEAL_LIGHT], [1, MARKEN_TEAL]],
        text=[[format_currency(v) for v in row] for row in heat_pivot.values],
        texttemplate="%{text}",
        textfont=dict(family="Plus Jakarta Sans", size=10),
        hovertemplate="Service: %{y}<br>Stage: %{x}<br>Value: $%{z:,.0f}<extra></extra>",
    ))
    make_chart_layout(fig_heat, height=max(300, 50 * len(heat_pivot)))
    fig_heat.update_layout(xaxis=dict(tickfont=dict(size=10)), yaxis=dict(tickfont=dict(size=10)))
    st.plotly_chart(fig_heat, use_container_width=True)

    # ── Value Distribution ───────────────────────────────────────────────────
    st.markdown('<div class="section-header">Opportunity Value Distribution</div>', unsafe_allow_html=True)

    vc1, vc2 = st.columns(2)
    with vc1:
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(
            x=df["Opportunity PAR"],
            nbinsx=20,
            marker_color=MARKEN_TEAL,
            opacity=0.85,
        ))
        make_chart_layout(fig_hist, title="Distribution of PAR Values", height=350)
        fig_hist.update_layout(
            xaxis=dict(title="PAR Value ($)", titlefont=dict(size=10)),
            yaxis=dict(title="Count", titlefont=dict(size=10)),
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with vc2:
        fig_scatter = go.Figure()
        fig_scatter.add_trace(go.Scatter(
            x=df["Stage Duration"],
            y=df["Opportunity PAR"],
            mode="markers",
            marker=dict(
                color=[STAGE_COLORS.get(s, MARKEN_TEAL) for s in df["Stage"]],
                size=10,
                line=dict(width=1, color=WHITE),
            ),
            text=df["Account Name"],
            hovertemplate="<b>%{text}</b><br>Duration: %{x} days<br>Value: $%{y:,.0f}<extra></extra>",
        ))
        make_chart_layout(fig_scatter, title="Value vs. Stage Duration", height=350)
        fig_scatter.update_layout(
            xaxis=dict(title="Stage Duration (days)", titlefont=dict(size=10)),
            yaxis=dict(title="PAR Value ($)", titlefont=dict(size=10)),
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    # ── Close Date Timeline ──────────────────────────────────────────────────
    st.markdown('<div class="section-header">Close Date Timeline</div>', unsafe_allow_html=True)

    timeline_df = df.copy()
    timeline_df["Close Date Parsed"] = pd.to_datetime(timeline_df["Close Date"], errors="coerce")
    timeline_df = timeline_df.dropna(subset=["Close Date Parsed"]).sort_values("Close Date Parsed")

    if len(timeline_df) > 0:
        fig_timeline = go.Figure()
        fig_timeline.add_trace(go.Scatter(
            x=timeline_df["Close Date Parsed"],
            y=timeline_df["Opportunity PAR"],
            mode="markers",
            marker=dict(
                size=timeline_df["Opportunity PAR"].apply(lambda x: max(8, min(30, x / 50000))),
                color=[STAGE_COLORS.get(s, MARKEN_TEAL) for s in timeline_df["Stage"]],
                line=dict(width=1, color=WHITE),
            ),
            text=timeline_df.apply(lambda r: f"{r['Account Name']}<br>{r['Stage']}", axis=1),
            hovertemplate="<b>%{text}</b><br>Close: %{x|%b %d, %Y}<br>Value: $%{y:,.0f}<extra></extra>",
        ))
        make_chart_layout(fig_timeline, title="Expected Close Dates (bubble size = deal value)", height=380)
        fig_timeline.update_layout(
            xaxis=dict(title="Close Date", titlefont=dict(size=10)),
            yaxis=dict(title="PAR Value ($)", titlefont=dict(size=10)),
        )
        st.plotly_chart(fig_timeline, use_container_width=True)

    # ── Executive Summary Stats ──────────────────────────────────────────────
    st.markdown('<div class="section-header">Executive Summary</div>', unsafe_allow_html=True)

    total = df["Opportunity PAR"].sum()
    stage_summary = df.groupby("Stage").agg(
        Count=("Opportunity Name", "count"),
        Value=("Opportunity PAR", "sum"),
        AvgDuration=("Stage Duration", "mean"),
    ).reset_index()

    top_customer = df.groupby("Account Name")["Opportunity PAR"].sum().idxmax()
    top_customer_val = df.groupby("Account Name")["Opportunity PAR"].sum().max()
    top_service = df.groupby("Main Primary Service")["Opportunity PAR"].sum().idxmax()

    st.markdown(f"""
    <div style="background:{WHITE}; border:1px solid {NEUTRAL_200}; border-radius:10px; padding:1.5rem; font-family:'Plus Jakarta Sans',sans-serif;">
        <p style="font-size:0.85rem; color:{NEUTRAL_800}; line-height:1.7;">
            The Solutions team is currently managing <b>{len(df)} active opportunities</b> with a combined pipeline value of
            <b>{format_currency(total)}</b> across <b>{df['Account Name'].nunique()} unique customers</b>.
            The largest account by pipeline value is <b>{top_customer}</b> at {format_currency(top_customer_val)},
            and the most prevalent service type is <b>{top_service}</b>.
            Average stage duration across all opportunities is <b>{df['Stage Duration'].mean():.0f} days</b>.
        </p>
        <p style="font-size:0.85rem; color:{NEUTRAL_800}; line-height:1.7; margin-top:0.75rem;">
            The pipeline spans <b>{df['Owner Role'].nunique()} regions</b> with
            <b>{df['Solution Resource'].nunique()} solution resources</b> actively engaged.
            <b>{df['Main Primary Service'].nunique()} distinct service categories</b> are represented in the current pipeline.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center; padding:2rem 0 1rem 0; font-family:'Plus Jakarta Sans',sans-serif;">
    <div style="font-size:0.65rem; font-weight:600; color:{NEUTRAL_400}; letter-spacing:0.1em; text-transform:uppercase;">
        Marken · UPS Healthcare Precision Logistics
    </div>
    <div style="font-size:0.6rem; color:{NEUTRAL_400}; margin-top:0.2rem;">
        Solutions Team Pipeline Report · Confidential
    </div>
</div>
""", unsafe_allow_html=True)
