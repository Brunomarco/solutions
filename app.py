import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Solutions Pipeline | Marken",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# MARKEN BRAND PALETTE  (from marken.com)
# ─────────────────────────────────────────────────────────────────────────────
NAVY       = "#002B49"
NAVY_MID   = "#003A63"
TEAL       = "#00857C"
TEAL_LIGHT = "#E8F5F3"
UPS_GOLD   = "#FFB500"
WHITE      = "#FFFFFF"
GRAY_50    = "#FAFBFC"
GRAY_100   = "#F4F5F7"
GRAY_200   = "#E1E4E8"
GRAY_400   = "#A0A8B4"
GRAY_600   = "#6B7280"
GRAY_800   = "#2D3748"
BLUE_ACC   = "#2E86AB"

CHART_SEQ = [NAVY, TEAL, UPS_GOLD, BLUE_ACC, "#6C5B7B", "#E06C47", "#2ECC71", "#9B59B6", "#F39C12", "#1ABC9C"]

# ─────────────────────────────────────────────────────────────────────────────
# CSS – MBB CLEAN STYLE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Instrument+Serif&display=swap');

:root {{ --navy: {NAVY}; --teal: {TEAL}; --gold: {UPS_GOLD}; }}

.stApp {{
    background: {GRAY_50};
    font-family: 'DM Sans', -apple-system, sans-serif;
    color: {GRAY_800};
}}
h1,h2,h3,h4 {{ font-family: 'DM Sans', sans-serif; color: {NAVY}; }}

/* Sidebar */
section[data-testid="stSidebar"] {{ background: {NAVY}; }}
section[data-testid="stSidebar"] * {{ color: {WHITE} !important; font-family: 'DM Sans', sans-serif; }}
section[data-testid="stSidebar"] .stRadio label {{ font-size: 0.78rem; font-weight: 500; letter-spacing: 0.04em; }}
section[data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,0.12); }}

/* Header */
.rh {{
    background: {NAVY};
    padding: 1.6rem 2rem 1.4rem;
    border-radius: 6px;
    margin-bottom: 1.2rem;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
}}
.rh-brand {{ font-size:.62rem; font-weight:600; letter-spacing:.22em; text-transform:uppercase; color:{UPS_GOLD}; margin-bottom:.35rem; }}
.rh-title {{ font-family:'Instrument Serif',Georgia,serif; font-size:1.5rem; color:{WHITE}; line-height:1.2; }}
.rh-sub {{ font-size:.78rem; color:rgba(255,255,255,0.55); margin-top:.25rem; }}
.rh-right {{ text-align:right; }}
.rh-date {{ font-size:.72rem; color:rgba(255,255,255,0.5); font-weight:500; }}
.rh-conf {{ font-size:.58rem; color:{UPS_GOLD}; font-weight:600; letter-spacing:.12em; text-transform:uppercase; margin-top:.15rem; }}

/* KPIs */
.kr {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(155px,1fr)); gap:.75rem; margin-bottom:1.2rem; }}
.kp {{
    background:{WHITE}; border:1px solid {GRAY_200}; border-top:3px solid var(--ac,{TEAL});
    border-radius:4px; padding:1rem 1.1rem .85rem;
}}
.kp-l {{ font-size:.62rem; font-weight:600; letter-spacing:.1em; text-transform:uppercase; color:{GRAY_400}; margin-bottom:.3rem; }}
.kp-v {{ font-size:1.55rem; font-weight:700; color:{NAVY}; letter-spacing:-.03em; line-height:1.1; }}
.kp-d {{ font-size:.7rem; color:{GRAY_600}; margin-top:.15rem; }}

/* Section label */
.sec {{ font-size:.65rem; font-weight:700; letter-spacing:.14em; text-transform:uppercase; color:{NAVY};
    margin:1.4rem 0 .55rem 0; padding-bottom:.35rem; border-bottom:2px solid {TEAL}; display:inline-block; }}

/* Summary */
.es {{ background:{WHITE}; border-left:4px solid {TEAL}; border-radius:0 4px 4px 0;
    padding:1.1rem 1.4rem; font-size:.82rem; line-height:1.65; color:{GRAY_800}; }}
