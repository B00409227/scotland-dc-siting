import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from scoring import (
    compute_scores,
    load_sample_data,
    READINESS_INDICATORS,
    BENEFIT_INDICATOR,
    BURDEN_INDICATORS,
    CATEGORY_LABELS,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Scotland AI Data Centre Siting",
    page_icon="🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    layout="wide",
)

# ── Constants ─────────────────────────────────────────────────────────────────
CATEGORY_COLOURS = {
    CATEGORY_LABELS["strong"]:       "#2e7d32",
    CATEGORY_LABELS["safeguards"]:   "#e65100",
    CATEGORY_LABELS["not_suitable"]: "#b71c1c",
    CATEGORY_LABELS["evidence"]:     "#5c6bc0",
}

INDICATOR_LABELS = {
    "energy_capacity":        "Energy Capacity",
    "digital_connectivity":   "Digital Connectivity",
    "future_grid_headroom":   "Future Grid Headroom",
    "infrastructure_reuse":   "Infrastructure Reuse",
    "community_benefit":      "Community Benefit",
    "environmental_burden":   "Environmental Burden",
    "vulnerability_exposure": "Vulnerability Exposure",
}

# (col_key, radar_label, invert_for_radar)
# Burden axes are inverted so "bigger polygon = better" is always true
RADAR_AXES = [
    ("energy_capacity",        "Energy\nCapacity",      False),
    ("digital_connectivity",   "Digital\nConnectivity", False),
    ("future_grid_headroom",   "Grid\nHeadroom",        False),
    ("infrastructure_reuse",   "Infra.\nReuse",         False),
    ("community_benefit",      "Community\nBenefit",    False),
    ("environmental_burden",   "Low Env.\nBurden",      True),
    ("vulnerability_exposure", "Low\nVulnerability",    True),
]

BURDEN_THRESHOLDS = {
    "environmental_burden":   3.0,
    "vulnerability_exposure": 3.0,
}

RISK_CHIP_LABELS = {
    "environmental_burden":   "Water stress / heat / noise",
    "vulnerability_exposure": "Deprived households in impact radius",
}

CONFIDENCE_COLOURS = {"high": "#2e7d32", "medium": "#e65100", "low": "#b71c1c"}


# ── Session state ─────────────────────────────────────────────────────────────
if "selected_area" not in st.session_state:
    st.session_state.selected_area = "Falkirk"


# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    return load_sample_data("data/areas.csv")


raw_df     = load_data()
area_names = sorted(raw_df["area_name"].tolist())

if st.session_state.selected_area not in area_names:
    st.session_state.selected_area = area_names[0]


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🏴󠁧󠁢󠁳󠁣󠁴󠁿 Scotland AI Data Centre Siting")
    st.caption("Decision-support dashboard — human sign-off required.")

    st.warning(
        "⚠️ **Prototype — mixed data.** Digital connectivity uses real Ofcom 2025 "
        "figures. Deprivation uses real SIMD 2020 data. Energy and grid values are "
        "DNO-zone-informed estimates. No siting decisions should be based on this tool alone.",
    )

    st.divider()
    st.subheader("Indicator Weights")
    st.caption(
        "Move these sliders to re-score and re-rank all areas instantly. "
        "Setting Readiness to 0 means only equity matters; setting Distribution to 0 "
        "means only infrastructure readiness counts."
    )
    w_readiness    = st.slider("Readiness",              0, 100, 50, key="w_readiness")
    w_distribution = st.slider("Distribution (equity)",  0, 100, 50, key="w_distribution")

    st.divider()
    st.subheader("Select Location")
    st.caption("Click a dot on the map, or use the dropdown. Both are synced.")

    sidebar_area = st.selectbox(
        "Focus area",
        area_names,
        index=area_names.index(st.session_state.selected_area),
        key="sidebar_selectbox",
    )
    if sidebar_area != st.session_state.selected_area:
        st.session_state.selected_area = sidebar_area

    compare_area = st.selectbox(
        "Compare with (optional)",
        ["— none —"] + area_names,
        index=0,
        key="compare_selectbox",
    )
    compare_mode = (compare_area != "— none —" and compare_area != st.session_state.selected_area)

    st.divider()
    st.markdown("**No Bias Intended**")
    st.caption(
        "Scottish Government Innovation Challenge · 2026\n\n"
        "Abdul Hannaan Mohammed · Calum Lang · Danny Lee · Laraine Ukwu-George · Vasyl Shvets\n\n"
        "🔗 [no-bias-intended.streamlit.app](https://no-bias-intended.streamlit.app)"
    )


