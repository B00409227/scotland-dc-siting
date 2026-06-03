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
    "environmental_burden":   "Water stress / environmental pressure",
    "vulnerability_exposure": "Deprived households in impact radius",
}

# McLellan (2026) health risk thresholds — derived from pop density and urban class
# Diesel generator pollution spikes: risk near dense population
# Urban heat island: Urban class + high env burden
# Noise nuisance: any area with population density > 300/km²
MCLELLAN_RISKS = {
    "diesel_generator": {
        "label": "Diesel generator pollution risk — dense population nearby (McLellan, 2026)",
        "colour": "#6a1a1a",
    },
    "urban_heat_island": {
        "label": "Urban heat island risk — waste heat in dense urban area (McLellan, 2026)",
        "colour": "#bf360c",
    },
    "noise_nuisance": {
        "label": "Noise nuisance risk — residential density exceeds 300/km² (McLellan, 2026)",
        "colour": "#4a148c",
    },
    "water_competition": {
        "label": "Water competition risk — high environmental burden catchment (McLellan, 2026)",
        "colour": "#01579b",
    },
}

# Scottish AI Strategy 2026-2031 governance checklist
AI_STRATEGY_CHECKS = [
    ("Transparent scoring — no black-box ML",            True),
    ("Human decision-maker retains final approval",      True),
    ("Equity indicators given equal weight to readiness",True),
    ("Evidence confidence rated and shown per indicator", True),
    ("Data sources cited and limitations documented",    True),
    ("Community consultation mechanism included",        False),
    ("Environmental Impact Assessment completed",        False),
    ("Equalities Impact Assessment completed",           False),
]

# NPF National Outcomes mapping
NPF_MAPPING = [
    ("Environment",   "We value, enjoy, protect and enhance our environment.",
     "environmental_burden"),
    ("Communities",   "We live in communities that are inclusive, empowered, resilient and safe.",
     "vulnerability_exposure"),
    ("Economy",       "We have a globally competitive, entrepreneurial, inclusive and sustainable economy.",
     "community_benefit"),
    ("Fair Work",     "We have thriving and innovative businesses, with quality jobs and fair work for everyone.",
     "community_benefit"),
]

CONFIDENCE_COLOURS = {"high": "#2e7d32", "medium": "#e65100", "low": "#b71c1c"}

# Map colour-by options: display label → (column, colorscale, invert, unit)
MAP_COLOUR_OPTIONS = {
    "Recommendation":          ("recommendation",       None,        False, ""),
    "Environmental Burden":    ("environmental_burden", "RdYlGn_r",  False, "% water bodies not Good/High"),
    "Digital Connectivity":    ("digital_connectivity", "Blues",     False, "% full-fibre (FTTP)"),
    "SIMD Deprivation":        ("vulnerability_exposure","RdYlGn_r", False, "% in most deprived 20%"),
    "Infrastructure Reuse":    ("infrastructure_reuse", "Greens",    False, "derelict + vacant ha"),
    "Weighted Score":          ("weighted_total",       "RdYlGn",    False, "/ 100"),
}


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
        "⚠️ **Prototype — mixed data.** Digital connectivity = real Ofcom 2025. "
        "Deprivation & vulnerability = real SIMD 2020. Environmental burden = real SEPA "
        "water classification. Infrastructure reuse = real SVDLS 2024. "
        "Energy & grid = DNO-zone estimates. Demographics = NRS Scotland 2023.",
    )

    st.divider()
    st.subheader("Indicator Weights")
    st.caption(
        "Move these sliders to re-score and re-rank all areas instantly. "
        "Setting Readiness to 0 means only equity matters; Distribution to 0 "
        "means only infrastructure counts."
    )
    w_readiness    = st.slider("Readiness",              0, 100, 50, key="w_readiness")
    w_distribution = st.slider("Distribution (equity)",  0, 100, 50, key="w_distribution")

    st.divider()
    st.subheader("Map display")
    map_colour_label = st.selectbox(
        "Colour dots by",
        list(MAP_COLOUR_OPTIONS.keys()),
        index=0,
        key="map_colour_by",
    )
    map_size_by_pop = st.checkbox(
        "Scale dot size by population",
        value=False,
        key="map_size_pop",
    )

    st.divider()
    st.subheader("Select Location")
    st.caption("Click a dot on the map, or choose below.")

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
        "Abdul Hannaan Mohammed · Calum Lang · Danny Lee · "
        "Laraine Ukwu-George · Vasyl Shvets\n\n"
        "🔗 [no-bias-intended.streamlit.app](https://no-bias-intended.streamlit.app)"
    )


