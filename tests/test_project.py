"""Integrity, license, privacy, copy and numeric lock tests for Malaga Exercise Lab."""
import json
import re
import shutil
import subprocess
import sys
from fnmatch import fnmatch
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from malaga_exercise_lab import analysis as A  # noqa: E402
from malaga_exercise_lab import data as D  # noqa: E402
from malaga_exercise_lab import figures as F  # noqa: E402

DOCS = ["README.md", "RESULTS.md", "DATA_LICENSE.md", "PROVENANCE.md", "PORTFOLIO_BRIEF.md", "ANALYSIS_PLAN.md", "LICENSE",
        "DISCUSSION.md", "requirements.txt", ".gitignore"]
DASHES = ["\u2010", "\u2011", "\u2012", "\u2013", "\u2014", "\u2015", "\u2212", "-" * 2]
FORBIDDEN_NAMES = ["optimo", "malqa", "riyadh"]
FORBIDDEN_CLAIMS = ["we replicate", "replicates the", "successfully replicated", "outperform", "beats the", "beat the paper",
                    "better than the paper", "kaggle.com", "uploaded to kaggle", "kaggle dataset is live", "you should train",
                    "we recommend training", "clinical recommendation", "proves equivalence", "are interchangeable", "vercel.app"]
OFFICIAL = D.EXPECTED


