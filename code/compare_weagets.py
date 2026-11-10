"""Compare WeaGETS outputs for all Markov orders and precipitation distributions with the observations.

Reads data/<STATION>_O<order>_D<distribution>_OUT.mat (made by run_weagets_all.m) and writes
- data/<STATION>_weagets_comparison.csv: one row per combination
- images/weagets_comparison/<STATION>_weagets_comparison.md: the same table, for the report
- images/weagets_comparison/<STATION>_weagets_ranking.png: error of each statistic, coloured by rank

Usage (from the climate-impacts folder):
    python code/compare_weagets.py GSTEIG
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data_processing import process_mat_file  # noqa: E402
from paths import DATA_DIR, IMAGES_DIR, weagets_input  # noqa: E402

WET = 0.1  # mm, wet-day threshold (same as WeaGETS and climate_stats.py)
DISTRIBUTIONS = {1: "Exponential", 2: "Gamma", 3: "Skewed normal", 4: "Mixed exponential"}
KS_QUANTILE = 0.95  # same as the tutorial notebook


def spell_lengths(wet: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Lengths of the dry and wet spells in a boolean series."""
    change = np.flatnonzero(np.diff(wet.astype(int))) + 1
    runs = np.split(wet, change)
    lengths = np.array([len(r) for r in runs])
    is_wet = np.array([r[0] for r in runs])
    return lengths[~is_wet], lengths[is_wet]


def series_stats(df: pd.DataFrame) -> dict:
    """Statistics of one 30-year series (observed, or one realization)."""
    p = df["Precipitation"].to_numpy()
    wet = p > WET
    dry_spells, wet_spells = spell_lengths(wet)
    n_years = df["Year"].nunique()
    month = df["Month"].cat.codes.to_numpy() if hasattr(df["Month"], "cat") else df["Month"].to_numpy()
    return {
        "annual_P": p.sum() / n_years,
        "wet_days_month": np.bincount(month, weights=wet, minlength=12) / n_years,
        "intensity": p[wet].mean(),
        "dry_spell": dry_spells.mean(),
        "wet_spell": wet_spells.mean(),
        "max_dry_spell": dry_spells.max(),
        "annual_max_P": df.groupby("Year")["Precipitation"].max().mean(),
        "T_mean_month": df.groupby(month)["T_avg"].mean().to_numpy(),
        "T_std_month": df.groupby(month)["T_avg"].std().to_numpy(),
    }


def compare(obs: pd.DataFrame, sim: pd.DataFrame) -> dict:
    """Compare all realizations of one WeaGETS output with the observations."""
    o = series_stats(obs)
    threshold = obs["Precipitation"].quantile(KS_QUANTILE)
    obs_extreme = obs.loc[obs["Precipitation"] >= threshold, "Precipitation"]

    per_sim, p_values = [], []
    for _, s in sim.groupby("Simulation"):
        per_sim.append(series_stats(s))
        sim_extreme = s.loc[s["Precipitation"] >= threshold, "Precipitation"]
        p_values.append(ks_2samp(obs_extreme, sim_extreme).pvalue)
    p_values = np.array(p_values)

    def mean_of(key):
        return np.mean([x[key] for x in per_sim], axis=0)

    def bias_pct(key):
        return 100 * (mean_of(key) / o[key] - 1)

    return {
        "Annual P bias [%]": bias_pct("annual_P"),
        "Wet days/month MAE [d]": np.abs(mean_of("wet_days_month") - o["wet_days_month"]).mean(),
        "Wet-day intensity bias [%]": bias_pct("intensity"),
        "Dry spell bias [%]": bias_pct("dry_spell"),
        "Wet spell bias [%]": bias_pct("wet_spell"),
        "Longest dry spell bias [%]": bias_pct("max_dry_spell"),
        "Annual max P bias [%]": bias_pct("annual_max_P"),
        "KS extremes p<0.05 [n]": int((p_values < 0.05).sum()),
        "KS extremes median p": float(np.median(p_values)),
        "T mean MAE [degC]": np.abs(mean_of("T_mean_month") - o["T_mean_month"]).mean(),
        "T std MAE [degC]": np.abs(mean_of("T_std_month") - o["T_std_month"]).mean(),
        "n realizations": len(per_sim),
    }