# ── Scoring ───────────────────────────────────────────────────────────────────
weights   = {"readiness": w_readiness / 50.0, "distribution": w_distribution / 50.0}
scored_df = compute_scores(raw_df, weights)
scored_df = scored_df.sort_values("weighted_total", ascending=False).reset_index(drop=True)


# ── Map builder ───────────────────────────────────────────────────────────────
def build_map(df: pd.DataFrame, selected: str,
              colour_label: str, size_by_pop: bool) -> go.Figure:

    col_info = MAP_COLOUR_OPTIONS[colour_label]
    colour_col = col_info[0]
    colorscale = col_info[1]
    unit       = col_info[3]
    use_discrete = (colour_col == "recommendation")

    sel_mask = df["area_name"] == selected
    unsel_df = df[~sel_mask]
    sel_df   = df[sel_mask]

    # Dot sizes
    if size_by_pop:
        max_pop  = df["population"].max()
        sizes_unsel = (unsel_df["population"] / max_pop * 30 + 8).tolist()
        sizes_sel   = (sel_df["population"]   / max_pop * 30 + 8).tolist()
    else:
        sizes_unsel = [16] * len(unsel_df)
        sizes_sel   = [22]

    # Build hover template with demographic snapshot
    hover_tmpl = (
        "<b>%{customdata[0]}</b><br>"
        "Pop: %{customdata[6]:,} · %{customdata[7]} km²<br>"
        "Score: %{customdata[1]:.1f}/100 · B:B %{customdata[2]:.1f}×<br>"
        "SIMD decile: %{customdata[3]} · Deprivation: %{customdata[4]}%<br>"
        "Env burden: %{customdata[5]}%<br>"
        "<i>Click to select</i><extra></extra>"
    )
    hover_sel_tmpl = (
        "<b>%{customdata[0]}</b> ✓ selected<br>"
        "Pop: %{customdata[6]:,} · %{customdata[7]} km²<br>"
        "Score: %{customdata[1]:.1f}/100 · B:B %{customdata[2]:.1f}×<br>"
        "SIMD decile: %{customdata[3]} · Deprivation: %{customdata[4]}%<br>"
        "Env burden: %{customdata[5]}%<extra></extra>"
    )

    def make_customdata(sub):
        return sub[[
            "area_name", "weighted_total", "benefit_to_burden_ratio",
            "simd_decile", "vulnerability_exposure", "environmental_burden",
            "population", "area_km2"
        ]].values

    fig = go.Figure()

    if use_discrete:
        # Legend traces (invisible)
        for cat, colour in CATEGORY_COLOURS.items():
            fig.add_trace(go.Scattermap(
                lat=[None], lon=[None], mode="markers",
                marker=dict(size=12, color=colour),
                name=cat, showlegend=True, hoverinfo="skip",
            ))
        # Unselected dots
        fig.add_trace(go.Scattermap(
            lat=unsel_df["lat"], lon=unsel_df["lon"], mode="markers",
            marker=dict(
                size=sizes_unsel,
                color=[CATEGORY_COLOURS.get(r, "#555") for r in unsel_df["recommendation"]],
                opacity=0.85,
            ),
            text=unsel_df["area_name"],
            customdata=make_customdata(unsel_df),
            hovertemplate=hover_tmpl,
            showlegend=False,
        ))
    else:
        # Continuous colorscale — all unselected points
        vals = df[colour_col].tolist()
        vmin, vmax = min(vals), max(vals)
        unsel_vals = unsel_df[colour_col].tolist()
        fig.add_trace(go.Scattermap(
            lat=unsel_df["lat"], lon=unsel_df["lon"], mode="markers",
            marker=dict(
                size=sizes_unsel,
                color=unsel_vals,
                colorscale=colorscale,
                cmin=vmin, cmax=vmax,
                opacity=0.9,
                colorbar=dict(
                    title=dict(text=f"{colour_label}<br><sup>{unit}</sup>", side="right"),
                    thickness=14, len=0.6, y=0.5,
                    tickfont=dict(size=10),
                ),
            ),
            text=unsel_df["area_name"],
            customdata=make_customdata(unsel_df),
            hovertemplate=hover_tmpl,
            showlegend=False,
        ))

    # Selected dot — white ring then coloured dot
    if len(sel_df) > 0:
        if use_discrete:
            sel_colour = CATEGORY_COLOURS.get(sel_df.iloc[0]["recommendation"], "#555")
        else:
            sel_colour = "#1565c0"  # ring colour independent of colorscale

        fig.add_trace(go.Scattermap(           # white ring
            lat=sel_df["lat"], lon=sel_df["lon"], mode="markers",
            marker=dict(size=int(sizes_sel[0]) + 12, color="white", opacity=1.0),
            hoverinfo="skip", showlegend=False,
        ))
        fig.add_trace(go.Scattermap(           # coloured dot
            lat=sel_df["lat"], lon=sel_df["lon"], mode="markers",
            marker=dict(
                size=int(sizes_sel[0]),
                color=[float(sel_df.iloc[0][colour_col])] if not use_discrete else [sel_colour],
                colorscale=colorscale if not use_discrete else None,
                cmin=vmin if not use_discrete else None,
                cmax=vmax if not use_discrete else None,
                showscale=False,
            ),
            text=sel_df["area_name"],
            customdata=make_customdata(sel_df),
            hovertemplate=hover_sel_tmpl,
            showlegend=False,
        ))

    fig.update_layout(
        map=dict(style="carto-positron", zoom=5.2, center=dict(lat=57.0, lon=-4.2)),
        margin=dict(l=0, r=0, t=0, b=0),
        height=500,
        legend=dict(
            title="Recommendation", orientation="h",
            yanchor="bottom", y=1.02, xanchor="left", x=0,
        ),
        uirevision="stable",
    )
    return fig


