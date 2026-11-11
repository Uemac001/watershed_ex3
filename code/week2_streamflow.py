"""Week 2: present vs future streamflow (seasonality and annual maxima).

Runs the Bucket Model for the present WeaGETS ensemble and for the future (delta change) ensemble,
keeps per realization the mean monthly runoff and the annual maximum daily runoff, and makes
- plot_monthly_boxplot: mean monthly runoff, boxes = the 5 climate models per RCP, line = present ensemble
- plot_return_periods: empirical return periods of the annual maxima (Weibull plotting positions,
  T = (n+1)/rank) of each 30-year realization, median and 5-95% band per rank and group
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from BucketModel import BucketModel
from BucketModel.data_processing import preprocess_for_bucket_model, run_multiple_simulations
from climate_simulation import get_model_from_filename

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
GROUPS = ["Present", "RCP4.5", "RCP8.5"]
COLORS = {"Present": "#222222", "RCP4.5": "#2a78b5", "RCP8.5": "#d1495b"}


def make_bucket_model() -> BucketModel:
    """Bucket Model with the Exercise 2 parameters (NSE calibration), as in tutorial.ipynb."""
    model = BucketModel(k=1.0155, S_max=10.0, fr=0.1184, rg=24.6808, snow_threshold_temp=-0.8451)
    model.set_catchment_properties(
        lapse_rate=0.5 / 100, basin_mean_elevation=2035, hru_mean_elevation=2035,
        snowmelt_temp_threshold=0, latitude=46.59,
    )
    return model


def summarize(results: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Per realization: mean monthly runoff [mm/month] (12 columns) and annual maxima [mm/d] (one row per year)."""
    q = (results["Q_s"] + results["Q_gw"]).astype(float)
    sim = results["Simulation"].astype(int).to_numpy()
    df = pd.DataFrame({"q": q.to_numpy(), "sim": sim, "year": q.index.year, "month": q.index.month})
    monthly = (df.groupby(["sim", "year", "month"])["q"].sum()
               .groupby(["sim", "month"]).mean().unstack("month"))
    annual_max = df.groupby(["sim", "year"])["q"].max().unstack("year")
    return monthly, annual_max


def run_ensemble(preprocessed: pd.DataFrame, model: BucketModel) -> tuple[pd.DataFrame, pd.DataFrame]:
    n = preprocessed["Simulation"].nunique()
    return summarize(run_multiple_simulations(preprocessed, model, n_simulations=n))


def run_all(present_simulated: pd.DataFrame, future_dir: Path, cache: Path | None = None,
            model: BucketModel | None = None) -> dict:
    """Run present and all future scenarios; returns {"monthly": df, "annual_max": df, "annual_mean": series}
    with index (group, climate model, realization). Results are cached in `cache` (pickle) if given.

    annual_mean is the mean annual runoff [mm/yr] of each realization (sum of the 12 mean monthly totals,
    the same as the mean of the yearly totals), used for the uncertainty partition (Task 3)."""
    if cache is not None and Path(cache).exists():
        result = pd.read_pickle(cache)
        if "annual_mean" not in result:
            result["annual_mean"] = result["monthly"].sum(axis=1).rename("annual_mean")
            pd.to_pickle(result, cache)
        return result
    model = model or make_bucket_model()
    monthly, annual_max = {}, {}
    m, a = run_ensemble(preprocess_for_bucket_model(present_simulated), model)
    monthly[("Present", "-")], annual_max[("Present", "-")] = m, a
    for path in sorted(Path(future_dir).glob("*.csv")):
        rcp = "RCP4.5" if path.stem.endswith("RCP4.5") else "RCP8.5"
        climate_model = get_model_from_filename(path.name)
        print(f"running {rcp} {climate_model}", flush=True)
        m, a = run_ensemble(preprocess_for_bucket_model(pd.read_csv(path)), model)
        monthly[(rcp, climate_model)], annual_max[(rcp, climate_model)] = m, a

    def stack(parts):
        out = pd.concat({k: v.set_axis(range(v.shape[1]) if v.columns.name == "year" else v.columns, axis=1)
                         for k, v in parts.items()}, names=["group", "climate_model", "sim"])
        return out

    result = {"monthly": stack(monthly), "annual_max": stack(annual_max)}
    result["annual_mean"] = result["monthly"].sum(axis=1).rename("annual_mean")
    if cache is not None:
        pd.to_pickle(result, cache)
    return result


