# Málaga Exercise Lab

A transparent, reproducible re-analysis of one open PhysioNet deposit of 992 maximal treadmill
exercise tests: how far common age-predicted maximal heart rate formulas, and the training zones
taken as percentages of them, depart from the peak heart rate actually observed.

**Status: public on GitHub** at https://github.com/victorgomezadapty/malaga-exercise-lab.
No Kaggle dataset or notebook, and no dedicated Vercel site. The deposited CSV files are not
redistributed (see [DATA_LICENSE.md](DATA_LICENSE.md)).

## About the name

The deposit's official title is *Treadmill Maximal Exercise Tests from the Exercise Physiology and
Human Performance Lab of the University of Malaga* (PhysioNet, version 1.0.1, DOI
10.13026/7ezk-j442), by Denis Mongin, Jeronimo García Romero and Jose Ramon Alvero Cruz.
"Málaga Exercise Lab" is only this project's short name (package `malaga_exercise_lab`).

## Main result (primary, pre-specified)

Adults (18 and over), first test per person, n = 735 tests from 735 people (102 women), age 18.0
to 63.0. Error = formula HRmax minus observed effort phase HRpeak, 95% CI.

| Formula | Bias, bpm | MAE, bpm | RMSE, bpm | abs error > 10 bpm |
|-|-|-|-|-|
| 220 minus age | 3.0 (2.3 to 3.8) | 8.2 (7.8 to 8.7) | 10.5 (9.9 to 11.1) | 30.5% (27.3 to 33.9) |
| Tanaka 2001, 208 - 0.7 x age | 0.4 (-0.3 to 1.1) | 7.1 (6.7 to 7.6) | 9.2 (8.6 to 9.8) | 26.3% (23.2 to 29.6) |
| Gellish 2007, 206.9 - 0.67 x age | 0.2 (-0.4 to 0.9) | 7.1 (6.7 to 7.5) | 9.2 (8.6 to 9.8) | 26.7% (23.6 to 30.0) |

The honest headline: on average Tanaka and Gellish land close to the observed peak in this table,
and 220 minus age sits about 3 bpm high. But for a single person every formula misses by about 7 to
8 bpm on average, and by more than 10 bpm in roughly one test in four (Tanaka, Gellish) to one in
three (220 minus age). A small average bias is not individual accuracy.

**Zone discordance.** With zones at 70% and 85% of HRmax, the share of effort phase time that would
be labelled in a different zone (below 70%, 70 to 85%, above 85%) when the formula replaces the
observed peak is, on average per test:
220 minus age 14.7% (13.7 to 15.7), Tanaka 12.4% (11.5 to 13.2), Gellish 12.3% (11.5 to 13.1).
The 85% boundary from 220 minus age is on average
2.6 bpm (2.0 to 3.2) above the observed one, with a 10th to 90th percentile range of -7.4 to 13.3 bpm.
This describes discordance only; it is not training advice and not evidence of equivalence.

**Age pattern (descriptive).** The 220 minus age bias falls from 8.5 bpm at 18 to 21 years to
-4.1 bpm at 45 and over. Sensitivities (any time maximum, spike robust peak, regular protocols only,
first adult test, all adult tests clustered by person) move the bias by less than 0.5 bpm and the MAE
by less than 0.2 bpm. Full numbers: [RESULTS.md](RESULTS.md) and `results/summary.json`.

## What this project adds

1. **Deposit audit.** Both files are checked against the deposit page; mismatches are flagged, none
   silently corrected. Gas data (VO2, VCO2) are missing in 11 tests, not the 30 stated, and VE is
   never missing; the GET index in ID_test is not a running test count (largest index 371); 145
   tests are under 18; humidity and temperature are missing in 30 rows; 53 HR values are below
   30 bpm.
2. **A written effort phase rule, fixed before results** ([ANALYSIS_PLAN.md](ANALYSIS_PLAN.md)):
   warmup, effort and recovery are separated from treadmill speed, and HRpeak is taken inside the
   effort phase, with irregular protocols flagged.
