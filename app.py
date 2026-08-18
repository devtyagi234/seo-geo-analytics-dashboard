import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
from data_processor import load_clean_seo_data, load_clean_geo_data

# Page configuration for a professional SaaS feel
st.set_page_config(
    page_title="Helix Search Audit | Enterprise SEO/GEO Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium CSS Injector
st.markdown("""
<style>
    /* Import modern clean font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Core header styles */
    .dashboard-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.2rem;
        letter-spacing: -0.025em;
    }
    .dashboard-subtitle {
        font-size: 1.05rem;
        color: #64748b;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Metric Cards Grid Layout */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.25rem;
        margin-bottom: 2rem;
    }
    @media (max-width: 768px) {
        .metric-grid {
            grid-template-columns: 1fr;
        }
    }
    
    /* Premium Metric Card */
    .card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease-in-out;
    }
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -4px rgba(0, 0, 0, 0.05);
        border-color: #cbd5e1;
    }
    .card-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    .card-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #0f172a;
        letter-spacing: -0.03em;
        display: inline-block;
    }
    
    /* Trend badges */
    .badge {
        display: inline-flex;
        align-items: center;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.25rem 0.5rem;
        border-radius: 9999px;
        margin-left: 0.75rem;
        vertical-align: middle;
    }
    .badge-positive {
        background-color: #ecfdf5;
        color: #059669;
    }
    .badge-negative {
        background-color: #fef2f2;
        color: #dc2626;
    }
    .badge-neutral {
        background-color: #f1f5f9;
        color: #64748b;
    }
    
    /* Executive Briefing Cards */
    .briefing-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.02);
    }
    .briefing-card h4 {
        margin-top: 0;
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e293b;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .briefing-card p {
        font-size: 0.95rem;
        color: #475569;
        line-height: 1.5;
        margin-bottom: 0.5rem;
    }
    .briefing-card .action-label {
        font-size: 0.8rem;
        font-weight: 700;
        color: #2563eb;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.75rem;
    }
    .border-info { border-left: 5px solid #3b82f6; }
    .border-success { border-left: 5px solid #10b981; }
    .border-warning { border-left: 5px solid #f59e0b; }
    .border-danger { border-left: 5px solid #ef4444; }
    
    /* Custom Sidebar adjustments */
    .sidebar .sidebar-content {
        background-color: #f8fafc;
    }
    
    /* Highlight code blocks in card descriptions */
    code {
        background-color: #f1f5f9;
        color: #0f172a;
        padding: 0.125rem 0.25rem;
        border-radius: 4px;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 0.85em;
    }
</style>
""", unsafe_allow_html=True)

# Cache data loading pipelines
@st.cache_data
def get_seo_data():
    return load_clean_seo_data("data/seo_data_processed.csv")

@st.cache_data
def get_geo_data():
    return load_clean_geo_data("data/geo_citations_processed.csv")

try:
    seo_raw = get_seo_data()
    geo_raw = get_geo_data()
except Exception as e:
    import os
    st.error(f"Error loading datasets: {e}")
    st.info(f"**Diagnostic Info:**")
    st.write(f"- **Current Working Directory:** `{os.getcwd()}`")
    st.write(f"- **Dashboard Script Path:** `{os.path.abspath(__file__)}`")
    st.write(f"- **Data Directory Contents:** `{os.listdir('data') if os.path.exists('data') else 'data directory not found'}`")
    st.stop()

# ----------------- SIDEBAR FILTER PANELS -----------------
st.sidebar.markdown("### 🎛️ Control Panel")

# Client selector
client_option = st.sidebar.selectbox(
    "Select Client Portfolio",
    options=["Client A", "Client B"],
    format_func=lambda x: f"Client A (Healthcare)" if x == "Client A" else f"Client B (Wellness)"
)

# Date filter
min_date = seo_raw["date"].min().date()
max_date = seo_raw["date"].max().date()
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

# Page type filter
available_page_types = seo_raw[seo_raw["client"] == client_option]["page_type"].unique().tolist()
selected_page_types = st.sidebar.multiselect(
    "Filter by Page Type",
    options=available_page_types,
    default=available_page_types
)

# Query search filter
query_search = st.sidebar.text_input("Search Queries / Keywords", value="", placeholder="Enter keyword...")

# ----------------- DATA SUBSET FILTERING -----------------
filtered_seo = seo_raw[
    (seo_raw["client"] == client_option) &
    (seo_raw["date"].dt.date >= start_date) &
    (seo_raw["date"].dt.date <= end_date) &
    (seo_raw["page_type"].isin(selected_page_types))
]

if query_search:
    filtered_seo = filtered_seo[filtered_seo["query"].str.contains(query_search, case=False, na=False)]

filtered_geo = geo_raw[
    (geo_raw["client"] == client_option) &
    (geo_raw["week_start_date"].dt.date >= start_date) &
    (geo_raw["week_start_date"].dt.date <= end_date)
]

# Calculate previous period data for WoW comparison
date_diff = (end_date - start_date).days + 1
prev_start = start_date - datetime.timedelta(days=date_diff)
prev_end = start_date - datetime.timedelta(days=1)

prev_seo = seo_raw[
    (seo_raw["client"] == client_option) &
    (seo_raw["date"].dt.date >= prev_start) &
    (seo_raw["date"].dt.date <= prev_end) &
    (seo_raw["page_type"].isin(selected_page_types))
]
if query_search:
    prev_seo = prev_seo[prev_seo["query"].str.contains(query_search, case=False, na=False)]

if filtered_seo.empty:
    st.warning("No search records found matching the current criteria. Adjust filters.")
    st.stop()

# ----------------- KPI MATH & COMPUTATION -----------------
total_clicks = filtered_seo["clicks"].sum()
total_impressions = filtered_seo["impressions"].sum()
avg_ctr = total_clicks / total_impressions if total_impressions > 0 else 0.0
avg_pos = filtered_seo["position"].mean()

prev_clicks = prev_seo["clicks"].sum()
prev_impressions = prev_seo["impressions"].sum()
prev_ctr = prev_clicks / prev_impressions if prev_impressions > 0 else 0.0
prev_pos = prev_seo["position"].mean()

clicks_delta = ((total_clicks - prev_clicks) / prev_clicks * 100) if prev_clicks > 0 else 0.0
impressions_delta = ((total_impressions - prev_impressions) / prev_impressions * 100) if prev_impressions > 0 else 0.0
ctr_delta = (avg_ctr - prev_ctr) * 100 
pos_delta = avg_pos - prev_pos 

# ----------------- TITLE HERO SECTION -----------------
st.markdown('<h1 class="dashboard-title">Helix Search Audit</h1>', unsafe_allow_html=True)
desc = "Patient Acquisition & Local Services Optimization" if client_option == "Client A" else "Core Wellness Services & Subscription Insights"
st.markdown(f'<div class="dashboard-subtitle">SEO & GEO (Generative Engine Optimization) Citation Dashboard | <strong>{client_option} ({desc})</strong></div>', unsafe_allow_html=True)

# ----------------- RENDER METRIC CARDS GRID -----------------
# Setup HTML trend badges
clicks_badge = f'<span class="badge badge-positive">▲ {clicks_delta:+.1f}% WoW</span>' if clicks_delta >= 0 else f'<span class="badge badge-negative">▼ {clicks_delta:.1f}% WoW</span>'
impressions_badge = f'<span class="badge badge-positive">▲ {impressions_delta:+.1f}% WoW</span>' if impressions_delta >= 0 else f'<span class="badge badge-negative">▼ {impressions_delta:.1f}% WoW</span>'
ctr_badge = f'<span class="badge badge-positive">▲ {ctr_delta:+.2f} pp</span>' if ctr_delta >= 0 else f'<span class="badge badge-negative">▼ {abs(ctr_delta):.2f} pp</span>'
# Lower rank position is better, so color code negatively if it goes up
pos_badge = f'<span class="badge badge-positive">▲ {-pos_delta:+.1f} ranks</span>' if pos_delta <= 0 else f'<span class="badge badge-negative">▼ {pos_delta:+.1f} ranks</span>'

if prev_clicks == 0: clicks_badge = '<span class="badge badge-neutral">N/A</span>'
if prev_impressions == 0: impressions_badge = '<span class="badge badge-neutral">N/A</span>'
if prev_ctr == 0: ctr_badge = '<span class="badge badge-neutral">N/A</span>'
if np.isnan(prev_pos): pos_badge = '<span class="badge badge-neutral">N/A</span>'

st.markdown(f"""
<div class="metric-grid">
    <div class="card">
        <div class="card-label">Total Clicks</div>
        <div>
            <div class="card-value">{total_clicks:,}</div>
            {clicks_badge}
        </div>
    </div>
    <div class="card">
        <div class="card-label">Total Impressions</div>
        <div>
            <div class="card-value">{total_impressions:,}</div>
            {impressions_badge}
        </div>
    </div>
    <div class="card">
        <div class="card-label">Average CTR</div>
        <div>
            <div class="card-value">{avg_ctr * 100:.2f}%</div>
            {ctr_badge}
        </div>
    </div>
    <div class="card">
        <div class="card-label">Average Position</div>
        <div>
            <div class="card-value">{avg_pos:.1f}</div>
            {pos_badge}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------- TABS SYSTEM -----------------
tab1, tab2, tab3 = st.tabs([
    "📊 Traditional & AI Search Analysis", 
    "🔑 Keyword & Landing Page Reports", 
    "💡 Strategic Executive Briefing"
])

with tab1:
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("#### CTR vs. Search Rank Performance")
        st.caption("Fitted expected click-through rate curve vs. actual queries. Sub-baseline bubbles represent target optimization opportunities.")
        
        # Prepare query data for Seaborn plot
        plot_df = filtered_seo.groupby("query").agg(
            clicks=("clicks", "sum"),
            impressions=("impressions", "sum"),
            avg_position=("position", "mean")
        ).reset_index()
        plot_df["ctr"] = plot_df["clicks"] / plot_df["impressions"]
        plot_df = plot_df[plot_df["impressions"] >= 10]
        
        if not plot_df.empty:
            fig, ax = plt.subplots(figsize=(10, 6.5), dpi=150)
            
            # Premium color choices
            sns.scatterplot(
                data=plot_df,
                x="avg_position",
                y="ctr",
                size="impressions",
                sizes=(40, 400),
                alpha=0.6,
                color="#2563eb",
                edgecolor="#ffffff",
                linewidth=1,
                ax=ax
            )
            
            # Draw expected CTR baseline curve
            x_curve = np.linspace(1, max(plot_df["avg_position"]), 100)
            y_curve = 0.35 / (x_curve ** 0.85)
            ax.plot(x_curve, y_curve, color="#ef4444", linestyle="--", linewidth=2, label="Expected Organic Baseline")
            
            # Calculate correlation
            p_corr = plot_df["avg_position"].corr(plot_df["ctr"], method="pearson")
            
            # Customize graph lines and spines
            ax.set_title(f"CTR vs Rank Distribution (Pearson r: {p_corr:.2f})", fontsize=11, fontweight='600', color='#0f172a', pad=12)
            ax.set_xlabel("Average Organic Position", fontsize=10, fontweight='500', color='#475569')
            ax.set_ylabel("Click-Through Rate (CTR)", fontsize=10, fontweight='500', color='#475569')
            ax.set_xlim(0.8, max(plot_df["avg_position"]) + 1)
            ax.set_ylim(-0.01, max(plot_df["ctr"]) + 0.05)
            ax.grid(True, linestyle=":", alpha=0.6, color="#cbd5e1")
            ax.legend(loc="upper right", frameon=True, facecolor="#ffffff", edgecolor="#e2e8f0")
            
            # Styling tick parameters
            ax.tick_params(colors='#475569', labelsize=9)
            sns.despine()
            st.pyplot(fig)
            plt.close()
        else:
            st.info("Insufficient query records to fit standard curve.")

    with col_right:
        st.markdown("#### SEO Organic Clicks vs. AI Citations")
        st.caption("Overlay of Google organic clicks against citations across ChatGPT, Perplexity, and Google AI Overviews.")
        
        # Aggregate week-over-week GEO
        filtered_seo_weekly = filtered_seo.copy()
        filtered_seo_weekly["week_start"] = filtered_seo_weekly["date"].dt.to_period("W").dt.start_time
        weekly_seo = filtered_seo_weekly.groupby("week_start").agg(
            clicks=("clicks", "sum")
        ).reset_index()
        
        weekly_geo = filtered_geo.groupby("week_start_date").agg(
            citations=("citation_count", "sum")
        ).reset_index()
        weekly_geo["week_start"] = pd.to_datetime(weekly_geo["week_start_date"])
        
        merged_chart = pd.merge(weekly_seo, weekly_geo, on="week_start", how="inner")
        
        if not merged_chart.empty:
            fig, ax1 = plt.subplots(figsize=(10, 6.5), dpi=150)
            
            # Primary line: Organic clicks
            color_seo = "#2563eb"
            ax1.set_xlabel("Week Start Date", fontsize=10, color="#475569", labelpad=10)
            ax1.set_ylabel("Traditional SEO Clicks", color=color_seo, fontsize=10, fontweight='600')
            ax1.plot(merged_chart["week_start"], merged_chart["clicks"], color=color_seo, marker="o", markersize=6, linewidth=2.5, label="SEO Clicks")
            ax1.tick_params(axis='y', labelcolor=color_seo, colors='#475569', labelsize=9)
            ax1.grid(True, linestyle=":", alpha=0.5, color="#cbd5e1")
            
            # Secondary line: GEO citations
            ax2 = ax1.twinx()
            color_geo = "#10b981"
            ax2.set_ylabel("GEO citations (AI Engines)", color=color_geo, fontsize=10, fontweight='600')
            ax2.plot(merged_chart["week_start"], merged_chart["citations"], color=color_geo, marker="s", markersize=6, linewidth=2.5, linestyle="--", label="GEO Citations")
            ax2.tick_params(axis='y', labelcolor=color_geo, colors='#475569', labelsize=9)
            
            # Combine legends
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", frameon=True, facecolor="#ffffff", edgecolor="#e2e8f0")
            
            corr_val = merged_chart["clicks"].corr(merged_chart["citations"])
            plt.title(f"SEO Clicks vs. AI Citation Trend (Correlation: {corr_val:.2f})", fontsize=11, fontweight='600', color='#0f172a', pad=12)
            sns.despine(ax=ax1, right=False)
            st.pyplot(fig)
            plt.close()
        else:
            st.info("GEO Citation history missing for filtered range.")

    st.markdown("---")
    st.markdown("#### Page Type Comparative Breakdown")
    col_pt1, col_pt2 = st.columns(2)
    
    pt_data = filtered_seo.groupby("page_type").agg(
        clicks=("clicks", "sum"),
        impressions=("impressions", "sum")
    ).reset_index()
    pt_data["ctr"] = pt_data["clicks"] / pt_data["impressions"]
    
    with col_pt1:
        fig, ax = plt.subplots(figsize=(8, 4), dpi=150)
        # Custom color scheme: slate-gray, royal-blue, clean teal
        colors = ["#1e293b", "#3b82f6", "#0d9488"]
        sns.barplot(data=pt_data, x="page_type", y="clicks", palette=colors, ax=ax)
        ax.set_title("Organic Clicks by Category", fontsize=10, fontweight='600', color='#0f172a')
        ax.set_ylabel("Clicks", fontsize=9, color="#475569")
        ax.set_xlabel("Page Type", fontsize=9, color="#475569")
        ax.grid(True, axis='y', linestyle=":", alpha=0.4)
        sns.despine()
        st.pyplot(fig)
        plt.close()
        
    with col_pt2:
        fig, ax = plt.subplots(figsize=(8, 4), dpi=150)
        colors_ctr = ["#334155", "#60a5fa", "#14b8a6"]
        from matplotlib.ticker import PercentFormatter
        sns.barplot(data=pt_data, x="page_type", y="ctr", palette=colors_ctr, ax=ax)
        ax.set_title("Click-Through Rate (CTR) by Category", fontsize=10, fontweight='600', color='#0f172a')
        ax.set_ylabel("CTR", fontsize=9, color="#475569")
        ax.set_xlabel("Page Type", fontsize=9, color="#475569")
        ax.yaxis.set_major_formatter(PercentFormatter(1.0))
        ax.grid(True, axis='y', linestyle=":", alpha=0.4)
        sns.despine()
        st.pyplot(fig)
        plt.close()

with tab2:
    col_kw, col_pg = st.columns(2)
    
    with col_kw:
        st.markdown("#### Search Keyword (Query) Leaderboard")
        kw_report = filtered_seo.groupby("query").agg(
            clicks=("clicks", "sum"),
            impressions=("impressions", "sum"),
            avg_position=("position", "mean")
        ).reset_index()
        kw_report["ctr"] = (kw_report["clicks"] / kw_report["impressions"] * 100).round(2)
        kw_report["avg_position"] = kw_report["avg_position"].round(1)
        kw_report = kw_report.sort_values(by="clicks", ascending=False).rename(
            columns={
                "query": "Search Keyword",
                "clicks": "Clicks",
                "impressions": "Impressions",
                "ctr": "CTR (%)",
                "avg_position": "Avg Position"
            }
        )
        st.dataframe(kw_report.style.format({"Clicks": "{:,}", "Impressions": "{:,}", "CTR (%)": "{:.2f}%", "Avg Position": "{:.1f}"}), use_container_width=True, hide_index=True)

    with col_pg:
        st.markdown("#### Page-Level Lead Performance")
        page_report = filtered_seo.groupby(["page_path", "page_type"]).agg(
            clicks=("clicks", "sum"),
            impressions=("impressions", "sum"),
            avg_position=("position", "mean")
        ).reset_index()
        page_report["ctr"] = (page_report["clicks"] / page_report["impressions"] * 100).round(2)
        page_report["avg_position"] = page_report["avg_position"].round(1)
        page_report = page_report.sort_values(by="clicks", ascending=False).rename(
            columns={
                "page_path": "Page Path URL",
                "page_type": "Page Category",
                "clicks": "Clicks",
                "impressions": "Impressions",
                "ctr": "CTR (%)",
                "avg_position": "Avg Position"
            }
        )
        st.dataframe(page_report.style.format({"Clicks": "{:,}", "Impressions": "{:,}", "CTR (%)": "{:.2f}%", "Avg Position": "{:.1f}"}), use_container_width=True, hide_index=True)

with tab3:
    st.markdown("### 💡 Executive Briefing & Actionable SEO/GEO Tasks")
    st.markdown("Data-driven takeaways automatically calculated from the active dataset filters:")
    
    # 1. Performance Driver Highlight
    top_page = filtered_seo.groupby("page_path")["clicks"].sum().idxmax()
    top_page_clicks = filtered_seo.groupby("page_path")["clicks"].sum().max()
    top_page_share = (top_page_clicks / total_clicks) * 100
    
    st.markdown(
        f"""
        <div class="briefing-card border-info">
            <h4>📈 Traffic Driver Highlight</h4>
            <p>The URL <code>{top_page}</code> is the primary traffic driver for the selected filters, 
            generating <strong>{top_page_clicks:,} clicks</strong> (representing <strong>{top_page_share:.1f}%</strong> of total filtered organic traffic).</p>
            <div class="action-label">Strategic Action Item</div>
            <p>Protect search authority: Set up automated page-level uptime monitoring, verify no incoming internal links contain broken redirects, and optimize core page load speed to minimize mobile bounce rates.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # 2. Opportunity / CTR Deficit
    page_summary = filtered_seo.groupby(["page_path", "page_type"]).agg(
        clicks=("clicks", "sum"),
        impressions=("impressions", "sum"),
        avg_position=("position", "mean"),
        expected_ctr=("expected_ctr", "mean"),
        actual_ctr=("ctr", "mean")
    ).reset_index()
    
    opps = page_summary[
        (page_summary["avg_position"] >= 3.0) & 
        (page_summary["avg_position"] <= 15.0) & 
        (page_summary["actual_ctr"] < page_summary["expected_ctr"])
    ].copy()
    
    if not opps.empty:
        opps["click_upside"] = opps["impressions"] * (opps["expected_ctr"] - opps["actual_ctr"])
        top_opp = opps.sort_values(by="click_upside", ascending=False).iloc[0]
        
        st.markdown(
            f"""
            <div class="briefing-card border-success">
                <h4>🎯 Organic SEO Quick Win (CTR Opportunity)</h4>
                <p>URL <code>{top_opp['page_path']}</code> (avg rank: {top_opp['avg_position']:.1f}) is underperforming its click expectations. 
                Its click-through rate of <strong>{top_opp['actual_ctr']*100:.2f}%</strong> is significantly below the standard expected rate of <strong>{top_opp['expected_ctr']*100:.2f}%</strong> for this rank, resulting in a traffic deficit.</p>
                <div class="action-label">Strategic Action Item</div>
                <p><strong>Unlocks up to {int(np.round(top_opp['click_upside'])):,} additional clicks</strong>: Refactor search snippet title metadata to include emotional search modifiers or local schema, write a compelling meta description matching search intent, and implement structured FAQ schema to expand the visual search footprint.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div class="briefing-card border-success">
                <h4>🎯 Organic SEO Quick Win</h4>
                <p>All pages within striking distance (ranking positions 3.0 to 15.0) are performing at or above baseline expected CTRs. Snippet and metadata alignments are optimal.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    # 3. Content Decay
    half_days = date_diff // 2
    mid_date = start_date + datetime.timedelta(days=half_days)
    
    p1 = filtered_seo[filtered_seo["date"].dt.date < mid_date].groupby("page_path")["clicks"].sum()
    p2 = filtered_seo[filtered_seo["date"].dt.date >= mid_date].groupby("page_path")["clicks"].sum()
    
    comp = pd.DataFrame({"p1": p1, "p2": p2}).fillna(0)
    comp = comp[comp["p1"] >= 15] # filter out low-volume pages
    comp["pct_change"] = (comp["p2"] - comp["p1"]) / comp["p1"] * 100
    decay_pages = comp[comp["pct_change"] < -15.0].sort_values(by="pct_change")
    
    if not decay_pages.empty:
        top_decay_path = decay_pages.index[0]
        top_decay_pct = decay_pages.iloc[0]["pct_change"]
        st.markdown(
            f"""
            <div class="briefing-card border-danger">
                <h4>⚠️ Content Decay Alert</h4>
                <p>URL <code>{top_decay_path}</code> has seen organic clicks decline by <strong>{abs(top_decay_pct):.1f}%</strong> 
                between the first half and second half of the selected date range, indicating search erosion or competitor out-ranking.</p>
                <div class="action-label">Strategic Action Item</div>
                <p>Execute content refresh: Audit keywords using Google Search Console to detect lost rankings, update outdated statistics/references, improve text-to-code ratios, resolve any outbound broken links, and re-request indexing in Google Search Console.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div class="briefing-card border-danger">
                <h4>⚠️ Content Decay Alert</h4>
                <p>No major search pages showed click decay (>15% reduction) between the halves of the selected period. Content performance is stable.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    # 4. GEO Citation Analysis
    if not filtered_geo.empty:
        geo_counts = filtered_geo.groupby("engine")["citation_count"].sum()
        top_engine = geo_counts.idxmax()
        top_engine_count = geo_counts.max()
        total_citations = geo_counts.sum()
        
        geo_pt = filtered_geo.groupby("page_path")["citation_count"].sum()
        top_cited_page = geo_pt.idxmax() if not geo_pt.empty else "N/A"
        
        st.markdown(
            f"""
            <div class="briefing-card border-warning">
                <h4>🤖 Generative Engine Optimization (GEO) Insights</h4>
                <p>AI engine references total <strong>{total_citations:,} citations</strong> across the filtered range. 
                The leading LLM engine citation driver is <strong>{top_engine}</strong> with <strong>{top_engine_count:,} references</strong>, and the most cited page path is <code>{top_cited_page}</code>.</p>
                <div class="action-label">Strategic Action Item</div>
                <p>Scale AI answer visibility: To expand citation rates in ChatGPT and Perplexity, write structured summaries (key bullet takeaways) at the top of other service and blog pages, implement schema markup, and provide clean, data-backed tables that LLM scrapers can digest easily.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div class="briefing-card border-warning">
                <h4>🤖 Generative Engine Optimization (GEO) Insights</h4>
                <p>No LLM search citations were recorded in the selected period. This indicates a visibility gap in generative AI engines.</p>
                <div class="action-label">Strategic Action Item</div>
                <p>Adopt GEO formatting: Insert summarizing bullet blocks, clear definitions, Q&A blocks, and high-quality outbound citation links into blog posts to encourage LLM bots (like GPTBot, PerplexityBot) to index and cite the content.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