def rank_table(table: pd.DataFrame) -> pd.DataFrame:
    """Rank each statistic (1 = closest to the observations)."""
    error = table.drop(columns=["n realizations"]).abs()
    error["KS extremes median p"] = -table["KS extremes median p"]  # higher p is better
    return error.rank(method="min").astype(int)


def markdown_table(table: pd.DataFrame) -> str:
    """Markdown table without the optional tabulate package."""
    header = ["Combination", *table.columns]
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    for name, row in table.iterrows():
        lines.append("| " + " | ".join([str(name), *(f"{v:g}" for v in row)]) + " |")
    return "\n".join(lines)


def plot_ranking(table: pd.DataFrame, ranks: pd.DataFrame, station: str, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(13, 0.45 * len(table) + 2.2))
    ax.imshow(ranks.to_numpy(), cmap="Blues_r", vmin=1, vmax=len(table) + 3, aspect="auto")
    for i in range(table.shape[0]):
        for j, col in enumerate(ranks.columns):
            value = table.iloc[i][col]
            text = f"{value:.0f}" if col == "KS extremes p<0.05 [n]" else f"{value:.2f}"
            ax.text(j, i, text, ha="center", va="center", fontsize=9,
                    color="white" if ranks.iloc[i, j] <= 3 else "#222222")
    short = {
        "Annual P bias [%]": "Annual P\nbias [%]",
        "Wet days/month MAE [d]": "Wet days\nper month\nMAE [d]",
        "Wet-day intensity bias [%]": "Wet-day\nintensity\nbias [%]",
        "Dry spell bias [%]": "Dry spell\nbias [%]",
        "Wet spell bias [%]": "Wet spell\nbias [%]",
        "Longest dry spell bias [%]": "Longest\ndry spell\nbias [%]",
        "Annual max P bias [%]": "Annual\nmax P\nbias [%]",
        "KS extremes p<0.05 [n]": "KS extremes\np<0.05\n[of 50]",
        "KS extremes median p": "KS extremes\nmedian p",
        "T mean MAE [degC]": "T mean\nMAE [°C]",
        "T std MAE [degC]": "T std\nMAE [°C]",
    }
    ax.set_xticks(range(ranks.shape[1]), [short.get(c, c) for c in ranks.columns], fontsize=8)
    ax.set_yticks(range(table.shape[0]), table.index, fontsize=9)
    ax.xaxis.tick_top()
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_title(f"{station}: WeaGETS combinations vs observations "
                 "(value in cell; darker = closer to observed, rank per column)", fontsize=10, pad=40)
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    station = sys.argv[1] if len(sys.argv) > 1 else "GSTEIG"
    obs = process_mat_file(weagets_input(station))

    rows = {}
    for order in (1, 2, 3):
        for distr, name in DISTRIBUTIONS.items():
            path = DATA_DIR / f"{station}_O{order}_D{distr}_OUT.mat"
            if not path.exists():
                print(f"missing: {path.name}")
                continue
            print(f"comparing {path.name}", flush=True)
            rows[f"Order {order} + {name}"] = compare(obs, process_mat_file(path))
    if not rows:
        raise SystemExit("no WeaGETS outputs found: run run_weagets_all.m first")

    table = pd.DataFrame(rows).T
    ranks = rank_table(table)
    table["Mean rank"] = ranks.mean(axis=1).round(1)
    table = table.sort_values("Mean rank")
    ranks = ranks.loc[table.index]

    out_dir = IMAGES_DIR / "weagets_comparison"
    out_dir.mkdir(exist_ok=True)
    table.to_csv(DATA_DIR / f"{station}_weagets_comparison.csv")
    (out_dir / f"{station}_weagets_comparison.md").write_text(
        f"# {station}: WeaGETS combinations vs observations\n\n"
        "Bias = mean over realizations relative to observed; MAE over the 12 months. "
        f"KS: truncated 2-sample test on precipitation above the observed {KS_QUANTILE:.0%} quantile, "
        "one test per 30-year realization. Sorted by mean rank (1 = closest to observed).\n\n"
        + markdown_table(table.round(3)) + "\n",
        encoding="utf-8",
    )
    plot_ranking(table.drop(columns=["Mean rank", "n realizations"]), ranks, station,
                 out_dir / f"{station}_weagets_ranking.png")
    pd.set_option("display.width", 250)
    print(table.round(2).to_string())


if __name__ == "__main__":
    main()
