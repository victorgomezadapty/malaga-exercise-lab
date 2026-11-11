"""Codebook and missingness audit of the two deposited files against the deposit page."""
from __future__ import annotations

import numpy as np
import pandas as pd

# Statements on the PhysioNet page for version 1.0.1 (read 11 Nov 2026).
PAGE = {
    "tests": 992, "people": 857, "measure_rows": 575087, "female_tests": 149, "female_pct": 15.0,
    "age_median_iqr": (27.10, 21.10, 36.32), "weight_median_iqr": (73.00, 66.00, 80.23),
    "height_median_iqr": (175.00, 170.00, 180.00), "humidity_median_iqr": (47.00, 42.00, 54.00),
    "temperature_median_iqr": (22.90, 20.80, 24.40), "measures_median_iqr": (580, 484, 673),
    "duration_median_iqr": (1093.00, 978.75, 1208.00), "gas_missing_tests": 30,
    "age_text": "10 to 63 years",
}
SUBJ_COLS = ["Age", "Weight", "Height", "Humidity", "Temperature", "Sex", "ID", "ID_test"]
MEAS_COLS = ["time", "Speed", "HR", "VO2", "VCO2", "RR", "VE", "ID_test", "ID"]


def _miqr(x: pd.Series) -> tuple:
    return (float(x.median()), float(x.quantile(0.25)), float(x.quantile(0.75)))