# ── Radar chart builder ───────────────────────────────────────────────────────
def build_radar_trace(row: pd.Series, colour: str, name: str) -> go.Scatterpolar:
    values, labels = [], []
    for col, label, invert in RADAR_AXES:
        v = float(row[f"{col}_score"])
        values.append(5.0 - v if invert else v)
        labels.append(label)
    values.append(values[0])
    labels.append(labels[0])
    return go.Scatterpolar(
        r=values, theta=labels, fill="toself",
        fillcolor=colour, line=dict(color=colour, width=2),
        opacity=0.5, name=name,
    )


# ── Info card helper (demographics / geography / economics) ───────────────────
def info_card(title: str, colour: str, items: list[tuple]):
    """Render a titled card with (label, value, help_text) rows."""
    rows_html = "".join(
        f"<tr><td style='color:#888;font-size:0.78rem;padding:3px 8px 3px 0'>{lbl}</td>"
        f"<td style='font-weight:600;font-size:0.9rem;padding:3px 0'>{val}</td></tr>"
        for lbl, val, _ in items
    )
    st.markdown(
        f"<div style='border-left:4px solid {colour};padding:10px 14px;"
        f"background:#fafafa;border-radius:4px;margin-bottom:8px'>"
        f"<div style='font-size:0.8rem;font-weight:700;color:{colour};"
        f"letter-spacing:0.05em;margin-bottom:6px'>{title}</div>"
        f"<table style='border-collapse:collapse;width:100%'>{rows_html}</table>"
        f"</div>",
        unsafe_allow_html=True,
    )