# ── Scoring ───────────────────────────────────────────────────────────────────
weights   = {"readiness": w_readiness / 50.0, "distribution": w_distribution / 50.0}
scored_df = compute_scores(raw_df, weights)
scored_df = scored_df.sort_values("weighted_total", ascending=False).reset_index(drop=True)


# ── Map builder ───────────────────────────────────────────────────────────────
def build_map(df: pd.DataFrame, selected: str) -> go.Figure:
    sel_mask  = df["area_name"] == selected
    unsel_df  = df[~sel_mask]
    sel_df    = df[sel_mask]

    fig = go.Figure()

    # Invisible legend-only traces (one per category colour)
    for cat, colour in CATEGORY_COLOURS.items():
        fig.add_trace(go.Scattermapbox(
            lat=[None], lon=[None],
            mode="markers",
            marker=dict(size=12, color=colour),
            name=cat,
            showlegend=True,
            hoverinfo="skip",
        ))

    # Unselected dots
    cd_unsel = unsel_df[["area_name", "weighted_total", "benefit_to_burden_ratio"]].values
    fig.add_trace(go.Scattermapbox(
        lat=unsel_df["lat"],
        lon=unsel_df["lon"],
        mode="markers",
        marker=dict(
            size=16,
            color=[CATEGORY_COLOURS.get(r, "#555") for r in unsel_df["recommendation"]],
            opacity=0.85,
        ),
        text=unsel_df["area_name"],
        customdata=cd_unsel,
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Score: %{customdata[1]:.1f} / 100<br>"
            "B:B Ratio: %{customdata[2]:.1f}×<br>"
            "<i>Click to select</i><extra></extra>"
        ),
        showlegend=False,
    ))

    # Selected dot — white ring + filled coloured dot
    if len(sel_df) > 0:
        sel_colour = CATEGORY_COLOURS.get(sel_df.iloc[0]["recommendation"], "#555")
        cd_sel = sel_df[["area_name", "weighted_total", "benefit_to_burden_ratio"]].values
        fig.add_trace(go.Scattermapbox(            # outer ring
            lat=sel_df["lat"], lon=sel_df["lon"],
            mode="markers",
            marker=dict(size=32, color="white", opacity=1.0),
            hoverinfo="skip",
            showlegend=False,
        ))
        fig.add_trace(go.Scattermapbox(            # inner dot
            lat=sel_df["lat"], lon=sel_df["lon"],
            mode="markers",
            marker=dict(size=22, color=sel_colour),
            text=sel_df["area_name"],
            customdata=cd_sel,
            hovertemplate=(
                "<b>%{customdata[0]}</b> ✓ selected<br>"
                "Score: %{customdata[1]:.1f} / 100<br>"
                "B:B Ratio: %{customdata[2]:.1f}×<extra></extra>"
            ),
            showlegend=False,
        ))

    fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            zoom=5.2,
            center=dict(lat=57.0, lon=-4.2),
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=480,
        legend=dict(
            title="Recommendation",
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="left",   x=0,
        ),
        uirevision="stable",  # keeps pan/zoom between reruns
    )
    return fig


# ── Radar chart builder ───────────────────────────────────────────────────────
def build_radar_trace(row: pd.Series, colour: str, name: str) -> go.Scatterpolar:
    values, labels = [], []
    for col, label, invert in RADAR_AXES:
        v = float(row[f"{col}_score"])
        values.append(5.0 - v if invert else v)
        labels.append(label)
    values.append(values[0])   # close the polygon
    labels.append(labels[0])
    return go.Scatterpolar(
        r=values, theta=labels,
        fill="toself",
        fillcolor=colour,
        line=dict(color=colour, width=2),
        opacity=0.5,
        name=name,
    )