.es b {{ color:{NAVY}; }}

/* Workflow */
.wf {{ background:{TEAL_LIGHT}; border:1px solid {TEAL}33; border-radius:4px;
    padding:1rem 1.2rem; font-size:.82rem; line-height:1.55; color:{GRAY_800}; margin-bottom:1rem; }}
.wf b {{ color:{NAVY}; }}
.ws {{ display:inline-flex; align-items:center; gap:.4rem; background:{NAVY}; color:{WHITE};
    font-size:.65rem; font-weight:600; padding:.18rem .55rem; border-radius:3px; letter-spacing:.03em; margin-right:.25rem; }}

/* Footer */
.ft {{ text-align:center; padding:1.8rem 0 .8rem; font-size:.6rem; color:{GRAY_400}; letter-spacing:.06em; }}

/* Hide chrome */
#MainMenu, footer, header {{ visibility:hidden; }}

/* Widget tweaks */
.stTabs [data-baseweb="tab"] {{ font-family:'DM Sans',sans-serif; font-weight:600; font-size:.8rem; }}
.stDownloadButton button {{
    background:{NAVY} !important; color:{WHITE} !important; border:none !important;
    font-family:'DM Sans',sans-serif !important; font-weight:600 !important; font-size:.78rem !important;
}}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
SF_COLS = [
    "Stage","Solution Resource","Account Name","Owner Role",
    "Opportunity Name","Opportunity Owner","Main Primary Service",
    "Opportunity PAR","Stage Duration","Close Date","Notes",
]
TEAM_COLS = ["Solutions Notes","Tasks","Action Items","Comments / Results"]
ALL_COLS  = SF_COLS + TEAM_COLS


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def clean_upload(df):
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")].copy()
    rename = {}
    for c in df.columns:
        for s in SF_COLS + TEAM_COLS:
            if c.strip().lower().replace(" ","") == s.lower().replace(" ",""):
                rename[c] = s
    df.rename(columns=rename, inplace=True)
    if "Opportunity PAR" in df.columns:
        df["Opportunity PAR"] = pd.to_numeric(df["Opportunity PAR"], errors="coerce").fillna(0)
    if "Stage Duration" in df.columns:
        df["Stage Duration"] = pd.to_numeric(df["Stage Duration"], errors="coerce").fillna(0).astype(int)
    if "Close Date" in df.columns:
        df["Close Date"] = pd.to_datetime(df["Close Date"], errors="coerce", dayfirst=False).dt.strftime("%m/%d/%Y")
    return df.reset_index(drop=True)


def merge_masterfile(master, new_sf):
    for c in TEAM_COLS:
        if c not in master.columns:
            master[c] = ""
    old_opps = set(master["Opportunity Name"].dropna())
    new_opps = set(new_sf["Opportunity Name"].dropna())
    updated = 0
    for idx, row in master.iterrows():
        opp = row.get("Opportunity Name")
        if opp in new_opps:
            match = new_sf[new_sf["Opportunity Name"] == opp].iloc[0]
            for c in SF_COLS:
                if c in new_sf.columns:
                    master.at[idx, c] = match[c]
            updated += 1
    added_opps = new_opps - old_opps
    new_rows = new_sf[new_sf["Opportunity Name"].isin(added_opps)].copy()
    for c in TEAM_COLS:
        new_rows[c] = ""
    master = pd.concat([master, new_rows], ignore_index=True)
    removed_opps = old_opps - new_opps
    for opp in removed_opps:
        mask = master["Opportunity Name"] == opp
        master.loc[mask, "Solutions Notes"] = master.loc[mask, "Solutions Notes"].fillna("").astype(str) + " [Removed from SF]"
    cols = [c for c in ALL_COLS if c in master.columns]
    stats = {"updated": updated, "added": len(added_opps), "removed": len(removed_opps), "total": len(master)}
    return master[cols].reset_index(drop=True), stats