3. **A practical formula check** that the companion papers do not address: three cited
   age-predicted HRmax formulas against observed HRpeak, with bias, MAE, RMSE and the share beyond
   10 bpm, robust 95% CIs, adults only and one test per person.
4. **Zone discordance**: how much effort time changes zone label when a formula replaces the
   measured peak.

## What this project is not

* Not a replication of the companion papers (dynamical analysis of HR and VO2; heart rate recovery
  methods). They are cited only; their text, tables, figures, code and coefficients are not reused,
  compared or "beaten".
* Not a new maximal heart rate formula. A descriptive age line is reported and labelled as such.
* Not a ventilatory threshold analysis.
* Not clinical advice, not a training prescription, and not evidence that any formula is
  equivalent to a measured peak.
* Not a data release. No row-level data, identifiers or individual traces appear in any output.

## Discussion and open questions

A current literature search (November 2026) is in [DISCUSSION.md](DISCUSSION.md). Recent external
checks also find small mean bias with individual errors of about 7 to 10 bpm, and they do not
support treating a formula as a measured peak. What this project adds, beyond those papers, is the
zone discordance at 70% and 85% of maximal heart rate. Open questions include threshold
concordance on this same table, sex-specific and under-18 accuracy, older adults, repeat tests, a
stricter maximal-effort rule, and clinical populations. The search does not change the primary
numbers above.


## Project layout

| Path | Content |
|-|-|
| `data/raw/LICENSE.txt`, `data/raw/SHA256SUMS.txt` | Unmodified deposit files |
| `data/raw/subject-info.csv`, `data/raw/test_measure.csv` | Local only, gitignored, never redistributed |
| `src/malaga_exercise_lab/` | `data` (metadata, hashes), `audit`, `phases` (effort rule), `analysis`, `figures`, `report` |
| `scripts/fetch_data.py` | Downloads missing files from PhysioNet and stops on any size or sha256 mismatch |
| `scripts/run_analysis.py` | Regenerates `tables/`, `figures/`, `results/summary.json`, `RESULTS.md` |
| `tests/` | Integrity, refusal on mismatch, license, privacy, copy and numeric lock tests |
| `tables/` | 13 CSV tables, aggregates only |
| `figures/` | 6 figures as PNG with WebP twins |
| `ANALYSIS_PLAN.md` | Pre-specified plan |
| `PORTFOLIO_BRIEF.md` | Locked facts for a later portfolio case |
| `DISCUSSION.md` | Current literature (November 2026) and open questions |

## Reproduce

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/fetch_data.py     # downloads from PhysioNet and verifies sha256
.venv/bin/python scripts/run_analysis.py
.venv/bin/python -m pytest -q
```

## Citation and license

Data: Mongin, D., García Romero, J., and Alvero Cruz, J. R. (2021). Treadmill Maximal Exercise
Tests from the Exercise Physiology and Human Performance Lab of the University of Malaga (version
1.0.1). PhysioNet. RRID:SCR_007345. https://doi.org/10.13026/7ezk-j442. The deposited license file is
CC BY-NC-SA 4.0, while the project card lists the PhysioNet Contributor Review Health Data License
1.5.0; see [DATA_LICENSE.md](DATA_LICENSE.md). Also cite PhysioNet: Pollard et al. 2026, Nature
Health, https://doi.org/10.1038/s44360-026-00096-z.

Formulas: Fox, Naughton and Haskell 1971 (220 minus age form); Tanaka, Monahan and Seals 2001,
https://doi.org/10.1016/S0735-1097(00)01054-8; Gellish et al. 2007,
https://doi.org/10.1097/mss.0b013e31803349c6.

Code: MIT ([LICENSE](LICENSE)), copyright 2026 Víctor Andrés Gómez López. Provenance:
[PROVENANCE.md](PROVENANCE.md).