# ── Scorecard renderer ────────────────────────────────────────────────────────
def render_scorecard(row: pd.Series):
    colour = CATEGORY_COLOURS.get(row["recommendation"], "#555")

    # ── Headline row
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.markdown(
            f"### {row['area_name']} "
            f"<span style='padding:4px 12px;border-radius:12px;background:{colour};"
            f"color:white;font-size:0.78rem;font-weight:600'>{row['recommendation']}</span>",
            unsafe_allow_html=True,
        )
        st.caption(f"{row['urban_rural_class']} · SIMD deprivation decile {int(row['simd_decile'])}")
    with col_b:
        ratio_colour = (
            "#2e7d32" if row["benefit_to_burden_ratio"] >= 1.5 else
            "#e65100" if row["benefit_to_burden_ratio"] >= 1.0 else "#b71c1c"
        )
        st.markdown(
            f"<div style='text-align:center'>"
            f"<div style='font-size:2.6rem;font-weight:700;color:{ratio_colour}'>"
            f"{row['benefit_to_burden_ratio']:.1f}×</div>"
            f"<div style='font-size:0.75rem;color:#888'>Benefit-to-burden ratio</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        interp = (
            "Benefits clearly outweigh burdens."  if row["benefit_to_burden_ratio"] >= 1.5 else
            "Benefits broadly balance burdens."   if row["benefit_to_burden_ratio"] >= 1.0 else
            "Burdens outweigh benefits — review."
        )
        st.caption(interp)

    st.divider()

    # ── Radar chart
    st.markdown("**Overall profile (all 7 dimensions)**")
    st.caption(
        "Each axis is 0–5. Burden axes (Low Env. Burden, Low Vulnerability) are "
        "flipped so that a larger filled area always means a better profile. "
        "The colour matches the recommendation category."
    )
    radar_fig = go.Figure(build_radar_trace(row, colour, row["area_name"]))
    radar_fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 5], tickfont_size=9),
            angularaxis=dict(tickfont_size=10),
        ),
        showlegend=False,
        margin=dict(l=50, r=50, t=30, b=30),
        height=300,
        paper_bgcolor="white",
    )
    st.plotly_chart(radar_fig, width="stretch", key=f"radar_{row['area_name']}")

    st.divider()

    # ── Readiness bars
    st.markdown("**Readiness indicators**")
    st.caption(
        "How ready is this site's infrastructure? Higher = better. "
        "These four dimensions measure grid capacity, digital connectivity, "
        "grid headroom for future demand, and whether existing brownfield sites "
        "or grid connections can be reused (avoiding new build)."
    )
    r_labels = [INDICATOR_LABELS[c] for c in READINESS_INDICATORS]
    r_scores = [float(row[f"{c}_score"]) for c in READINESS_INDICATORS]

    r_fig = go.Figure(go.Bar(
        x=r_scores, y=r_labels,
        orientation="h",
        marker_color=["#1565c0"] * len(r_labels),
        text=[f"{v:.1f}" for v in r_scores],
        textposition="outside",
    ))
    r_fig.update_layout(
        xaxis=dict(range=[0, 5.5], showgrid=False, tickvals=[0, 1, 2, 3, 4, 5]),
        yaxis=dict(autorange="reversed"),
        margin=dict(l=0, r=30, t=10, b=0),
        height=30 + 40 * len(r_labels),
        plot_bgcolor="white", paper_bgcolor="white", showlegend=False,
    )
    st.plotly_chart(r_fig, width="stretch", key=f"readiness_{row['area_name']}")

    # ── Distribution bars
    st.markdown("**Distribution indicators**")
    st.caption(
        "Who gains and who bears the cost? "
        "Community Benefit (green, higher = better) measures jobs and investment "
        "reaching deprived areas. Burden indicators (red, higher = MORE burden) "
        "show environmental stress and vulnerable households in the impact zone. "
        "A well-sited facility scores high on benefit and low on burden."
    )
    d_labels = (
        [f"{INDICATOR_LABELS[BENEFIT_INDICATOR]} (higher = better)"]
        + [f"{INDICATOR_LABELS[c]} (higher = more burden)" for c in BURDEN_INDICATORS]
    )
    d_scores = (
        [float(row[f"{BENEFIT_INDICATOR}_score"])]
        + [float(row[f"{c}_score"]) for c in BURDEN_INDICATORS]
    )
    d_colours = ["#2e7d32"] + ["#b71c1c"] * len(BURDEN_INDICATORS)

    d_fig = go.Figure(go.Bar(
        x=d_scores, y=d_labels,
        orientation="h",
        marker_color=d_colours,
        text=[f"{v:.1f}" for v in d_scores],
        textposition="outside",
    ))
    d_fig.update_layout(
        xaxis=dict(range=[0, 5.5], showgrid=False, tickvals=[0, 1, 2, 3, 4, 5]),
        yaxis=dict(autorange="reversed"),
        margin=dict(l=0, r=30, t=10, b=0),
        height=30 + 40 * len(d_labels),
        plot_bgcolor="white", paper_bgcolor="white", showlegend=False,
    )
    st.plotly_chart(d_fig, width="stretch", key=f"distribution_{row['area_name']}")

    # ── Risk chips
    chips = [
        RISK_CHIP_LABELS[col]
        for col, threshold in BURDEN_THRESHOLDS.items()
        if float(row[f"{col}_score"]) >= threshold
    ]
    if chips:
        chip_html = "".join(
            f"<span style='background:#b71c1c;color:white;border-radius:10px;"
            f"padding:3px 10px;margin:3px;font-size:0.78rem;display:inline-block'>⚠ {c}</span>"
            for c in chips
        )
        st.markdown(
            "**Risk flags** — burden indicators exceeded the 3/5 threshold:<br>" + chip_html,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<span style='color:#2e7d32;font-size:0.85rem'>✓ No high-threshold risk flags raised</span>",
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Jobs chart
    st.markdown("**Illustrative jobs breakdown**")
    st.caption(
        "Construction jobs are temporary and front-loaded. Operational jobs are permanent "
        "but far fewer — a critical equity point. Indirect jobs (supply chain, services) "
        "depend heavily on local procurement policy."
    )
    jobs_fig = go.Figure(go.Bar(
        x=["Construction\n(temporary)", "Operational\n(permanent)", "Indirect\n(supply chain)"],
        y=[int(row["jobs_construction"]), int(row["jobs_operational"]), int(row["jobs_indirect"])],
        marker_color=["#1565c0", "#0277bd", "#4fc3f7"],
        text=[int(row["jobs_construction"]), int(row["jobs_operational"]), int(row["jobs_indirect"])],
        textposition="outside",
    ))
    jobs_fig.update_layout(
        yaxis=dict(showgrid=False, title="FTE (illustrative)"),
        margin=dict(l=0, r=0, t=10, b=0),
        height=220,
        plot_bgcolor="white", paper_bgcolor="white", showlegend=False,
    )
    st.plotly_chart(jobs_fig, width="stretch", key=f"jobs_{row['area_name']}")

    st.divider()

    # ── Explanation + confidence
    st.markdown("**Plain-language summary**")
    st.caption(
        "Generated from a rule-based template (no AI). Summarises the top driver "
        "and top risk for this location."
    )
    st.info(row["explanation"])

    conf        = row["confidence_level"]
    conf_colour = CONFIDENCE_COLOURS.get(conf, "#555")
    st.markdown(
        f"**Evidence confidence:** "
        f"<span style='background:{conf_colour};color:white;border-radius:8px;"
        f"padding:2px 10px;font-size:0.82rem'>{conf.upper()}</span>",
        unsafe_allow_html=True,
    )
    st.caption({
        "low":    "Several indicators are based on limited or missing evidence. "
                  "Seek additional data before advancing this site.",
        "medium": "Most indicators are adequately evidenced; some assumptions remain.",
        "high":   "Indicators are well evidenced across all dimensions.",
    }.get(conf, ""))

    st.markdown(f"**Weighted total score:** `{row['weighted_total']:.1f} / 100`")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN PANEL
# ══════════════════════════════════════════════════════════════════════════════

# ── Map ───────────────────────────────────────────────────────────────────────
st.subheader("Scotland — candidate locations")
st.caption(
    "Each dot is a Scottish council area, coloured by recommendation. "
    "**Click any dot** to load its full scorecard below. "
    "Pan and zoom freely — your view is preserved between updates."
)

map_fig   = build_map(scored_df, st.session_state.selected_area)
map_event = st.plotly_chart(
    map_fig,
    on_select="rerun",
    selection_mode="points",
    key="map_chart",
    width="stretch",
)

# Handle map click → update selected area
if map_event and hasattr(map_event, "selection") and map_event.selection.points:
    pt = map_event.selection.points[0]
    cd = pt.get("customdata")
    if isinstance(cd, (list, tuple)) and cd:
        clicked = str(cd[0])
    else:
        clicked = str(cd) if cd else pt.get("text", "")
    if clicked in area_names and clicked != st.session_state.selected_area:
        st.session_state.selected_area = clicked
        st.rerun()

st.divider()

# ── Priority matrix + ranked table ────────────────────────────────────────────
col_matrix, col_table = st.columns([1, 1])

with col_matrix:
    st.subheader("Priority matrix")
    st.caption(
        "X-axis = Readiness score (infrastructure). Y-axis = Distribution score (equity). "
        "Top-right = ready AND equitable. Bottom-left = neither. "
        "The dashed lines mark the midpoint — use them to identify which dimension "
        "is the binding constraint for each area."
    )
    pm_sizes = [18 if n == st.session_state.selected_area else 10 for n in scored_df["area_name"]]
    pm_fig = px.scatter(
        scored_df,
        x="readiness_pct",
        y="distribution_pct",
        color="recommendation",
        color_discrete_map=CATEGORY_COLOURS,
        text="area_name",
        hover_data={"weighted_total": ":.1f", "benefit_to_burden_ratio": ":.1f",
                    "readiness_pct": False, "distribution_pct": False},
        size=pm_sizes,
        size_max=18,
        labels={"readiness_pct": "Readiness %", "distribution_pct": "Distribution %"},
    )
    pm_fig.update_traces(textposition="top center", textfont_size=10)
    pm_fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        height=340,
        xaxis=dict(range=[0, 108], title="Readiness %"),
        yaxis=dict(range=[0, 108], title="Distribution (equity) %"),
        plot_bgcolor="#f8f8f8",
        paper_bgcolor="white",
        showlegend=False,
        shapes=[
            dict(type="line", x0=50, x1=50, y0=0, y1=108,
                 line=dict(dash="dot", color="#aaa", width=1)),
            dict(type="line", x0=0, x1=108, y0=50, y1=50,
                 line=dict(dash="dot", color="#aaa", width=1)),
        ],
        annotations=[
            dict(x=97, y=97, text="Ready &\nequitable",   showarrow=False,
                 font=dict(size=9, color="#2e7d32")),
            dict(x=5,  y=97, text="Equitable\nnot ready", showarrow=False,
                 font=dict(size=9, color="#888"), xanchor="left"),
            dict(x=97, y=3,  text="Ready, not\nequitable", showarrow=False,
                 font=dict(size=9, color="#888"), xanchor="right"),
        ],
    )
    st.plotly_chart(pm_fig, width="stretch", key="priority_matrix")