# ── Scorecard renderer ────────────────────────────────────────────────────────
def render_scorecard(row: pd.Series):
    colour = CATEGORY_COLOURS.get(row["recommendation"], "#555")

    # ── Headline ──────────────────────────────────────────────────────────────
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.markdown(
            f"### {row['area_name']} "
            f"<span style='padding:4px 12px;border-radius:12px;background:{colour};"
            f"color:white;font-size:0.78rem;font-weight:600'>{row['recommendation']}</span>",
            unsafe_allow_html=True,
        )
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
        st.caption(
            "Benefits clearly outweigh burdens."  if row["benefit_to_burden_ratio"] >= 1.5 else
            "Benefits broadly balance burdens."   if row["benefit_to_burden_ratio"] >= 1.0 else
            "Burdens outweigh benefits — review."
        )

    st.divider()

    # ── Demographics | Geography | Economics ──────────────────────────────────
    st.markdown("**Area profile**")
    st.caption(
        "Static context for this council area. Sources: NRS Scotland Mid-2023 "
        "Population Estimates; SIMD 2020; ONS ASHE 2023; Scottish Government Urban "
        "Rural Classification 2022; SP/SSEN DNO licence areas."
    )

    d_col, g_col, e_col = st.columns(3)

    with d_col:
        info_card("Demographics", "#1565c0", [
            ("Population",          f"{int(row['population']):,}",                  "NRS mid-2023"),
            ("Population density",  f"{int(row['pop_density_per_km2']):,} /km²",    "NRS mid-2023"),
            ("Median age",          f"{int(row['median_age'])} years",              "Census 2022"),
            ("SIMD decile",         f"{int(row['simd_decile'])} / 10",              "SIMD 2020 (1=most deprived)"),
            ("Deprivation",         f"{int(row['vulnerability_exposure'])}% in most deprived 20%", "SIMD 2020"),
        ])

    with g_col:
        info_card("Geography", "#4a148c", [
            ("Area",                f"{int(row['area_km2']):,} km²",                "OS boundaries"),
            ("Urban/Rural class",   str(row["urban_rural_class"]),                  "ScotGov 2022"),
            ("DNO zone",            str(row["dno_zone"]),                           "SSEN/SP licence area"),
            ("FTTP coverage",       f"{int(row['digital_connectivity'])}%",         "Ofcom 2025"),
            ("Env. burden",         f"{row['environmental_burden']}% water bodies not Good/High", "SEPA 2024"),
        ])

    with e_col:
        info_card("Economics", "#1b5e20", [
            ("Employment rate",     f"{row['employment_rate_pct']}%",               "ONS APS 2023"),
            ("Median weekly pay",   f"£{int(row['median_weekly_earnings_gbp'])}",   "ONS ASHE 2023"),
            ("GVA index",           f"{int(row['gva_index'])} (Scotland=100)",      "ONS Regional GVA"),
            ("Derelict land",       f"{row['infrastructure_reuse']:.0f} ha",        "SVDLS 2024"),
            ("Operational jobs est.",f"{int(row['jobs_operational'])} (illustrative)", "Scale estimate"),
        ])

    st.divider()

    # ── Radar chart ───────────────────────────────────────────────────────────
    st.markdown("**Overall profile (all 7 siting indicators)**")
    st.caption(
        "Each axis is 0–5 (normalised across all 32 Scottish council areas). "
        "Burden axes (Low Env. Burden, Low Vulnerability) are flipped "
        "so a larger filled area always means a better siting profile."
    )
    radar_fig = go.Figure(build_radar_trace(row, colour, row["area_name"]))
    radar_fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 5], tickfont_size=9),
            angularaxis=dict(tickfont_size=10),
        ),
        showlegend=False,
        margin=dict(l=50, r=50, t=30, b=30),
        height=300, paper_bgcolor="white",
    )
    st.plotly_chart(radar_fig, width="stretch", key=f"radar_{row['area_name']}")

    st.divider()

    # ── Readiness bars ────────────────────────────────────────────────────────
    st.markdown("**Readiness indicators**")
    st.caption(
        "How ready is this site's infrastructure? Each bar is the normalised "
        "0–5 score. Higher = better. Energy and grid headroom are DNO-zone estimates; "
        "digital connectivity is real Ofcom FTTP data; infrastructure reuse is real "
        "SVDLS 2024 derelict + vacant land hectares."
    )
    r_labels = [INDICATOR_LABELS[c] for c in READINESS_INDICATORS]
    r_scores = [float(row[f"{c}_score"]) for c in READINESS_INDICATORS]
    r_conf   = [str(row[f"{c}_confidence"]) for c in READINESS_INDICATORS]
    r_colours = ["#1565c0" if c == "high" else "#64b5f6" if c == "medium" else "#bbdefb"
                 for c in r_conf]

    r_fig = go.Figure(go.Bar(
        x=r_scores, y=r_labels, orientation="h",
        marker_color=r_colours,
        text=[f"{v:.1f}  ({c})" for v, c in zip(r_scores, r_conf)],
        textposition="outside",
    ))
    r_fig.update_layout(
        xaxis=dict(range=[0, 6.5], showgrid=False, tickvals=[0,1,2,3,4,5]),
        yaxis=dict(autorange="reversed"),
        margin=dict(l=0, r=80, t=10, b=0),
        height=30 + 44 * len(r_labels),
        plot_bgcolor="white", paper_bgcolor="white", showlegend=False,
    )
    st.plotly_chart(r_fig, width="stretch", key=f"readiness_{row['area_name']}")

    # ── Distribution bars ─────────────────────────────────────────────────────
    st.markdown("**Distribution indicators**")
    st.caption(
        "Community Benefit (green) — higher = more benefit reaching deprived areas. "
        "Burden indicators (red) — higher = MORE burden on the community. "
        "Environmental burden uses real SEPA river water body classification; "
        "vulnerability exposure uses real SIMD 2020 deprivation data."
    )
    d_cols   = [BENEFIT_INDICATOR] + BURDEN_INDICATORS
    d_labels = (
        [f"{INDICATOR_LABELS[BENEFIT_INDICATOR]} (higher = better)"]
        + [f"{INDICATOR_LABELS[c]} (higher = more burden)" for c in BURDEN_INDICATORS]
    )
    d_scores  = [float(row[f"{c}_score"]) for c in d_cols]
    d_conf    = [str(row[f"{c}_confidence"]) for c in d_cols]
    d_colours = ["#2e7d32" if i == 0 else "#b71c1c" for i in range(len(d_cols))]

    d_fig = go.Figure(go.Bar(
        x=d_scores, y=d_labels, orientation="h",
        marker_color=d_colours,
        text=[f"{v:.1f}  ({c})" for v, c in zip(d_scores, d_conf)],
        textposition="outside",
    ))
    d_fig.update_layout(
        xaxis=dict(range=[0, 6.5], showgrid=False, tickvals=[0,1,2,3,4,5]),
        yaxis=dict(autorange="reversed"),
        margin=dict(l=0, r=80, t=10, b=0),
        height=30 + 44 * len(d_labels),
        plot_bgcolor="white", paper_bgcolor="white", showlegend=False,
    )
    st.plotly_chart(d_fig, width="stretch", key=f"distribution_{row['area_name']}")

    # ── Risk chips (siting indicators + McLellan 2026 health risks) ─────────────
    st.markdown("**Risk flags**")
    st.caption(
        "Raised automatically from indicator thresholds and McLellan (2026) "
        "public health criteria. These are screening flags — each requires "
        "site-specific assessment before any planning decision."
    )

    chips = []
    # Siting indicator thresholds
    for col, thr in BURDEN_THRESHOLDS.items():
        if float(row[f"{col}_score"]) >= thr:
            chips.append(("#b71c1c", f"⚠ {RISK_CHIP_LABELS[col]}"))

    # McLellan (2026) health risk flags
    pop_d = int(row["pop_density_per_km2"])
    is_urban = str(row["urban_rural_class"]) == "Urban"
    env_b = float(row["environmental_burden"])

    if pop_d > 500:
        chips.append(("#6a1a1a", f"⚠ {MCLELLAN_RISKS['diesel_generator']['label']}"))
    if is_urban and env_b > 60:
        chips.append(("#bf360c", f"⚠ {MCLELLAN_RISKS['urban_heat_island']['label']}"))
    if pop_d > 300:
        chips.append(("#4a148c", f"⚠ {MCLELLAN_RISKS['noise_nuisance']['label']}"))
    if env_b > 75:
        chips.append(("#01579b", f"⚠ {MCLELLAN_RISKS['water_competition']['label']}"))

    # Renewable energy advantage flag
    is_ssen = str(row["dno_zone"]) == "SSEN SHEPD"
    env_low = float(row["environmental_burden"]) < 50
    if is_ssen and env_low:
        chips.append(("#1b5e20", "✓ Renewable energy advantage — SSEN SHEPD zone near offshore/onshore wind; potential for near-zero carbon data centre operations"))

    if chips:
        chip_html = "".join(
            f"<span style='background:{col};color:white;border-radius:10px;"
            f"padding:4px 11px;margin:3px 3px 3px 0;font-size:0.78rem;"
            f"display:inline-block;line-height:1.4'>{label}</span>"
            for col, label in chips
        )
        st.markdown(chip_html, unsafe_allow_html=True)
    else:
        st.markdown(
            "<span style='color:#2e7d32;font-size:0.85rem'>✓ No risk flags raised</span>",
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Jobs chart ────────────────────────────────────────────────────────────
    st.markdown("**Illustrative jobs breakdown**")
    st.caption(
        "Construction jobs are large but temporary. Operational (permanent) jobs are "
        "far fewer — a critical equity point. Indirect jobs depend heavily on local "
        "procurement policy. All figures are illustrative scale estimates only."
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
        margin=dict(l=0, r=0, t=10, b=0), height=220,
        plot_bgcolor="white", paper_bgcolor="white", showlegend=False,
    )
    st.plotly_chart(jobs_fig, width="stretch", key=f"jobs_{row['area_name']}")

    st.divider()

    # ── Explanation + confidence ──────────────────────────────────────────────
    st.markdown("**Plain-language summary**")
    st.caption("Rule-based template — no AI. Summarises the top driver and top risk.")
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
        "low":    "Several indicators are based on limited evidence — gather more data before advancing this site.",
        "medium": "Most indicators are adequately evidenced; some assumptions remain.",
        "high":   "Indicators are well evidenced across all dimensions.",
    }.get(conf, ""))
    st.markdown(f"**Weighted total score:** `{row['weighted_total']:.1f} / 100`")

    st.divider()

    # ── Responsible AI governance checklist ───────────────────────────────────
    st.markdown("**Responsible AI governance checklist**")
    st.caption(
        "Based on Scotland's AI Strategy 2026–2031 principles: trustworthy, ethical, "
        "inclusive, transparent, accountable, human-overseen AI infrastructure."
    )
    for check, passed in AI_STRATEGY_CHECKS:
        icon   = "✅" if passed else "❌"
        colour = "#1b5e20" if passed else "#b71c1c"
        st.markdown(
            f"<span style='color:{colour};font-size:0.85rem'>{icon} {check}</span>",
            unsafe_allow_html=True,
        )
    st.caption(
        "❌ items are not blocking — they are the next steps a policymaker "
        "would commission after this screening tool identifies a candidate site."
    )

    st.divider()

    # ── NPF National Outcomes alignment ───────────────────────────────────────
    st.markdown("**National Performance Framework alignment**")
    st.caption("How this scorecard supports Scotland's NPF National Outcomes.")
    for outcome, desc, indicator in NPF_MAPPING:
        score = float(row.get(f"{indicator}_score", 0))
        bar_pct = int(score / 5 * 100)
        colour = "#2e7d32" if score >= 3 else "#e65100" if score >= 1.5 else "#b71c1c"
        st.markdown(
            f"<div style='margin-bottom:6px'>"
            f"<span style='font-size:0.8rem;font-weight:600;color:#333'>{outcome}</span> "
            f"<span style='font-size:0.75rem;color:#888'>— {desc}</span><br>"
            f"<div style='background:#eee;border-radius:4px;height:8px;width:100%;margin-top:3px'>"
            f"<div style='background:{colour};border-radius:4px;height:8px;width:{bar_pct}%'></div>"
            f"</div></div>",
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
# MAIN PANEL
# ══════════════════════════════════════════════════════════════════════════════

# ── Map ───────────────────────────────────────────────────────────────────────
col_info     = MAP_COLOUR_OPTIONS[map_colour_label]
colour_col   = col_info[0]
colour_unit  = col_info[3]

st.subheader("Scotland — candidate locations")
st.caption(
    f"Dots coloured by **{map_colour_label}**"
    + (f" ({colour_unit})" if colour_unit else "")
    + ". **Click any dot** to load its full scorecard. "
    "Use the sidebar to switch colour scheme or scale by population. Pan and zoom freely."
)

map_fig = build_map(
    scored_df,
    st.session_state.selected_area,
    map_colour_label,
    map_size_by_pop,
)
map_event = st.plotly_chart(
    map_fig, on_select="rerun", selection_mode="points",
    key="map_chart", width="stretch",
)

# Handle map click
if map_event and hasattr(map_event, "selection") and map_event.selection.points:
    pt = map_event.selection.points[0]
    cd = pt.get("customdata")
    clicked = str(cd[0]) if isinstance(cd, (list, tuple)) and cd else str(cd or pt.get("text", ""))
    if clicked in area_names and clicked != st.session_state.selected_area:
        st.session_state.selected_area = clicked
        st.rerun()

st.divider()

# ── Priority matrix + ranked table ────────────────────────────────────────────
col_matrix, col_table = st.columns([1, 1])

with col_matrix:
    st.subheader("Priority matrix")
    st.caption(
        "X = Readiness %, Y = Distribution (equity) %. "
        "Top-right = ready AND equitable. Dashed lines = midpoints. "
        "Dot size = population."
    )
    pm_sizes = [
        max(10, int(row["population"] / scored_df["population"].max() * 32))
        for _, row in scored_df.iterrows()
    ]
    pm_fig = px.scatter(
        scored_df,
        x="readiness_pct", y="distribution_pct",
        color="recommendation",
        color_discrete_map=CATEGORY_COLOURS,
        text="area_name",
        hover_data={
            "weighted_total": ":.1f",
            "benefit_to_burden_ratio": ":.1f",
            "population": ":,",
            "readiness_pct": False, "distribution_pct": False,
        },
        size=pm_sizes, size_max=32,
        labels={"readiness_pct": "Readiness %", "distribution_pct": "Distribution %"},
    )
    pm_fig.update_traces(textposition="top center", textfont_size=10)
    pm_fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=0), height=360,
        xaxis=dict(range=[0, 108], title="Readiness %"),
        yaxis=dict(range=[0, 108], title="Distribution (equity) %"),
        plot_bgcolor="#f8f8f8", paper_bgcolor="white", showlegend=False,
        shapes=[
            dict(type="line", x0=50, x1=50, y0=0, y1=108,
                 line=dict(dash="dot", color="#aaa", width=1)),
            dict(type="line", x0=0, x1=108, y0=50, y1=50,
                 line=dict(dash="dot", color="#aaa", width=1)),
        ],
        annotations=[
            dict(x=97, y=97, text="Ready &\nequitable",   showarrow=False, font=dict(size=9, color="#2e7d32")),
            dict(x=5,  y=97, text="Equitable\nnot ready", showarrow=False, font=dict(size=9, color="#888"), xanchor="left"),
            dict(x=97, y=3,  text="Ready, not\nequitable", showarrow=False, font=dict(size=9, color="#888"), xanchor="right"),
        ],
    )
    st.plotly_chart(pm_fig, width="stretch", key="priority_matrix")

