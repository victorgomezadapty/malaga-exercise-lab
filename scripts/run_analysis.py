"""Run the full Malaga Exercise Lab analysis offline from the verified local deposit files.

Usage (from the project root):
    .venv/bin/python scripts/run_analysis.py

Stops with an error if the size or sha256 of any deposited file differs from SHA256SUMS.txt.
Writes tables/ (aggregates), figures/ (PNG and WebP), results/summary.json and RESULTS.md.
"""
from __future__ import annotations

import json
import platform
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from malaga_exercise_lab import analysis as A  # noqa: E402
from malaga_exercise_lab import audit as AU  # noqa: E402
from malaga_exercise_lab import data as D  # noqa: E402
from malaga_exercise_lab import figures as F  # noqa: E402
from malaga_exercise_lab import phases as P  # noqa: E402
from malaga_exercise_lab.report import write_results_md  # noqa: E402

TABLES, FIGS, RES = ROOT / "tables", ROOT / "figures", ROOT / "results"
KEYS = ["n_tests", "n_people", "bias_bpm", "bias_ci95_low", "bias_ci95_high", "mae_bpm", "mae_ci95_low", "mae_ci95_high",
        "rmse_bpm", "rmse_ci95_low", "rmse_ci95_high", "n_abs_error_over_10", "pct_abs_error_over_10", "pct_ci95_low",
        "pct_ci95_high", "pct_formula_above_observed"]


def r(x, k=4):
    if isinstance(x, (list, tuple)):
        return [r(v, k) for v in x]
    if isinstance(x, (bool, np.bool_)):
        return bool(x)
    if isinstance(x, (int, np.integer)):
        return int(x)
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), k)


def metrics(t: pd.DataFrame) -> dict:
    return {row["formula"]: {k: r(row[k]) for k in KEYS} for _, row in t.iterrows()}


def compute():
    hashes = D.verify_raw()
    subj, meas = D.load_raw()
    s = D.prepare_subjects(subj)
    pt, extra = P.per_test(meas)
    df = A.build_frame(s, pt)
    cmp_df, flags, facts = AU.audit(subj, s, meas)
    miss = AU.missingness_table(subj, meas)
    S = A.samples(df)
    prim, sens, minors = A.primary_and_sensitivity(S)
    sub = A.by_subgroup(S["primary"])
    shifts, disc = A.zone_discordance(S["primary"], extra["effort_samples"])
    desc = A.descriptors(S["primary"])
    band = F.band_table(S["primary"])
    return locals()


