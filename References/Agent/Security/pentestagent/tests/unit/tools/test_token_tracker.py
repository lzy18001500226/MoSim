"""Tests for pentestagent.tools.token_tracker."""

import json
from datetime import date
from pathlib import Path

import pytest

import pentestagent.tools.token_tracker as tt


@pytest.fixture(autouse=True)
def isolated_tracker(tmp_path):
    data_file = tmp_path / "token_usage.json"
    tt.set_data_file(data_file)
    tt._data = {
        "daily_usage": 0,
        "last_reset_date": date.today().isoformat(),
        "last_input_tokens": 0,
        "last_output_tokens": 0,
        "last_total_tokens": 0,
    }
    yield data_file
    tt._custom_data_file = None


class TestRecordUsageSync:
    def test_records_input_and_output(self, isolated_tracker):
        tt.record_usage_sync(100, 50)
        stats = tt.get_stats_sync()
        assert stats["last_input_tokens"] == 100
        assert stats["last_output_tokens"] == 50
        assert stats["last_total_tokens"] == 150

    def test_daily_usage_accumulates(self, isolated_tracker):
        tt.record_usage_sync(100, 50)
        tt.record_usage_sync(200, 100)
        stats = tt.get_stats_sync()
        assert stats["daily_usage"] == 450

    def test_persists_to_file(self, isolated_tracker):
        tt.record_usage_sync(10, 20)
        data = json.loads(isolated_tracker.read_text())
        assert data["last_input_tokens"] == 10
        assert data["last_output_tokens"] == 20

    def test_handles_zero_tokens(self, isolated_tracker):
        tt.record_usage_sync(0, 0)
        stats = tt.get_stats_sync()
        assert stats["last_total_tokens"] == 0

    def test_handles_none_tokens(self, isolated_tracker):
        tt.record_usage_sync(None, None)
        stats = tt.get_stats_sync()
        assert stats["last_total_tokens"] == 0

    def test_handles_string_tokens_gracefully(self, isolated_tracker):
        tt.record_usage_sync("abc", "def")
        stats = tt.get_stats_sync()
        assert stats["last_total_tokens"] == 0


class TestDailyReset:
    def test_same_date_no_reset(self, isolated_tracker):
        today = date.today().isoformat()
        tt._data["last_reset_date"] = today
        tt._data["daily_usage"] = 999
        tt.record_usage_sync(10, 10)
        stats = tt.get_stats_sync()
        assert stats["daily_usage"] == 999 + 20

    def test_different_date_triggers_reset(self, isolated_tracker):
        tt._data["last_reset_date"] = "2000-01-01"
        tt._data["daily_usage"] = 999
        tt.record_usage_sync(10, 10)
        stats = tt.get_stats_sync()
        assert stats["daily_usage"] == 20

    def test_reset_updates_date(self, isolated_tracker):
        tt._data["last_reset_date"] = "2000-01-01"
        tt.record_usage_sync(0, 0)
        stats = tt.get_stats_sync()
        assert stats["last_reset_date"] == date.today().isoformat()


class TestGetStatsSync:
    def test_returns_dict(self, isolated_tracker):
        stats = tt.get_stats_sync()
        assert isinstance(stats, dict)

    def test_has_required_keys(self, isolated_tracker):
        stats = tt.get_stats_sync()
        for key in ("daily_usage", "last_reset_date", "last_input_tokens",
                    "last_output_tokens", "last_total_tokens", "current_date"):
            assert key in stats

    def test_current_date_is_today(self, isolated_tracker):
        stats = tt.get_stats_sync()
        assert stats["current_date"] == date.today().isoformat()

    def test_daily_usage_non_negative(self, isolated_tracker):
        stats = tt.get_stats_sync()
        assert stats["daily_usage"] >= 0

    def test_reset_pending_flag(self, isolated_tracker):
        tt._data["last_reset_date"] = "2000-01-01"
        stats = tt.get_stats_sync()
        assert stats["reset_pending"] is True

    def test_no_reset_pending_same_day(self, isolated_tracker):
        stats = tt.get_stats_sync()
        assert stats["reset_pending"] is False


class TestCorruptFileHandling:
    def test_corrupt_json_resets_to_defaults(self, isolated_tracker):
        isolated_tracker.write_text("{invalid json}", encoding="utf-8")
        tt.record_usage_sync(5, 5)
        stats = tt.get_stats_sync()
        assert stats["last_total_tokens"] == 10
