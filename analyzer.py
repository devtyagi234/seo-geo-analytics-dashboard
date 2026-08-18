import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from data_processor import load_clean_seo_data, load_clean_geo_data

# Set styling for plots
sns.set_theme(style="whitegrid")
plt.rcParams.update({
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.titlesize': 16
})

def analyze_top_performers(seo_df, client_name):
    """1. Top-performing keywords/pages by clicks"""
    client_df = seo_df[seo_df["client"] == client_name]
    
    # By Keyword (Query)
    kw_perf = client_df.groupby("query").agg(
        clicks=("clicks", "sum"),
        impressions=("impressions", "sum"),
        avg_position=("position", "mean")
    ).reset_index()
    kw_perf["ctr"] = kw_perf["clicks"] / kw_perf["impressions"]
    kw_perf = kw_perf.sort_values(by="clicks", ascending=False)
    
    # By Page Path
    page_perf = client_df.groupby(["page_path", "page_type"]).agg(
        clicks=("clicks", "sum"),
        impressions=("impressions", "sum"),
        avg_position=("position", "mean")
    ).reset_index()
    page_perf["ctr"] = page_perf["clicks"] / page_perf["impressions"]
    page_perf = page_perf.sort_values(by="clicks", ascending=False)
    
    return kw_perf, page_perf

def analyze_ctr_vs_position(seo_df, client_name, output_dir):
    """2. CTR vs. average position scatter plot with correlation"""
    client_df = seo_df[seo_df["client"] == client_name]
    
    # Group by query to get overall stats
    query_summary = client_df.groupby("query").agg(
        clicks=("clicks", "sum"),
        impressions=("impressions", "sum"),
        avg_position=("position", "mean")
    ).reset_index()
    query_summary["ctr"] = query_summary["clicks"] / query_summary["impressions"]
    
    # Filter out low impression keywords to remove noise from CTR
    query_summary = query_summary[query_summary["impressions"] >= 50]
    
    if query_summary.empty:
        print(f"Not enough data for CTR vs Position analysis for {client_name}")
        return 0.0
    
    # Calculate Pearson and Spearman correlation
    pearson_corr = query_summary["avg_position"].corr(query_summary["ctr"], method="pearson")
    spearman_corr = query_summary["avg_position"].corr(query_summary["ctr"], method="spearman")
    
    # Generate plot
    plt.figure(figsize=(10, 6))
    
    # Fit curve for visualization (exponential decay or power law)
    # y = a * x^b => log(y) = log(a) + b * log(x)
    pos = query_summary["avg_position"].values
    ctr = query_summary["ctr"].values
    
    sns.scatterplot(
        data=query_summary,
        x="avg_position",
        y="ctr",
        size="impressions",
        sizes=(20, 200),
        alpha=0.7,
        color="#1f77b4",
        edgecolor="w",
        legend="brief"
    )
    
    # Add expected CTR baseline curve
    x_curve = np.linspace(1, max(pos), 100)
    # Base curve used in synthetic data: 0.35 / (pos ^ 0.85)
    y_curve = 0.35 / (x_curve ** 0.85)
    plt.plot(x_curve, y_curve, color="red", linestyle="--", linewidth=2, label="Expected CTR Curve")
    
    plt.title(f"CTR vs. Average Position for {client_name}\n(Pearson Corr: {pearson_corr:.2f}, Spearman Corr: {spearman_corr:.2f})")
    plt.xlabel("Average Position (Rank)")
    plt.ylabel("Click-Through Rate (CTR)")
    plt.xlim(0.9, max(pos) + 2)
    plt.ylim(-0.01, max(ctr) + 0.05)
    plt.legend(loc="upper right")
    plt.tight_layout()
    
    plot_path = os.path.join(output_dir, f"{client_name.lower().replace(' ', '_')}_ctr_vs_position.png")
    plt.savefig(plot_path, dpi=150)
    plt.close()
    
    return pearson_corr