with col_table:
    st.subheader("All areas — ranked")
    st.caption("Live rankings — move the weight sliders to re-order.")
    rank_df = scored_df[[
        "area_name", "weighted_total", "readiness_pct", "distribution_pct",
        "benefit_to_burden_ratio", "recommendation", "confidence_level",
        "population", "dno_zone",
    ]].copy()
    rank_df.columns = [
        "Area", "Score /100", "Readiness %", "Distribution %",
        "B:B Ratio", "Recommendation", "Confidence", "Population", "DNO Zone",
    ]
    for col in ["Score /100", "Readiness %", "Distribution %", "B:B Ratio"]:
        rank_df[col] = rank_df[col].round(1)
    rank_df["Population"] = rank_df["Population"].apply(lambda x: f"{int(x):,}")
    st.dataframe(rank_df.reset_index(drop=True), width="stretch", hide_index=True)

st.divider()

# ── Scorecard(s) ──────────────────────────────────────────────────────────────
focus_row = scored_df[scored_df["area_name"] == st.session_state.selected_area].iloc[0]
st.subheader(f"Scorecard — {st.session_state.selected_area}")
st.caption(
    "Full breakdown for the selected location — area profile, "
    "radar chart, readiness/distribution bars, risk flags, jobs, "
    "and evidence confidence."
)

