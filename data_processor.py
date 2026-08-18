import os
import pandas as pd
import numpy as np

def load_clean_seo_data(filepath="data/seo_data.csv"):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Source file {filepath} not found. Please run data_generator.py first.")
    
    df = pd.read_csv(filepath)
    
    # 1. Date Standardization
    df["date"] = pd.to_datetime(df["date"])
    
    # 2. Handling Missing/Duplicate Values
    df = df.dropna(subset=["date", "client", "page_path", "query"])
    df = df.drop_duplicates(subset=["date", "client", "page_path", "query"])
    
    # Fill numeric NaNs
    df["clicks"] = df["clicks"].fillna(0).astype(int)
    df["impressions"] = df["impressions"].fillna(0).astype(int)
    df["position"] = df["position"].fillna(50.0).astype(float)
    
    # Recalculate CTR to ensure consistency
    df["ctr"] = np.where(df["impressions"] > 0, df["clicks"] / df["impressions"], 0.0)
    
    # 3. Feature Engineering: CTR-vs-position deltas
    # Empirical standard SEO curve: CTR_expected = 0.35 / (position ^ 0.85)
    # We adjust the exponent slightly for different page types
    df["expected_ctr"] = np.where(
        df["page_type"] == "location page",
        0.35 * 1.2 / (df["position"] ** 0.85),
        np.where(
            df["page_type"] == "blog",
            0.35 * 0.8 / (df["position"] ** 0.85),
            0.35 / (df["position"] ** 0.85) # service page
        )
    )
    # Clamp expected CTR to reasonable values [0.002, 0.50]
    df["expected_ctr"] = df["expected_ctr"].clip(0.002, 0.50)
    df["ctr_delta"] = df["ctr"] - df["expected_ctr"]
    
    # 4. Feature Engineering: WoW (Week-over-Week) daily metrics
    # To get WoW, we compare today's metrics with metrics from 7 days ago
    # Sort by date for proper shift operations
    df = df.sort_values(by=["client", "page_path", "query", "date"])
    
    # Group by unique identifier and shift 7 days
    group_cols = ["client", "page_path", "query"]
    df["clicks_7d_ago"] = df.groupby(group_cols)["clicks"].shift(7)
    df["impressions_7d_ago"] = df.groupby(group_cols)["impressions"].shift(7)
    
    # Calculate WoW percentage changes
    df["wow_clicks_pct"] = (df["clicks"] - df["clicks_7d_ago"]) / df["clicks_7d_ago"]
    df["wow_impressions_pct"] = (df["impressions"] - df["impressions_7d_ago"]) / df["impressions_7d_ago"]
    
    # Replace infinite values and NaNs resulting from division by zero
    df["wow_clicks_pct"] = df["wow_clicks_pct"].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    df["wow_impressions_pct"] = df["wow_impressions_pct"].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    
    # Drop temp columns
    df = df.drop(columns=["clicks_7d_ago", "impressions_7d_ago"])
    
    return df

def load_clean_geo_data(filepath="data/geo_citations.csv"):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Source file {filepath} not found. Please run data_generator.py first.")
    
    df = pd.read_csv(filepath)
    
    # 1. Date Standardization
    df["week_start_date"] = pd.to_datetime(df["week_start_date"])
    
    # 2. Handling Missing/Duplicates
    df = df.dropna(subset=["week_start_date", "client", "page_path", "engine"])
    df = df.drop_duplicates(subset=["week_start_date", "client", "page_path", "engine"])
    
    # Fill numeric NaNs
    df["citation_count"] = df["citation_count"].fillna(0).astype(int)
    
    return df

def main():
    print("Loading and cleaning raw datasets...")
    seo_processed = load_clean_seo_data()
    geo_processed = load_clean_geo_data()
    
    # Save processed files
    seo_processed.to_csv("data/seo_data_processed.csv", index=False)
    geo_processed.to_csv("data/geo_citations_processed.csv", index=False)
    
    print(f"Successfully processed and saved:")
    print(f" - Processed SEO data: data/seo_data_processed.csv ({len(seo_processed)} rows)")
    print(f" - Processed GEO data: data/geo_citations_processed.csv ({len(geo_processed)} rows)")

if __name__ == "__main__":
    main()