def analyze_opportunity_pages(seo_df, client_name):
    """3. 'Opportunity' pages — high impressions, low CTR (negative delta), ranked by potential upside"""
    client_df = seo_df[seo_df["client"] == client_name]
    
    # Aggregate at page level
    page_summary = client_df.groupby(["page_path", "page_type"]).agg(
        clicks=("clicks", "sum"),
        impressions=("impressions", "sum"),
        avg_position=("position", "mean"),
        expected_ctr=("expected_ctr", "mean"),
        actual_ctr=("ctr", "mean")
    ).reset_index()
    
    # Filter for pages ranking in positions 3-15 (striking distance / high opportunity)
    # and having actual CTR less than expected CTR
    opps = page_summary[
        (page_summary["avg_position"] >= 3.0) & 
        (page_summary["avg_position"] <= 15.0) & 
        (page_summary["actual_ctr"] < page_summary["expected_ctr"])
    ].copy()
    
    # Calculate Click Upside = Impressions * (Expected CTR - Actual CTR)
    opps["click_upside"] = opps["impressions"] * (opps["expected_ctr"] - opps["actual_ctr"])
    opps["click_upside"] = opps["click_upside"].round(0).astype(int)
    opps["ctr_deficit_pct"] = ((opps["expected_ctr"] - opps["actual_ctr"]) * 100).round(2)
    
    opps = opps.sort_values(by="click_upside", ascending=False)
    
    return opps

def analyze_content_decay(seo_df, client_name):
    """4. Content decay detection — pages with declining clicks/impressions over 90 days.
       We compare performance in the first 30 days of the period vs. the last 30 days.
    """
    client_df = seo_df[seo_df["client"] == client_name].copy()
    
    min_date = client_df["date"].min()
    max_date = client_df["date"].max()
    
    first_30_end = min_date + pd.Timedelta(days=30)
    last_30_start = max_date - pd.Timedelta(days=30)
    
    # First 30 days
    first_period = client_df[client_df["date"] <= first_30_end]
    first_perf = first_period.groupby("page_path").agg(
        clicks_start=("clicks", "sum"),
        impressions_start=("impressions", "sum")
    )
    
    # Last 30 days
    last_period = client_df[client_df["date"] >= last_30_start]
    last_perf = last_period.groupby("page_path").agg(
        clicks_end=("clicks", "sum"),
        impressions_end=("impressions", "sum")
    )
    
    # Merge and compute change
    decay_df = pd.merge(first_perf, last_perf, on="page_path", how="outer").fillna(0)
    
    # Filter out very low click pages at start to avoid noise
    decay_df = decay_df[decay_df["clicks_start"] >= 15]
    
    decay_df["clicks_change_abs"] = decay_df["clicks_end"] - decay_df["clicks_start"]
    decay_df["clicks_change_pct"] = (decay_df["clicks_change_abs"] / decay_df["clicks_start"]) * 100
    decay_df["impressions_change_pct"] = ((decay_df["impressions_end"] - decay_df["impressions_start"]) / decay_df["impressions_start"]) * 100
    
    # Flag decay where clicks declined by more than 15%
    decay_df["decay_status"] = np.where(decay_df["clicks_change_pct"] < -15.0, "Decaying", "Stable/Improving")
    decay_df = decay_df.sort_values(by="clicks_change_pct")
    
    return decay_df.reset_index()

def analyze_page_type_performance(seo_df, client_name):
    """5. Page-type comparison (location vs service vs blog performance)"""
    client_df = seo_df[seo_df["client"] == client_name]
    
    page_type_perf = client_df.groupby("page_type").agg(
        total_clicks=("clicks", "sum"),
        total_impressions=("impressions", "sum"),
        avg_position=("position", "mean"),
    ).reset_index()
    
    page_type_perf["ctr"] = page_type_perf["total_clicks"] / page_type_perf["total_impressions"]
    page_type_perf = page_type_perf.sort_values(by="total_clicks", ascending=False)
    
    return page_type_perf