if compare_mode:
    compare_row = scored_df[scored_df["area_name"] == compare_area].iloc[0]

    st.markdown("**Combined radar — head-to-head comparison**")
    st.caption("Both areas overlaid. Larger polygon coverage = stronger siting profile.")
    c1 = st.session_state.selected_area
    focus_colour   = CATEGORY_COLOURS.get(focus_row["recommendation"],   "#1565c0")
    compare_colour = CATEGORY_COLOURS.get(compare_row["recommendation"], "#b71c1c")
    combined_fig = go.Figure()
    combined_fig.add_trace(build_radar_trace(focus_row,   focus_colour,   c1))
    combined_fig.add_trace(build_radar_trace(compare_row, compare_colour, compare_area))
    combined_fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5], tickfont_size=9),
                   angularaxis=dict(tickfont_size=10)),
        showlegend=True,
        margin=dict(l=50, r=50, t=40, b=30), height=360, paper_bgcolor="white",
    )
    st.plotly_chart(combined_fig, width="stretch", key="combined_radar")
    st.divider()

    col_left, col_right = st.columns(2)
    with col_left:
        render_scorecard(focus_row)
    with col_right:
        render_scorecard(compare_row)
else:
    render_scorecard(focus_row)

# ── Not in scope ──────────────────────────────────────────────────────────────
st.divider()
st.subheader("⚠️ What this tool does not cover")
st.caption(
    "This is a **screening tool**, not a decision tool. "
    "A positive score means a site warrants further investigation — not that it is approved."
)

