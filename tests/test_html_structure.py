"""
Structural tests for dashboard.html.

These guard against sections being accidentally deleted, cards losing
required child elements, invalid badge/status classes, and timeline
percentages going out of range.
"""

import re
import pytest


REQUIRED_SECTION_LABELS = [
    "Alerts",
    "Today's Focus",
    "Money",
    "Client Projects",
    "This Week",
]

VALID_BADGE_CLASSES = {
    "badge-active",
    "badge-waiting",
    "badge-upcoming",
    "badge-blocked",
}

VALID_CALENDAR_EVENT_CLASSES = {"urgent", "now", "normal"}


# ---------------------------------------------------------------------------
# Section labels
# ---------------------------------------------------------------------------

def test_all_required_sections_present(soup):
    labels = [el.get_text(strip=True) for el in soup.select(".section-label")]
    for expected in REQUIRED_SECTION_LABELS:
        assert expected in labels, f"Missing section label: '{expected}'"


# ---------------------------------------------------------------------------
# Cards
# ---------------------------------------------------------------------------

def test_every_card_has_a_header(soup):
    for card in soup.select(".card"):
        assert card.select_one(".card-header"), (
            f"Card '{card.select_one('.card-title') and card.select_one('.card-title').get_text(strip=True)}' "
            "is missing .card-header"
        )


def test_every_card_has_a_title(soup):
    for card in soup.select(".card"):
        title = card.select_one(".card-title")
        assert title and title.get_text(strip=True), (
            "Found a .card without a non-empty .card-title"
        )


def test_every_card_has_at_least_one_row(soup):
    for card in soup.select(".card"):
        rows = card.select(".row")
        title = card.select_one(".card-title")
        name = title.get_text(strip=True) if title else "(unknown)"
        assert rows, f"Card '{name}' has no .row elements"


def test_every_row_has_a_label_and_value(soup):
    for row in soup.select(".row"):
        assert row.select_one(".row-label"), "A .row is missing .row-label"
        assert row.select_one(".row-value"), "A .row is missing .row-value"


# ---------------------------------------------------------------------------
# Badges
# ---------------------------------------------------------------------------

def test_all_badges_have_valid_class(soup):
    for badge in soup.select(".badge"):
        badge_classes = set(badge.get("class", []))
        valid = badge_classes & VALID_BADGE_CLASSES
        assert valid, (
            f"Badge '{badge.get_text(strip=True)}' has no recognised status class. "
            f"Classes: {badge_classes}. Expected one of: {VALID_BADGE_CLASSES}"
        )


def test_badges_have_non_empty_text(soup):
    for badge in soup.select(".badge"):
        assert badge.get_text(strip=True), "Found a .badge with no text content"


# ---------------------------------------------------------------------------
# Timeline bars
# ---------------------------------------------------------------------------

def _parse_width_percent(style: str) -> float:
    match = re.search(r"width\s*:\s*([\d.]+)%", style)
    assert match, f"Could not parse width from style: {style!r}"
    return float(match.group(1))


def test_timeline_fills_are_within_range(soup):
    for fill in soup.select(".timeline-fill"):
        style = fill.get("style", "")
        pct = _parse_width_percent(style)
        assert 0 <= pct <= 100, f"Timeline fill width {pct}% is outside 0–100%"


def test_timeline_meta_has_two_spans(soup):
    for meta in soup.select(".timeline-meta"):
        spans = meta.select("span")
        assert len(spans) == 2, (
            f".timeline-meta should have exactly 2 spans, found {len(spans)}"
        )


# ---------------------------------------------------------------------------
# Alerts
# ---------------------------------------------------------------------------

def test_alert_box_exists(soup):
    assert soup.select_one(".alert-box"), "No .alert-box found on the dashboard"


def test_alert_box_has_a_heading(soup):
    alert = soup.select_one(".alert-box")
    h3 = alert.select_one("h3")
    assert h3 and h3.get_text(strip=True), ".alert-box is missing a non-empty h3"


def test_alert_items_have_non_empty_text(soup):
    alert = soup.select_one(".alert-box")
    items = alert.select(".focus-item")
    assert items, ".alert-box contains no .focus-item elements"
    for item in items:
        assert item.get_text(strip=True), "An alert .focus-item has no text content"


# ---------------------------------------------------------------------------
# Focus box
# ---------------------------------------------------------------------------

def test_focus_box_exists(soup):
    assert soup.select_one(".focus-box"), "No .focus-box found on the dashboard"


def test_focus_box_has_items(soup):
    focus = soup.select_one(".focus-box")
    items = focus.select(".focus-item")
    assert items, ".focus-box contains no .focus-item elements"


def test_focus_items_have_non_empty_text(soup):
    for item in soup.select(".focus-box .focus-item"):
        assert item.get_text(strip=True), "A .focus-item in .focus-box has no text"


# ---------------------------------------------------------------------------
# Calendar
# ---------------------------------------------------------------------------

def test_calendar_section_exists(soup):
    assert soup.select_one(".cal-section"), "No .cal-section found on the dashboard"


def test_calendar_has_at_least_one_day(soup):
    days = soup.select(".cal-day")
    assert days, "No .cal-day elements found in .cal-section"


def test_every_calendar_day_has_a_label(soup):
    for day in soup.select(".cal-day"):
        label = day.select_one(".cal-day-label")
        assert label and label.get_text(strip=True), (
            "A .cal-day is missing a non-empty .cal-day-label"
        )


def test_every_calendar_event_has_required_children(soup):
    for event in soup.select(".cal-event"):
        assert event.select_one(".cal-time"), "A .cal-event is missing .cal-time"
        assert event.select_one(".cal-title"), "A .cal-event is missing .cal-title"


def test_calendar_events_have_valid_type_class(soup):
    for event in soup.select(".cal-event"):
        event_classes = set(event.get("class", []))
        valid = event_classes & VALID_CALENDAR_EVENT_CLASSES
        assert valid, (
            f"Calendar event '{event.select_one('.cal-title') and event.select_one('.cal-title').get_text(strip=True)}' "
            f"has no recognised type class. Classes: {event_classes}. "
            f"Expected one of: {VALID_CALENDAR_EVENT_CLASSES}"
        )


# ---------------------------------------------------------------------------
# Page shell
# ---------------------------------------------------------------------------

def test_page_has_title(soup):
    title = soup.select_one("title")
    assert title and title.get_text(strip=True), "<title> is missing or empty"


def test_header_exists_with_h1(soup):
    h1 = soup.select_one("header h1")
    assert h1 and h1.get_text(strip=True), "header h1 is missing or empty"


def test_header_subtitle_exists(soup):
    subtitle = soup.select_one("header p")
    assert subtitle and subtitle.get_text(strip=True), "header p (subtitle) is missing or empty"