with col_table:
    st.subheader("All areas — ranked")
    st.caption(
        "Rankings update live as you move the weight sliders. "
        "Areas with low evidence confidence are automatically flagged as "
        "'Needs further evidence' regardless of their raw score."
    )
    rank_df = scored_df[[
        "area_name", "weighted_total", "readiness_pct", "distribution_pct",
        "benefit_to_burden_ratio", "recommendation", "confidence_level"
    ]].copy()
    rank_df.columns = [
        "Area", "Score /100", "Readiness %", "Distribution %",
        "B:B Ratio", "Recommendation", "Confidence"
    ]
    rank_df["Score /100"]     = rank_df["Score /100"].round(1)
    rank_df["Readiness %"]    = rank_df["Readiness %"].round(1)
    rank_df["Distribution %"] = rank_df["Distribution %"].round(1)
    rank_df["B:B Ratio"]      = rank_df["B:B Ratio"].round(1)
    st.dataframe(rank_df.reset_index(drop=True), width="stretch", hide_index=True)

st.divider()

# ── Scorecard(s) ──────────────────────────────────────────────────────────────
focus_row = scored_df[scored_df["area_name"] == st.session_state.selected_area].iloc[0]
st.subheader(f"Scorecard — {st.session_state.selected_area}")
st.caption(
    "Full breakdown for the selected location. "
    "The radar chart gives a quick visual summary; "
    "scroll down for the detailed readiness and distribution bars, risk flags, "
    "jobs breakdown, and evidence confidence rating."
)