def audit(subj: pd.DataFrame, s: pd.DataFrame, meas: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    g = meas.groupby("ID_test")
    gas_all_missing = {c: int(g[c].apply(lambda x: x.isna().all()).sum()) for c in ("VO2", "VCO2", "VE")}
    gas_rows_missing = {c: int(meas[c].isna().sum()) for c in ("VO2", "VCO2", "VE")}
    gas_partial = {c: int(g[c].apply(lambda x: x.isna().any() and not x.isna().all()).sum()) for c in ("VO2", "VCO2", "VE")}
    hum_missing = s["Humidity"].isna()
    temp_missing = s["Temperature"].isna()
    gas_missing_tests = set(g["VO2"].apply(lambda x: x.isna().all()).pipe(lambda z: z[z].index))
    hum_tests = set(s.loc[hum_missing, "ID_test"])
    per_person = s.groupby("ID").size()
    idx_max_per_person = s.groupby("ID")["get_index"].max()
    multi = per_person[per_person > 1].index
    idx_consecutive = all(sorted(s.loc[s["ID"] == i, "get_index"]) == list(range(1, per_person[i] + 1)) for i in multi)
    age_order_ok = bool(s[s["ID"].isin(multi)].sort_values(["ID", "get_index"]).groupby("ID")["Age"]
                        .apply(lambda a: (a.diff().dropna() >= 0).all()).all())
    sex_consistent = bool((s.groupby("ID")["Sex"].nunique() == 1).all())
    dur = g["time"].max() - g["time"].min()
    n_meas = g.size()
    hr_lt30 = int((meas["HR"] < 30).sum())
    facts = {
        "tests": int(len(s)), "people": int(s["ID"].nunique()), "measure_rows": int(len(meas)),
        "tests_in_measure_file": int(meas["ID_test"].nunique()),
        "id_test_sets_equal": set(s["ID_test"]) == set(meas["ID_test"]),
        "id_prefix_matches_ID": bool((s["id_prefix"] == s["ID"]).all()),
        "measure_ID_matches_ID_test": bool((meas["ID_test"].str.split("_").str[0].astype(int) == meas["ID"]).all()),
        "female_tests": int((s["Sex"] == 1).sum()), "female_people": int(s.loc[s["Sex"] == 1, "ID"].nunique()),
        "sex_values": sorted(int(v) for v in s["Sex"].unique()), "sex_consistent_within_person": sex_consistent,
        "age_min": float(s["Age"].min()), "age_max": float(s["Age"].max()),
        "tests_under_18": int((s["Age"] < 18).sum()), "people_with_any_test_under_18": int(s.loc[s["Age"] < 18, "ID"].nunique()),
        "people_more_than_one_test": int((per_person > 1).sum()), "max_tests_per_person": int(per_person.max()),
        "tests_per_person_counts": {str(k): int(v) for k, v in per_person.value_counts().sort_index().items()},
        "every_person_has_get_index_1": bool((s.groupby("ID")["get_index"].min() == 1).all()),
        "get_index_consecutive_within_person": bool(idx_consecutive),
        "get_index_max": int(s["get_index"].max()),
        "people_with_index_above_their_test_count": int((idx_max_per_person > per_person).sum()),
        "age_non_decreasing_with_get_index": age_order_ok,
        "humidity_missing": int(hum_missing.sum()), "temperature_missing": int(temp_missing.sum()),
        "humidity_and_temperature_missing_same_rows": bool((hum_missing == temp_missing).all()),
        "gas_tests_all_missing": gas_all_missing, "gas_rows_missing": gas_rows_missing, "gas_tests_partially_missing": gas_partial,
        "gas_missing_overlap_with_humidity_missing": len(gas_missing_tests & hum_tests),
        "hr_missing_rows": int(meas["HR"].isna().sum()), "hr_tests_with_missing": int(g["HR"].apply(lambda x: x.isna().any()).sum()),
        "hr_below_30_rows": hr_lt30, "hr_zero_rows": int((meas["HR"] == 0).sum()), "hr_max": float(meas["HR"].max()),
        "speed_max": float(meas["Speed"].max()), "time_monotonic_within_test": bool(g["time"].apply(lambda x: x.is_monotonic_increasing).all()),
        "max_gap_s": float(g["time"].diff().max()),
        "measures_per_test_median_iqr": _miqr(n_meas), "duration_median_iqr": _miqr(dur),
        "age_median_iqr": _miqr(s["Age"]), "weight_median_iqr": _miqr(s["Weight"]), "height_median_iqr": _miqr(s["Height"]),
        "humidity_median_iqr": _miqr(s["Humidity"].dropna()), "temperature_median_iqr": _miqr(s["Temperature"].dropna()),
        "subject_columns_match": list(subj.columns) == SUBJ_COLS, "measure_columns_match": list(meas.columns) == MEAS_COLS,
        "measure_column_order_differs_from_page": list(meas.columns) != ["time", "Speed", "HR", "VO2", "VCO2", "RR", "VE", "ID", "ID_test"],
    }
    checks = [
        ("tests (subject-info rows)", PAGE["tests"], facts["tests"]),
        ("people (unique ID)", PAGE["people"], facts["people"]),
        ("test_measure rows", PAGE["measure_rows"], facts["measure_rows"]),
        ("tests with Sex = 1 (female)", PAGE["female_tests"], facts["female_tests"]),
        ("age median [IQR]", PAGE["age_median_iqr"], facts["age_median_iqr"]),
        ("weight median [IQR]", PAGE["weight_median_iqr"], facts["weight_median_iqr"]),
        ("height median [IQR]", PAGE["height_median_iqr"], facts["height_median_iqr"]),
        ("humidity median [IQR]", PAGE["humidity_median_iqr"], facts["humidity_median_iqr"]),
        ("temperature median [IQR]", PAGE["temperature_median_iqr"], facts["temperature_median_iqr"]),
        ("measures per test median [IQR]", PAGE["measures_median_iqr"], facts["measures_per_test_median_iqr"]),
        ("duration s median [IQR]", PAGE["duration_median_iqr"], facts["duration_median_iqr"]),
        ("tests with VO2, VCO2 and VE missing", PAGE["gas_missing_tests"],
         f"VO2 {gas_all_missing['VO2']}, VCO2 {gas_all_missing['VCO2']}, VE {gas_all_missing['VE']}"),
        ("age range", PAGE["age_text"], f"{facts['age_min']} to {facts['age_max']}"),
    ]
    cmp_rows = []
    for item, page, obs in checks:
        if isinstance(page, tuple):
            match = all(abs(a - b) < 0.006 for a, b in zip(page, obs))
        elif isinstance(page, (int, float)):
            match = page == obs
        else:
            match = None
        shown = ", ".join(f"{v:g}" for v in obs) if isinstance(obs, tuple) else str(obs)
        page_shown = ", ".join(f"{v:g}" for v in page) if isinstance(page, tuple) else str(page)
        cmp_rows.append({"item": item, "deposit_page": page_shown, "files": shown,
                         "match": "yes" if match else ("see note" if match is None else "no")})
    cmp_df = pd.DataFrame(cmp_rows)
    flags = [
        ("A1", "main", "Gas missingness differs from the page",
         f"Page: VO2, VCO2 and VE missing for 30 tests. Files: VO2 and VCO2 fully missing in {gas_all_missing['VO2']} tests "
         f"({gas_rows_missing['VO2']} rows), VE present in every row. Not corrected; gas analyses use tests with VO2."),
        ("A2", "main", "GET index is not a consecutive test count",
         f"Page: the GET index counts the tests of a person (its example is the third test). Files: every person has index 1, but later indices are not a running count "
         f"(largest index {facts['get_index_max']}; {facts['people_with_index_above_their_test_count']} of "
         f"{facts['people_more_than_one_test']} repeat testers have an index above their number of tests). "
         f"Ordering is consistent with age, so the lowest index is used as the first test."),
        ("A3", "main", "Minors are included",
         f"{facts['tests_under_18']} tests are under 18 (youngest {facts['age_min']}); page states 10 to 63. "
         "Excluded from the primary family, described separately, never shown at row level."),
        ("A4", "minor", "Humidity and temperature missing",
         f"{facts['humidity_missing']} rows each, the same rows; not mentioned on the page; no overlap with gas missing tests "
         f"({facts['gas_missing_overlap_with_humidity_missing']}). Not used in the primary analysis."),
        ("A5", "minor", "Heart rate artefacts",
         f"{facts['hr_missing_rows']} HR values missing and {facts['hr_below_30_rows']} values below 30 bpm "
         f"(including {facts['hr_zero_rows']} zero). Values below 30 bpm are set to missing in memory before peaks."),
        ("A6", "minor", "Column order in test_measure.csv",
         "Files list ID_test before ID; page lists ID before ID_test. No effect."),
        ("A7", "minor", "Sex coding",
         f"Sex takes values {facts['sex_values']}; 1 is female per the page; consistent within person: {facts['sex_consistent_within_person']}."),
        ("A8", "minor", "Breath sampling gaps",
         f"Time is increasing within every test; the largest gap between samples is {facts['max_gap_s']:.0f} s. "
         "Zone time weights are capped at 10 s."),
        ("A9", "minor", "Median measures per test",
         f"Page: 580 [484, 673]. Files: {facts['measures_per_test_median_iqr'][0]:g} [{facts['measures_per_test_median_iqr'][1]:g}, "
         f"{facts['measures_per_test_median_iqr'][2]:g}]; the page value looks truncated (992 tests, even count). Weight Q3 80.225 is shown as 80.23 on the page."),
    ]
    flags_df = pd.DataFrame(flags, columns=["flag", "severity", "item", "detail"])
    return cmp_df, flags_df, facts


def missingness_table(subj: pd.DataFrame, meas: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for c in subj.columns:
        rows.append({"file": "subject-info.csv", "column": c, "rows": len(subj), "missing_rows": int(subj[c].isna().sum()),
                     "tests_all_missing": int(subj[c].isna().sum())})
    g = meas.groupby("ID_test")
    for c in meas.columns:
        rows.append({"file": "test_measure.csv", "column": c, "rows": len(meas), "missing_rows": int(meas[c].isna().sum()),
                     "tests_all_missing": int(g[c].apply(lambda x: x.isna().all()).sum())})
    return pd.DataFrame(rows)
