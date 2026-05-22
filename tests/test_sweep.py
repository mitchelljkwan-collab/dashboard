"""
Tests for the sweep.py generator script.

sweep.py is gitignored (it contains credentials) but produces dashboard.html.
These tests describe the contract it must satisfy — run them after each sweep
to validate the output is structurally sound.

All tests are automatically skipped when sweep.py is not present.
"""

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).parent.parent
SWEEP_PATH = REPO_ROOT / "sweep.py"
DASHBOARD_PATH = REPO_ROOT / "dashboard.html"


# Skip the entire module when sweep.py doesn't exist
pytestmark = pytest.mark.skipif(
    not SWEEP_PATH.exists(),
    reason="sweep.py not present (gitignored) — skipping sweep output tests",
)


@pytest.fixture(scope="module")
def swept_html(tmp_path_factory):
    """Run sweep.py and capture the HTML it writes to dashboard.html."""
    out_dir = tmp_path_factory.mktemp("sweep_output")
    out_file = out_dir / "dashboard.html"

    result = subprocess.run(
        [sys.executable, str(SWEEP_PATH), "--output", str(out_file)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    if result.returncode != 0:
        pytest.fail(f"sweep.py exited with code {result.returncode}:\n{result.stderr}")

    return BeautifulSoup(out_file.read_text(), "lxml")


REQUIRED_SECTION_LABELS = [
    "Alerts",
    "Today's Focus",
    "Money",
    "Client Projects",
    "This Week",
]


def test_sweep_produces_all_required_sections(swept_html):
    labels = [el.get_text(strip=True) for el in swept_html.select(".section-label")]
    for expected in REQUIRED_SECTION_LABELS:
        assert expected in labels, f"sweep.py output is missing section: '{expected}'"


def test_sweep_produces_at_least_one_client_card(swept_html):
    cards = swept_html.select(".card")
    assert cards, "sweep.py produced no .card elements"


def test_sweep_all_timeline_fills_in_range(swept_html):
    import re
    for fill in swept_html.select(".timeline-fill"):
        style = fill.get("style", "")
        match = re.search(r"width\s*:\s*([\d.]+)%", style)
        assert match, f"Timeline fill missing width in style: {style!r}"
        pct = float(match.group(1))
        assert 0 <= pct <= 100, f"Timeline fill width {pct}% is out of range"


def test_sweep_all_badges_have_recognised_class(swept_html):
    valid = {"badge-active", "badge-waiting", "badge-upcoming", "badge-blocked"}
    for badge in swept_html.select(".badge"):
        classes = set(badge.get("class", []))
        assert classes & valid, (
            f"Badge '{badge.get_text(strip=True)}' has no recognised status class: {classes}"
        )


def test_sweep_header_contains_swept_timestamp(swept_html):
    subtitle = swept_html.select_one("header p")
    assert subtitle, "sweep.py output missing header subtitle"
    text = subtitle.get_text(strip=True)
    assert "swept" in text.lower(), (
        f"Header subtitle does not contain a 'swept' timestamp: {text!r}"
    )


def test_sweep_alert_box_present(swept_html):
    assert swept_html.select_one(".alert-box"), "sweep.py output has no .alert-box"


def test_sweep_focus_box_present(swept_html):
    assert swept_html.select_one(".focus-box"), "sweep.py output has no .focus-box"