if compare_mode:
    compare_row = scored_df[scored_df["area_name"] == compare_area].iloc[0]

    # Combined radar at the top when comparing
    st.markdown("**Combined radar — head-to-head comparison**")
    st.caption(
        "Both areas overlaid on the same axes. The area with more polygon coverage "
        "across all seven dimensions has the stronger overall profile."
    )
    c1, c2 = st.session_state.selected_area, compare_area
    focus_colour   = CATEGORY_COLOURS.get(focus_row["recommendation"],   "#1565c0")
    compare_colour = CATEGORY_COLOURS.get(compare_row["recommendation"], "#b71c1c")
    combined_radar_fig = go.Figure()
    combined_radar_fig.add_trace(build_radar_trace(focus_row,   focus_colour,   c1))
    combined_radar_fig.add_trace(build_radar_trace(compare_row, compare_colour, c2))
    combined_radar_fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 5], tickfont_size=9),
            angularaxis=dict(tickfont_size=10),
        ),
        showlegend=True,
        margin=dict(l=50, r=50, t=40, b=30),
        height=360,
        paper_bgcolor="white",
    )
    st.plotly_chart(combined_radar_fig, width="stretch", key="combined_radar")
    st.divider()

    col_left, col_right = st.columns(2)
    with col_left:
        render_scorecard(focus_row)
    with col_right:
        render_scorecard(compare_row)
