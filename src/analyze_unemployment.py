from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data_raw" / "UnemploymentinIndia.csv"
CLEAN_DIR = ROOT / "data_clean"
FIG_DIR = ROOT / "figures"
DOC_DIR = ROOT / "docs"

RATE = "Estimated Unemployment Rate (%)"
EMPLOYED = "Estimated Employed"
LPR = "Estimated Labour Participation Rate (%)"


def load_clean() -> pd.DataFrame:
    df = pd.read_csv(RAW, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    df = df.dropna(how="all").copy()
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    for col in [RATE, EMPLOYED, LPR]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["Region"] = df["Region"].astype("string").str.strip()
    df["Area"] = df["Area"].astype("string").str.strip()
    # The available data ends in June 2020, so define the COVID shock as
    # March-June 2020 and the baseline as May 2019-February 2020.
    df["Period"] = pd.Categorical(
        df["Date"].map(lambda x: "Pre-COVID" if x < pd.Timestamp("2020-03-01") else "COVID shock"),
        categories=["Pre-COVID", "COVID shock"],
        ordered=True,
    )
    df["Month"] = df["Date"].dt.to_period("M").dt.to_timestamp()
    return df.dropna(subset=["Date", RATE, "Region", "Area"]).sort_values("Date")


def style() -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update({
        "figure.dpi": 140,
        "savefig.dpi": 180,
        "font.size": 10,
        "axes.titlesize": 14,
        "axes.labelsize": 10,
        "axes.titleweight": "bold",
        "axes.edgecolor": "#CBD5E1",
        "grid.color": "#E2E8F0",
        "grid.linewidth": 0.8,
    })


def save_fig(fig: plt.Figure, name: str) -> None:
    fig.tight_layout()
    fig.savefig(FIG_DIR / name, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def build_outputs(df: pd.DataFrame) -> dict:
    FIG_DIR.mkdir(exist_ok=True)
    CLEAN_DIR.mkdir(exist_ok=True)
    DOC_DIR.mkdir(exist_ok=True)
    df.to_csv(CLEAN_DIR / "unemployment_clean.csv", index=False)

    monthly = df.groupby("Month", as_index=False, observed=True)[RATE].mean()
    monthly_area = df.groupby(["Month", "Area"], as_index=False, observed=True)[RATE].mean()
    period = df.groupby("Period", observed=True)[RATE].agg(["count", "mean", "median", "min", "max"]).reset_index()
    area_period = df.groupby(["Period", "Area"], observed=True)[RATE].mean().reset_index()
    region = df.groupby("Region", as_index=False)[RATE].agg(["count", "mean", "median", "max"]).reset_index()
    region_period = df.groupby(["Region", "Period"], observed=True)[RATE].mean().reset_index()
    monthly_area = monthly_area.sort_values("Month")

    pre = df.loc[df["Period"].eq("Pre-COVID"), RATE].mean()
    shock = df.loc[df["Period"].eq("COVID shock"), RATE].mean()
    increase_pct = (shock / pre - 1) * 100
    peak_row = monthly.loc[monthly[RATE].idxmax()]
    top_region = region.sort_values("mean", ascending=False).iloc[0]
    area_delta = area_period.pivot(index="Area", columns="Period", values=RATE)
    urban_delta = (area_delta.loc["Urban", "COVID shock"] / area_delta.loc["Urban", "Pre-COVID"] - 1) * 100
    rural_delta = (area_delta.loc["Rural", "COVID shock"] / area_delta.loc["Rural", "Pre-COVID"] - 1) * 100

    # 1. National monthly trend with rural/urban comparison and COVID shading.
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(monthly["Month"], monthly[RATE], color="#0F766E", linewidth=3, marker="o", label="All areas")
    for area, color in [("Urban", "#F97316"), ("Rural", "#2563EB")]:
        tmp = monthly_area[monthly_area["Area"].eq(area)]
        ax.plot(tmp["Month"], tmp[RATE], color=color, linewidth=1.8, marker="o", alpha=0.9, label=area)
    ax.axvspan(pd.Timestamp("2020-03-01"), pd.Timestamp("2020-06-30"), color="#FDE68A", alpha=0.42, label="COVID shock window")
    ax.set_title("India unemployment rate surged during the COVID shock")
    ax.set_ylabel("Estimated unemployment rate (%)")
    ax.set_xlabel("")
    ax.legend(frameon=False, ncol=3, loc="upper left")
    save_fig(fig, "01_monthly_trend_covid.png")

    # 2. Pre-COVID vs COVID shock.
    fig, ax = plt.subplots(figsize=(7.5, 5))
    bars = ax.bar(period["Period"], period["mean"], color=["#94A3B8", "#DC2626"], width=0.58)
    ax.bar_label(bars, labels=[f"{v:.1f}%" for v in period["mean"]], padding=4, fontweight="bold")
    ax.set_title("Average unemployment rate: pre-COVID vs shock period")
    ax.set_ylabel("Average rate (%)")
    ax.set_ylim(0, max(period["mean"]) * 1.25)
    save_fig(fig, "02_covid_comparison.png")

    # 3. Regional ranking.
    rank = region.sort_values("mean", ascending=True)
    fig, ax = plt.subplots(figsize=(9, 8))
    ax.barh(rank["Region"], rank["mean"], color="#0F766E")
    ax.set_title("Average unemployment rate by region")
    ax.set_xlabel("Average estimated unemployment rate (%)")
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    save_fig(fig, "03_regional_ranking.png")

    # 4. Regional COVID change, top 10 absolute rates.
    wide = region_period.pivot(index="Region", columns="Period", values=RATE).dropna()
    wide["Change (pp)"] = wide["COVID shock"] - wide["Pre-COVID"]
    change = wide.sort_values("Change (pp)")
    fig, ax = plt.subplots(figsize=(9, 8))
    colors = ["#2563EB" if x < 0 else "#DC2626" for x in change["Change (pp)"]]
    ax.barh(change.index, change["Change (pp)"], color=colors)
    ax.axvline(0, color="#334155", linewidth=1)
    ax.set_title("COVID-period change in unemployment by region")
    ax.set_xlabel("Change in average rate, percentage points")
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    save_fig(fig, "04_regional_covid_change.png")

    # 5. Labour participation relationship.
    fig, ax = plt.subplots(figsize=(8, 5.5))
    for period_name, color in [("Pre-COVID", "#64748B"), ("COVID shock", "#DC2626")]:
        tmp = df[df["Period"].eq(period_name)]
        ax.scatter(tmp[LPR], tmp[RATE], s=22, alpha=0.42, color=color, label=period_name)
    ax.set_title("Labour participation and unemployment")
    ax.set_xlabel("Estimated labour participation rate (%)")
    ax.set_ylabel("Estimated unemployment rate (%)")
    ax.legend(frameon=False)
    save_fig(fig, "05_participation_vs_unemployment.png")

    summary = {
        "rows_after_cleaning": int(len(df)),
        "regions": int(df["Region"].nunique()),
        "date_start": str(df["Date"].min().date()),
        "date_end": str(df["Date"].max().date()),
        "pre_covid_average_rate": round(float(pre), 2),
        "covid_shock_average_rate": round(float(shock), 2),
        "covid_increase_percent": round(float(increase_pct), 1),
        "peak_month": str(peak_row["Month"].strftime("%Y-%m")),
        "peak_month_average_rate": round(float(peak_row[RATE]), 2),
        "highest_average_region": str(top_region["Region"]),
        "highest_average_region_rate": round(float(top_region["mean"]), 2),
        "urban_increase_percent": round(float(urban_delta), 1),
        "rural_increase_percent": round(float(rural_delta), 1),
        "urban_pre_covid_rate": round(float(area_delta.loc["Urban", "Pre-COVID"]), 2),
        "urban_covid_rate": round(float(area_delta.loc["Urban", "COVID shock"]), 2),
        "rural_pre_covid_rate": round(float(area_delta.loc["Rural", "Pre-COVID"]), 2),
        "rural_covid_rate": round(float(area_delta.loc["Rural", "COVID shock"]), 2),
    }
    (CLEAN_DIR / "summary_metrics.json").write_text(json.dumps(summary, indent=2))
    return summary


def write_report(summary: dict) -> None:
    report = f"""# Unemployment Analysis in India — CodeAlpha Task 2

## Executive summary

This analysis covers {summary['rows_after_cleaning']:,} cleaned monthly observations across {summary['regions']} Indian regions from {summary['date_start']} to {summary['date_end']}. The dataset shows a clear COVID-period labour-market shock: the mean estimated unemployment rate increased from **{summary['pre_covid_average_rate']:.2f}%** before March 2020 to **{summary['covid_shock_average_rate']:.2f}%** during March–June 2020, an increase of **{summary['covid_increase_percent']:.1f}%**.

The highest national monthly average occurred in **{summary['peak_month']}**, at **{summary['peak_month_average_rate']:.2f}%**. **{summary['highest_average_region']}** had the highest average regional unemployment rate across the study period at **{summary['highest_average_region_rate']:.2f}%**.

## Data preparation

The uploaded file was labelled `.xls` but contains UTF-8 CSV data. It was read using `utf-8-sig`, stripped of the 28 blank records, parsed with day-first dates, and converted to a clean CSV. Numeric columns were explicitly coerced to numeric types. The resulting dataset has no blank rows and is saved at `data_clean/unemployment_clean.csv`.

## COVID-19 impact

The analysis defines the pre-COVID baseline as May 2019–February 2020 and the COVID shock window as March–June 2020. This is a descriptive before/after comparison, not a causal estimate: the dataset ends in June 2020 and does not control for region-specific economic structure, measurement changes, or other simultaneous shocks.

Urban unemployment increased from **{summary['urban_pre_covid_rate']:.2f}%** to **{summary['urban_covid_rate']:.2f}%** (**{summary['urban_increase_percent']:.1f}%**), while rural unemployment increased from **{summary['rural_pre_covid_rate']:.2f}%** to **{summary['rural_covid_rate']:.2f}%** (**{summary['rural_increase_percent']:.1f}%**). The monthly pattern shows the sharpest national stress in April and May 2020, followed by partial easing in June.

## Patterns and seasonality

- The series is monthly and short, so seasonal claims should be treated cautiously.
- The largest signal is a structural shock in spring 2020 rather than a stable recurring seasonal pattern.
- Regional dispersion is substantial: national averages conceal very different local labour-market outcomes.
- Rural and urban rates move together during the shock, but their levels and magnitude of change differ.
- Labour participation should be monitored alongside unemployment: a lower unemployment rate can coexist with weaker labour-market engagement if people leave the labour force.

## Policy implications

1. **Target emergency employment support geographically.** High-average and high-increase regions should receive priority for public works, wage support, and local job matching.
2. **Track rural and urban markets separately.** A single national rate can hide different transmission channels and recovery speeds.
3. **Pair unemployment with participation.** Monitoring both indicators helps distinguish job creation from labour-force withdrawal.
4. **Use high-frequency dashboards.** Monthly regional monitoring can identify renewed shocks earlier than annual statistics.
5. **Treat the results as descriptive evidence.** A causal policy evaluation would require longer pre-periods, post-period observations, controls, and a transparent identification strategy.

## Reproducibility

Run:

```bash
python src/analyze_unemployment.py
```

Charts are saved in `figures/`, cleaned data in `data_clean/`, and the notebook is in `notebooks/unemployment_analysis.ipynb`.
"""
    (DOC_DIR / "ANALYSIS_REPORT.md").write_text(report)


def main() -> None:
    style()
    df = load_clean()
    summary = build_outputs(df)
    write_report(summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