@pytest.fixture(scope="module")
def summary():
    return json.loads((ROOT / "results" / "summary.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def computed():
    import run_analysis
    return run_analysis.compute()


def our_texts():
    files = [ROOT / n for n in DOCS]
    files += sorted((ROOT / "src").rglob("*.py")) + sorted((ROOT / "scripts").glob("*.py")) + sorted((ROOT / "tests").glob("*.py"))
    files += sorted((ROOT / "tables").glob("*.csv")) + [ROOT / "results" / "summary.json", ROOT / "results" / "run_log.txt"]
    return {str(p.relative_to(ROOT)): p.read_text(encoding="utf-8") for p in files}


def output_texts():
    files = [ROOT / n for n in ["README.md", "RESULTS.md", "PORTFOLIO_BRIEF.md"]]
    files += sorted((ROOT / "tables").glob("*.csv")) + [ROOT / "results" / "summary.json"]
    return {p.name: p.read_text(encoding="utf-8") for p in files}


# Integrity

def test_official_sums_file_lists_pinned_hashes():
    listed = D.parse_sums((D.RAW_DIR / "SHA256SUMS.txt").read_text())
    assert listed == {k: v["sha256"] for k, v in OFFICIAL.items()}
    assert OFFICIAL["test_measure.csv"]["sha256"] == "3b5ed5586dc7412ccdfb26f804e29c06482a2a1df2060399c2731ebc68d4613d"
    assert OFFICIAL["subject-info.csv"]["sha256"] == "e9ca5ba20eb1272df56c11d3e584ec3997d5484454812bd94966e58082415f16"
    assert OFFICIAL["LICENSE.txt"]["sha256"] == "92905d58fa4b1d55f2ad00ece3a8282073565d228ce888a18274ca6e556e7361"


def test_local_files_match_official_hashes():
    res = D.verify_raw()
    for name, exp in OFFICIAL.items():
        assert res[name]["sha256"] == exp["sha256"] and res[name]["bytes"] == exp["bytes"]


def _copy_raw(tmp_path):
    for p in D.RAW_DIR.iterdir():
        if p.is_file():
            shutil.copy2(p, tmp_path / p.name)
    return tmp_path


def test_refuses_on_content_mismatch(tmp_path):
    raw = _copy_raw(tmp_path)
    f = raw / "subject-info.csv"
    b = bytearray(f.read_bytes()); b[-2] = ord("9") if b[-2] != ord("9") else ord("8"); f.write_bytes(bytes(b))
    with pytest.raises(D.IntegrityError, match="sha256 mismatch"):
        D.load_raw(raw)


def test_refuses_on_size_mismatch_and_missing(tmp_path):
    raw = _copy_raw(tmp_path)
    with open(raw / "test_measure.csv", "ab") as fh:
        fh.write(b"\n")
    with pytest.raises(D.IntegrityError, match="size mismatch"):
        D.verify_raw(raw)
    (raw / "test_measure.csv").unlink()
    with pytest.raises(D.IntegrityError, match="missing"):
        D.verify_raw(raw)


def test_refuses_on_tampered_sums_file(tmp_path):
    raw = _copy_raw(tmp_path)
    (raw / "SHA256SUMS.txt").write_text("0" * 64 + " test_measure.csv\n")
    with pytest.raises(D.IntegrityError):
        D.verify_raw(raw)


def test_fetch_script_refuses_mismatch(tmp_path, monkeypatch):
    import fetch_data
    monkeypatch.setattr(D, "RAW_DIR", tmp_path)

    class Fake:
        def __init__(self): self.done = False
        def read(self, n):
            if self.done:
                return b""
            self.done = True
            return b"not the file"
        def __enter__(self): return self
        def __exit__(self, *a): return False

    monkeypatch.setattr(fetch_data.urllib.request, "urlopen", lambda *a, **k: Fake())
    assert fetch_data.main() == 1
    assert not (tmp_path / "SHA256SUMS.txt").exists()


# Repository hygiene and license

def test_gitignore_covers_csvs_and_caches():
    pats = [l.strip() for l in (ROOT / ".gitignore").read_text().splitlines() if l.strip() and not l.startswith("#")]
    for path in ["data/raw/subject-info.csv", "data/raw/test_measure.csv"]:
        assert any(fnmatch(path, p) for p in pats), path
    for p in [".venv/", "__pycache__/", ".pytest_cache/"]:
        assert p in pats


def test_csvs_not_tracked():
    if not (ROOT / ".git").exists():
        pytest.skip("no local git repository")
    tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    assert not any(t.startswith("data/raw/") and t.endswith(".csv") for t in tracked)
    for t in ["data/raw/subject-info.csv", "data/raw/test_measure.csv"]:
        assert subprocess.run(["git", "check-ignore", "-q", t], cwd=ROOT).returncode == 0


def test_license_contradiction_documented():
    t = (ROOT / "DATA_LICENSE.md").read_text()
    for s in ["Creative Commons Attribution-NonCommercial-", "CC BY-NC-SA 4.0", D.CARD_LICENSE, D.CARD_DUA,
              "forbids", "does not redistribute `subject-info.csv` or `test_measure.csv`", "MIT"]:
        assert s in t.replace("\n", " ").replace("-   ", "-"), s
    assert (D.RAW_DIR / "LICENSE.txt").read_text().startswith(D.LICENSE_FILE_NAME)
    for name in ["README.md", "PORTFOLIO_BRIEF.md", "DATA_LICENSE.md"]:
        for line in (ROOT / name).read_text().splitlines():
            if "CC BY 4.0" in line:
                assert "not" in line.lower(), (name, line)


def test_official_title_and_three_creators():
    for name in ["README.md", "DATA_LICENSE.md", "PROVENANCE.md", "PORTFOLIO_BRIEF.md"]:
        t = " ".join((ROOT / name).read_text().replace("\n> ", "\n").split())
        assert D.DATASET_TITLE in t, name
        assert "10.13026/7ezk-j442" in t
    for name in ["README.md", "PROVENANCE.md", "PORTFOLIO_BRIEF.md"]:
        t = (ROOT / name).read_text()
        pos = [t.index(c) for c in D.CREATORS]
        assert pos == sorted(pos), name
    assert D.CREATORS == ["Denis Mongin", "Jeronimo García Romero", "Jose Ramon Alvero Cruz"]


def test_status_public(summary):
    assert summary["status"] == "public on GitHub"
    readme = (ROOT / "README.md").read_text()
    brief = (ROOT / "PORTFOLIO_BRIEF.md").read_text()
    assert "https://github.com/victorgomezadapty/malaga-exercise-lab" in readme
    assert "https://github.com/victorgomezadapty/malaga-exercise-lab" in brief
    assert "publicLink: null" in brief
    assert "no Kaggle" in readme or "No Kaggle" in readme


# Copy rules

def test_no_typographic_dashes_in_our_copy():
    for name, t in our_texts().items():
        for d in DASHES:
            assert d not in t, (name, repr(d))
    for t in list(F.TITLES.values()) + [F.FOOTER]:
        assert not any(d in t for d in DASHES)


def test_no_forbidden_names():
    for name, t in our_texts().items():
        if name.startswith("tests/"):
            continue
        low = t.lower()
        for w in FORBIDDEN_NAMES:
            assert w not in low, (name, w)


def test_no_forbidden_claims():
    for name, t in our_texts().items():
        if name.startswith("tests/"):
            continue
        low = " ".join(t.lower().split())
        for c in FORBIDDEN_CLAIMS:
            assert c not in low, (name, c)


# Privacy: aggregates only

def test_no_row_level_ids_in_outputs():
    pat = re.compile(r"\b\d{1,3}_\d{1,3}\b")
    for name, t in output_texts().items():
        assert not pat.search(t), name
    for p in (ROOT / "tables").glob("*.csv"):
        head = p.read_text().splitlines()[0].split(",")
        assert "ID" not in head and "ID_test" not in head, p.name
        assert len(p.read_text().splitlines()) < 100, p.name


def test_figures_exist_png_and_webp(summary):
    figs = summary["outputs"]["figures"]
    assert len([f for f in figs if f.endswith(".png")]) == 6
    for f in figs:
        assert (ROOT / "figures" / f).stat().st_size > 5000
        if f.endswith(".png"):
            assert f.replace(".png", ".webp") in figs


# Numeric locks

def test_audit_counts(summary):
    f = summary["audit"]["facts"]
    assert (f["tests"], f["people"], f["measure_rows"], f["female_tests"], f["tests_under_18"]) == (992, 857, 575087, 149, 145)
    assert (f["age_min"], f["age_max"]) == (10.8, 63.0)
    assert f["people_more_than_one_test"] == 116 and f["max_tests_per_person"] == 5
    assert f["humidity_missing"] == 30 and f["temperature_missing"] == 30
    assert f["gas_tests_all_missing"]["VO2"] == 11 and f["gas_tests_all_missing"]["VE"] == 0


def test_primary_n_and_headline_regenerate(computed, summary):
    S, prim, disc = computed["S"], computed["prim"], computed["disc"]
    assert len(S["primary"]) == summary["primary_sample"]["n_tests"] == 735
    assert S["primary"]["ID"].is_unique and (S["primary"]["Age"] >= 18).all()
    for _, row in prim.iterrows():
        lock = summary["primary"][row["formula"]]
        for k in ["bias_bpm", "mae_bpm", "rmse_bpm", "pct_abs_error_over_10", "bias_ci95_low", "rmse_ci95_low", "pct_ci95_high"]:
            assert row[k] == pytest.approx(lock[k], abs=1e-4), (row["formula"], k)
    for _, row in disc.iterrows():
        assert row["mean_pct_time_discordant"] == pytest.approx(summary["zone_discordance"][row["formula"]]["mean_pct_time_discordant"], abs=1e-4)


def test_headline_numbers_in_readme_and_brief(summary):
    readme = (ROOT / "README.md").read_text()
    brief = (ROOT / "PORTFOLIO_BRIEF.md").read_text()
    for f, m in summary["primary"].items():
        for txt in [f"{m['bias_bpm']:.1f} ({m['bias_ci95_low']:.1f} to {m['bias_ci95_high']:.1f})",
                    f"{m['mae_bpm']:.1f} ({m['mae_ci95_low']:.1f} to {m['mae_ci95_high']:.1f})",
                    f"{m['pct_abs_error_over_10']:.1f}% ({m['pct_ci95_low']:.1f} to {m['pct_ci95_high']:.1f})"]:
            assert txt in readme, (f, txt)
            assert txt in brief, (f, txt)
    for f, z in summary["zone_discordance"].items():
        txt = f"{z['mean_pct_time_discordant']:.1f}% ({z['ci95_low']:.1f} to {z['ci95_high']:.1f})"
        assert txt in readme and txt in brief, (f, txt)
    assert "n = 735" in readme



def test_discussion_cites_verified_dois():
    t = (ROOT / "DISCUSSION.md").read_text()
    for doi in [
        "10.1371/journal.pone.0335842",
        "10.3389/fphys.2021.695950",
        "10.3390/jcm12082884",
        "10.3390/jcm13185562",
        "10.1155/tsm2/2008291",
        "10.5535/arm.21181",
        "10.1016/S0735-1097(00)01054-8",
        "10.1097/mss.0b013e31803349c6",
        "10.13026/7ezk-j442",
    ]:
        assert doi in t, doi
    assert "November 2026" in t
    assert "not computed here" in t
    assert "26.3%" in t and "n = 735" in t
    brief = (ROOT / "PORTFOLIO_BRIEF.md").read_text()
    assert "Búsqueda bibliográfica, noviembre de 2026" in brief
    assert "discussion: { en, es }" in brief
    assert "Qué queda por investigar" in brief


def test_formulas_as_specified():
    assert A.FORMULAS["220 minus age"](40) == 180
    assert A.FORMULAS["Tanaka 2001"](40) == pytest.approx(180.0)
    assert A.FORMULAS["Gellish 2007"](40) == pytest.approx(180.1)


def test_effort_phase_rule_on_synthetic_profile():
    import numpy as np
    from malaga_exercise_lab import phases as P
    t = np.arange(0, 100, 1.0)
    sp = np.r_[np.zeros(5), np.full(15, 5.0), np.linspace(5.5, 15, 60), np.full(20, 5.0)]
    b = P.effort_bounds(t, sp)
    assert b["i_start"] == 20 and b["i_end"] == 79 and b["s0"] == 5.0 and b["vmax"] == 15