else:
    render_scorecard(focus_row)

# ── Not in scope ─────────────────────────────────────────────────────────────
st.divider()
st.subheader("⚠️ What this tool does not cover")
st.caption(
    "This dashboard is a **screening tool**, not a decision tool. "
    "A positive score does not mean a site is approved — it means it warrants closer investigation. "
    "The following are outside the current scope and would be required before any real siting decision:"
)

not_scope_col1, not_scope_col2 = st.columns(2)
with not_scope_col1:
    st.markdown("""
**Environmental & physical**
- Full Environmental Impact Assessment (EIA) — legally required before planning
- Site-level water consumption modelling vs actual source capacity ([BBC: 27 million bottles/year](https://www.bbc.co.uk/news/articles/c77zxx43x4vo))
- Flood risk and climate change projections (SEPA flood maps)
- Noise propagation modelling to nearest dwellings
- Operational carbon footprint and net-zero pathway
- Cooling system design and heat rejection impact

**Infrastructure**
- Real-time grid capacity data from SSEN / SP Energy Networks portals
- Dark fibre and telecoms backbone routing
- Road and rail access for construction logistics
- Water supply infrastructure capacity
""")
with not_scope_col2:
    st.markdown("""
**Community & social**
- Actual community consultation outcomes — no mechanism here for public voice
- Cumulative impact — what if multiple sites are approved in one area simultaneously?
- Skills gap analysis — is there a local workforce for operational jobs?
- Equalities impact assessment under the Public Sector Equality Duty
- Community benefit agreement terms and enforceability

**Governance & legal**
- Land ownership and acquisition feasibility
- Planning permission status and National Planning Framework 4 compliance
- National security review (NCSC data centre security considerations)
- Scottish AI Strategy 2026–2031 qualitative governance checklist
- Lifecycle decommissioning obligations
""")

