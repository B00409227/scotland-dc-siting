# 🏴󠁧󠁢󠁳󠁣󠁴󠁿 Scotland AI Data Centre Siting Dashboard

**No Bias Intended** — Scottish Government Innovation Challenge 2026  
Abdul Hannaan Mohammed · Calum Lang · Danny Lee · Laraine Ukwu-George · Vasyl Shvets

🔗 **Live app:** [scotland-dc-siting.streamlit.app](https://scotland-dc-siting.streamlit.app)  
📁 **GitHub:** [github.com/B00409227/No-Bias-Intended](https://github.com/B00409227/No-Bias-Intended)

---

## What is this?

A local, interactive decision-support dashboard that helps Scottish Government policymakers decide **where to site AI data centres** across Scotland.

The dashboard scores candidate council areas against seven evidence-based indicators, groups them into two lenses — **infrastructure readiness** and **community equity** — and presents the trade-offs visually so a human decision-maker can weigh them up. It does **not** auto-approve sites. Every recommendation is advisory; the final call belongs to a person.

The central question the tool asks is: **"Who gains and who bears the cost?"** Data centres bring jobs and investment but also place environmental stress, noise, water demand, and heat burden on nearby communities — often the most deprived ones. Making that trade-off visible and adjustable is the core purpose of this tool.

---

## Why does this matter?

Scotland's AI Strategy 2026–2031 commits to responsible, people-centred AI infrastructure. UK-wide demand for data centre capacity is growing rapidly, with [concerns already being raised](https://www.bbc.co.uk/news/articles/clyr9nx0jrzo) about the environmental and social impact of rapid construction. Scottish data centres are [already using enough water to fill 27 million bottles a year](https://www.bbc.co.uk/news/articles/c77zxx43x4vo), and [public health concerns are escalating](https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(26)00033-4/fulltext).

Siting decisions made purely on infrastructure criteria risk:
- Concentrating economic benefits in already-prosperous areas
- Placing environmental and noise burdens on deprived communities with the least political voice
- Missing opportunities to repurpose brownfield land and existing grid connections

SEPA's [regulatory guidance on data centres](https://beta.sepa.scot/topics/energy/data-centres/) is clear that environmental regulation applies to associated activities. This tool embeds equity and environment directly into the scoring methodology, giving policymakers a transparent, auditable approach aligned with Scotland's Just Transition principles.

---

## What benefit does it bring?

| Stakeholder | Benefit |
|---|---|
| **Policymakers** | Transparent, adjustable scoring replaces ad-hoc judgement. Slide a weight to instantly see how priorities change the ranking. |
| **Communities** | Equity indicators (environmental burden, vulnerability exposure) are first-class metrics, not afterthoughts. |
| **Infrastructure teams** | Readiness scores surface the highest-capacity sites quickly, with confidence ratings flagging where data gaps exist. |
| **Auditors / scrutineers** | No black-box ML — every score is a documented weighted sum reproducible in a spreadsheet. |
| **Future teams** | Designed for real data swap-in: replace the sample CSV with live datasets and the tool works immediately. |

---

## Features

- 🗺️ **Interactive map of Scotland** — click any dot to load that area's full scorecard; pan and zoom freely
- ⚖️ **Live weight sliders** — drag Readiness vs Distribution sliders to re-score and re-rank all areas in real time
- 🕸️ **Radar chart** — all seven dimensions at a glance; burden axes are flipped so a bigger polygon always means a better profile
- 📊 **Priority matrix** — Readiness % vs Distribution % scatter, quadrant-labelled to identify binding constraints
- 🔴 **Risk-flag chips** — automatically raised when burden indicators exceed a threshold
- 💼 **Jobs breakdown** — construction vs operational vs indirect, with the equity caveat that permanent jobs are far fewer
- 🔍 **Compare mode** — select two areas to show side-by-side scorecards and an overlaid radar
- 📋 **Ranked table** — all areas sorted by weighted total, updates live with every slider move
- 🟡 **Evidence confidence meter** — high / medium / low rating per indicator, gating the recommendation category

---

## Scoring methodology

All scoring is a **transparent weighted composite indicator** — no machine learning, no pre-trained models.

### Steps

1. **Normalise** each raw indicator to 0–5 using min-max scaling across all candidate areas.
2. **Group** into two buckets:
   - **Readiness** = Energy Capacity + Digital Connectivity + Future Grid Headroom + Infrastructure Reuse
   - **Distribution** = Community Benefit (positive) − Environmental Burden − Vulnerability Exposure
3. **Compute** a benefit-to-burden ratio = community benefit score ÷ sum of burden scores.
4. **Apply weights** (user-adjustable) to compute a weighted total out of 100.
5. **Map** to a recommendation category:
   - 🟢 Strong candidate (score ≥ 70, confidence medium+)
   - 🟠 Possible with safeguards (score ≥ 50)
   - 🔴 Not suitable now (score < 50)
   - 🔵 Needs further evidence (low overall confidence, regardless of score)

### Indicators

| Indicator | Group | Direction | Data status |
|---|---|---|---|
| Energy Capacity | Readiness | Higher = better | ⚠️ Estimated |
| Digital Connectivity | Readiness | Higher = better | ⚠️ Estimated from urban/rural pattern |
| Future Grid Headroom | Readiness | Higher = better | ⚠️ Estimated |
| Infrastructure Reuse | Readiness | Higher = better | ⚠️ Estimated |
| Community Benefit | Distribution | Higher = better | ⚠️ SIMD-informed estimate |
| Environmental Burden | Distribution | Higher = **worse** | ⚠️ SEPA-informed estimate |
| Vulnerability Exposure | Distribution | Higher = **worse** | ✅ Real — SIMD 2020 deprivation % |

---

## Data — what's real and what's estimated

### ✅ Real data used

| Column | Real value used | Source |
|---|---|---|
| `vulnerability_exposure` | % of datazones in most deprived 20% per council area | [SIMD 2020 — Scottish Government](https://www.gov.scot/collections/scottish-index-of-multiple-deprivation-2020/) |
| `simd_decile` | Median SIMD decile per council area | [SIMD 2020 — Scottish Government](https://www.gov.scot/collections/scottish-index-of-multiple-deprivation-2020/) |
| `urban_rural_class` | Official classification per council | [Scottish Government Urban Rural Classification 2022](https://www.gov.scot/publications/scottish-government-urban-rural-classification-2022/) |
| `lat`, `lon` | Council area centroid coordinates | [Spatial Data Scotland](https://spatialdata.gov.scot/) |

**Real vulnerability values used (SIMD 2020 — % of area in most deprived 20% of Scotland):**

| Council Area | % most deprived 20% | SIMD Decile |
|---|---|---|
| Glasgow City | 44% | 2 |
| Dundee City | 38% | 3 |
| Falkirk | 27% | 4 |
| Fife | 20% | 5 |
| West Lothian | 20% | 5 |
| Highland | 10% | 6 |
| Argyll & Bute | 10% | 7 |
| Aberdeenshire | 3% | 8 |

### ⚠️ Estimated / illustrative values

These columns use plausible estimates informed by the data sources below, but **have not been extracted directly from a downloaded dataset**. Confidence is marked as `low` or `medium` accordingly, and the dashboard displays this prominently.

| Column | Basis for estimate | Real source to replace it |
|---|---|---|
| `energy_capacity` | Urban > rural proxy; central belt higher than remote | [SSEN Distribution Data Portal](https://data.ssen.co.uk/) — Network Capacity heatmaps; [Scottish Energy Statistics](https://www.gov.scot/collections/quarterly-energy-statistics-scotland/) |
| `digital_connectivity` | Urban/rural pattern: Glasgow ~88%, Argyll & Bute ~32% | [Ofcom Connected Nations 2025](https://www.ofcom.org.uk/phones-and-broadband/coverage-and-speeds/connected-nations-20252) — download LA-level gigabit % |
| `future_grid_headroom` | NESO FES 2025 direction (Scotland can absorb 20% of GB DC demand) | [NESO FES 2025 dataworkbook](https://www.neso.energy/document/364696/download) — sheets BB1/ED1, SEPD/SHEPD/SPTL/SHETL zones |
| `infrastructure_reuse` | Rural areas score higher on open/derelict land availability | [Scottish Vacant & Derelict Land Survey 2024](https://www.gov.scot/publications/scottish-vacant-derelict-land-statistics-2024/) — hectares by council |
| `community_benefit` | SIMD-informed: deprived urban areas have more potential beneficiaries | SIMD 2020 + [Scottish Annual Business Statistics 2023](https://www.gov.scot/publications/scottish-annual-business-statistics-2023/) |
| `environmental_burden` | Eastern Scotland higher water stress (SEPA); urban heat + noise penalty | [SEPA Water Classification Hub](https://informatics.sepa.org.uk/WaterClassificationHub/); [SEPA Data Centres regulatory guide](https://beta.sepa.scot/topics/energy/data-centres/) |
| `jobs_*` | Scale estimates only; operational jobs deliberately low | [NOMIS / BRES](https://www.nomisweb.co.uk/); [Scottish Annual Business Statistics 2023](https://www.gov.scot/publications/scottish-annual-business-statistics-2023/) |

---

## Full data source list

These are the datasets and reports the tool draws on or is designed to integrate with:

| Source | Type | Used for |
|---|---|---|
| [SIMD 2020 — Scottish Government](https://www.gov.scot/collections/scottish-index-of-multiple-deprivation-2020/) | Dataset | Vulnerability exposure (real), SIMD decile (real), community benefit proxy |
| [Scottish Government Urban Rural Classification 2022](https://www.gov.scot/publications/scottish-government-urban-rural-classification-2022/) | Dataset | Urban/rural classification per council (real) |
| [Ofcom Connected Nations 2025](https://www.ofcom.org.uk/phones-and-broadband/coverage-and-speeds/connected-nations-20252) | Report + Data | Digital connectivity % by local authority |
| [NESO Future Energy Scenarios 2025](https://www.neso.energy/publications/future-energy-scenarios-fes#FES-2025-Key-message-and-actions) | Dataset | Grid headroom, future energy demand — FES dataworkbook sheets BB1, ED1 |
| [NESO FES 2025 Dataworkbook](https://www.neso.energy/document/364696/download) | Dataset | Peak demand by zone (SEPD, SHEPD, SPTL, SHETL); data centre demand sheet ED1 |
| [SSEN Distribution Data Portal](https://data.ssen.co.uk/) | Dataset + Map | Network capacity heatmaps, embedded capacity register, substation ratings |
| [Scottish Vacant & Derelict Land Survey 2024](https://www.gov.scot/publications/scottish-vacant-derelict-land-statistics-2024/) | Dataset | Infrastructure reuse — brownfield hectares by council |
| [SEPA Water Classification Hub](https://informatics.sepa.org.uk/WaterClassificationHub/) | Dashboard + Dataset | Environmental burden — water quality and stress by catchment |
| [SEPA Data Centres Regulatory Guide](https://beta.sepa.scot/topics/energy/data-centres/) | Report | Environmental regulation scope for data centres in Scotland |
| [SEPA Environmental Data](https://www.sepa.org.uk/environment/environmental-data/) | Dataset | Wider environmental quality indicators |
| [Scottish Energy Statistics — Quarterly Bulletins](https://www.gov.scot/collections/quarterly-energy-statistics-scotland/) | Dataset | Energy capacity and generation by region |
| [Domestic Energy Performance Certificates](https://statistics.gov.scot/data/domestic-energy-performance-certificates) | Dataset | Local energy efficiency context |
| [Scottish Annual Business Statistics 2023](https://www.gov.scot/publications/scottish-annual-business-statistics-2023/) | Dataset | Employment and turnover by sector; jobs baseline |
| [NOMIS / BRES](https://www.nomisweb.co.uk/) | Dataset | Jobs estimates by sector and local authority |
| [Scotland's AI Strategy 2026–2031](https://www.gov.scot/binaries/content/documents/govscot/publications/strategy-plan/2026/03/scotlands-ai-strategy-2026-2031/documents/ai-strategy-scotland/ai-strategy-scotland/govscot%3Adocument/ai-strategy-scotland.pdf) | Report | Policy alignment; responsible AI infrastructure principles |
| [Business Insights & Conditions Survey Wave 155](https://www.gov.scot/publications/bics-weighted-scotland-estimates-data-to-wave-155/documents/) | Dataset | Business AI adoption by sector (row 467) |
| [Spatial Data Scotland](https://spatialdata.gov.scot/) | Repository | Geographic boundaries and coordinates |
| [find.data.gov.scot](https://find.data.gov.scot) | Search Engine | Discovery of Scottish public datasets |
| [Ordnance Survey Data Hub](https://osdatahub.os.uk/) | Dataset + Map | Topographic and land use mapping |
| [Digimap / OS Collection](https://digimap.edina.ac.uk/os) | Map | Detailed topographic OS data for the UK |
| [Scotland's Labour Market — APS 2021](https://www.gov.scot/publications/scotlands-labour-market-people-places-regions-protected-characteristics-statistics-annual-population-survey-2021/) | Report | Labour market by protected characteristics |
| [UNESCO Ethics of AI](https://www.unesco.org/en/artificial-intelligence/recommendation-ethics) | Report | Ethical framework context |
| [The Lancet — AI data centre health impacts (McLellan, 2026)](https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(26)00033-4/fulltext) | Report | Public health burden justification |

**Context articles:**
- [BBC: Scottish data centres using enough water to fill 27 million bottles a year](https://www.bbc.co.uk/news/articles/c77zxx43x4vo)
- [BBC: Data centres to be expanded across UK as concerns mount](https://www.bbc.co.uk/news/articles/clyr9nx0jrzo)
- [BBC: Could a huge data centre revitalise Ayrshire — or ruin it?](https://www.bbc.co.uk/news/articles/c2d1ny161yyo)
- [BBC: Miliband says climate impact of data centres is uncertain](https://www.bbc.co.uk/news/articles/cx2drxgz7x8o)
- [BBC: UK firm pioneers data centres using lampposts](https://www.bbc.co.uk/news/articles/c98r4e594p7o)
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
├── app.py          # Streamlit UI — layout, charts, map, interactivity
├── scoring.py      # Scoring logic — normalisation, weighting, ratio, recommendations
├── requirements.txt
└── data/
    └── areas.csv   # Current data (mix of real SIMD + estimated indicators — see table above)
```

`scoring.py` has no Streamlit dependency and can be unit-tested independently.

---

## Swapping in real data

Replace `data/areas.csv` with a file matching the schema below. No code changes needed.

```
area_name, lat, lon, urban_rural_class, simd_decile,
energy_capacity, energy_capacity_confidence,
digital_connectivity, digital_connectivity_confidence,
future_grid_headroom, future_grid_headroom_confidence,
infrastructure_reuse, infrastructure_reuse_confidence,
community_benefit, community_benefit_confidence,
environmental_burden, environmental_burden_confidence,
vulnerability_exposure, vulnerability_exposure_confidence,
jobs_construction, jobs_operational, jobs_indirect
```

- Raw indicator columns: any numeric scale (the tool normalises them 0–5)
- `*_confidence` columns: `"high"`, `"medium"`, or `"low"`

---

## Policy alignment

| Policy / Framework | Relevance |
|---|---|
| [Scotland's AI Strategy 2026–2031](https://www.gov.scot/binaries/content/documents/govscot/publications/strategy-plan/2026/03/scotlands-ai-strategy-2026-2031/documents/ai-strategy-scotland/ai-strategy-scotland/govscot%3Adocument/ai-strategy-scotland.pdf) | Responsible, people-centred AI infrastructure |
| Just Transition principles | Benefits and costs of economic change distributed fairly |
| National Planning Framework 4 (NPF4) | Sustainability and community benefit in infrastructure siting |
| [UNESCO Ethics of AI](https://www.unesco.org/en/artificial-intelligence/recommendation-ethics) | Ethical guardrails against bias and harm |
| [SEPA regulatory framework](https://beta.sepa.scot/topics/energy/data-centres/) | Environmental compliance for data centre operations |

---

## Limitations & caveats

- Most indicator values are estimates — confidence levels in the dashboard reflect this honestly
- Scores are relative to the candidate set; adding or removing areas rescales all scores
- Jobs figures are illustrative; real estimates require site-specific economic modelling
- Environmental burden is a composite proxy; a full EIA would be required before any real decision
- The benefit-to-burden ratio uses normalised scores, not absolute impact assessments

---

## Licence

MIT — free to use, adapt, and build on.
