"""Aggregate only figures. No identifiers, no per test points, cells under MIN_CELL tests suppressed."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from PIL import Image  # noqa: E402

from . import analysis as A  # noqa: E402

MIN_CELL = 10
COLORS = {"220 minus age": "#c0504d", "Tanaka 2001": "#1f77b4", "Gellish 2007": "#2ca02c"}
FOOTER = ("Re-analysis of Mongin, García Romero and Alvero Cruz 2021, PhysioNet, doi 10.13026/7ezk-j442. "
          "Aggregates only, no individual rows.")
TITLES = {
    "fig01": "Deposit audit: page versus files, flagged and not corrected",
    "fig02": "Effort phase rule, fixed before results (schematic, not participant data)",
    "fig03": "Age-predicted HRmax minus observed HRpeak, adults, first test",
    "fig04": "Observed HRpeak by age band and three formulas",
    "fig05": "Zone discordance: effort time labelled in a different zone",
    "fig06": "Sensitivity of formula bias and MAE to sample and peak definitions",
}
plt.rcParams.update({"axes.unicode_minus": False, "font.size": 10, "axes.spines.top": False, "axes.spines.right": False})


def _save(fig, path: Path, caption: str) -> list[Path]:
    fig.text(0.01, 0.01, caption + "\n" + FOOTER, fontsize=7.5, color="#444", va="bottom", wrap=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    webp = path.with_suffix(".webp")
    Image.open(path).save(webp, "WEBP", quality=90, method=6)
    return [path, webp]


def age_bands(age: pd.Series) -> pd.Series:
    edges = [18, 22, 26, 30, 35, 40, 45, 200]
    labels = ["18 to 21", "22 to 25", "26 to 29", "30 to 34", "35 to 39", "40 to 44", "45 and over"]
    return pd.cut(age, edges, right=False, labels=labels)


def band_table(prim: pd.DataFrame) -> pd.DataFrame:
    d = prim.assign(band=age_bands(prim["Age"]))
    rows = []
    for band, g in d.groupby("band", observed=True, sort=True):
        n = len(g)
        rec = {"age_band": str(band), "n_tests": n, "suppressed": n < MIN_CELL}
        if n >= MIN_CELL:
            m, se, lo, hi = A._mean_ci(g["hrpeak_effort"].to_numpy(float))
            rec.update({"mean_age": float(g["Age"].mean()), "observed_hrpeak_mean": m, "ci95_low": lo, "ci95_high": hi})
            for f, fn in A.FORMULAS.items():
                e = fn(g["Age"].to_numpy(float)) - g["hrpeak_effort"].to_numpy(float)
                b, _, bl, bh = A._mean_ci(e)
                rec.update({f"bias_{f}": b, f"bias_{f}_ci95_low": bl, f"bias_{f}_ci95_high": bh,
                            f"mae_{f}": float(np.mean(np.abs(e)))})
        rows.append(rec)
    return pd.DataFrame(rows)


def fig_audit(cmp_df: pd.DataFrame, facts: dict, path: Path) -> list[Path]:
    fig = plt.figure(figsize=(12, 6.2))
    ax1 = fig.add_axes([0.03, 0.2, 0.5, 0.68]); ax1.axis("off")
    ax1.set_title("Deposit page versus deposited files", loc="left", fontsize=11)
    y = 0.98
    for r in cmp_df.itertuples():
        col = {"yes": "#2c7a2c", "no": "#c0504d"}.get(r.match, "#b8860b")
        ax1.text(0.0, y, r.item, fontsize=8.5, va="top", transform=ax1.transAxes)
        ax1.text(0.42, y, f"page {r.deposit_page}", fontsize=8, va="top", transform=ax1.transAxes, color="#333")
        ax1.text(0.75, y, f"files {r.files}", fontsize=8, va="top", transform=ax1.transAxes, color=col)
        y -= 0.075
    ax2 = fig.add_axes([0.6, 0.58, 0.37, 0.3])
    vals = [facts["gas_tests_all_missing"]["VO2"], facts["gas_tests_all_missing"]["VCO2"], facts["gas_tests_all_missing"]["VE"], 30]
    ax2.barh(["VO2", "VCO2", "VE", "page says"], vals, color=["#1f77b4", "#1f77b4", "#1f77b4", "#999"])
    for i, v in enumerate(vals):
        ax2.text(v + 0.5, i, str(v), va="center", fontsize=8)
    ax2.set_xlabel("tests with the variable fully missing")
    ax2.set_title("A1: gas missing in 11 tests, not 30; VE never missing", loc="left", fontsize=9.5)
    ax3 = fig.add_axes([0.6, 0.2, 0.37, 0.25])
    cnt = facts["tests_per_person_counts"]
    ax3.bar(list(cnt.keys()), list(cnt.values()), color="#555")
    for k, v in cnt.items():
        ax3.text(k, v, str(v), ha="center", va="bottom", fontsize=8)
    ax3.set_yscale("log"); ax3.set_xlabel("tests per person"); ax3.set_ylabel("people (log)")
    ax3.set_title(f"A2: {facts['people_more_than_one_test']} people repeat; GET index not consecutive", loc="left", fontsize=9.5)
    fig.suptitle(TITLES["fig01"], x=0.03, ha="left", fontsize=13)
    cap = (f"992 tests, 857 people, {facts['tests_under_18']} tests under 18 (A3), humidity and temperature missing in "
           f"{facts['humidity_missing']} rows (A4), {facts['hr_below_30_rows']} HR values below 30 bpm set to missing (A5).")
    return _save(fig, path, cap)


def fig_schematic(path: Path) -> list[Path]:
    t = np.arange(0, 1200, 2.0)
    speed = np.where(t < 180, 5.0, np.where(t < 900, 5.0 + (t - 180) / 60.0, 5.0))
    fig, ax = plt.subplots(figsize=(11, 4.6))
    fig.subplots_adjust(bottom=0.28, top=0.85)
    ax.plot(t, speed, color="#333")
    ax.axvspan(180, 898, color="#1f77b4", alpha=0.12)
    ax.text(90, 17, "warmup\nwalk at S0\n(about 5 km/h)", ha="center", fontsize=9)
    ax.text(540, 17, "effort phase: after the last sample at S0 + 0.05 km/h,\nup to the last sample before speed falls below Vmax - 1 km/h", ha="center", fontsize=9)
    ax.text(1050, 17, "recovery\nback to 5 km/h", ha="center", fontsize=9)
    ax.set_ylim(0, 19.5); ax.set_xlabel("time, s (illustrative)"); ax.set_ylabel("treadmill speed, km/h")
    fig.suptitle(TITLES["fig02"], x=0.03, ha="left", fontsize=13)
    cap = ("Primary HRpeak = highest HR inside the effort phase. Sensitivities: highest HR at any time; 5 sample rolling median. "
           "HR below 30 bpm is set to missing.\nIrregular protocols are flagged and removed in one sensitivity.")
    return _save(fig, path, cap)


def fig_formula_error(prim_tab: pd.DataFrame, band: pd.DataFrame, path: Path) -> list[Path]:
    fig, axes = plt.subplots(1, 4, figsize=(13, 5.0))
    fig.subplots_adjust(bottom=0.3, top=0.82, wspace=0.45)
    metrics = [("bias_bpm", "bias_ci95_low", "bias_ci95_high", "signed bias, bpm"),
               ("mae_bpm", "mae_ci95_low", "mae_ci95_high", "MAE, bpm"),
               ("rmse_bpm", "rmse_ci95_low", "rmse_ci95_high", "RMSE, bpm"),
               ("pct_abs_error_over_10", "pct_ci95_low", "pct_ci95_high", "% tests with |error| > 10 bpm")]
    names = list(prim_tab["formula"])
    for ax, (m, lo, hi, lab) in zip(axes, metrics):
        v = prim_tab[m].to_numpy(); l = prim_tab[lo].to_numpy(); h = prim_tab[hi].to_numpy()
        ax.bar(range(3), v, color=[COLORS[n] for n in names], alpha=0.85)
        ax.errorbar(range(3), v, yerr=[v - l, h - v], fmt="none", ecolor="black", capsize=4)
        for i, x in enumerate(v):
            ax.text(i, h[i] + (0.4 if m != "pct_abs_error_over_10" else 1.0), f"{x:.1f}", ha="center", fontsize=9)
        ax.set_xticks(range(3)); ax.set_xticklabels([n.replace(" ", "\n", 1) for n in names], fontsize=8.5)
        ax.set_title(lab, fontsize=10, pad=14)
        ax.set_ylim(min(0, float(l.min()) * 1.3), float(h.max()) * 1.18)
        if m == "bias_bpm":
            ax.axhline(0, color="#888", lw=0.8)
    fig.suptitle(TITLES["fig03"] + f" (n = {int(prim_tab['n_tests'].iloc[0])}, 95% CI)", x=0.03, ha="left", fontsize=13)
    p = prim_tab.set_index("formula")
    cap = ("Error = formula minus observed effort phase HRpeak. "
           + "; ".join(f"{f}: bias {p.loc[f,'bias_bpm']:.1f} ({p.loc[f,'bias_ci95_low']:.1f} to {p.loc[f,'bias_ci95_high']:.1f}), "
                       f"MAE {p.loc[f,'mae_bpm']:.1f}, >10 bpm {p.loc[f,'pct_abs_error_over_10']:.1f}%" for f in names)
           + ". Bias and MAE CI: HC3; RMSE: bootstrap; share: Wilson.")
    return _save(fig, path, cap)


def fig_by_age(band: pd.DataFrame, path: Path) -> list[Path]:
    b = band[~band["suppressed"]]
    fig, ax = plt.subplots(figsize=(10, 5.4))
    fig.subplots_adjust(bottom=0.26, top=0.86)
    x = np.arange(len(b))
    ax.errorbar(x, b["observed_hrpeak_mean"], yerr=[b["observed_hrpeak_mean"] - b["ci95_low"], b["ci95_high"] - b["observed_hrpeak_mean"]],
                fmt="o", color="black", capsize=4, label="observed HRpeak, band mean (95% CI)")
    for f, fn in A.FORMULAS.items():
        ax.plot(x, fn(b["mean_age"].to_numpy(float)), "-", marker="s", ms=4, color=COLORS[f], label=f"{f}: {A.FORMULA_TEXT[f]}, at band mean age" if f != "220 minus age" else "220 minus age, at band mean age")
    ax.set_xticks(x); ax.set_xticklabels([f"{a}\nn = {n}" for a, n in zip(b["age_band"], b["n_tests"])], fontsize=8.5)
    ax.set_ylabel("heart rate, bpm"); ax.set_xlabel("age band at the test, years")
    ax.legend(fontsize=8.5, frameon=False, loc="lower left")
    fig.suptitle(TITLES["fig04"], x=0.03, ha="left", fontsize=13)
    cap = ("Primary sample, adults, first test per person. Bands with fewer than 10 tests would be suppressed. "
           "Band means only; no individual points are drawn.")
    return _save(fig, path, cap)


def fig_zones(disc: pd.DataFrame, path: Path) -> list[Path]:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 5.2), gridspec_kw={"width_ratios": [1.25, 1]})
    fig.subplots_adjust(bottom=0.3, top=0.82, wspace=0.35)
    labels = ["observed HRpeak"] + list(disc["formula"])
    zc = ["#9ecae1", "#fdae6b", "#e6550d"]
    rows = [[disc.iloc[0][f"pooled_pct_time_observed_{z}"] for z in A.ZONE_NAMES]] + \
           [[r[f"pooled_pct_time_formula_{z}"] for z in A.ZONE_NAMES] for _, r in disc.iterrows()]
    left = np.zeros(len(rows))
    for k, z in enumerate(A.ZONE_NAMES):
        vals = np.array([r[k] for r in rows])
        ax1.barh(labels, vals, left=left, color=zc[k], label=f"{z} of HRmax")
        for i, v in enumerate(vals):
            ax1.text(left[i] + v / 2, i, f"{v:.1f}", ha="center", va="center", fontsize=8)
        left += vals
    ax1.invert_yaxis(); ax1.set_xlabel("% of pooled effort phase time"); ax1.legend(fontsize=8, frameon=False, ncol=3, loc="lower left", bbox_to_anchor=(0, -0.32))
    ax1.set_title("Time in zones by HRmax source", loc="left", fontsize=10)
    y = np.arange(len(disc))
    lo = disc["mean_pct_time_formula_lower_zone"].to_numpy(); hi = disc["mean_pct_time_formula_higher_zone"].to_numpy()
    ax2.barh(y, lo, color="#6a51a3", label="formula labels a lower zone")
    ax2.barh(y, hi, left=lo, color="#bcbddc", label="formula labels a higher zone")
    tot = disc["mean_pct_time_discordant"].to_numpy()
    ax2.errorbar(tot, y, xerr=[tot - disc["ci95_low"], disc["ci95_high"] - tot], fmt="none", ecolor="black", capsize=4)
    for i, v in enumerate(tot):
        ax2.text(disc["ci95_high"].iloc[i] + 0.4, i, f"{v:.1f}%", va="center", fontsize=9)
    ax2.set_yticks(y); ax2.set_yticklabels(disc["formula"]); ax2.invert_yaxis()
    ax2.set_xlabel("mean % of effort time per test (95% CI)"); ax2.legend(fontsize=8, frameon=False, ncol=2, loc="lower left", bbox_to_anchor=(0, -0.32))
    ax2.set_xlim(0, float(disc["ci95_high"].max()) * 1.25)
    ax2.set_title("Effort time with a different zone label", loc="left", fontsize=10)
    fig.suptitle(TITLES["fig05"] + f" (zones at 70% and 85% of HRmax, n = {int(disc['n_tests'].iloc[0])})", x=0.03, ha="left", fontsize=12.5)
    cap = ("; ".join(f"{r.formula}: {r.mean_pct_time_discordant:.1f}% ({r.ci95_low:.1f} to {r.ci95_high:.1f})" for r in disc.itertuples())
           + ". Description of discordance only; not training advice and not evidence of equivalence.")
    return _save(fig, path, cap)


def fig_sensitivity(prim_tab: pd.DataFrame, sens: pd.DataFrame, minors: pd.DataFrame, path: Path) -> list[Path]:
    allt = pd.concat([prim_tab, sens, minors], ignore_index=True)
    order = list(dict.fromkeys(allt["sample"]))
    fig, axes = plt.subplots(1, 2, figsize=(13, 6.2), sharey=True)
    fig.subplots_adjust(left=0.33, bottom=0.2, top=0.86, wspace=0.08)
    for ax, (m, lo, hi, lab) in zip(axes, [("bias_bpm", "bias_ci95_low", "bias_ci95_high", "signed bias, bpm"),
                                           ("mae_bpm", "mae_ci95_low", "mae_ci95_high", "MAE, bpm")]):
        for j, f in enumerate(A.FORMULAS):
            sub = allt[allt["formula"] == f].set_index("sample").loc[order]
            yy = np.arange(len(order)) + (j - 1) * 0.22
            ax.errorbar(sub[m], yy, xerr=[sub[m] - sub[lo], sub[hi] - sub[m]], fmt="o", ms=4, color=COLORS[f], capsize=2, label=f)
        if m == "bias_bpm":
            ax.axvline(0, color="#888", lw=0.8)
        ax.set_xlabel(lab)
    axes[0].set_yticks(range(len(order)))
    axes[0].set_yticklabels([f"{s}\n(n = {int(allt[allt['sample']==s]['n_tests'].iloc[0])})" for s in order], fontsize=8)
    axes[0].invert_yaxis(); axes[1].legend(fontsize=8.5, frameon=False, loc="upper right")
    fig.suptitle(TITLES["fig06"], x=0.03, ha="left", fontsize=13)
    cap = "Top row is the primary result. The under 18 row is descriptive only and is not part of the primary family."
    return _save(fig, path, cap)
