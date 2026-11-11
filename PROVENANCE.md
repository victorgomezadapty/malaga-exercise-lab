# Data provenance

| Field | Value |
|-|-|
| Source | PhysioNet project `treadmill-exercise-cardioresp`, version 1.0.1 |
| Page | https://physionet.org/content/treadmill-exercise-cardioresp/1.0.1/ |
| Official title | Treadmill Maximal Exercise Tests from the Exercise Physiology and Human Performance Lab of the University of Malaga |
| Short name | "Málaga Exercise Lab" is only this project's short name (package `malaga_exercise_lab`); it is not the deposit title |
| Creators | Denis Mongin, Jeronimo García Romero, Jose Ramon Alvero Cruz |
| Version DOI | 10.13026/7ezk-j442 |
| Concept DOI | 10.13026/94yv-6145 |
| Published | 10 December 2021 (version 1.0.0 was 30 April 2021) |
| Access | Open access, anyone can download |
| License file | `LICENSE.txt`, CC BY-NC-SA 4.0 |
| Project card | PhysioNet Contributor Review Health Data License 1.5.0 and Data Use Agreement 1.5.0 (contradiction, see DATA_LICENSE.md) |
| Content | 992 graded treadmill exercise tests of 857 people, 2008 to 2018; breath by breath HR, VO2, VCO2, RR, VE and speed |
| Identifiers | ID (person) and ID_test (person plus GET index) study codes; no names or dates. They never appear in outputs |

## Files and official checksums

| File | Bytes | sha256 (from `SHA256SUMS.txt`) | In repo tree |
|-|-|-|-|
| `LICENSE.txt` | 14700 | `92905d58fa4b1d55f2ad00ece3a8282073565d228ce888a18274ca6e556e7361` | yes, unmodified |
| `subject-info.csv` | 33045 | `e9ca5ba20eb1272df56c11d3e584ec3997d5484454812bd94966e58082415f16` | no, local and gitignored |
| `test_measure.csv` | 23145166 | `3b5ed5586dc7412ccdfb26f804e29c06482a2a1df2060399c2731ebc68d4613d` | no, local and gitignored |
| `SHA256SUMS.txt` | 241 | `354d3bafbd02bdc37a3f212f44e0b024d864da271bede95af923a317bebf42aa` (sha256 of the sums file itself, measured) | yes, unmodified |

## How the local copy was made

On 11 Nov 2026 (UTC+3) `LICENSE.txt`, `SHA256SUMS.txt` and `test_measure.csv` were
downloaded from `https://physionet.org/files/treadmill-exercise-cardioresp/1.0.1/` and checked against
`SHA256SUMS.txt`. `subject-info.csv` came from an earlier local license check download; its sha256 was
re-verified and it was copied (not moved) into `data/raw/`. All four hashes match. The files in
`data/raw/` are never edited.

## Rules for this project

1. This PhysioNet deposit is the only data source. Nothing else is merged in.
2. Size and sha256 of all four files are checked on every load (`malaga_exercise_lab.data.verify_raw`),
   in the analysis script and in the tests. The analysis stops on any mismatch.
3. Outputs are aggregates only. No participant or test identifiers, no individual rows, no individual
   traces. Minors are described only as a group.
4. The companion papers are cited only. Their text, tables, figures, code and coefficients are not reused.
5. Nothing is published from this local draft: no git remote, no GitHub, no Kaggle, no new Vercel.
