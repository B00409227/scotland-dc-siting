# 🏴󠁧󠁢󠁳󠁣󠁴󠁿 Scotland AI Data Centre Siting Dashboard

**No Bias Intended** — Scottish Government Innovation Challenge 2026  
Abdul Hannaan Mohammed · Calum Lang · Danny Lee · Laraine Ukwu-George · Vasyl Shvets

🔗 **Live app:** [no-bias-intended.streamlit.app](https://no-bias-intended.streamlit.app)  
📁 **GitHub:** [github.com/B00409227/No-Bias-Intended](https://github.com/B00409227/No-Bias-Intended)

---

## Challenge questions answered

**Q1 — What methods can we use to assess, model, and communicate the impact of hosting AI data centres in Scotland?**  
A transparent weighted composite indicator (no ML, reproducible in a spreadsheet) across 7 evidence-based dimensions, visualised through an interactive map, radar charts, a priority matrix, and a ranked table. All 32 Scottish council areas covered.

**Q2 — How do the impacts of data centres differ by geography and demographics? Which communities stand to gain most, and which bear the greatest costs?**  
The dashboard makes this directly visible. The Forth catchment (Scotland's most infrastructure-ready corridor) has 83% of its river water bodies NOT at Good/High ecological status — the communities most likely to gain investment are the same ones already bearing environmental pressure. Glasgow scores highest for community benefit potential (44% of its population is in the most deprived 20%) but also carries high environmental burden. Highland and Aberdeenshire score lowest on community benefit but have a renewable energy advantage for net-zero data centre operations.

---

## What is this?

A decision-support dashboard for Scottish Government policymakers comparing all **32 Scottish council areas** as candidate locations for AI data centre siting. It scores each area against seven evidence-based indicators, splits them into infrastructure readiness and community equity lenses, and presents trade-offs interactively so a human decision-maker can weigh them up.

The tool **does not auto-approve sites**. It is a screening tool — a positive score means a council area warrants further investigation, not that a site is approved.

The central equity question: **"Who gains and who bears the cost?"**

---

## Why it matters

Scotland's AI Strategy 2026–2031 commits to responsible, people-centred AI infrastructure. UK-wide demand for data centre capacity is growing rapidly, with serious public health concerns now documented:

- Scottish data centres already use [enough water to fill 27 million bottles per year](https://www.bbc.co.uk/news/articles/c77zxx43x4vo) (BBC)
- [McLellan (The Lancet, 2026)](https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(26)00033-4/fulltext) documents diesel generator pollution spikes, urban heat island effects, noise nuisance, and water competition as primary public health risks
- [SEPA regulates associated data centre activities](https://beta.sepa.scot/topics/energy/data-centres/) and must be involved in any siting decision

Siting decisions made on purely technical criteria risk concentrating benefits in prosperous areas while placing environmental and health burdens on deprived communities. This dashboard makes those trade-offs impossible to ignore.

---

## Dashboard features

- 🗺️ **Interactive map** — all 32 council areas, click to select, 6 colour-by modes (recommendation, burden, connectivity, deprivation, land reuse, score)
- ⚖️ **Live weight sliders** — Readiness vs Distribution; re-scores and re-ranks all 32 areas in real time
- 🕸️ **Radar chart** — 7 dimensions at a glance; burden axes flipped so larger = better
- 📊 **Priority matrix** — Readiness % vs Distribution %, dot-sized by population, quadrant-labelled
- 🏥 **McLellan health risk flags** — diesel generator risk, urban heat island, noise nuisance, water competition (McLellan, Lancet 2026)
- 🌿 **Renewable energy advantage flag** — SSEN SHEPD areas near offshore/onshore wind generation
- 📋 **Responsible AI governance checklist** — Scottish AI Strategy 2026–2031, 8 checks
- 🏴󠁧󠁢󠁳󠁣󠁴󠁿 **NPF National Outcomes alignment** — 4 National Performance Framework outcomes with progress bars
- 👤 **Area profile** — demographics, geography, economics per council (population, density, age, employment, earnings, GVA, DNO zone)
- 🔍 **Compare mode** — side-by-side scorecards with overlaid radar chart
- ⚠️ **"Not in scope" section** — explicit list of what a screening tool cannot replace

---

## Data — what is real vs estimated

### ✅ Real data (all 32 councils)

| Column | Status | Source |
|---|---|---|
| `digital_connectivity` | **Real** — Ofcom FTTP % per council | [Ofcom Connected Nations 2025](https://www.ofcom.org.uk/phones-and-broadband/coverage-and-speeds/connected-nations-20252) via [ThinkBroadband](https://labs.thinkbroadband.com/local/scotland) — fetched June 2026 |
| `infrastructure_reuse` | **Real** — derelict + urban vacant land (ha) | [Scottish Vacant & Derelict Land Survey 2024, Table 2](https://www.gov.scot/publications/scottish-vacant-derelict-land-statistics-2024/) |
| `environmental_burden` | **Real** — % river water bodies NOT at Good/High status per sub-basin | [SEPA Water Classification Hub ArcGIS API](https://map.sepa.org.uk/server/rest/services/Open/Hydrography/MapServer/4) — 2,410 water bodies, mapped to council areas via sub-basin |
| `vulnerability_exposure` | **Real** — % datazones in most deprived 20% | [SIMD 2020, Scottish Government](https://www.gov.scot/collections/scottish-index-of-multiple-deprivation-2020/) |
| `simd_decile` | **Real** — median SIMD decile per council | SIMD 2020 |
| `urban_rural_class` | **Real** | [Scottish Government Urban Rural Classification 2022](https://www.gov.scot/publications/scottish-government-urban-rural-classification-2022/) |
| `population` | **Real** — mid-2023 estimate | [NRS Scotland Mid-Year Population Estimates 2023](https://www.nrscotland.gov.uk/) |
| `area_km2` | **Real** | OS / Scottish Government boundaries |
| `median_age` | **Real** | [Scotland Census 2022](https://www.scotlandscensus.gov.uk/) |
| `employment_rate_pct` | **Real** | [ONS Annual Population Survey 2023](https://www.ons.gov.uk/) |
| `median_weekly_earnings_gbp` | **Real** | [ONS Annual Survey of Hours & Earnings (ASHE) 2023](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/ashe) |
| `gva_index` | **Real** — Scotland=100 | [ONS Regional GVA (balanced) 2023](https://www.ons.gov.uk/economy/grossvalueaddedgva) |
| `dno_zone` | **Real** — SP Distribution or SSEN SHEPD | [SP Energy Networks PES 18](https://www.energybrokers.co.uk/electricity/pes-areas/pes-area-18); [SSEN SHEPD PES 17](https://www.energybrokers.co.uk/electricity/pes-areas/pes-area-17) |
| `community_benefit` | **Formula-derived from real data** — (SIMD deprivation % × 1.2) + ((100 − employment rate) × 0.9) | SIMD 2020 + ONS APS 2023 — formula weights are transparent but subjective |

### ⚠️ Estimated (all 32 councils)

| Column | Basis | How to replace |
|---|---|---|
| `energy_capacity` | DNO zone proxy: SP Distribution areas (central belt) scored higher than SSEN SHEPD (north) | [SSEN Distribution Data Portal](https://data.ssen.co.uk/); [SPEN DFES 2024](https://www.spenergynetworks.co.uk/) — extract substation capacity by council |
| `future_grid_headroom` | NESO FES 2025 directional: central belt more constrained; Scotland can absorb up to 20% of GB data centre demand | [NESO FES 2025 Dataworkbook](https://www.neso.energy/document/364696/download) — sheets BB1 (zone data) and ED1 (data centre demand by scenario) |

### ❌ Illustrative only

| Column | Note | Real source |
|---|---|---|
| `jobs_construction/operational/indirect` | Scale estimates only; operational jobs deliberately far fewer than construction | [NOMIS / Business Register & Employment Survey (BRES)](https://www.nomisweb.co.uk/) |

---

## Key findings from the real data

1. **The Forth catchment paradox:** Falkirk, West Lothian, Fife, Edinburgh, Midlothian, Clackmannanshire — Scotland's most infrastructure-connected corridor — sit in the Forth sub-basin where 83% of river water bodies are NOT at Good/High ecological status (SEPA 2024). The most technically attractive areas carry the greatest existing environmental burden.

2. **Glasgow's equity dilemma:** Glasgow scores highest for community benefit (44% of population in most deprived 20%; high unemployment) but also faces high environmental burden (Clyde sub-basin, 72% not at Good/High). The community that would gain most from investment is the same community bearing the existing burden.

3. **The renewable advantage:** SSEN SHEPD areas — Highland, Aberdeenshire, Orkney, Shetland — have access to significant offshore and onshore renewable generation and low environmental burden. A data centre in Highland could run on near-zero carbon electricity. But community benefit potential is low (these are prosperous, low-deprivation areas), so community benefit agreements and local procurement would be essential.

4. **Digital divide:** Shetland (23%), Na h-Eileanan Siar (25%) and Argyll & Bute (32%) have the weakest digital connectivity, making them unsuitable without major connectivity investment first.

---

## Scoring methodology

All scoring is a **transparent weighted composite indicator — no machine learning, no pre-trained models.**

### Steps

1. **Normalise** each raw indicator to 0–5 using min-max scaling across all 32 council areas. Adding or removing areas rescales all scores.
2. **Group** into two buckets:
   - **Readiness** = Energy Capacity + Digital Connectivity + Future Grid Headroom + Infrastructure Reuse
   - **Distribution** = Community Benefit (positive) − Environmental Burden − Vulnerability Exposure
3. **Benefit-to-burden ratio** = community_benefit_score ÷ (environmental_burden_score + vulnerability_exposure_score). Below 1.0 = burdens outweigh benefits.
4. **Apply weights** (user-adjustable via sliders) to compute a weighted total out of 100.
5. **Recommendation category:**
   - 🟢 Strong candidate (score ≥ 70, confidence medium+)
   - 🟠 Possible with safeguards (score ≥ 50)
   - 🔴 Not suitable now (score < 50)
   - 🔵 Needs further evidence (overall confidence low)

### Community benefit formula

`community_benefit = min(85, vulnerability_exposure × 1.2 + (100 − employment_rate) × 0.9)`

Where both inputs are real data (SIMD 2020 and ONS APS 2023). The coefficients (1.2, 0.9) are transparent but subjective. Higher scores = more potential for investment to reach people who need it.

### McLellan (Lancet, 2026) health risk flags

Raised automatically when:
- **Diesel generator risk**: population density > 500/km² — pollution spikes from emergency generator testing
- **Urban heat island risk**: Urban class + environmental burden > 60% — waste heat compounds existing pressures
- **Noise nuisance**: population density > 300/km² — continuous low-frequency noise, sleep disturbance
- **Water competition**: environmental burden > 75% — data centre cooling demands on already-pressured catchments

### Responsible AI governance

Based on Scotland's AI Strategy 2026–2031. The dashboard checks 8 criteria; 5 are met by design (transparent scoring, human final approval, equity given equal weight, confidence ratings, sources documented). 3 require post-screening action (community consultation, EIA, equalities impact assessment).

### National Performance Framework alignment

The dashboard maps to four NPF National Outcomes:
- **Environment** — measured via environmental_burden (SEPA)
- **Communities** — measured via vulnerability_exposure (SIMD)
- **Economy / Fair Work** — measured via community_benefit (SIMD + employment)

---

## What this tool does NOT cover

This is a screening tool. A positive score means an area warrants investigation — not that a site is approved.

**Environmental & physical (require EIA):**
- Site-level water consumption vs source capacity
- Flood risk and climate change projections
- Noise propagation modelling
- Operational carbon footprint
- Green space / canopy loss assessment
- Chemical discharge from cooling systems

**Community & social:**
- Community consultation — no public voice mechanism
- Cumulative impact — multiple concurrent sites in one area
- Skills gap / workforce pipeline for operational jobs
- Equalities impact assessment

**Governance & legal:**
- Land ownership and acquisition feasibility
- Planning permission status (NPF4 compliance)
- National security review (NCSC)
- Site-specific EIA and ecological survey

---

## Full data source list

| Source | Type | Used for |
|---|---|---|
| [SIMD 2020](https://www.gov.scot/collections/scottish-index-of-multiple-deprivation-2020/) | Dataset | Vulnerability exposure, SIMD decile, community benefit formula |
| [Ofcom Connected Nations 2025](https://www.ofcom.org.uk/phones-and-broadband/coverage-and-speeds/connected-nations-20252) | Dataset | Digital connectivity FTTP % (all 32 councils) |
| [SEPA Water Classification Hub](https://informatics.sepa.org.uk/WaterClassificationHub/) | ArcGIS API | Environmental burden (2,410 river water bodies) |
| [SVDLS 2024](https://www.gov.scot/publications/scottish-vacant-derelict-land-statistics-2024/) | Dataset | Infrastructure reuse — derelict + vacant land (ha) |
| [Scottish Government Urban Rural Classification 2022](https://www.gov.scot/publications/scottish-government-urban-rural-classification-2022/) | Dataset | Urban/rural/suburban classification |
| [NRS Scotland Mid-2023 Population Estimates](https://www.nrscotland.gov.uk/) | Dataset | Population, population density |
| [Scotland Census 2022](https://www.scotlandscensus.gov.uk/) | Dataset | Median age |
| [ONS Annual Population Survey 2023](https://www.ons.gov.uk/) | Dataset | Employment rate |
| [ONS ASHE 2023](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/ashe) | Dataset | Median weekly earnings |
| [ONS Regional GVA 2023](https://www.ons.gov.uk/economy/grossvalueaddedgva) | Dataset | GVA index (Scotland=100) |
| [SP Energy Networks PES 18](https://www.energybrokers.co.uk/electricity/pes-areas/pes-area-18) | Reference | DNO zone mapping (central/southern Scotland) |
| [SSEN SHEPD PES 17](https://www.energybrokers.co.uk/electricity/pes-areas/pes-area-17) | Reference | DNO zone mapping (northern Scotland) |
| [NESO FES 2025](https://www.neso.energy/publications/future-energy-scenarios-fes) | Dataset | Future grid headroom directional estimate |
| [SSEN Distribution Data Portal](https://data.ssen.co.uk/) | Dataset | Energy capacity estimate basis |
| [Scotland's AI Strategy 2026–2031](https://www.gov.scot/binaries/content/documents/govscot/publications/strategy-plan/2026/03/scotlands-ai-strategy-2026-2031/documents/ai-strategy-scotland/ai-strategy-scotland/govscot%3Adocument/ai-strategy-scotland.pdf) | Report | Responsible AI governance checklist |
| [SEPA Data Centres Regulatory Guide](https://beta.sepa.scot/topics/energy/data-centres/) | Report | Environmental regulation scope |
| [McLellan, The Lancet, 2026](https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(26)00033-4/fulltext) | Report | Public health risk flags (diesel, heat, noise, water) |
| [Business Insights & Conditions Survey Wave 155](https://www.gov.scot/publications/bics-weighted-scotland-estimates-data-to-wave-155/documents/) | Dataset | Business AI adoption context |
| [Scottish Annual Business Statistics 2023](https://www.gov.scot/publications/scottish-annual-business-statistics-2023/) | Dataset | Employment context |
| [NOMIS / BRES](https://www.nomisweb.co.uk/) | Dataset | Jobs figures (illustrative scale only) |

**Context articles:**
- [BBC: Scottish data centres using 27M bottles of water/year](https://www.bbc.co.uk/news/articles/c77zxx43x4vo)
- [BBC: Data centres to be expanded across UK as concerns mount](https://www.bbc.co.uk/news/articles/clyr9nx0jrzo)
- [BBC: Could a huge data centre revitalise Ayrshire — or ruin it?](https://www.bbc.co.uk/news/articles/c2d1ny161yyo)
- [Envirolink: Scotland's Data Center Climate Policy Falls Short on AI Energy Demands](https://www.envirolink.org/2026/05/25/scotlands-data-center-climate-policy-falls-short-on-ai-energy-demands/)

---

## How to run locally

```bash
git clone https://github.com/B00409227/No-Bias-Intended.git
cd No-Bias-Intended
pip install -r requirements.txt
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## Project structure

```
No-Bias-Intended/
├── app.py           # Streamlit UI — all layout, charts, map, interactivity
├── scoring.py       # Scoring logic — normalisation, weighting, ratio, recommendations
├── requirements.txt
└── data/
    └── areas.csv    # All 32 Scottish council areas (see data quality table above)
```

`scoring.py` has no Streamlit dependency and can be unit-tested independently.

---

## Swapping in better data

Replace `data/areas.csv` with a file matching the column schema. No code changes needed.

The two columns most worth improving:
1. **`energy_capacity`** — download [SSEN Distribution Data Portal](https://data.ssen.co.uk/) network capacity heatmaps, extract MW headroom by GSP, aggregate to council area
2. **`future_grid_headroom`** — download [NESO FES 2025 dataworkbook](https://www.neso.energy/document/364696/download), open sheets BB1 (zone-level data) and ED1 (data centre demand by scenario), filter for SEPD/SHEPD/SPTL/SHETL zones

---

## Policy alignment

| Policy / Framework | Relevance |
|---|---|
| [Scotland's AI Strategy 2026–2031](https://www.gov.scot/binaries/content/documents/govscot/publications/strategy-plan/2026/03/scotlands-ai-strategy-2026-2031/documents/ai-strategy-scotland/ai-strategy-scotland/govscot%3Adocument/ai-strategy-scotland.pdf) | Responsible, people-centred AI infrastructure |
| National Performance Framework — Environment, Communities, Economy, Fair Work | 4 NPF outcomes mapped in every scorecard |
| Just Transition principles | Benefits and costs of economic change distributed fairly |
| National Planning Framework 4 (NPF4) | Sustainability and community benefit in infrastructure siting |
| [SEPA regulatory framework](https://beta.sepa.scot/topics/energy/data-centres/) | Environmental compliance for data centre operations |
| [UNESCO Ethics of AI](https://www.unesco.org/en/artificial-intelligence/recommendation-ethics) | Ethical guardrails against bias and harm |

---

## Licence

MIT — free to use, adapt, and build on.
