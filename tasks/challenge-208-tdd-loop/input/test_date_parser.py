"""Test suite for date_parser module — 25 tests, ALL failing (no implementation exists).

The framework must implement date_parser.py to make these pass.
Uses ONLY the Python standard library.
"""
import pytest
from datetime import datetime, timezone, timedelta, date


def get_parse_date():
    """Import parse_date from date_parser module."""
    from date_parser import parse_date
    return parse_date


@pytest.fixture
def parse():
    return get_parse_date()


# =============================================================================
# ISO 8601 formats (5 tests)
# =============================================================================

def test_iso_date_only(parse):
    """Parse ISO date: 2026-03-26"""
    result = parse("2026-03-26")
    assert result.year == 2026
    assert result.month == 3
    assert result.day == 26


def test_iso_datetime(parse):
    """Parse ISO datetime: 2026-03-26T14:30:00"""
    result = parse("2026-03-26T14:30:00")
    assert result.year == 2026
    assert result.month == 3
    assert result.day == 26
    assert result.hour == 14
    assert result.minute == 30
    assert result.second == 0


def test_iso_datetime_utc(parse):
    """Parse ISO datetime with Z suffix: 2026-03-26T14:30:00Z"""
    result = parse("2026-03-26T14:30:00Z")
    assert result.year == 2026
    assert result.hour == 14
    assert result.tzinfo is not None


def test_iso_datetime_offset(parse):
    """Parse ISO datetime with offset: 2026-03-26T14:30:00+02:00"""
    result = parse("2026-03-26T14:30:00+02:00")
    assert result.year == 2026
    assert result.hour == 14
    assert result.tzinfo is not None
    assert result.utcoffset() == timedelta(hours=2)


def test_iso_datetime_negative_offset(parse):
    """Parse ISO datetime with negative offset: 2026-03-26T12:00:00-05:00"""
    result = parse("2026-03-26T12:00:00-05:00")
    assert result.hour == 12
    assert result.tzinfo is not None
    assert result.utcoffset() == timedelta(hours=-5)


# =============================================================================
# Relative dates (6 tests)
# =============================================================================

def test_today(parse):
    """Parse 'today' — should return today's date."""
    result = parse("today")
    today = date.today()
    assert result.year == today.year
    assert result.month == today.month
    assert result.day == today.day


def test_yesterday(parse):
    """Parse 'yesterday'."""
    result = parse("yesterday")
    expected = date.today() - timedelta(days=1)
    assert result.year == expected.year
    assert result.month == expected.month
    assert result.day == expected.day


def test_tomorrow(parse):
    """Parse 'tomorrow'."""
    result = parse("tomorrow")
    expected = date.today() + timedelta(days=1)
    assert result.year == expected.year
    assert result.month == expected.month
    assert result.day == expected.day


def test_n_days_ago(parse):
    """Parse '3 days ago'."""
    result = parse("3 days ago")
    expected = date.today() - timedelta(days=3)
    assert result.year == expected.year
    assert result.month == expected.month
    assert result.day == expected.day


def test_next_week(parse):
    """Parse 'next week' — should return 7 days from now."""
    result = parse("next week")
    expected = date.today() + timedelta(weeks=1)
    assert result.year == expected.year
    assert result.month == expected.month
    assert result.day == expected.day


def test_last_month(parse):
    """Parse 'last month' — should return same day, previous month."""
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
    """Parse 'March 26, 2026'."""
    result = parse("March 26, 2026")
    assert result.year == 2026
    assert result.month == 3
    assert result.day == 26


def test_day_abbrev_month_year(parse):
    """Parse '26 Mar 2026'."""
    result = parse("26 Mar 2026")
    assert result.year == 2026
    assert result.month == 3
    assert result.day == 26


def test_us_date_format(parse):
    """Parse '03/26/2026' (US format MM/DD/YYYY)."""
    result = parse("03/26/2026")
    assert result.year == 2026
    assert result.month == 3
    assert result.day == 26


def test_european_date_format(parse):
    """Parse '26.03.2026' (European format DD.MM.YYYY)."""
    result = parse("26.03.2026")
    assert result.year == 2026
    assert result.month == 3
    assert result.day == 26


# =============================================================================
# Edge cases (6 tests)
# =============================================================================

def test_leap_year_valid(parse):
    """Parse leap year date: 2024-02-29."""
    result = parse("2024-02-29")
    assert result.year == 2024
    assert result.month == 2
    assert result.day == 29


def test_end_of_month(parse):
    """Parse end of month: 2026-01-31."""
    result = parse("2026-01-31")
    assert result.year == 2026
    assert result.month == 1
    assert result.day == 31


def test_invalid_date_raises(parse):
    """Invalid date 2026-02-30 should raise ValueError."""
    with pytest.raises(ValueError):
        parse("2026-02-30")


def test_empty_string_raises(parse):
    """Empty string should raise ValueError."""
    with pytest.raises(ValueError):
        parse("")


def test_garbage_input_raises(parse):
    """Garbage input should raise ValueError."""
    with pytest.raises(ValueError):
        parse("not a date at all xyz")


# =============================================================================
# Additional relative/natural combos (4 tests)
# =============================================================================

def test_n_days_ago_large(parse):
    """Parse '30 days ago'."""
    result = parse("30 days ago")
    expected = date.today() - timedelta(days=30)
    assert result.year == expected.year
    assert result.month == expected.month
    assert result.day == expected.day


def test_january_first(parse):
    """Parse 'January 1, 2026'."""
    result = parse("January 1, 2026")
    assert result.year == 2026
    assert result.month == 1
    assert result.day == 1


def test_december_31(parse):
    """Parse '31 Dec 2025'."""
    result = parse("31 Dec 2025")
    assert result.year == 2025
    assert result.month == 12
    assert result.day == 31


def test_return_type_is_datetime(parse):
    """parse_date always returns a datetime object, not date."""
    result = parse("2026-03-26")
    assert isinstance(result, datetime)


def test_non_leap_year_feb_29_raises(parse):
    """Non-leap year Feb 29 should raise ValueError."""
    with pytest.raises(ValueError):
        parse("2025-02-29")