def main() -> None:
    for p in (TABLES, FIGS, RES):
        p.mkdir(exist_ok=True)
    for old in list(TABLES.glob("*.csv")) + list(FIGS.glob("*.png")) + list(FIGS.glob("*.webp")):
        old.unlink()  # generated outputs only; data/raw is never touched
    c = compute()
    df, S, pt = c["df"], c["S"], c["pt"]
    prim, sens, minors, sub, shifts, disc = c["prim"], c["sens"], c["minors"], c["sub"], c["shifts"], c["disc"]
    flag_cols = [k for k in pt.columns if k.startswith("flag_")]
    phase_tab = pd.DataFrame([{"flag": k, "tests_all": int(pt[k].sum()), "tests_primary": int(S["primary"][k].sum())} for k in flag_cols] +
                             [{"flag": "any irregular flag", "tests_all": int(pt["irregular"].sum()), "tests_primary": int(S["primary"]["irregular"].sum())},
                              {"flag": "max HR any time above effort max", "tests_all": int(pt["hrpeak_in_recovery"].sum()),
                               "tests_primary": int(S["primary"]["hrpeak_in_recovery"].sum())}])
    sample_tab = pd.DataFrame([{"sample": k, "tests": len(v), "people": int(v["ID"].nunique()), "female_tests": int((v["Sex"] == 1).sum()),
                                "age_min": float(v["Age"].min()), "age_max": float(v["Age"].max()),
                                "gas_available_tests": int(v["gas_available"].sum())} for k, v in S.items()])
    outs = [("t01_page_vs_files.csv", c["cmp_df"]), ("t02_audit_flags.csv", c["flags"]), ("t03_missingness.csv", c["miss"]),
            ("t04_samples.csv", sample_tab), ("t05_effort_phase_flags.csv", phase_tab), ("t06_primary_descriptors.csv", c["desc"]),
            ("t07_primary_formula_error.csv", prim), ("t08_sensitivity_formula_error.csv", sens),
            ("t09_under18_descriptive_formula_error.csv", minors), ("t10_primary_by_age_band_and_sex.csv", sub),
            ("t11_observed_hrpeak_by_age_band.csv", c["band"]), ("t12_zone_boundary_shift.csv", shifts),
            ("t13_zone_discordance.csv", disc)]
    for name, t in outs:
        t.to_csv(TABLES / name, index=False, float_format="%.6g")
    made = []
    made += F.fig_audit(c["cmp_df"], c["facts"], FIGS / "fig01_deposit_audit.png")
    made += F.fig_schematic(FIGS / "fig02_effort_phase_rule.png")
    made += F.fig_formula_error(prim, c["band"], FIGS / "fig03_formula_error.png")
    made += F.fig_by_age(c["band"], FIGS / "fig04_hrpeak_by_age_band.png")
    made += F.fig_zones(disc, FIGS / "fig05_zone_discordance.png")
    made += F.fig_sensitivity(prim, sens, minors, FIGS / "fig06_sensitivity.png")
    facts = {k: (list(v) if isinstance(v, tuple) else v) for k, v in c["facts"].items()}
    summary = {
        "project": D.SHORT_NAME, "package": D.PACKAGE, "status": "public on GitHub",
        "dataset": {"title": D.DATASET_TITLE, "physionet_slug": D.SLUG, "version": D.VERSION, "page": D.PAGE_URL,
                    "version_doi": D.VERSION_DOI, "concept_doi": D.CONCEPT_DOI, "published": D.PUBLISHED,
                    "creators": D.CREATORS, "citation": D.DATASET_CITATION, "access": "open access",
                    "license_file": D.LICENSE_FILE_NAME, "project_card_license": D.CARD_LICENSE, "project_card_dua": D.CARD_DUA,
                    "license_contradiction": True, "csv_redistributed": False, "files_verified": c["hashes"]},
        "companion_work": [{"citation": x["citation"], "doi": x["doi"], "use": "cited only"} for x in D.COMPANION],
        "formulas": {k: {"expression": A.FORMULA_TEXT[k], "reference": D.FORMULA_REFS[k]} for k in A.FORMULAS},
        "environment": {"python": platform.python_version(), "pandas": pd.__version__, "numpy": np.__version__},
        "audit": {"facts": facts, "flags": {row.flag: {"severity": row.severity, "item": row.item} for row in c["flags"].itertuples()}},
        "effort_phase": {"rule": "after last sample at warmup speed S0 + 0.05 km/h, up to last sample before speed < Vmax - 1 km/h",
                         "hr_artefact_rule": "HR below 30 bpm set to missing", **{k: r(v) for k, v in c["extra"]["artefacts"].items()},
                         "flag_counts_all_tests": {k: int(pt[k].sum()) for k in flag_cols},
                         "irregular_all_tests": int(pt["irregular"].sum()), "irregular_primary": int(S["primary"]["irregular"].sum()),
                         "hrpeak_in_recovery_primary": int(S["primary"]["hrpeak_in_recovery"].sum())},
        "samples": {k: len(v) for k, v in S.items()},
        "primary_sample": {"definition": "first test per person (lowest GET index), age 18 or over at that test",
                           "n_tests": len(S["primary"]), "n_people": int(S["primary"]["ID"].nunique()),
                           "female": int((S["primary"]["Sex"] == 1).sum()), "age_range": r([S["primary"]["Age"].min(), S["primary"]["Age"].max()], 1),
                           "observed_hrpeak_mean": r(S["primary"]["hrpeak_effort"].mean()), "observed_hrpeak_sd": r(S["primary"]["hrpeak_effort"].std())},
        "primary": metrics(prim),
        "sensitivity": {lab: metrics(g) for lab, g in sens.groupby("sample", sort=False)},
        "under18_descriptive": metrics(minors),
        "subgroups_descriptive": {lab: metrics(g) for lab, g in sub.groupby("subgroup", sort=False)},
        "age_line_descriptive": {k: r(v) if not isinstance(v, str) else v for k, v in A.age_line(S["primary"]).items()},
        "zone_boundary_shift": {f"{row['formula']}|{row['boundary_pct_hrmax']}": {k: r(row[k]) for k in
                                ["mean_shift_bpm", "ci95_low", "ci95_high", "median_shift_bpm", "p10_shift_bpm", "p90_shift_bpm", "pct_tests_shift_over_5bpm"]}
                                for _, row in shifts.iterrows()},
        "zone_discordance": {row["formula"]: {k: (r(row[k]) if not isinstance(row[k], str) else row[k]) for k in disc.columns if k != "formula"}
                             for _, row in disc.iterrows()},
        "figure_titles": F.TITLES, "figure_footer": F.FOOTER,
        "outputs": {"tables": sorted(p.name for p in TABLES.glob("*.csv")), "figures": sorted(p.name for p in made)},
    }
    (RES / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_results_md(ROOT / "RESULTS.md", summary, c["cmp_df"], c["flags"], prim, sens, minors, sub, shifts, disc, c["desc"], c["band"])
    log = [f"verified {json.dumps(c['hashes'])}", f"primary n {len(S['primary'])}",
           f"tables {len(summary['outputs']['tables'])} figures {len(made)}"]
    (RES / "run_log.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
    print("\n".join(log))


if __name__ == "__main__":
    main()
