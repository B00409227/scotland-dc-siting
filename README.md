# 🏴󠁧󠁢󠁳󠁣󠁴󠁿 Scotland AI Data Centre Siting Dashboard

**No Bias Intended** — Scottish Government Innovation Challenge 2026  
Abdul Hannaan Mohammed · Calum Lang · Danny Lee · Laraine Ukwu-George · Vasyl Shvets

🔗 **Live app:** [scotland-dc-siting.streamlit.app](https://scotland-dc-siting.streamlit.app)

---

## What is this?

A local, interactive decision-support dashboard that helps Scottish Government policymakers decide **where to site AI data centres** across Scotland.

The dashboard scores candidate council areas against seven evidence-based indicators, splits them into two lenses — **infrastructure readiness** and **community equity** — and presents the trade-offs visually so that a human decision-maker can weigh them up. It does **not** auto-approve sites. Every recommendation is advisory, and the final call belongs to a person.

The central question the tool asks is: **"Who gains and who bears the cost?"** Data centres bring jobs and investment but also place environmental stress, noise, and heat burden on nearby communities — often the most deprived ones. Making that trade-off visible and adjustable is the core purpose of this tool.

---

## Why does this matter?

Scotland has committed to becoming a leader in responsible AI (Scottish AI Strategy 2022–2031), and UK-wide demand for data centre capacity is growing rapidly. But siting decisions made purely on infrastructure criteria risk:

- Concentrating economic benefits in already-prosperous areas
- Placing environmental and noise burdens on deprived communities with the least political voice
- Missing opportunities to repurpose brownfield land and existing grid connections

This dashboard embeds equity directly into the scoring methodology, giving policymakers a transparent, auditable tool that is aligned with Scotland's Just Transition principles.

---

## What benefit does it bring?

| Stakeholder | Benefit |
|---|---|
| **Policymakers** | Transparent, adjustable scoring replaces ad-hoc judgement. Slide a weight to instantly see how priorities change the ranking. |
| **Communities** | Equity indicators (environmental burden, vulnerability exposure) are first-class metrics, not afterthoughts. |
| **Infrastructure teams** | Readiness scores surface the highest-capacity sites quickly, with confidence ratings flagging where data gaps exist. |
| **Auditors / scrutineers** | No black-box ML — every score is a documented weighted sum that can be reproduced in a spreadsheet. |
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
- 🟡 **Evidence confidence meter** — high / medium / low rating derived from data source quality, gating the recommendation category

---

## Scoring methodology

All scoring is a **transparent weighted composite indicator** — no machine learning, no pre-trained models.

### Step-by-step

1. **Normalise** each raw indicator to 0–5 using min-max scaling across all candidate areas.
2. **Group** indicators into two buckets:
   - **Readiness** = Energy Capacity + Digital Connectivity + Future Grid Headroom + Infrastructure Reuse
   - **Distribution** = Community Benefit (positive) − Environmental Burden − Vulnerability Exposure
3. **Compute** a benefit-to-burden ratio per area = community benefit score ÷ sum of burden scores.
4. **Apply weights** (user-adjustable) to compute a weighted total out of 100.
5. **Map** the total + evidence confidence to a recommendation category:
   - 🟢 Strong candidate (score ≥ 70, confidence medium+)
   - 🟠 Possible with safeguards (score ≥ 50)
   - 🔴 Not suitable now (score < 50)
   - 🔵 Needs further evidence (low confidence, regardless of score)

### Indicators

| Indicator | Group | Direction |
|---|---|---|
| Energy Capacity | Readiness | Higher = better |
| Digital Connectivity | Readiness | Higher = better |
| Future Grid Headroom | Readiness | Higher = better |
| Infrastructure Reuse | Readiness | Higher = better |
| Community Benefit | Distribution | Higher = better |
| Environmental Burden | Distribution | Higher = **worse** |
| Vulnerability Exposure | Distribution | Higher = **worse** |

---

## Data sources

> ⚠️ **All values in the current prototype are illustrative sample figures.** They are structured to match the real data schema so that live datasets can be dropped in as a CSV replacement with no code changes.

The real-world sources the tool is designed to ingest are:

| Indicator | Source |
|---|---|
| Energy capacity & grid headroom | [Scottish Energy Statistics Hub](https://www.gov.scot/collections/scottish-energy-statistics/) — Scottish Government; [SSEN](https://www.ssen.co.uk/) / [SP Energy Networks](https://www.spenergynetworks.co.uk/) capacity maps; NESO Future Energy Scenarios |
| Digital connectivity | [Ofcom Connected Nations Report 2025](https://www.ofcom.org.uk/research-and-data/telecoms-research/connected-nations) |
| Infrastructure reuse (brownfield) | [Scottish Vacant and Derelict Land Survey](https://www.gov.scot/collections/scottish-vacant-and-derelict-land-survey/) — Scottish Government |
| Community benefit & deprivation | [Scottish Index of Multiple Deprivation (SIMD) 2020](https://www.gov.scot/collections/scottish-index-of-multiple-deprivation-2020/); [Scotland Census 2022](https://www.scotlandscensus.gov.uk/) |
| Jobs estimates | [NOMIS — Business Register and Employment Survey (BRES)](https://www.nomisweb.co.uk/) |
| Environmental burden (water stress, noise, heat) | [SEPA Water Classification](https://www.sepa.org.uk/environment/water/); Scottish noise mapping data |
| Governance & strategy alignment | [Scottish AI Strategy 2022–2031](https://www.gov.scot/publications/scotlands-ai-strategy/) (qualitative checklist — not numerically scored in this version) |
| Geographic boundaries & coordinates | [Spatial Data Scotland](https://spatialdata.gov.scot/) — Scottish Government |

---

## Sample areas

The prototype covers eight Scottish council areas chosen to represent a range of urban/rural contexts and deprivation profiles:

| Area | Urban/Rural | SIMD Decile |
|---|---|---|
| Aberdeenshire | Rural | 7 |
| Argyll & Bute | Rural | 8 |
| Dundee City | Urban | 4 |
| Falkirk | Urban | 5 |
| Fife | Urban | 5 |
| Glasgow City | Urban | 2 |
| Highland | Rural | 6 |
| West Lothian | Suburban | 4 |

---

## How to run locally

```bash
# 1. Clone the repo
git clone https://github.com/B00409227/scotland-dc-siting.git
cd scotland-dc-siting

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the dashboard
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## Project structure

```
scotland-dc-siting/
├── app.py          # Streamlit UI — all layout, charts, map, and interactivity
├── scoring.py      # Scoring logic — normalisation, weighting, ratio, recommendations
├── requirements.txt
└── data/
    └── areas.csv   # Sample data (replace with real CSV — schema must match)
```

`scoring.py` has no Streamlit dependency and can be imported and unit-tested independently.

---

## Swapping in real data

Replace `data/areas.csv` with a CSV that matches the column schema below. No code changes needed.

**Required columns:**

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

- Raw indicator columns: numeric, any scale (the tool normalises them)
- `*_confidence` columns: `"high"`, `"medium"`, or `"low"`

---

## Policy alignment

This tool supports the following Scottish Government commitments:

- **Scottish AI Strategy 2022–2031** — responsible, people-centred AI infrastructure
- **Just Transition principles** — ensuring the benefits and costs of economic change are fairly distributed
- **National Planning Framework 4 (NPF4)** — sustainability and community benefit in infrastructure siting

---

## Limitations & caveats

- Scores are relative to the candidate set — adding or removing areas rescales all scores
- Confidence levels reflect data source quality, not statistical uncertainty bands
- The benefit-to-burden ratio uses normalised scores, not absolute impact assessments
- Jobs figures are illustrative; real estimates require site-specific economic modelling
- Environmental burden is currently a composite proxy; a full EIA would be required before any real siting decision

---

## Licence

MIT — free to use, adapt, and build on.