def fc(v):
    if pd.isna(v) or v == 0: return "$0"
    if abs(v) >= 1e6: return f"${v/1e6:,.1f}M"
    if abs(v) >= 1e3: return f"${v/1e3:,.0f}K"
    return f"${v:,.0f}"


def pl(fig, h=340, mb=30):
    fig.update_layout(
        font=dict(family="DM Sans,sans-serif", size=11, color=GRAY_800),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=h, margin=dict(l=10,r=10,t=32,b=mb),
        legend=dict(font=dict(size=10), orientation="h", y=-0.18, x=0.5, xanchor="center"),
    )
    fig.update_xaxes(gridcolor=GRAY_200, showline=True, linecolor=GRAY_200, linewidth=1)
    fig.update_yaxes(gridcolor=GRAY_200, showline=True, linecolor=GRAY_200, linewidth=1)
    return fig


def to_excel(df):
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="Masterfile")
        ws = w.sheets["Masterfile"]
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        hf = PatternFill("solid", fgColor="002B49")
        hw = Font(name="Calibri", bold=True, color="FFFFFF", size=10)
        tf = PatternFill("solid", fgColor="E8F5F3")
        bd = Border(*(Side(style="thin", color="E1E4E8"),)*4)
        for ci, cn in enumerate(df.columns, 1):
            cell = ws.cell(row=1, column=ci)
            cell.fill, cell.font, cell.border = hf, hw, bd
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            if cn in TEAM_COLS:
                for ri in range(2, len(df)+2):
                    ws.cell(row=ri, column=ci).fill = tf
            ml = max(len(str(cn)), *(len(str(x)) for x in df[cn].head(50))) if len(df) else len(str(cn))
            ws.column_dimensions[ws.cell(1, ci).column_letter].width = min(ml+4, 42)
        bf = Font(name="Calibri", size=10)
        for ri in range(2, len(df)+2):
            for ci in range(1, len(df.columns)+1):
                c = ws.cell(row=ri, column=ci)
                c.font, c.border = bf, bd
                c.alignment = Alignment(vertical="center", wrap_text=True)
    return buf.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
