# Data license and attribution

## Data source

The only data used in this project is the following PhysioNet deposit:

> Mongin, D., García Romero, J., and Alvero Cruz, J. R. (2021). Treadmill Maximal Exercise Tests from
> the Exercise Physiology and Human Performance Lab of the University of Malaga (version 1.0.1).
> PhysioNet. RRID:SCR_007345. https://doi.org/10.13026/7ezk-j442

* Creators, in the official order: Denis Mongin, Jeronimo García Romero, Jose Ramon Alvero Cruz.
* Version DOI 10.13026/7ezk-j442; concept DOI 10.13026/94yv-6145; published 10 December 2021; open access.
* PhysioNet standard citation, as requested on the page: Pollard, T., et al. (2026). PhysioNet as a
  global platform for biomedical research. Nature Health. https://doi.org/10.1038/s44360-026-00096-z

## The license contradiction

The deposit carries two different sets of terms, and they do not agree:

1. **The deposited file `LICENSE.txt`** is the standard *Creative Commons Attribution-NonCommercial-
   ShareAlike 4.0 International Public License* (CC BY-NC-SA 4.0), sha256
   `92905d58fa4b1d55f2ad00ece3a8282073565d228ce888a18274ca6e556e7361`.
2. **The PhysioNet project card** lists the *PhysioNet Contributor Review Health Data License 1.5.0*
   and the *PhysioNet Contributor Review Health Data Use Agreement 1.5.0*. That agreement forbids
   sharing the data with anyone else.

Until the depositors or PhysioNet resolve this, the project follows the more restrictive reading.

## What this project does and does not do with the data

* **This project does not redistribute `subject-info.csv` or `test_measure.csv`, in whole, in part,
  or in any transformed row-level form.** Both CSV files are kept only under `data/raw/` on the
  local machine and are listed in `.gitignore`. Anyone who wants to run the code must download them
  from PhysioNet under PhysioNet's terms (`scripts/fetch_data.py` does this and checks the hashes).
* `LICENSE.txt` and `SHA256SUMS.txt` are kept unmodified in `data/raw/` so the terms and the official
  checksums travel with the code. The official license text is not edited.
* All outputs (`tables/`, `figures/`, `results/summary.json`, `RESULTS.md`) are aggregate research
  results: means, proportions, intervals and counts. No participant ID, test ID or individual row
  appears in any of them. The deposit includes minors (youngest 10.8 years); they are summarised
  only as a group.
* No Kaggle dataset or notebook, and no other public dump of the table, is made from this project.
* The derived aggregate figures and tables are not relicensed. They are not offered under CC BY 4.0.
  If they are ever shown publicly they are treated as aggregate research results with the
  attribution above, and, as far as CC BY-NC-SA 4.0 applies, as non-commercial ShareAlike
  adaptations that carry the same attribution and terms.

### Changes made (CC BY-NC-SA 4.0 section 3(a)(1)(B))

* No change to any deposited file. All four are hash checked on every load.
* In memory only: heart rate values below 30 bpm are set to missing; the GET index is parsed from
  ID_test; effort phase windows are derived from treadmill speed.
* Aggregation and statistical modelling only.

The creators, PhysioNet and the University of Malaga do not endorse this project or its interpretation.

## Companion publications (cited only)

The papers below are cited for attribution and to make clear what this project does not repeat.
No text, tables, figures, code or coefficients from them are reused.

* Mongin D, Chabert C, Courvoisier DS, García-Romero J, Alvero-Cruz JR. Heart rate recovery to assess
  fitness: comparison of different calculation methods in a large cross-sectional study. Research in
  Sports Medicine. 31:157-170. Published online 2021. https://doi.org/10.1080/15438627.2021.1954513
* Mongin D, Chabert C, Uribe Caparros A, Collado A, Hermand E, Hue O, et al. Validity of dynamical
  analysis to characterize heart rate and oxygen consumption during effort tests. Scientific Reports.
  2020;10:12420. https://doi.org/10.1038/s41598-020-69218-1
* Mongin D, Chabert C, Uribe Caparros A, Vico Guzmán JF, Hue O, Alvero-Cruz JR, Courvoisier DS. The
  complex relationship between effort and heart rate: a hint from dynamic analysis. Physiological
  Measurement. 2020;41(10):105003. https://doi.org/10.1088/1361-6579/abbb6e

## Code

The code in `src/`, `scripts/` and `tests/` is licensed under the MIT License (see `LICENSE`),
copyright 2026 Víctor Andrés Gómez López. The MIT license does not apply to the data, to the
deposited files, or to the derived results.
