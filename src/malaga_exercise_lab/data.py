"""Source metadata, integrity checks and loading for the PhysioNet treadmill deposit.

Only data source: PhysioNet project treadmill-exercise-cardioresp, version 1.0.1
(version DOI 10.13026/7ezk-j442, concept DOI 10.13026/94yv-6145).
The deposited files are never modified. Derived columns exist in memory only.
The two CSV files are kept only under data/raw/ and are gitignored; they are never redistributed.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"

DATASET_TITLE = ("Treadmill Maximal Exercise Tests from the Exercise Physiology and Human "
                 "Performance Lab of the University of Malaga")
SHORT_NAME = "Málaga Exercise Lab"
PACKAGE = "malaga_exercise_lab"
SLUG = "treadmill-exercise-cardioresp"
VERSION = "1.0.1"
PAGE_URL = "https://physionet.org/content/treadmill-exercise-cardioresp/1.0.1/"
FILES_URL = "https://physionet.org/files/treadmill-exercise-cardioresp/1.0.1/"
VERSION_DOI = "10.13026/7ezk-j442"
CONCEPT_DOI = "10.13026/94yv-6145"
PUBLISHED = "2021-12-10"
CREATORS = ["Denis Mongin", "Jeronimo García Romero", "Jose Ramon Alvero Cruz"]
DATASET_CITATION = (
    "Mongin, D., García Romero, J., and Alvero Cruz, J. R. (2021). " + DATASET_TITLE +
    " (version 1.0.1). PhysioNet. RRID:SCR_007345. https://doi.org/10.13026/7ezk-j442"
)
SHORT_CITATION = "Mongin, García Romero and Alvero Cruz 2021, PhysioNet, doi 10.13026/7ezk-j442"
PHYSIONET_CITATION = (
    "Pollard, T., Moody, B. E., Lehman, L., Gow, B., Fernandes, C., Xie, C., Johnson, A., Mark, R. G., "
    "and Heldt, T. (2026). PhysioNet as a global platform for biomedical research. Nature Health. "
    "https://doi.org/10.1038/s44360-026-00096-z"
)
LICENSE_FILE_NAME = "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International Public License"
LICENSE_FILE_SHORT = "CC BY-NC-SA 4.0"
CARD_LICENSE = "PhysioNet Contributor Review Health Data License 1.5.0"
CARD_DUA = "PhysioNet Contributor Review Health Data Use Agreement 1.5.0"

# Official SHA256SUMS.txt of version 1.0.1, plus byte sizes measured on the verified files.
EXPECTED = {
    "LICENSE.txt": {"sha256": "92905d58fa4b1d55f2ad00ece3a8282073565d228ce888a18274ca6e556e7361", "bytes": 14700},
    "subject-info.csv": {"sha256": "e9ca5ba20eb1272df56c11d3e584ec3997d5484454812bd94966e58082415f16", "bytes": 33045},
    "test_measure.csv": {"sha256": "3b5ed5586dc7412ccdfb26f804e29c06482a2a1df2060399c2731ebc68d4613d", "bytes": 23145166},
}
SUMS_FILE = "SHA256SUMS.txt"
SUMS_SHA256 = "354d3bafbd02bdc37a3f212f44e0b024d864da271bede95af923a317bebf42aa"
SUMS_BYTES = 241
RAW_CSVS = ["subject-info.csv", "test_measure.csv"]

COMPANION = [
    {"key": "rsm2021", "role": "original publication requested by the deposit page",
     "citation": ("Mongin D, Chabert C, Courvoisier DS, García-Romero J, Alvero-Cruz JR. Heart rate recovery "
                  "to assess fitness: comparison of different calculation methods in a large cross-sectional "
                  "study. Research in Sports Medicine. 31:157-170. Published online 2021."),
     "doi": "10.1080/15438627.2021.1954513"},
    {"key": "scirep2020", "role": "companion reference on the deposit page",
     "citation": ("Mongin D, Chabert C, Uribe Caparros A, Collado A, Hermand E, Hue O, et al. Validity of "
                  "dynamical analysis to characterize heart rate and oxygen consumption during effort tests. "
                  "Scientific Reports. 2020;10:12420."),
     "doi": "10.1038/s41598-020-69218-1"},
    {"key": "physmeas2020", "role": "companion reference on the deposit page",
     "citation": ("Mongin D, Chabert C, Uribe Caparros A, Vico Guzmán JF, Hue O, Alvero-Cruz JR, Courvoisier DS. "
                  "The complex relationship between effort and heart rate: a hint from dynamic analysis. "
                  "Physiological Measurement. 2020;41(10):105003."),
     "doi": "10.1088/1361-6579/abbb6e"},
]
FORMULA_REFS = {
    "220 minus age": ("Fox SM, Naughton JP, Haskell WL. Physical activity and the prevention of coronary heart "
                      "disease. Annals of Clinical Research. 1971;3(6):404-432."),
    "Tanaka 2001": ("Tanaka H, Monahan KD, Seals DR. Age-predicted maximal heart rate revisited. Journal of the "
                    "American College of Cardiology. 2001;37(1):153-156. https://doi.org/10.1016/S0735-1097(00)01054-8"),
    "Gellish 2007": ("Gellish RL, Goslin BR, Olson RE, McDonald A, Russi GD, Moudgil VK. Longitudinal modeling of the "
                     "relationship between age and maximal heart rate. Medicine and Science in Sports and Exercise. "
                     "2007;39(5):822-829. https://doi.org/10.1097/mss.0b013e31803349c6"),
}


class IntegrityError(RuntimeError):
    """Raised when a deposited file is missing or differs from the official sums."""


def sha256sum(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_sums(text: str) -> dict:
    out = {}
    for line in text.splitlines():
        parts = line.split()
        if len(parts) == 2:
            out[parts[1].lstrip("*")] = parts[0].lower()
    return out


def verify_file(path: Path, sha256: str, nbytes: int | None = None) -> dict:
    if not path.exists():
        raise IntegrityError(f"missing file: {path.name}")
    size = path.stat().st_size
    if nbytes is not None and size != nbytes:
        raise IntegrityError(f"size mismatch for {path.name}: {size} bytes, expected {nbytes}")
    digest = sha256sum(path)
    if digest != sha256:
        raise IntegrityError(f"sha256 mismatch for {path.name}: {digest}, expected {sha256}")
    return {"sha256": digest, "bytes": size}


def verify_raw(raw_dir: Path = RAW_DIR) -> dict:
    """Raise IntegrityError unless every file matches the official SHA256SUMS and size."""
    out = {SUMS_FILE: verify_file(raw_dir / SUMS_FILE, SUMS_SHA256, SUMS_BYTES)}
    listed = parse_sums((raw_dir / SUMS_FILE).read_text(encoding="utf-8"))
    for name, exp in EXPECTED.items():
        if listed.get(name) != exp["sha256"]:
            raise IntegrityError(f"SHA256SUMS.txt entry for {name} differs from the pinned official value")
        out[name] = verify_file(raw_dir / name, exp["sha256"], exp["bytes"])
    return out


def load_raw(raw_dir: Path = RAW_DIR) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Verify, then load the two deposited CSV files unchanged."""
    verify_raw(raw_dir)
    subj = pd.read_csv(raw_dir / "subject-info.csv")
    meas = pd.read_csv(raw_dir / "test_measure.csv")
    return subj, meas


def prepare_subjects(subj: pd.DataFrame) -> pd.DataFrame:
    """Add the GET index parsed from ID_test and the female flag (in memory only)."""
    s = subj.copy()
    parts = s["ID_test"].astype(str).str.split("_", expand=True)
    s["id_prefix"] = parts[0].astype(int)
    s["get_index"] = parts[1].astype(int)
    s["female"] = (s["Sex"] == 1).astype(int)
    s["first_test"] = s["get_index"] == s.groupby("ID")["get_index"].transform("min")
    s["adult"] = s["Age"] >= 18
    return s
