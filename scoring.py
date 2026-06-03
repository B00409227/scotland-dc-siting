import pandas as pd

RAW_INDICATORS = [
    "energy_capacity",
    "digital_connectivity",
    "future_grid_headroom",
    "infrastructure_reuse",
    "community_benefit",
    "environmental_burden",
    "vulnerability_exposure",
]

READINESS_INDICATORS = [
    "energy_capacity",
    "digital_connectivity",
    "future_grid_headroom",
    "infrastructure_reuse",
]

BENEFIT_INDICATOR = "community_benefit"
BURDEN_INDICATORS = ["environmental_burden", "vulnerability_exposure"]

RECOMMENDATION_THRESHOLDS = {
    "strong": 70,
    "safeguards": 50,
    "not_suitable": 0,
}

CATEGORY_LABELS = {
    "strong": "Strong candidate",
    "safeguards": "Possible with safeguards",
    "not_suitable": "Not suitable now",
    "evidence": "Needs further evidence",
}

CONFIDENCE_RANK = {"low": 0, "medium": 1, "high": 2}


def minmax_scale(series: pd.Series, floor: float = 0.0, ceiling: float = 5.0) -> pd.Series:
    min_val = series.min()
    max_val = series.max()
    if min_val == max_val:
        return pd.Series([ceiling / 2] * len(series), index=series.index)
    scaled = (series - min_val) / (max_val - min_val) * (ceiling - floor) + floor
    return scaled


def normalize_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in RAW_INDICATORS:
        df[f"{col}_score"] = minmax_scale(df[col])
    return df


def inverted_burden_score(value: float) -> float:
    return 5.0 - value


def compute_bucket_scores(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["readiness_score"] = df[[f"{col}_score" for col in READINESS_INDICATORS]].sum(axis=1)
    df["benefit_score"] = df[f"{BENEFIT_INDICATOR}_score"]
    df["burden_score"] = df[[f"{col}_score" for col in BURDEN_INDICATORS]].sum(axis=1)
    df["distribution_score"] = (
        df[f"{BENEFIT_INDICATOR}_score"]
        + 5.0 * len(BURDEN_INDICATORS)
        - df["burden_score"]
    )
    return df


def normalize_bucket(df: pd.DataFrame, raw_score: str, max_value: float) -> pd.Series:
    return (df[raw_score] / max_value) * 100 if max_value > 0 else pd.Series(0.0, index=df.index)


def compute_weighted_total(df: pd.DataFrame, weights: dict[str, float]) -> pd.DataFrame:
    df = df.copy()
    readiness_pct = normalize_bucket(df, "readiness_score", len(READINESS_INDICATORS) * 5)
    distribution_pct = normalize_bucket(df, "distribution_score", (1 + len(BURDEN_INDICATORS)) * 5)
    weight_readiness = float(weights.get("readiness", 1.0))
    weight_distribution = float(weights.get("distribution", 1.0))
    total_weight = weight_readiness + weight_distribution
    if total_weight <= 0:
        total_weight = 1.0
    df["weighted_total"] = (
        readiness_pct * weight_readiness + distribution_pct * weight_distribution
    ) / total_weight
    df["readiness_pct"] = readiness_pct
    df["distribution_pct"] = distribution_pct
    return df


def compute_benefit_to_burden_ratio(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    denominator = df["burden_score"].replace(0, 0.1)
    df["benefit_to_burden_ratio"] = (df["benefit_score"] / denominator).round(1)
    return df


def aggregate_confidence(row: pd.Series) -> str:
    confidences = [row[f"{col}_confidence"] for col in RAW_INDICATORS if pd.notna(row.get(f"{col}_confidence"))]
    if not confidences:
        return "low"
    ranks = [CONFIDENCE_RANK.get(value, 0) for value in confidences]
    avg_rank = sum(ranks) / len(ranks)
    if avg_rank >= 1.7:
        return "high"
    if avg_rank >= 1.0:
        return "medium"
    return "low"


def determine_recommendation_category(row: pd.Series) -> str:
    if row.get("confidence_level") == "low":
        return CATEGORY_LABELS["evidence"]
    score = row.get("weighted_total", 0.0)
    if score >= RECOMMENDATION_THRESHOLDS["strong"]:
        return CATEGORY_LABELS["strong"]
    if score >= RECOMMENDATION_THRESHOLDS["safeguards"]:
        return CATEGORY_LABELS["safeguards"]
    return CATEGORY_LABELS["not_suitable"]


def top_driver(row: pd.Series) -> str:
    scores = {col: row[f"{col}_score"] for col in READINESS_INDICATORS + [BENEFIT_INDICATOR]}
    top = max(scores, key=scores.get)
    label = top.replace("_", " ").title()
    return label


def top_risk(row: pd.Series) -> str:
    burden_values = {col: row[f"{col}_score"] for col in BURDEN_INDICATORS}
    top = max(burden_values, key=burden_values.get)
    risk_map = {
        "environmental_burden": "environmental burden",
        "vulnerability_exposure": "vulnerability exposure",
    }
    return risk_map.get(top, top.replace("_", " "))


def format_explanation(row: pd.Series) -> str:
    driver = top_driver(row)
    risk = top_risk(row)
    ratio_text = f"Benefit-to-burden ratio is {row['benefit_to_burden_ratio']:.1f}."
    return (
        f"This location is strongest in {driver.lower()}, while its top risk is {risk}. "
        f"Use the ratio and confidence level to compare trade-offs across shortlisted areas. {ratio_text}"
    )


def compute_scores(df: pd.DataFrame, weights: dict[str, float] | None = None) -> pd.DataFrame:
    if weights is None:
        weights = {"readiness": 1.0, "distribution": 1.0}
    df = normalize_indicators(df)
    df = compute_bucket_scores(df)
    df = compute_weighted_total(df, weights)
    df = compute_benefit_to_burden_ratio(df)
    df = df.copy()
    df["confidence_level"] = df.apply(aggregate_confidence, axis=1)
    df["recommendation"] = df.apply(determine_recommendation_category, axis=1)
    df["explanation"] = df.apply(format_explanation, axis=1)
    return df


def load_sample_data(path: str = "data/areas.csv") -> pd.DataFrame:
    return pd.read_csv(path)


if __name__ == "__main__":
    data = load_sample_data()
    scored = compute_scores(data)
    print(scored[["area_name", "weighted_total", "benefit_to_burden_ratio", "recommendation", "confidence_level"]])
