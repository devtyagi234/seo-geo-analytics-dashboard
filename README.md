# Organic Search & AI Answer Engine (SEO/GEO) Analytics Dashboard
### Multi-Location Healthcare & Wellness Search Audit Case Study (Anonymized Portfolio Project)

This repository contains a full-stack SEO (Search Engine Optimization) and GEO (Generative Engine Optimization) analytics pipeline and dashboard. It is modeled after real client engagements for two brands:
* **Client A (Multi-Location Orthopaedic Healthcare Chain)**: Focused on regional patient acquisition and localized service delivery.
* **Client B (Wellness and Health Business)**: Focused on information queries, subscription services, and digital products.

The project demonstrates end-to-end data engineering, statistical analysis, and interactive dashboard creation using **Python, Pandas, NumPy, Seaborn, and Streamlit**.

---

## 📋 Executive Summary & Business Context

In modern organic marketing, tracking traditional search engine results pages (SERPs) is no longer sufficient. The rise of AI search engines (e.g., ChatGPT Search, Perplexity) and LLM snippets (e.g., Google AI Overviews) has created a new channel: **Generative Engine Optimization (GEO)**. 

This project solves a critical business problem for digital marketers: **How do we measure and correlate traditional SEO keyword positions with visibility in AI answer engines?**

By building a standardized, automated ingestion and analysis pipeline, this project helps marketers identify:
1. **Core Organic Drivers**: Top-performing keywords and landing page URLs.
2. **CTR Anomalies**: Pages ranking high on Google but underperforming their expected Click-Through Rate.
3. **Content Decay**: Outdated blog and service pages losing momentum over a rolling 90-day window.
4. **GEO Visibility (AI Citations)**: Which assets are being cited by LLMs, and how that corresponds with traditional search clicks.

---

## 🛠️ Tech Stack & Project Architecture

* **Data Engineering & Wrangling**: Python, Pandas, NumPy
* **Statistical Analysis**: SciPy (Pearson/Spearman correlation modeling)
* **Data Visualization**: Matplotlib, Seaborn
* **Interactive Dashboard**: Streamlit (modular UI, markdown-styled custom components)
* **Project Structure**:
  ```text
  ├── data/                        # CSV data directory (raw & processed)
  │   ├── seo_data.csv             # Raw simulated Google Search Console data
  │   ├── geo_citations.csv        # Raw simulated AI engine citation logs
  │   ├── seo_data_processed.csv   # Cleaned GSC data with calculated features
  │   └── geo_citations_processed.csv # Cleaned GEO weekly citation records
  ├── reports/                     # Output folder for analytical reports
  │   ├── plots/                   # Saved analysis visualizations (PNGs)
  │   └── [client]_top_*.csv       # Segmented analytical tabular reports
  ├── data_generator.py            # Data simulation script
  ├── data_processor.py            # ETL and feature engineering pipeline
  ├── analyzer.py                  # Static analysis and plot exporting script
  ├── app.py                       # Streamlit interactive dashboard
  ├── requirements.txt             # Project dependencies
  └── README.md                    # Project documentation
  ```

---

## 📊 Analytical Methodology & Calculated Features

### 1. Expected CTR Modeling
To find pages with bad meta titles/descriptions, we model the standard organic CTR curve as a power law function:
$$\text{Expected CTR} = \frac{a}{\text{Position}^b}$$
* We define custom baseline parameters $a=0.35$ and $b=0.85$ adjusted by page type (e.g., location pages tend to have higher transactional CTR than blog guides at the same position).
* The **CTR Delta** ($\text{CTR}_{\text{Actual}} - \text{Expected CTR}$) measures under/over-performance.

### 2. Click Opportunity Upside (Quick Wins)
We target pages in the **striking distance** (ranking average position between 3.0 and 15.0) where CTR Delta is negative.
$$\text{Click Upside} = \text{Impressions} \times (\text{Expected CTR} - \text{Actual CTR})$$
Ranking pages by Click Upside prioritizes metadata optimization (writing better title tags and descriptions) for maximum click retrieval without needing to rank higher.

### 3. Content Decay Detection
To distinguish structural decay from daily noise, the pipeline aggregates performance for the **first 30 days** of the dataset and compares it directly with the **last 30 days**. Pages with a click reduction $>15\%$ are flagged as **Decaying** and prioritized for content refreshes.

### 4. GEO vs. SEO Correlation
Citations across ChatGPT, Perplexity, and Google AI Overviews are aggregated weekly and correlated with traditional Google organic clicks using Pearson correlation coefficients, tracing whether AI search citations act as leading indicators of traditional search behavior.

---

## 🚀 How to Run the Project Locally

### Prerequisites
Make sure you have Python 3.9+ installed.

### Step 1: Clone and Install Dependencies
```bash
# Clone the repository
git clone https://github.com/AkshandraSingh/Password-Manager.git seo-geo-dashboard
cd seo-geo-dashboard

# Install required libraries
pip install -r requirements.txt
```

### Step 2: Generate and Process Data
Execute the pipeline to generate raw datasets and compute features:
```bash
# 1. Generate realistic SEO & GEO source data
python data_generator.py

# 2. Run ETL pipeline (standardize, clean, engineer features)
python data_processor.py
```

### Step 3: Run the Analytical Report Export
Run the static analysis script to generate static CSVs and high-quality figures in the `reports/` folder:
```bash
python analyzer.py
```

### Step 4: Launch the Streamlit Dashboard
Start the interactive application:
```bash
streamlit run app.py
```
Open the local URL (usually `http://localhost:8501`) in your web browser.

---

## 📈 Dashboard Walkthrough & Key Features
1. **Interactive Client Portfolios**: Toggle seamlessly between Client A (Healthcare) and Client B (Wellness).
2. **Dynamic Period-over-Period KPIs**: Total Clicks, Impressions, CTR, and Position display WoW percentage metrics.
3. **CTR Curve Visualization**: Scatter plot comparing keywords against the expected CTR curve.
4. **GEO vs SEO Line Graph**: Visualizes organic search clicks alongside AI citation frequencies over time.
5. **Auto-Generated Takeaways**: Uses statistical rule-triggers to write executive insights (e.g., identifying the top traffic-decay page and estimating the exact traffic gain from fixing a target opportunity URL).
