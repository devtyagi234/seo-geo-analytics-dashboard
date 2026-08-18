import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_seo_data(start_date, end_date):
    dates = pd.date_range(start_date, end_date)
    np.random.seed(42)
    
    # Define client profiles
    clients = {
        "Client A": {
            "industry": "Orthopaedic Healthcare Chain",
            "pages": {
                "/locations/chicago": ("location page", ["orthopaedic doctor chicago", "joint specialist chicago", "ortho clinic chicago"]),
                "/locations/houston": ("location page", ["orthopaedic surgery houston", "joint doctor houston", "houston ortho"]),
                "/locations/phoenix": ("location page", ["knee doctor phoenix", "phoenix ortho specialist", "hip surgeon phoenix"]),
                "/services/knee-pain": ("service page", ["knee replacement rehab", "knee arthroscopy surgery", "chronic knee pain treatment"]),
                "/services/hip-replacement": ("service page", ["hip replacement surgeon", "anterior hip replacement", "hip surgery recovery"]),
                "/services/sports-medicine": ("service page", ["sports medicine doctor", "acl tear recovery", "rotator cuff therapy"]),
                "/blog/recovery-tips": ("blog", ["orthopaedic surgery recovery", "exercises after hip surgery", "knee rehab exercises"]),
                "/blog/joint-health": ("blog", ["how to protect joint health", "supplements for joint pain", "foods for strong bones"])
            },
            # Trend directions: 'up', 'down', 'flat'
            "trends": {
                "/locations/chicago": "up",        # New marketing campaign
                "/locations/houston": "flat",
                "/locations/phoenix": "flat",
                "/services/knee-pain": "up",       # High ranking keyword focus
                "/services/hip-replacement": "down", # Rank decay due to competitor entry
                "/services/sports-medicine": "flat",
                "/blog/recovery-tips": "up",       # Gained a featured snippet
                "/blog/joint-health": "down"       # Content decay (outdated article)
            }
        },
        "Client B": {
            "industry": "Wellness and Health Business",
            "pages": {
                "/services/health-coaching": ("service page", ["integrative health coach", "online wellness coaching", "holistic life coach"]),
                "/services/nutrition-plan": ("service page", ["custom nutrition plan", "registered dietitian services", "weight loss nutritionist"]),
                "/services/mindfulness-app": ("service page", ["mindfulness app subscription", "meditation program online", "stress relief app"]),
                "/blog/sleep-hygiene": ("blog", ["how to sleep better naturally", "sleep hygiene checklist", "benefits of deep sleep"]),
                "/blog/healthy-recipes": ("blog", ["easy plant based dinners", "high protein breakfast ideas", "low sugar meal prep"]),
                "/blog/mindfulness-basics": ("blog", ["mindfulness practices for beginners", "daily meditation tips", "box breathing exercises"]),
                "/blog/stress-management": ("blog", ["how to reduce stress at work", "natural anxiety remedies", "cortisol lowering exercises"])
            },
            "trends": {
                "/services/health-coaching": "up",
                "/services/nutrition-plan": "flat",
                "/services/mindfulness-app": "down",   # App stores updates reduced ranking
                "/blog/sleep-hygiene": "up",          # Gained traction in AI Overviews
                "/blog/healthy-recipes": "flat",
                "/blog/mindfulness-basics": "down",   # Competitor published a better guide
                "/blog/stress-management": "up"       # High demand seasonal trend
            }
        }
    }
    
    seo_records = []
    
    for date in dates:
        # Determine weekend effect (typically lower search volume for business/healthcare)
        is_weekend = date.dayofweek >= 5
        volume_factor = 0.65 if is_weekend else 1.0
        
        # Calculate days elapsed for trending
        days_elapsed = (date - dates[0]).days
        total_days = len(dates)
        
        for client_name, client_info in clients.items():
            pages = client_info["pages"]
            trends = client_info["trends"]
            
            for page, (page_type, keywords) in pages.items():
                trend_type = trends.get(page, "flat")
                
                # Base performance metrics depending on page type
                if page_type == "location page":
                    base_impressions = 450
                    base_pos = 4.5
                elif page_type == "service page":
                    base_impressions = 600
                    base_pos = 8.0
                else:  # blog
                    base_impressions = 1200
                    base_pos = 12.0
                
                # Adjust metrics based on time and trends
                if trend_type == "up":
                    # Improving ranking (lower position number) and increasing impressions
                    pos_trend = - (days_elapsed / total_days) * 3.5
                    imp_trend = (days_elapsed / total_days) * 0.75
                elif trend_type == "down":
                    # Decaying ranking (higher position number) and decreasing impressions
                    pos_trend = (days_elapsed / total_days) * 6.0
                    imp_trend = - (days_elapsed / total_days) * 0.4
                else:  # flat
                    pos_trend = 0
                    imp_trend = 0
                
                # Add seasonality or weekly fluctuations
                pos_noise = np.random.normal(0, 0.4)
                imp_noise = np.random.normal(0, 0.05)
                
                # Compute finalized average position (clamped between 1 and 50)
                position = max(1.0, min(50.0, base_pos + pos_trend + pos_noise))
                
                # Compute finalized impressions
                impressions = int(max(10, base_impressions * volume_factor * (1.0 + imp_trend + imp_noise)))
                
                # Define expected CTR model as function of position
                # standard curve: CTR = 0.35 / (pos ^ 0.9)
                base_ctr = 0.35 / (position ** 0.85)
                
                # Personalize CTR based on page type (blogs might have lower CTR than transactional location pages at same position)
                if page_type == "location page":
                    base_ctr *= 1.2
                elif page_type == "blog":
                    base_ctr *= 0.8
                
                # Apply CTR variance
                ctr = max(0.005, min(0.45, base_ctr + np.random.normal(0, 0.01)))
                
                # Calculate clicks based on impressions and CTR
                clicks = int(np.round(impressions * ctr))
                
                # Re-calculate exact CTR based on generated clicks to maintain integrity
                ctr = clicks / impressions if impressions > 0 else 0.0
                
                # Attribute the metrics across keywords for this page
                # We distribute impressions and clicks among page queries
                num_kw = len(keywords)
                weights = np.random.dirichlet(np.ones(num_kw))
                
                for kw, weight in zip(keywords, weights):
                    kw_impressions = int(np.round(impressions * weight))
                    if kw_impressions == 0:
                        continue
                    
                    # Keywords position centered around page position
                    kw_position = max(1.0, min(80.0, position + np.random.normal(0, 1.5)))
                    
                    # Keywords CTR matches position
                    kw_base_ctr = 0.35 / (kw_position ** 0.85)
                    kw_ctr = max(0.002, min(0.5, kw_base_ctr + np.random.normal(0, 0.015)))
                    kw_clicks = int(np.round(kw_impressions * kw_ctr))
                    kw_ctr = kw_clicks / kw_impressions if kw_impressions > 0 else 0.0
                    
                    seo_records.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "client": client_name,
                        "query": kw,
                        "page_path": page,
                        "page_type": page_type,
                        "clicks": kw_clicks,
                        "impressions": kw_impressions,
                        "ctr": kw_ctr,
                        "position": round(kw_position, 2)
                    })
                    
    return pd.DataFrame(seo_records)

