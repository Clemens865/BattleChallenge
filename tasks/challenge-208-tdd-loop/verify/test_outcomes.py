"""Outcome-based tests for challenge-208: TDD Loop.

Verifies that date_parser.py implements parse_date correctly.
These 25 tests mirror the input test file but are self-contained.
"""
import importlib.util
import os
import sys
import pytest
from datetime import datetime, timezone, timedelta, date

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", os.getcwd())


def _load_parse_date():
    path = os.path.join(OUTPUT_DIR, "date_parser.py")
    if not os.path.exists(path):
        pytest.skip(f"date_parser.py not found in {OUTPUT_DIR}")
    if OUTPUT_DIR not in sys.path:
        sys.path.insert(0, OUTPUT_DIR)
    spec = importlib.util.spec_from_file_location("date_parser", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.parse_date


@pytest.fixture
def parse():
    return _load_parse_date()


# =============================================================================
# ISO 8601 formats (5 tests)
# =============================================================================

def test_iso_date_only(parse):
    result = parse("2026-03-26")
    assert result.year == 2026
    assert result.month == 3
    assert result.day == 26


def test_iso_datetime(parse):
    result = parse("2026-03-26T14:30:00")
    assert result.year == 2026
    assert result.month == 3
    assert result.day == 26
    assert result.hour == 14
    assert result.minute == 30
    assert result.second == 0


def test_iso_datetime_utc(parse):
    result = parse("2026-03-26T14:30:00Z")
    assert result.year == 2026
    assert result.hour == 14
    assert result.tzinfo is not None


def test_iso_datetime_offset(parse):
    result = parse("2026-03-26T14:30:00+02:00")
    assert result.year == 2026
    assert result.hour == 14
    assert result.tzinfo is not None
    assert result.utcoffset() == timedelta(hours=2)


def test_iso_datetime_negative_offset(parse):
    result = parse("2026-03-26T12:00:00-05:00")
    assert result.hour == 12
    assert result.tzinfo is not None
    assert result.utcoffset() == timedelta(hours=-5)


# =============================================================================
# Relative dates (6 tests)
# =============================================================================

def test_today(parse):
    result = parse("today")
    today = date.today()
    assert result.year == today.year
    assert result.month == today.month
    assert result.day == today.day


def test_yesterday(parse):
    result = parse("yesterday")
    expected = date.today() - timedelta(days=1)
    assert result.year == expected.year
    assert result.month == expected.month
    assert result.day == expected.day


def test_tomorrow(parse):
    result = parse("tomorrow")
    expected = date.today() + timedelta(days=1)
    assert result.year == expected.year
    assert result.month == expected.month
    assert result.day == expected.day


def test_n_days_ago(parse):
    result = parse("3 days ago")
    expected = date.today() - timedelta(days=3)
    assert result.year == expected.year
    assert result.month == expected.month
    assert result.day == expected.day


def test_next_week(parse):
    result = parse("next week")
    expected = date.today() + timedelta(weeks=1)
    assert result.year == expected.year
    assert result.month == expected.month
    assert result.day == expected.day


def test_last_month(parse):
    result = parse("last month")
    today = date.today()
    if today.month == 1:
        expected_month = 12
        expected_year = today.year - 1
    else:
        expected_month = today.month - 1
        expected_year = today.year
    assert result.month == expected_month
    assert result.year == expected_year


# =============================================================================
# Natural language date formats (4 tests)
# =============================================================================

def test_month_day_year(parse):
    result = parse("March 26, 2026")
    assert result.year == 2026
    assert result.month == 3
    assert result.day == 26


def test_day_abbrev_month_year(parse):
    result = parse("26 Mar 2026")
    assert result.year == 2026
    assert result.month == 3
    assert result.day == 26


def test_us_date_format(parse):
    result = parse("03/26/2026")
    assert result.year == 2026
    assert result.month == 3
    assert result.day == 26


def test_european_date_format(parse):
    result = parse("26.03.2026")
    assert result.year == 2026
    assert result.month == 3
    assert result.day == 26


# =============================================================================
# Edge cases (6 tests)
# =============================================================================

def test_leap_year_valid(parse):
    result = parse("2024-02-29")
    assert result.year == 2024
    assert result.month == 2
    assert result.day == 29


def test_end_of_month(parse):
    result = parse("2026-01-31")
    assert result.year == 2026
    assert result.month == 1
    assert result.day == 31


def test_invalid_date_raises(parse):
    with pytest.raises(ValueError):
        parse("2026-02-30")


def test_empty_string_raises(parse):
    with pytest.raises(ValueError):
        parse("")


def test_garbage_input_raises(parse):
    with pytest.raises(ValueError):
        parse("not a date at all xyz")


# =============================================================================
# Additional relative/natural combos (4 tests)
# =============================================================================

def test_n_days_ago_large(parse):
    result = parse("30 days ago")
    expected = date.today() - timedelta(days=30)
    assert result.year == expected.year
    assert result.month == expected.month
    assert result.day == expected.day


def test_january_first(parse):
    result = parse("January 1, 2026")
    assert result.year == 2026
    assert result.month == 1
    assert result.day == 1


def test_december_31(parse):
    result = parse("31 Dec 2025")
    assert result.year == 2025
    assert result.month == 12
    assert result.day == 31


def test_return_type_is_datetime(parse):
    result = parse("2026-03-26")
    assert isinstance(result, datetime)


def test_non_leap_year_feb_29_raises(parse):
    with pytest.raises(ValueError):
        parse("2025-02-29")