ns_left, ns_right = st.columns(2)
with ns_left:
    st.markdown("""
**Environmental & physical**
- Full Environmental Impact Assessment (EIA) — legally required before planning
- Site-level water consumption vs source capacity ([BBC: 27M bottles/year](https://www.bbc.co.uk/news/articles/c77zxx43x4vo))
- Flood risk and climate change projections
- Noise propagation modelling to nearest dwellings
- Operational carbon footprint and net-zero pathway
- Cooling system design and heat rejection

**Infrastructure**
- Real-time grid capacity from SSEN / SP Energy Networks portals
- Dark fibre and telecoms backbone routing
- Road and rail access for construction logistics
""")
with ns_right:
    st.markdown("""
**Community & social**
- Actual community consultation outcomes — no public voice mechanism here
- Cumulative impact — multiple sites approved simultaneously in one area
- Skills gap analysis — is there a local workforce for operational roles?
- Equalities impact under the Public Sector Equality Duty

**Governance & legal**
- Land ownership and acquisition feasibility
- Planning permission status and NPF4 compliance
- National security review (NCSC data centre security)
- Scottish AI Strategy 2026–2031 qualitative governance checklist
- Lifecycle decommissioning obligations
""")

# ── Data sources ──────────────────────────────────────────────────────────────
st.divider()
with st.expander("📚 Data sources, confidence levels & methodology"):
    st.markdown("""
### What's real vs estimated

| Indicator | Status | Source |
|---|---|---|
| Digital connectivity | ✅ **Real** — Ofcom FTTP % per council | [Ofcom Connected Nations 2025](https://www.ofcom.org.uk/phones-and-broadband/coverage-and-speeds/connected-nations-20252) via [ThinkBroadband](https://labs.thinkbroadband.com/local/scotland) |
| Vulnerability exposure | ✅ **Real** — SIMD 2020 % in most deprived 20% | [SIMD 2020 — Scottish Government](https://www.gov.scot/collections/scottish-index-of-multiple-deprivation-2020/) |
| Environmental burden | ✅ **Real** — SEPA ArcGIS API, % water bodies NOT at Good/High per sub-basin | [SEPA Water Classification Hub](https://informatics.sepa.org.uk/WaterClassificationHub/) |
| Infrastructure reuse | ✅ **Real** — SVDLS 2024 derelict + urban vacant land (ha) | [SVDLS 2024 Table 2](https://www.gov.scot/publications/scottish-vacant-derelict-land-statistics-2024/) |
| SIMD decile | ✅ **Real** | [SIMD 2020](https://www.gov.scot/collections/scottish-index-of-multiple-deprivation-2020/) |
| Urban/Rural class | ✅ **Real** | [ScotGov Urban Rural Classification 2022](https://www.gov.scot/publications/scottish-government-urban-rural-classification-2022/) |
| Population & density | ✅ **Real** | [NRS Scotland Mid-2023 Population Estimates](https://www.nrscotland.gov.uk/) |
| Median age | ✅ **Real** | [Scotland Census 2022](https://www.scotlandscensus.gov.uk/) |
| Employment rate | ✅ **Real** | [ONS Annual Population Survey 2023](https://www.ons.gov.uk/) |
| Median weekly earnings | ✅ **Real** | [ONS ASHE 2023](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/ashe) |
| GVA index | ✅ **Real** | [ONS Regional GVA (balanced)](https://www.ons.gov.uk/economy/grossvalueaddedgva) |
| Area km² | ✅ **Real** | [OS / ScotGov boundaries](https://spatialdata.gov.scot/) |
| DNO zone | ✅ **Real** | [SP Energy Networks PES 18](https://www.energybrokers.co.uk/electricity/pes-areas/pes-area-18); [SSEN SHEPD PES 17](https://www.energybrokers.co.uk/electricity/pes-areas/pes-area-17) |
| Energy capacity | ⚠️ **DNO-zone estimate** | [SSEN Data Portal](https://data.ssen.co.uk/); [SPEN DFES](https://www.spenergynetworks.co.uk/) |
| Future grid headroom | ⚠️ **Estimate** — NESO FES 2025 directional | [NESO FES 2025 Dataworkbook](https://www.neso.energy/document/364696/download) |
| Community benefit | ⚠️ **Formula-derived from real data** — (SIMD deprivation % × 1.2) + ((100 − employment rate) × 0.9) | SIMD 2020; [ONS APS 2023](https://www.ons.gov.uk/) — formula weights are transparent but subjective |
| Jobs figures | ❌ **Illustrative** | [NOMIS / BRES](https://www.nomisweb.co.uk/) for real estimates |

### Scoring
- Min-max normalisation to 0–5 across all 32 Scottish council areas. Adding/removing areas rescales all scores.
- Burden indicators shown raw (higher = worse); inverted only in the radar chart.
- Benefit-to-burden ratio = community_benefit_score ÷ (environmental_burden + vulnerability). Below 1.0 means burdens outweigh benefits.
- No machine learning — fully transparent weighted sum.
- Confidence aggregated from per-indicator `_confidence` fields. Below 1.0 average → "Needs further evidence."

### Key context
- [Scottish data centres already using 27M bottles of water/year equivalent (BBC)](https://www.bbc.co.uk/news/articles/c77zxx43x4vo)
- [SEPA regulates associated data centre activities](https://beta.sepa.scot/topics/energy/data-centres/)
- [Scotland's AI Strategy 2026–2031](https://www.gov.scot/binaries/content/documents/govscot/publications/strategy-plan/2026/03/scotlands-ai-strategy-2026-2031/documents/ai-strategy-scotland/ai-strategy-scotland/govscot%3Adocument/ai-strategy-scotland.pdf)
- [The Lancet: AI data centre public health concerns (McLellan, 2026)](https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(26)00033-4/fulltext)
""")