def analyze_geo_vs_seo(seo_df, geo_df, client_name, output_dir):
    """6. GEO citation frequency vs traditional search visibility, side by side"""
    # Filter for client
    client_seo = seo_df[seo_df["client"] == client_name].copy()
    client_geo = geo_df[geo_df["client"] == client_name].copy()
    
    # Group SEO by week to match GEO's weekly structure
    client_seo["week_start"] = client_seo["date"].dt.to_period("W").dt.start_time
    
    weekly_seo = client_seo.groupby("week_start").agg(
        clicks=("clicks", "sum"),
        impressions=("impressions", "sum")
    ).reset_index()
    
    weekly_geo = client_geo.groupby("week_start_date").agg(
        citations=("citation_count", "sum")
    ).reset_index()
    weekly_geo["week_start"] = pd.to_datetime(weekly_geo["week_start_date"])
    
    # Merge datasets
    merged = pd.merge(weekly_seo, weekly_geo, on="week_start", how="inner")
    
    # Correlation coefficient between weekly organic clicks and AI citations
    correlation = merged["clicks"].corr(merged["citations"])
    
    # Generate side-by-side or overlay plot
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    color = "#1f77b4"
    ax1.set_xlabel("Week Start Date", fontweight="bold")
    ax1.set_ylabel("Traditional SEO Clicks", color=color, fontweight="bold")
    line1 = ax1.plot(merged["week_start"], merged["clicks"], color=color, marker="o", linewidth=2.5, label="Organic SEO Clicks")
    ax1.tick_params(axis='y', labelcolor=color)
    
    ax2 = ax1.twinx()  
    color = "#2ca02c"
    ax2.set_ylabel("GEO Citations (AI Answer Engines)", color=color, fontweight="bold")
    line2 = ax2.plot(merged["week_start"], merged["citations"], color=color, marker="s", linewidth=2.5, linestyle="--", label="AI Engine Citations")
    ax2.tick_params(axis='y', labelcolor=color)
    
    # Align legends
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="upper left")
    
    plt.title(f"Weekly Traditional Organic Clicks vs. GEO Citations for {client_name}\n(Correlation: {correlation:.2f})")
    fig.tight_layout()
    
    plot_path = os.path.join(output_dir, f"{client_name.lower().replace(' ', '_')}_geo_vs_seo.png")
    plt.savefig(plot_path, dpi=150)
    plt.close()
    
    return merged, correlation

def main():
    print("Running analysis pipeline...")
    
    # Create directories
    os.makedirs("reports", exist_ok=True)
    os.makedirs("reports/plots", exist_ok=True)
    
    # Load processed data
    seo_df = load_clean_seo_data("data/seo_data_processed.csv")
    geo_df = load_clean_geo_data("data/geo_citations_processed.csv")
    
    clients = ["Client A", "Client B"]
    
    for client in clients:
        print(f"\nAnalyzing data for {client}...")
        
        # 1. Top Performers
        kw_perf, page_perf = analyze_top_performers(seo_df, client)
        kw_perf.to_csv(f"reports/{client.lower().replace(' ', '_')}_top_keywords.csv", index=False)
        page_perf.to_csv(f"reports/{client.lower().replace(' ', '_')}_top_pages.csv", index=False)
        print(f" - Top performers files exported.")
        
        # 2. CTR vs Position Scatter Plot
        corr = analyze_ctr_vs_position(seo_df, client, "reports/plots")
        print(f" - CTR vs Position plot saved. Correlation: {corr:.2f}")
        
        # 3. Opportunity Pages
        opps = analyze_opportunity_pages(seo_df, client)
        opps.to_csv(f"reports/{client.lower().replace(' ', '_')}_opportunity_pages.csv", index=False)
        print(f" - Found {len(opps)} opportunity pages. Summary saved.")
        
        # 4. Content Decay
        decay = analyze_content_decay(seo_df, client)
        decay.to_csv(f"reports/{client.lower().replace(' ', '_')}_content_decay.csv", index=False)
        decay_count = len(decay[decay["decay_status"] == "Decaying"])
        print(f" - Flagged {decay_count} decaying pages. Detailed report saved.")
        
        # 5. Page Type Performance
        pt_perf = analyze_page_type_performance(seo_df, client)
        pt_perf.to_csv(f"reports/{client.lower().replace(' ', '_')}_page_type_performance.csv", index=False)
        print(f" - Page type performance metrics saved.")
        
        # 6. GEO vs SEO Connection
        merged, geo_seo_corr = analyze_geo_vs_seo(seo_df, geo_df, client, "reports/plots")
        merged.to_csv(f"reports/{client.lower().replace(' ', '_')}_geo_vs_seo.csv", index=False)
        print(f" - GEO vs SEO weekly correlation: {geo_seo_corr:.2f}. Plot generated.")
        
    print("\nAnalysis pipeline complete. All reports and visual assets successfully exported to /reports directory.")

if __name__ == "__main__":
    main()