# ── Data sources & methodology ────────────────────────────────────────────────
st.divider()
with st.expander("📚 Data sources, confidence levels & methodology"):
    st.markdown("""
### What's real vs estimated

| Indicator | Status | Source |
|---|---|---|
| Digital connectivity | ✅ **Real** — Ofcom FTTP % per council | [Ofcom Connected Nations 2025](https://www.ofcom.org.uk/phones-and-broadband/coverage-and-speeds/connected-nations-20252) via [ThinkBroadband](https://labs.thinkbroadband.com/local/scotland) (mirrors Ofcom, updated weekly) |
| Vulnerability exposure | ✅ **Real** — SIMD 2020 deprivation % | [Scottish Index of Multiple Deprivation 2020](https://www.gov.scot/collections/scottish-index-of-multiple-deprivation-2020/) |
| SIMD decile | ✅ **Real** — median SIMD decile per council | [SIMD 2020 — Scottish Government](https://www.gov.scot/collections/scottish-index-of-multiple-deprivation-2020/) |
| Urban/Rural class | ✅ **Real** | [Scottish Government Urban Rural Classification 2022](https://www.gov.scot/publications/scottish-government-urban-rural-classification-2022/) |
| Energy capacity | ⚠️ **DNO-zone estimate** — SP Distribution areas (Falkirk, Glasgow, West Lothian, Fife) scored higher; SSEN SHEPD areas (Highland, Argyll & Bute, Dundee, Aberdeenshire) lower | [SSEN Data Portal](https://data.ssen.co.uk/); [SP Energy Networks DFES](https://www.spenergynetworks.co.uk/) |
| Future grid headroom | ⚠️ **Estimate** — based on NESO FES 2025 Scotland can absorb up to 20% of GB data centre demand; central belt has more constraints | [NESO FES 2025 Dataworkbook](https://www.neso.energy/document/364696/download) — sheets BB1 (zones), ED1 (data centre demand) |
| Environmental burden | ⚠️ **SEPA-catchment estimate** — Forth catchment (Falkirk/West Lothian/Fife) more pressured; western/highland areas cleaner | [SEPA Water Classification Hub](https://informatics.sepa.org.uk/WaterClassificationHub/); [SEPA Data Centres Guide](https://beta.sepa.scot/topics/energy/data-centres/) |
| Infrastructure reuse | ⚠️ **Estimate** — industrial history proxy (Falkirk/Aberdeenshire higher; Glasgow competition reduces score) | [Scottish Vacant & Derelict Land Survey 2024](https://www.gov.scot/publications/scottish-vacant-derelict-land-statistics-2024/) |
| Community benefit | ⚠️ **SIMD-informed estimate** — deprived urban areas score higher potential | SIMD 2020; [Scottish Annual Business Statistics 2023](https://www.gov.scot/publications/scottish-annual-business-statistics-2023/) |
| Jobs figures | ❌ **Illustrative only** — scale estimates, not site-specific modelling | [NOMIS / BRES](https://www.nomisweb.co.uk/) for real estimates |

### Scoring methodology
- Indicators are **min-max normalised to 0–5** across the candidate set. Adding or removing areas rescales all scores.
- Burden indicators (environmental burden, vulnerability exposure) are shown raw (higher = worse). In the radar chart they are inverted so larger polygon = better.
- **Benefit-to-burden ratio** = community_benefit_score ÷ (environmental_burden_score + vulnerability_exposure_score). Below 1.0 means burdens outweigh benefits.
- **No machine learning** — the composite score is a fully transparent weighted sum reproducible in a spreadsheet.
- Confidence is aggregated from per-indicator `_confidence` fields (high=2, medium=1, low=0). An area scoring below 1.0 average is gated to "Needs further evidence" regardless of its weighted total.

### Key context
- Scottish data centres are [already using enough water to fill 27 million bottles a year](https://www.bbc.co.uk/news/articles/c77zxx43x4vo)
- SEPA [regulates associated activities](https://beta.sepa.scot/topics/energy/data-centres/) even though data centres are not standalone regulated facilities
- [Scotland's AI Strategy 2026–2031](https://www.gov.scot/binaries/content/documents/govscot/publications/strategy-plan/2026/03/scotlands-ai-strategy-2026-2031/documents/ai-strategy-scotland/ai-strategy-scotland/govscot%3Adocument/ai-strategy-scotland.pdf) sets the responsible AI infrastructure framework this tool supports
- [The Lancet (McLellan, 2026)](https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(26)00033-4/fulltext) documents the public health concerns that drive the equity focus of this tool
""")
