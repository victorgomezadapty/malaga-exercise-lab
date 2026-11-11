"""Pre-specified effort phase rule and per test peak values (see ANALYSIS_PLAN.md, section 2)."""
from __future__ import annotations

import numpy as np
import pandas as pd

DROP_KMH = 1.0          # speed drop below Vmax that marks the start of recovery
WARMUP_TOL_KMH = 0.05   # tolerance above warmup speed S0
HR_MIN_VALID = 30.0     # heart rate below this is treated as an artefact
ROLL_N = 5              # centred rolling median window, samples
VO2_WINDOW_S = 30       # time window for VO2peak, seconds
WEIGHT_CAP_S = 10.0     # cap on sample time weight
MIN_EFFORT_S = 180
WARMUP_RANGE = (4.5, 5.5)
RECOVERY_RANGE = (3.5, 5.5)


def effort_bounds(time: np.ndarray, speed: np.ndarray) -> dict:
    """Return start and end positions (inclusive) of the effort phase, plus protocol flags."""
    n = len(speed)
    vmax = float(np.max(speed))
    i_vmax = int(np.argmax(speed >= vmax))
    after = np.where(speed[i_vmax:] < vmax - DROP_KMH)[0]
    i_end = i_vmax + int(after[0]) - 1 if len(after) else n - 1
    pos = speed[speed > 0]
    s0 = float(pos[0]) if len(pos) else float("nan")
    before = np.where(speed[:i_vmax + 1] <= s0 + WARMUP_TOL_KMH)[0]
    i_start = int(before[-1]) + 1 if len(before) else 0
    i_start = min(i_start, i_end)
    eff_speed = speed[i_start:i_end + 1]
    drop_inside = bool(np.any(np.maximum.accumulate(eff_speed) - eff_speed >= DROP_KMH))
    rec = speed[i_end + 1:]
    dur = float(time[i_end] - time[i_start])
    flags = {
        "flag_warmup_not_5kmh": not (WARMUP_RANGE[0] <= s0 <= WARMUP_RANGE[1]),
        "flag_effort_short": dur < MIN_EFFORT_S,
        "flag_drop_inside_effort": drop_inside,
        "flag_no_recovery": len(rec) == 0,
        "flag_recovery_not_5kmh": bool(len(rec) and not (RECOVERY_RANGE[0] <= float(np.median(rec)) <= RECOVERY_RANGE[1])),
    }
    return {"i_start": i_start, "i_end": i_end, "vmax": vmax, "s0": s0, "effort_s": dur,
            "warmup_s": float(time[i_start] - time[0]), "recovery_s": float(time[-1] - time[i_end]),
            "n_recovery": int(len(rec)), **flags}


def time_weights(time: np.ndarray) -> np.ndarray:
    dt = np.diff(time).astype(float)
    last = float(np.median(dt)) if len(dt) else 1.0
    return np.minimum(np.append(dt, last), WEIGHT_CAP_S)


def vo2_peak(time: np.ndarray, vo2: np.ndarray) -> float:
    ok = ~np.isnan(vo2)
    if ok.sum() == 0:
        return float("nan")
    t, v = time[ok].astype(float), vo2[ok]
    s = pd.Series(v, index=pd.to_datetime(t, unit="s"))
    return float(s.rolling(f"{VO2_WINDOW_S}s").mean().max())


def per_test(meas: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """One row per test with phase bounds, flags and peak values. Rows stay in memory only."""
    m = meas.copy()
    art = m["HR"] < HR_MIN_VALID
    artefacts = {"hr_values_below_30": int(art.sum()), "hr_values_missing_in_file": int(meas["HR"].isna().sum()),
                 "tests_with_hr_below_30": int(m.loc[art, "ID_test"].nunique())}
    m.loc[art, "HR"] = np.nan
    rows, effort_samples = [], []
    for tid, d in m.groupby("ID_test", sort=True):
        d = d.sort_values("time", kind="mergesort")
        t, sp, hr, vo2 = d["time"].to_numpy(), d["Speed"].to_numpy(float), d["HR"].to_numpy(float), d["VO2"].to_numpy(float)
        b = effort_bounds(t, sp)
        sl = slice(b["i_start"], b["i_end"] + 1)
        hr_e = hr[sl]
        roll = pd.Series(hr).rolling(ROLL_N, center=True, min_periods=ROLL_N).median().to_numpy()[sl]
        w = time_weights(t)[sl]
        rows.append({"ID_test": tid, **b,
                     "hrpeak_effort": float(np.nanmax(hr_e)) if np.isfinite(hr_e).any() else np.nan,
                     "hrpeak_any": float(np.nanmax(hr)) if np.isfinite(hr).any() else np.nan,
                     "hrpeak_effort_roll5": float(np.nanmax(roll)) if np.isfinite(roll).any() else np.nan,
                     "hr_at_effort_end": float(hr[b["i_end"]]),
                     "gas_available": bool(np.isfinite(vo2).any()),
                     "vo2peak_mlmin": vo2_peak(t[sl], vo2[sl]),
                     "n_samples": int(len(d)), "n_effort": int(len(hr_e))})
        effort_samples.append(pd.DataFrame({"ID_test": tid, "HR": hr_e, "w": w}))
    out = pd.DataFrame(rows)
    out["irregular"] = out[[c for c in out.columns if c.startswith("flag_")]].any(axis=1)
    out["hrpeak_in_recovery"] = out["hrpeak_any"] > out["hrpeak_effort"]
    return out, {"artefacts": artefacts, "effort_samples": pd.concat(effort_samples, ignore_index=True)}
