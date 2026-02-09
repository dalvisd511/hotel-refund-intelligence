# Hotel Refund Intelligence (Brighton vs Newhaven)
**Operational Drivers, Guest Experience Proxy Metrics & Cost Reduction Opportunities**

**Period analysed:** Nov 2025 – Jan 2026  
**Tools:** Python (pandas, numpy), Jupyter, Matplotlib  
**Context:** Real-world hotel operational refund data

---

## 📌 Problem Statement
Refunds are a direct operational cost and often a signal of service failure — including room quality issues, sleep disruption, maintenance problems, booking/payment errors, or food & beverage complaints.

This project analyses refund transactions from two Premier Inn sites (**Brighton** and **Newhaven**) to help leadership understand:
- Where refunds are concentrated (site, month, day)
- Whether refunds are driven by accommodation-related issues (guest experience proxy)
- Which periods show operational risk
- Which site carries higher **Sleep Quality Risk**

---

## 👥 Stakeholders
- Hotel General Manager (Brighton / Newhaven)
- Operations Manager
- Finance / Revenue Assurance
- Guest Relations / Customer Experience
- Regional Management

---

## 📊 Headline KPIs (3 months)
- **Total refund value:** **£3,151.88**
- **Refund count:** **63**
- **Average refund value:** **£50.03**

---

## 🏨 Refund Performance by Site

| Site      | Total Refunds (£) | Refund Count | Avg Refund (£) |
|----------|------------------:|-------------:|---------------:|
| Brighton | £1,817.40         | 20           | £90.87         |
| Newhaven| £1,334.48         | 43           | £31.03         |

**Insight**
- Brighton issues **fewer refunds**, but they are **significantly higher value**, indicating more severe service failures.
- Newhaven processes **more frequent but lower-value refunds**, suggesting minor service recovery gestures.

---

## 📆 Refund Performance by Month

| Month     | Total Refunds (£) | Refund Count | Avg Refund (£) |
|----------|------------------:|-------------:|---------------:|
| Nov 2025 | £632.84           | 9            | £70.32         |
| Dec 2025 | £1,207.48         | 19           | £63.55         |
| Jan 2026 | £1,311.56         | 35           | £37.47         |

**Insight**
- Refund activity peaks in **January**, driven by higher volume rather than severity.
- November shows fewer refunds but relatively **higher average value**, indicating isolated but impactful issues.

---

## 🛏️ Category Split (Accommodation vs F&B — Proxy)
Refunds were categorised using transaction descriptions (`BUSINESS_FORMAT_DATE`):

- **F&B**: breakfast, bar, restaurant, food, beverage, drink keywords  
- **Accommodation**: default when no F&B indicators are present

This acts as a **guest experience proxy**, particularly for sleep quality and room readiness.

---

## 🚨 Sleep Quality Risk Index (SQRI)

A composite **risk proxy** designed to prioritise operational focus areas.

### SQRI Components & Weights

| Component | Description | Weight |
|--------|------------|--------|
| Accommodation refund share (£) | Proportion of refund value linked to accommodation | 0.45 |
| Accommodation avg refund (£) | Severity of accommodation issues | 0.35 |
| High-value refund share | % of refunds ≥ £100 | 0.20 |

### SQRI Results (Higher = Higher Risk)

| Site      | Acc Share (£) | Acc Avg (£) | High-Value Share | SQRI |
|----------|---------------|------------|------------------|------|
| **Brighton** | 0.862 | £104.44 | 40.0% | **1.00** |
| Newhaven | 0.224 | £59.80 | 2.3% | 0.00 |

**Interpretation**
- **Brighton shows materially higher sleep-quality risk**, driven by:
  - High accommodation-related refund share
  - Very high average accommodation refund values
  - Large proportion of high-value refunds
- **Newhaven’s refunds are lower risk**, smaller in value, and less accommodation-driven.

> ⚠️ SQRI is a **directional prioritisation metric**, not a clinical measure of sleep quality.

---

## 📈 Visual Outputs
All charts are exported to `reports/figures/`:
- Refund value by site & month (clustered bar)
- Monthly refund trend (line)
- Category split by site (stacked bar)
- Daily anomaly heatmap (with legend & log scale)
- Week × Day operational heatmaps (Brighton & Newhaven)

These visuals are designed for **management review and operational discussions**.

---

## 🧠 Key Insights (Executive Summary)
1. **Brighton carries higher operational risk** despite lower refund volume.
2. High-value accommodation refunds indicate **room quality / sleep disruption issues**.
3. Newhaven’s pattern suggests **frequent but low-impact service recovery**.
4. January requires **post-holiday operational review** due to elevated refund activity.

---

## ✅ Recommended Actions
1. **Target Brighton accommodation issues**
   - Room readiness checks (noise, heating, maintenance)
   - Faster in-stay resolution to prevent post-stay refunds
2. **High-value refund governance**
   - Approval thresholds and mandatory reason codes for refunds ≥ £100
3. **Operational anomaly reviews**
   - Weekly review of peak refund days using heatmaps
4. **Ongoing monitoring**
   - Track refund value, accommodation share, and SQRI weekly

---
## Repo structure
hotel-refund-intelligence/
├─ data/
│ ├─ raw/
│ ├─ interim/
│ └─ processed/
├─ notebooks/
│ ├─ 01_ingestion_profiling.ipynb
│ ├─ 02_cleaning_validation.ipynb
│ └─ 03_analysis_storytelling.ipynb
├─ reports/
│ ├─ executive_summary.md
│ └─ figures/
├─ dashboards/
│ ├─ powerbi_outline.md
│ └─ tableau_outline.md
├─ src/
├─ README.md
└─ requirements.txt


## How to run locally (Windows)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