if "master" not in st.session_state:
    st.session_state.master = None


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:1.2rem 0 1rem; text-align:center;">
        <div style="font-size:.58rem; font-weight:700; letter-spacing:.24em; color:{UPS_GOLD}; text-transform:uppercase;">Marken · UPS Healthcare</div>
        <div style="font-size:1rem; font-weight:700; color:{WHITE}; margin-top:.2rem;">Solutions Pipeline</div>
        <div style="font-size:.65rem; color:rgba(255,255,255,0.4); margin-top:.15rem;">Precision Logistics</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    page = st.radio("", ["Dashboard", "Masterfile Manager"], label_visibility="collapsed")
    st.divider()
    st.markdown(f'<div style="font-size:.6rem; color:rgba(255,255,255,0.3); text-align:center; line-height:1.5;">Report generated<br>{datetime.now().strftime("%d %b %Y · %H:%M")}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="rh">
    <div>
        <div class="rh-brand">Marken · UPS Healthcare Precision Logistics</div>
        <div class="rh-title">Solutions Team — Global Pipeline Report</div>
        <div class="rh-sub">Opportunity overview &amp; masterfile management</div>
    </div>
    <div class="rh-right">
        <div class="rh-date">{datetime.now().strftime('%d %B %Y')}</div>
        <div class="rh-conf">Confidential</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# INITIAL UPLOAD
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.master is None:
    st.markdown("""<div class="wf"><b>Getting started</b> — Upload your Salesforce export or an existing Masterfile (.xlsx / .csv). The app detects the file type and adds team columns if needed.</div>""", unsafe_allow_html=True)
    f = st.file_uploader("Upload Salesforce Export or Masterfile", type=["xlsx","xls","csv"], label_visibility="collapsed")
    if f:
        raw = pd.read_csv(f) if f.name.endswith(".csv") else pd.read_excel(f)
        cleaned = clean_upload(raw)
        for c in TEAM_COLS:
            if c not in cleaned.columns:
                cleaned[c] = ""
        cols = [c for c in ALL_COLS if c in cleaned.columns]
        st.session_state.master = cleaned[cols]
        st.rerun()
    st.stop()

df = st.session_state.master.copy()
df["Opportunity PAR"] = pd.to_numeric(df.get("Opportunity PAR", 0), errors="coerce").fillna(0)
df["Stage Duration"]  = pd.to_numeric(df.get("Stage Duration", 0), errors="coerce").fillna(0).astype(int)


# ═════════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ═════════════════════════════════════════════════════════════════════════════
if page == "Dashboard":

    with st.expander("Filters", expanded=False):
        f1,f2,f3 = st.columns(3)
        sel_st = f1.multiselect("Stage", sorted(df["Stage"].dropna().unique()), default=sorted(df["Stage"].dropna().unique()))
        sel_sv = f2.multiselect("Service", sorted(df["Main Primary Service"].dropna().unique()), default=sorted(df["Main Primary Service"].dropna().unique()))
        sel_rg = f3.multiselect("Region", sorted(df["Owner Role"].dropna().unique()), default=sorted(df["Owner Role"].dropna().unique()))

    fdf = df[df["Stage"].isin(sel_st) & df["Main Primary Service"].isin(sel_sv) & df["Owner Role"].isin(sel_rg)]

    total_val = fdf["Opportunity PAR"].sum()
    n_opp     = len(fdf)
    n_cust    = fdf["Account Name"].nunique()
    n_svc     = fdf["Main Primary Service"].nunique()
    avg_deal  = fdf["Opportunity PAR"].mean() if n_opp else 0
    avg_dur   = fdf["Stage Duration"].mean() if n_opp else 0

    # KPIs
    st.markdown(f"""
    <div class="kr">
        <div class="kp" style="--ac:{TEAL};"><div class="kp-l">Total Pipeline Value</div><div class="kp-v">{fc(total_val)}</div><div class="kp-d">{n_opp} active opportunities</div></div>
        <div class="kp" style="--ac:{NAVY};"><div class="kp-l">Customers</div><div class="kp-v">{n_cust}</div><div class="kp-d">Unique accounts</div></div>
        <div class="kp" style="--ac:{UPS_GOLD};"><div class="kp-l">Products in Scope</div><div class="kp-v">{n_svc}</div><div class="kp-d">Service categories</div></div>
        <div class="kp" style="--ac:{BLUE_ACC};"><div class="kp-l">Avg Deal Size</div><div class="kp-v">{fc(avg_deal)}</div><div class="kp-d">Per opportunity</div></div>
        <div class="kp" style="--ac:{GRAY_400};"><div class="kp-l">Avg Stage Duration</div><div class="kp-v">{avg_dur:.0f} <span style="font-size:.85rem;font-weight:500;">days</span></div><div class="kp-d">In current stage</div></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Row 1: Pipeline by Stage | Products in Scope ─────────────────────────
    r1a, r1b = st.columns([1.1, 0.9])

    with r1a:
        st.markdown('<div class="sec">Pipeline by Stage</div>', unsafe_allow_html=True)
        sg = fdf.groupby("Stage").agg(Value=("Opportunity PAR","sum"), Count=("Opportunity Name","count")).reset_index().sort_values("Value", ascending=True)
        fig1 = go.Figure(go.Bar(
            y=sg["Stage"], x=sg["Value"], orientation="h", marker_color=NAVY,
            text=[f"  {fc(v)}  ·  {c} opp{'s' if c>1 else ''}" for v,c in zip(sg["Value"],sg["Count"])],
            textposition="outside", textfont=dict(size=10.5, color=GRAY_800),
        ))
        pl(fig1, h=max(220, 50*len(sg)))
        fig1.update_layout(showlegend=False, xaxis=dict(visible=False), yaxis=dict(tickfont=dict(size=11, color=NAVY)))
        fig1.update_xaxes(showgrid=False, showline=False); fig1.update_yaxes(showgrid=False, showline=False)
        st.plotly_chart(fig1, use_container_width=True)

    with r1b:
        st.markdown('<div class="sec">Products in Scope</div>', unsafe_allow_html=True)
        sv = fdf.groupby("Main Primary Service")["Opportunity PAR"].sum().reset_index().sort_values("Opportunity PAR", ascending=False)
        fig2 = go.Figure(go.Pie(
            labels=sv["Main Primary Service"], values=sv["Opportunity PAR"], hole=.52,
            marker=dict(colors=CHART_SEQ[:len(sv)]),
            textinfo="label+percent", textfont=dict(size=10),
            hovertemplate="<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}<extra></extra>", sort=True,
        ))
        pl(fig2, h=max(220, 50*len(sg))); fig2.update_layout(showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    # ── Row 2: Top Customers | Regional Split ────────────────────────────────
    r2a, r2b = st.columns([1.1, 0.9])

    with r2a:
        st.markdown('<div class="sec">Top 10 Customers by Pipeline Value</div>', unsafe_allow_html=True)
        cu = fdf.groupby("Account Name").agg(Value=("Opportunity PAR","sum"), Count=("Opportunity Name","count")).reset_index().sort_values("Value", ascending=True).tail(10)
        fig3 = go.Figure(go.Bar(
            y=cu["Account Name"], x=cu["Value"], orientation="h",
            marker=dict(color=cu["Value"], colorscale=[[0,"#B2DFDB"],[.5,TEAL],[1,NAVY]], showscale=False),
            text=[f"  {fc(v)}  ({c})" for v,c in zip(cu["Value"],cu["Count"])],
            textposition="outside", textfont=dict(size=10, color=GRAY_800),
        ))
        pl(fig3, h=max(300, 38*len(cu)))
        fig3.update_layout(showlegend=False, xaxis=dict(visible=False), yaxis=dict(tickfont=dict(size=10)))
        fig3.update_xaxes(showgrid=False, showline=False); fig3.update_yaxes(showgrid=False, showline=False)
        st.plotly_chart(fig3, use_container_width=True)

    with r2b:
        st.markdown('<div class="sec">Pipeline by Region</div>', unsafe_allow_html=True)
        rg = fdf.groupby("Owner Role").agg(Value=("Opportunity PAR","sum"), Count=("Opportunity Name","count")).reset_index().sort_values("Value", ascending=False)
        fig4 = go.Figure(go.Bar(
            x=rg["Owner Role"], y=rg["Value"],
            marker_color=[NAVY,TEAL,UPS_GOLD,BLUE_ACC,GRAY_600][:len(rg)],
            text=[f"{fc(v)}<br><span style='font-size:9px;color:{GRAY_600}'>{c} opps</span>" for v,c in zip(rg["Value"],rg["Count"])],
            textposition="inside", textfont=dict(size=11, color=WHITE),
        ))
        pl(fig4, h=max(300, 38*len(cu)))
        fig4.update_layout(showlegend=False, yaxis=dict(visible=False))
        fig4.update_xaxes(showgrid=False, tickfont=dict(size=10)); fig4.update_yaxes(showgrid=False, showline=False)
        st.plotly_chart(fig4, use_container_width=True)

    # ── Row 3: Solution Resource Workload ────────────────────────────────────
    st.markdown('<div class="sec">Solution Resource Workload</div>', unsafe_allow_html=True)
    rs = fdf.groupby("Solution Resource").agg(Value=("Opportunity PAR","sum"), Count=("Opportunity Name","count"), AvgDur=("Stage Duration","mean")).reset_index().sort_values("Value", ascending=False)

    rc1, rc2 = st.columns([.55,.45])
    with rc1:
        fig5 = go.Figure()
        fig5.add_trace(go.Bar(x=rs["Solution Resource"], y=rs["Count"], name="Opportunities", marker_color=NAVY, yaxis="y",
            text=rs["Count"], textposition="auto", textfont=dict(color=WHITE, size=10)))
        fig5.add_trace(go.Scatter(x=rs["Solution Resource"], y=rs["Value"], name="Total Value ($)",
            mode="markers+lines", marker=dict(color=UPS_GOLD, size=9, line=dict(width=1.5, color=NAVY)),
            line=dict(color=UPS_GOLD, width=2), yaxis="y2"))
        pl(fig5, h=320, mb=50)
        fig5.update_layout(
            yaxis=dict(title="# Opportunities", titlefont=dict(size=10), side="left"),
            yaxis2=dict(title="Pipeline Value ($)", titlefont=dict(size=10), side="right", overlaying="y", showgrid=False),
            xaxis=dict(tickangle=20, tickfont=dict(size=9)), legend=dict(font=dict(size=9)),
        )
        st.plotly_chart(fig5, use_container_width=True)
    with rc2:
        rd = rs.rename(columns={"Solution Resource":"Resource","Count":"Opps","Value":"Total Value","AvgDur":"Avg Days"}).copy()
        rd["Total Value"] = rd["Total Value"].apply(lambda x: f"${x:,.0f}")
        rd["Avg Days"] = rd["Avg Days"].apply(lambda x: f"{x:.0f}")
        st.dataframe(rd, use_container_width=True, height=320, hide_index=True)

    # ── Full Pipeline Table ──────────────────────────────────────────────────
    st.markdown('<div class="sec">Full Pipeline Detail</div>', unsafe_allow_html=True)
    tbl = fdf[["Stage","Account Name","Opportunity Name","Solution Resource","Opportunity Owner",
               "Main Primary Service","Opportunity PAR","Stage Duration","Close Date","Notes"]].copy()
    tbl = tbl.sort_values(["Stage","Opportunity PAR"], ascending=[True,False])
    st.dataframe(
        tbl.style.format({"Opportunity PAR":"${:,.0f}"}),
        use_container_width=True, height=min(500, 35*len(tbl)+38), hide_index=True,
        column_config={
            "Account Name": st.column_config.TextColumn("Customer", width="medium"),
            "Opportunity Name": st.column_config.TextColumn("Opportunity", width="large"),
            "Opportunity PAR": st.column_config.TextColumn("PAR ($)", width="small"),
            "Stage Duration": st.column_config.NumberColumn("Days", width="small"),
            "Main Primary Service": st.column_config.TextColumn("Service", width="medium"),
            "Solution Resource": st.column_config.TextColumn("Sol. Resource", width="medium"),
        },
    )

    # ── Executive Summary ────────────────────────────────────────────────────
    st.markdown('<div class="sec">Executive Summary</div>', unsafe_allow_html=True)
    top_cust = fdf.groupby("Account Name")["Opportunity PAR"].sum().idxmax() if n_opp else "N/A"
    top_cust_v = fdf.groupby("Account Name")["Opportunity PAR"].sum().max() if n_opp else 0
    top_svc = fdf.groupby("Main Primary Service")["Opportunity PAR"].sum().idxmax() if n_opp else "N/A"
    n_design = len(fdf[fdf["Stage"]=="Solutions Design"])
    n_proposal = len(fdf[fdf["Stage"].str.contains("Proposal|Price", case=False, na=False)])
    n_nego = len(fdf[fdf["Stage"]=="Negotiations"])

    st.markdown(f"""
    <div class="es">
        The Solutions team is currently managing <b>{n_opp} active opportunities</b> representing
        a total pipeline value of <b>{fc(total_val)}</b> across <b>{n_cust} unique customers</b>
        and <b>{n_svc} service categories</b>.
        <br><br>
        Of these, <b>{n_design}</b> are in Solutions Design, <b>{n_proposal}</b> in Proposal / Price Quote,
        and <b>{n_nego}</b> in Negotiations. The largest account by pipeline value is
        <b>{top_cust}</b> ({fc(top_cust_v)}), and the dominant service type is <b>{top_svc}</b>.
        <br><br>
        Pipeline coverage spans <b>{fdf['Owner Role'].nunique()} regions</b>
        with <b>{fdf['Solution Resource'].nunique()} Solution Resources</b> actively engaged.
        Average stage duration stands at <b>{avg_dur:.0f} days</b>, with individual opportunities ranging
        from {fdf['Stage Duration'].min()} to {fdf['Stage Duration'].max()} days.
    </div>
    """, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
#  MASTERFILE MANAGER
# ═════════════════════════════════════════════════════════════════════════════
elif page == "Masterfile Manager":

    st.markdown(f"""
    <div class="wf">
        <b>Workflow</b><br><br>
        <span class="ws">1</span> Download fresh data from Salesforce<br>
        <span class="ws">2</span> Upload here — the app <b>merges</b> new SF data into the Masterfile<br>
        <span class="ws">3</span> Salesforce fields are refreshed · <b>Team columns are preserved</b> (Solutions Notes, Tasks, Action Items, Comments)<br>
        <span class="ws">4</span> Edit team columns inline below<br>
        <span class="ws">5</span> Download the updated Masterfile
    </div>
    """, unsafe_allow_html=True)

    # Merge upload
    st.markdown('<div class="sec">Upload New Salesforce Export to Merge</div>', unsafe_allow_html=True)
    mf = st.file_uploader("Upload new Salesforce export. Team columns in the current Masterfile will be preserved.", type=["xlsx","xls","csv"], key="mu")
    if mf:
        raw = pd.read_csv(mf) if mf.name.endswith(".csv") else pd.read_excel(mf)
        new_sf = clean_upload(raw)
        merged, stats = merge_masterfile(st.session_state.master.copy(), new_sf)
        st.session_state.master = merged
        st.success(f"Merge complete — **{stats['updated']}** updated · **{stats['added']}** added · **{stats['removed']}** flagged removed · **{stats['total']}** total rows")
        st.rerun()

    # Editable table
    st.markdown('<div class="sec">Masterfile — Editable</div>', unsafe_allow_html=True)
    st.caption("Salesforce columns are locked. Edit the four team columns (highlighted teal in the Excel download).")

    edf = st.session_state.master.copy()
    for c in TEAM_COLS:
        if c not in edf.columns:
            edf[c] = ""

    edited = st.data_editor(
        edf, use_container_width=True, height=min(600, 35*len(edf)+38), num_rows="dynamic",
        column_config={
            "Stage": st.column_config.TextColumn("Stage", disabled=True),
            "Account Name": st.column_config.TextColumn("Customer", disabled=True),
            "Opportunity Name": st.column_config.TextColumn("Opportunity", disabled=True, width="large"),
            "Opportunity PAR": st.column_config.NumberColumn("PAR ($)", format="$%d", disabled=True),
            "Stage Duration": st.column_config.NumberColumn("Days", disabled=True),
            "Close Date": st.column_config.TextColumn("Close", disabled=True),
            "Owner Role": st.column_config.TextColumn("Region", disabled=True),
            "Opportunity Owner": st.column_config.TextColumn("Opp Owner", disabled=True),
            "Solution Resource": st.column_config.TextColumn("Sol. Resource", disabled=True),
            "Main Primary Service": st.column_config.TextColumn("Service", disabled=True),
            "Notes": st.column_config.TextColumn("SF Notes", disabled=True),
            "Solutions Notes": st.column_config.TextColumn("Solutions Notes", width="large"),
            "Tasks": st.column_config.TextColumn("Tasks", width="large"),
            "Action Items": st.column_config.TextColumn("Action Items", width="large"),
            "Comments / Results": st.column_config.TextColumn("Comments / Results", width="large"),
        },
        hide_index=True, key="editor",
    )

    if st.button("Save edits", type="primary"):
        st.session_state.master = edited.copy()
        st.success("Edits saved to session.")

    st.markdown("---")
    d1, d2, _ = st.columns([1,1,2])
    with d1:
        st.download_button("Download Masterfile (.xlsx)", data=to_excel(st.session_state.master),
            file_name=f"Solutions_Masterfile_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with d2:
        st.download_button("Download Masterfile (.csv)", data=st.session_state.master.to_csv(index=False).encode(),
            file_name=f"Solutions_Masterfile_{datetime.now().strftime('%Y-%m-%d')}.csv", mime="text/csv")


# Footer
st.markdown(f'<div class="ft">MARKEN · UPS HEALTHCARE PRECISION LOGISTICS &nbsp;|&nbsp; SOLUTIONS TEAM PIPELINE REPORT &nbsp;|&nbsp; CONFIDENTIAL</div>', unsafe_allow_html=True)