def plot_monthly_boxplot(monthly: pd.DataFrame, output_destination: str | None = None) -> pd.DataFrame:
    """Boxes: mean monthly runoff of the 5 climate models (each = mean of its realizations) per RCP.
    Line: mean of the present ensemble. Returns the values that were plotted."""
    per_model = monthly.groupby(["group", "climate_model"]).mean()
    present = per_model.loc["Present"].iloc[0]
    fig, ax = plt.subplots(figsize=(11, 5))
    x = np.arange(1, 13)
    for offset, rcp in [(-0.18, "RCP4.5"), (0.18, "RCP8.5")]:
        values = per_model.loc[rcp]
        ax.boxplot([values[mo] for mo in x], positions=x + offset, widths=0.3, patch_artist=True,
                   boxprops=dict(facecolor="white", edgecolor=COLORS[rcp], linewidth=1.5),
                   whiskerprops=dict(color=COLORS[rcp]), capprops=dict(color=COLORS[rcp]),
                   medianprops=dict(color=COLORS[rcp], linewidth=2), flierprops=dict(markeredgecolor=COLORS[rcp]))
        ax.plot([], [], color=COLORS[rcp], linewidth=6, alpha=0.6, label=f"{rcp} (5 climate models, each the mean of 50 realizations)")
    ax.plot(x, present.to_numpy(), color=COLORS["Present"], linewidth=2, marker="o", markersize=5,
            label="Present (WeaGETS ensemble)")
    ax.set_xticks(x, MONTHS)
    ax.set_ylabel("Mean monthly runoff [mm/month]")
    ax.set_title("Mean monthly runoff: present vs 2070-2099")
    ax.grid(axis="y", alpha=0.3)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(frameon=False)
    fig.tight_layout()
    if output_destination:
        fig.savefig(output_destination, dpi=300, bbox_inches="tight")
    table = per_model.copy()
    table.columns = MONTHS
    return table.round(1)


def plot_monthly_band(monthly: pd.DataFrame, output_destination: str | None = None) -> pd.DataFrame:
    """Mean monthly runoff, median and 5-95% over all realizations of each group
    (present: 50; each RCP: 5 climate models x 50), so the bands include both the climate model
    spread and the natural variability. Returns the plotted values."""
    x = np.arange(1, 13)
    fig, ax = plt.subplots(figsize=(11, 5))
    rows = {}
    for group in GROUPS:
        values = monthly.xs(group, level="group")
        q05, q50, q95 = values.quantile(0.05), values.median(), values.quantile(0.95)
        ax.fill_between(x, q05.to_numpy(), q95.to_numpy(), color=COLORS[group], alpha=0.18, linewidth=0)
        ax.plot(x, q50.to_numpy(), "-o", color=COLORS[group], linewidth=2, markersize=4,
                label=f"{group_label_monthly(values, group)}: median and 5-95%")
        for name, q in (("5%", q05), ("median", q50), ("95%", q95)):
            rows[(group, name)] = q.to_numpy()
    ax.set_xticks(x, MONTHS)
    ax.set_ylabel("Mean monthly runoff [mm/month]")
    ax.set_title("Mean monthly runoff: present vs 2070-2099")
    ax.grid(axis="y", alpha=0.3)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(frameon=False)
    fig.tight_layout()
    if output_destination:
        fig.savefig(output_destination, dpi=300, bbox_inches="tight")
    return pd.DataFrame.from_dict(rows, orient="index", columns=MONTHS).round(1)


def group_label_monthly(values: pd.DataFrame, group: str) -> str:
    """Label from the realizations of one group (index: climate_model, sim)."""
    if group == "Present":
        return f"Present ({len(values)} realizations)"
    per_model = values.groupby(level="climate_model").size()
    return f"{group} ({len(per_model)} climate models × {per_model.iloc[0]} realizations)"


def empirical_positions(annual_max: pd.DataFrame) -> pd.DataFrame:
    """Weibull plotting positions per realization: sorted maxima (largest first), T = (n+1)/rank."""
    sorted_values = -np.sort(-annual_max.to_numpy(), axis=1)
    n = sorted_values.shape[1]
    return pd.DataFrame(sorted_values, index=annual_max.index, columns=(n + 1) / np.arange(1, n + 1))


def group_label(annual_max: pd.DataFrame, group: str) -> str:
    """e.g. 'Present (50 realizations)' or 'RCP4.5 (5 climate models x 50 realizations)'."""
    am = annual_max.xs(group, level="group")
    if group == "Present":
        return f"Present ({len(am)} realizations)"
    per_model = am.groupby(level="climate_model").size()
    return f"{group} ({len(per_model)} climate models \u00d7 {per_model.iloc[0]} realizations)"