def generate_geo_citations(start_date, end_date):
    # Generates weekly records for GEO citations (AI engine mentions)
    dates = pd.date_range(start_date, end_date)
    # Group dates by week
    df_weeks = pd.DataFrame({"date": dates})
    df_weeks["week_start"] = df_weeks["date"].dt.to_period("W").dt.start_time
    weeks = df_weeks["week_start"].unique()
    
    np.random.seed(42)
    engines = ["ChatGPT", "Perplexity", "Google AI Overviews"]
    
    clients = {
        "Client A": [
            ("/locations/chicago", "location page"),
            ("/services/knee-pain", "service page"),
            ("/blog/recovery-tips", "blog"),
            ("/blog/joint-health", "blog")
        ],
        "Client B": [
            ("/services/health-coaching", "service page"),
            ("/blog/sleep-hygiene", "blog"),
            ("/blog/mindfulness-basics", "blog"),
            ("/blog/stress-management", "blog")
        ]
    }
    
    geo_records = []
    
    for week in weeks:
        week_str = week.strftime("%Y-%m-%d")
        
        for client_name, pages in clients.items():
            for page_path, page_type in pages:
                # Blogs are highly cited, locations rarely cited
                if page_type == "blog":
                    base_prob = 0.55
                    max_citations = 5
                elif page_type == "service page":
                    base_prob = 0.35
                    max_citations = 3
                else: # location page
                    base_prob = 0.10
                    max_citations = 1
                
                # Introduce a trend over time for AI Overviews / citations rising
                # Week number
                week_idx = list(weeks).index(week)
                time_multiplier = 1.0 + (week_idx / len(weeks)) * 0.5
                
                for engine in engines:
                    # Let Perplexity and ChatGPT cite more blogs, AI Overviews cite services too
                    prob = base_prob * time_multiplier
                    if engine == "Google AI Overviews" and page_type == "service page":
                        prob *= 1.3
                    
                    is_cited = np.random.rand() < min(0.9, prob)
                    count = np.random.randint(1, max_citations + 1) if is_cited else 0
                    
                    geo_records.append({
                        "week_start_date": week_str,
                        "client": client_name,
                        "page_path": page_path,
                        "engine": engine,
                        "citation_count": count
                    })
                    
    return pd.DataFrame(geo_records)

def main():
    print("Generating synthetic SEO and GEO analytics datasets...")
    
    # Generate 90 days of data ending yesterday
    end_date = datetime.now() - timedelta(days=1)
    start_date = end_date - timedelta(days=90)
    
    seo_df = generate_seo_data(start_date, end_date)
    geo_df = generate_geo_citations(start_date, end_date)
    
    # Ensure data folder exists
    os.makedirs("data", exist_ok=True)
    
    # Save datasets
    seo_path = os.path.join("data", "seo_data.csv")
    geo_path = os.path.join("data", "geo_citations.csv")
    
    seo_df.to_csv(seo_path, index=False)
    geo_df.to_csv(geo_path, index=False)
    
    print(f"Successfully generated datasets:")
    print(f" - SEO data: {seo_path} ({len(seo_df)} records)")
    print(f" - GEO citations: {geo_path} ({len(geo_df)} records)")

if __name__ == "__main__":
    main()
