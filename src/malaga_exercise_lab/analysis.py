"""Pre-specified formula error and zone discordance analysis (ANALYSIS_PLAN.md, sections 3 to 6).

All outputs are aggregates. Per test frames stay in memory and are never written to disk.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.proportion import proportion_confint

SEED = 20261111
N_BOOT = 2000
THRESH_BPM = 10.0
ZONE_BOUNDS = (0.70, 0.85)
ZONE_NAMES = ["below 70%", "70 to 85%", "above 85%"]

FORMULAS = {
    "220 minus age": lambda age: 220.0 - age,
    "Tanaka 2001": lambda age: 208.0 - 0.7 * age,
    "Gellish 2007": lambda age: 206.9 - 0.67 * age,
}
FORMULA_TEXT = {"220 minus age": "220 - age", "Tanaka 2001": "208 - 0.7 x age", "Gellish 2007": "206.9 - 0.67 x age"}
PEAKS = {"effort": "hrpeak_effort", "any_time": "hrpeak_any", "effort_roll5": "hrpeak_effort_roll5"}


def build_frame(subj: pd.DataFrame, pt: pd.DataFrame) -> pd.DataFrame:
    df = subj.merge(pt, on="ID_test", how="inner", validate="one_to_one")
    if len(df) != len(subj):
        raise ValueError("per test frame does not match subject-info rows")
    df["vo2peak_mlkgmin"] = df["vo2peak_mlmin"] / df["Weight"]
    return df


def samples(df: pd.DataFrame) -> dict:
    first = df[df["first_test"]]
    first_adult = (df[df["adult"]].sort_values(["ID", "get_index"]).groupby("ID", sort=True).head(1))
    prim = first[first["adult"]]
    return {
        "primary": prim,
        "all_adult_tests": df[df["adult"]],
        "first_adult_test": first_adult,
        "primary_regular_protocol": prim[~prim["irregular"]],
        "under18_first_test": first[~first["adult"]],
    }


def _mean_ci(y: np.ndarray, groups: np.ndarray | None = None) -> tuple[float, float, float, float]:
    X = np.ones((len(y), 1))
    model = sm.OLS(y, X)
    if groups is None:
        fit = model.fit(cov_type="HC3")
    else:
        fit = model.fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(groups)[0]})
    lo, hi = fit.conf_int()[0]
    return float(fit.params[0]), float(fit.bse[0]), float(lo), float(hi)


def _boot(stat, err: np.ndarray, groups: np.ndarray | None, rng: np.random.Generator) -> tuple[float, float]:
    vals = np.empty(N_BOOT)
    if groups is None:
        n = len(err)
        for b in range(N_BOOT):
            vals[b] = stat(err[rng.integers(0, n, n)])
    else:
        codes, uniq = pd.factorize(groups)
        idx_by = [np.where(codes == k)[0] for k in range(len(uniq))]
        g = len(uniq)
        for b in range(N_BOOT):
            pick = rng.integers(0, g, g)
            vals[b] = stat(err[np.concatenate([idx_by[k] for k in pick])])
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return float(lo), float(hi)


def error_metrics(d: pd.DataFrame, peak_col: str, label: str, cluster: bool = False) -> pd.DataFrame:
    rows = []
    d = d[d[peak_col].notna()]
    groups = d["ID"].to_numpy() if cluster else None
    for k, (name, f) in enumerate(FORMULAS.items()):
        rng = np.random.default_rng(SEED + k)
        err = (f(d["Age"].to_numpy(float)) - d[peak_col].to_numpy(float))
        bias, bias_se, bl, bh = _mean_ci(err, groups)
        mae, mae_se, ml, mh = _mean_ci(np.abs(err), groups)
        rmse = float(np.sqrt(np.mean(err ** 2)))
        rl, rh = _boot(lambda e: np.sqrt(np.mean(e ** 2)), err, groups, rng)
        over = np.abs(err) > THRESH_BPM
        k_over = int(over.sum())
        if cluster:
            pl, ph = _boot(lambda e: np.mean(np.abs(e) > THRESH_BPM), err, groups, rng)
            pmethod = "person cluster bootstrap"
        else:
            pl, ph = proportion_confint(k_over, len(err), alpha=0.05, method="wilson")
            pmethod = "Wilson"
        rows.append({
            "sample": label, "peak": peak_col, "formula": name, "formula_text": FORMULA_TEXT[name],
            "n_tests": int(len(d)), "n_people": int(d["ID"].nunique()),
            "bias_bpm": bias, "bias_se": bias_se, "bias_ci95_low": bl, "bias_ci95_high": bh,
            "mae_bpm": mae, "mae_ci95_low": ml, "mae_ci95_high": mh,
            "rmse_bpm": rmse, "rmse_ci95_low": rl, "rmse_ci95_high": rh,
            "n_abs_error_over_10": k_over, "pct_abs_error_over_10": 100 * k_over / len(err),
            "pct_ci95_low": 100 * pl, "pct_ci95_high": 100 * ph,
            "pct_formula_above_observed": 100 * float(np.mean(err > 0)),
            "se_method": "cluster robust by person" if cluster else "HC3",
            "pct_ci_method": pmethod, "rmse_ci_method": "percentile bootstrap 2000" + (" by person" if cluster else ""),
        })
    return pd.DataFrame(rows)


def primary_and_sensitivity(sm_: dict) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    prim = error_metrics(sm_["primary"], PEAKS["effort"], "primary: adults, first test")
    sens = pd.concat([
        error_metrics(sm_["primary"], PEAKS["any_time"], "sensitivity: primary sample, any time max HR"),
        error_metrics(sm_["primary"], PEAKS["effort_roll5"], "sensitivity: primary sample, 5 sample rolling median peak"),
        error_metrics(sm_["primary_regular_protocol"], PEAKS["effort"], "sensitivity: primary without irregular protocol flags"),
        error_metrics(sm_["first_adult_test"], PEAKS["effort"], "sensitivity: first adult test per person"),
        error_metrics(sm_["all_adult_tests"], PEAKS["effort"], "sensitivity: all adult tests, clustered by person", cluster=True),
    ], ignore_index=True)
    minors = error_metrics(sm_["under18_first_test"], PEAKS["effort"], "descriptive only: under 18, first test")
    return prim, sens, minors


def by_subgroup(d: pd.DataFrame) -> pd.DataFrame:
    d = d.copy()
    d["age_band"] = pd.cut(d["Age"], [18, 30, 40, 200], right=False, labels=["18 to 29", "30 to 39", "40 and over"])
    d["sex"] = np.where(d["Sex"] == 1, "female", "male")
    out = []
    for var in ("age_band", "sex"):
        for lvl, g in d.groupby(var, observed=True, sort=True):
            m = error_metrics(g, PEAKS["effort"], f"descriptive: primary, {var.replace('_', ' ')} {lvl}")
            m.insert(1, "subgroup", f"{var}={lvl}")
            m["observed_hrpeak_mean"] = float(g["hrpeak_effort"].mean())
            m["age_mean"] = float(g["Age"].mean())
            out.append(m)
    return pd.concat(out, ignore_index=True)


def age_line(d: pd.DataFrame) -> dict:
    """Descriptive OLS of observed HRpeak on age (HC3). Not offered as a new formula."""
    X = sm.add_constant(d["Age"].to_numpy(float))
    fit = sm.OLS(d["hrpeak_effort"].to_numpy(float), X).fit(cov_type="HC3")
    ci = fit.conf_int()
    resid_sd = float(np.sqrt(fit.mse_resid))
    return {"intercept": float(fit.params[0]), "intercept_ci95": [float(ci[0][0]), float(ci[0][1])],
            "slope_per_year": float(fit.params[1]), "slope_ci95": [float(ci[1][0]), float(ci[1][1])],
            "residual_sd_bpm": resid_sd, "r2": float(fit.rsquared), "n": int(len(d)),
            "note": "descriptive line of this open table only; not proposed as a formula"}


def _zone(hr: np.ndarray, hrmax: np.ndarray) -> np.ndarray:
    r = hr / hrmax
    return np.where(r < ZONE_BOUNDS[0], 0, np.where(r <= ZONE_BOUNDS[1], 1, 2))


def zone_discordance(d: pd.DataFrame, effort_samples: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Boundary shifts and share of effort time whose zone changes, primary sample only."""
    es = effort_samples[effort_samples["ID_test"].isin(d["ID_test"])].dropna(subset=["HR"])
    es = es.merge(d[["ID_test", "ID", "Age", "hrpeak_effort"]], on="ID_test", how="left", validate="many_to_one")
    shifts, disc = [], []
    for name, f in FORMULAS.items():
        fmax_t = f(d["Age"].to_numpy(float))
        obs_t = d["hrpeak_effort"].to_numpy(float)
        for b in ZONE_BOUNDS:
            sh = b * (fmax_t - obs_t)
            mean, se, lo, hi = _mean_ci(sh)
            shifts.append({"formula": name, "boundary_pct_hrmax": int(round(b * 100)), "n_tests": int(len(d)),
                           "mean_shift_bpm": mean, "ci95_low": lo, "ci95_high": hi,
                           "median_shift_bpm": float(np.median(sh)),
                           "p10_shift_bpm": float(np.percentile(sh, 10)), "p90_shift_bpm": float(np.percentile(sh, 90)),
                           "pct_tests_shift_over_5bpm": 100 * float(np.mean(np.abs(sh) > 5)),
                           "mean_obs_boundary_bpm": float(np.mean(b * obs_t)),
                           "mean_formula_boundary_bpm": float(np.mean(b * fmax_t))})
        z_obs = _zone(es["HR"].to_numpy(float), es["hrpeak_effort"].to_numpy(float))
        z_for = _zone(es["HR"].to_numpy(float), f(es["Age"].to_numpy(float)))
        w = es["w"].to_numpy(float)
        tmp = pd.DataFrame({"ID_test": es["ID_test"].to_numpy(), "w": w,
                            "diff": (z_obs != z_for) * w, "lower": (z_for < z_obs) * w, "higher": (z_for > z_obs) * w,
                            **{f"obs_{k}": (z_obs == k) * w for k in range(3)},
                            **{f"for_{k}": (z_for == k) * w for k in range(3)}})
        per = tmp.groupby("ID_test", sort=True).sum()
        share = per["diff"] / per["w"]
        lower = per["lower"] / per["w"]
        higher = per["higher"] / per["w"]
        m, se, lo, hi = _mean_ci(share.to_numpy())
        ml, _, lol, hil = _mean_ci(lower.to_numpy())
        mh, _, loh, hih = _mean_ci(higher.to_numpy())
        tot = per.sum()
        disc.append({"formula": name, "n_tests": int(len(per)), "effort_hours": float(tot["w"] / 3600),
                     "mean_pct_time_discordant": 100 * m, "ci95_low": 100 * lo, "ci95_high": 100 * hi,
                     "median_pct_time_discordant": 100 * float(share.median()),
                     "pct_tests_over_10pct_time_discordant": 100 * float(np.mean(share > 0.10)),
                     "mean_pct_time_formula_lower_zone": 100 * ml, "lower_ci95": f"{100*lol:.6g} to {100*hil:.6g}",
                     "mean_pct_time_formula_higher_zone": 100 * mh, "higher_ci95": f"{100*loh:.6g} to {100*hih:.6g}",
                     "pooled_pct_time_discordant": 100 * float(tot["diff"] / tot["w"]),
                     **{f"pooled_pct_time_observed_{ZONE_NAMES[k]}": 100 * float(tot[f'obs_{k}'] / tot['w']) for k in range(3)},
                     **{f"pooled_pct_time_formula_{ZONE_NAMES[k]}": 100 * float(tot[f'for_{k}'] / tot['w']) for k in range(3)}})
    return pd.DataFrame(shifts), pd.DataFrame(disc)


def descriptors(d: pd.DataFrame) -> pd.DataFrame:
    rows = []
    cols = {"Age": "age, years", "Weight": "weight, kg", "Height": "height, cm", "hrpeak_effort": "observed HRpeak effort, bpm",
            "hrpeak_any": "max HR any time, bpm", "hrpeak_effort_roll5": "HRpeak rolling median 5, bpm",
            "vmax": "peak treadmill speed, km/h", "effort_s": "effort phase, s",
            "vo2peak_mlmin": "VO2peak 30 s, mL/min", "vo2peak_mlkgmin": "VO2peak 30 s, mL/kg/min"}
    for c, lab in cols.items():
        x = d[c].dropna()
        rows.append({"variable": lab, "n": int(len(x)), "mean": float(x.mean()), "sd": float(x.std()),
                     "median": float(x.median()), "q1": float(x.quantile(0.25)), "q3": float(x.quantile(0.75)),
                     "min": float(x.min()), "max": float(x.max())})
    return pd.DataFrame(rows)