def plot_return_periods(annual_max: pd.DataFrame, output_destination: str | None = None) -> pd.DataFrame:
    """Empirical return period plot of the annual maximum daily runoff for present, RCP4.5 and RCP8.5.

    Each 30-year realization gives 30 points at T = (n+1)/rank = 31, 15.5, ..., 1.03 years (Weibull).
    Line = median over the realizations of each rank, band = 5-95%."""
    fig, ax = plt.subplots(figsize=(8, 5.5))
    for group in GROUPS:
        emp = empirical_positions(annual_max.xs(group, level="group"))
        T = emp.columns.to_numpy()
        ax.fill_between(T, emp.quantile(0.05), emp.quantile(0.95), color=COLORS[group], alpha=0.15, linewidth=0)
        ax.plot(T, emp.median(), "-o", color=COLORS[group], linewidth=1.8, markersize=3.5,
                label=f"{group_label(annual_max, group)}: median and 5-95%")
    ax.set_xscale("log")
    ax.set_xticks([1, 2, 5, 10, 20, 30], ["1", "2", "5", "10", "20", "30"])
    ax.set_xlim(1, 33)
    ax.set_xlabel("Return period T = (n+1)/rank [years] (Weibull, n = 30)")
    ax.set_ylabel("Annual maximum daily runoff [mm/d]")
    ax.set_title("Annual maximum daily runoff: present vs 2070-2099")
    ax.grid(alpha=0.3, which="both")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(frameon=False, loc="upper left", fontsize=9)
    fig.tight_layout()
    if output_destination:
        fig.savefig(output_destination, dpi=300, bbox_inches="tight")
    return return_period_table(annual_max)


def uncertainty_input(annual_mean: pd.Series) -> pd.DataFrame:
    """Future realizations in the format of simulate_and_aggregate_streamflows (tutorial.ipynb):
    columns Simulation, Streamflow (mean annual runoff [mm/yr]), Climate_Model, Scenario."""
    future = annual_mean.drop(index="Present", level="group")
    return pd.DataFrame({
        "Simulation": future.index.get_level_values("sim"),
        "Streamflow": future.to_numpy(),
        "Climate_Model": future.index.get_level_values("climate_model").str.replace("-", "_"),
        "Scenario": future.index.get_level_values("group"),
    })


def uncertainty_partition(annual_mean: pd.Series) -> pd.DataFrame:
    """Task 3 with the tutorial's UncertaintyAnalysis: total, emission, climate model and stochastic
    uncertainty of the mean annual runoff, and each one divided by the total."""
    from uncertainty_analysis import UncertaintyAnalysis

    ua = UncertaintyAnalysis(uncertainty_input(annual_mean))
    tu = ua.calculate_tu("Streamflow")
    eu, eu_p = ua.calculate_eu("Streamflow", tu)
    cmu, cmu_p = ua.calculate_cmu("Streamflow", tu)
    su, su_p = ua.calculate_su("Streamflow", tu)
    return pd.DataFrame(
        {"Uncertainty [mm/yr]": [tu, eu, cmu, su], "Partition [-]": [1.0, eu_p, cmu_p, su_p]},
        index=["Total (TU)", "Emission scenario (EU)", "Climate model (CMU)", "Stochastic (SU)"],
    )


def return_period_table(annual_max: pd.DataFrame, ranks=(15, 6, 3, 1)) -> pd.DataFrame:
    """Empirical (Weibull) values at the given ranks: median and 5-95% over the realizations, and the
    change of the median vs present. With n = 30 the ranks 15, 6, 3, 1 are T = 2.1, 5.2, 10.3, 31 years."""
    rows, present_median = [], None
    for group in GROUPS:
        emp = empirical_positions(annual_max.xs(group, level="group"))
        n = emp.shape[1]
        values = {r: emp.iloc[:, r - 1] for r in ranks}
        med = {r: v.median() for r, v in values.items()}
        if group == "Present":
            present_median = med
        for r, v in values.items():
            rows.append({
                "Group": group_label(annual_max, group), "T [years]": round((n + 1) / r, 1),
                "Median [mm/d]": round(med[r], 1),
                "5-95% [mm/d]": f"{v.quantile(0.05):.1f}-{v.quantile(0.95):.1f}",
                "Change vs present [%]": round(100 * (med[r] / present_median[r] - 1), 1),
            })
    return pd.DataFrame(rows).set_index(["Group", "T [years]"])
