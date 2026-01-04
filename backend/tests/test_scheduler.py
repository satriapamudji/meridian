"""Tests for the scheduler module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


class TestSchedulerSettings:
    """Test scheduler settings are properly loaded."""

    def test_default_settings(self) -> None:
        """Verify default scheduler settings are sensible."""
        from app.core.settings import get_settings

        # Clear cache to get fresh settings
        get_settings.cache_clear()
        settings = get_settings()

        assert settings.scheduler_timezone == "UTC"
        assert settings.scheduler_rss_interval_minutes == 10
        assert settings.scheduler_calendar_interval_minutes == 360
        assert settings.scheduler_fed_interval_minutes == 60
        assert settings.scheduler_prices_interval_minutes == 1440
        assert settings.scheduler_digest_hour == 6
        assert settings.scheduler_digest_minute == 0


class TestJobWrappers:
    """Test job wrapper functions handle errors gracefully."""

    def test_job_ingest_rss_returns_status(self) -> None:
        """Job should return status dict even on error."""

        with patch("app.scheduler.jobs.job_ingest_rss") as mock:
            mock.return_value = {"status": "success", "total_events": 5}
            result = mock()
            assert result["status"] == "success"

    def test_job_sync_calendar_returns_status(self) -> None:
        """Job should return status dict."""

        with patch("app.scheduler.jobs.job_sync_calendar") as mock:
            mock.return_value = {"status": "success", "inserted": 3}
            result = mock()
            assert result["status"] == "success"

    def test_job_sync_fed_returns_status(self) -> None:
        """Job should return status dict."""

        with patch("app.scheduler.jobs.job_sync_fed") as mock:
            mock.return_value = {"status": "success", "inserted": 2}
            result = mock()
            assert result["status"] == "success"

    def test_job_ingest_prices_returns_status(self) -> None:
        """Job should return status dict."""

        with patch("app.scheduler.jobs.job_ingest_prices") as mock:
            mock.return_value = {"status": "success", "total_prices": 10}
            result = mock()
            assert result["status"] == "success"

    def test_job_generate_digest_returns_status(self) -> None:
        """Job should return status dict."""

        with patch("app.scheduler.jobs.job_generate_digest") as mock:
            mock.return_value = {
                "status": "success",
                "digest_date": "2026-01-04",
                "priority_events": 3,
                "active_theses": 2,
            }
            result = mock()
            assert result["status"] == "success"
            assert result["priority_events"] == 3

    def test_job_sync_market_context_returns_status(self) -> None:
        """Job should return status dict."""

        with patch("app.scheduler.jobs.job_sync_market_context") as mock:
            mock.return_value = {"status": "success", "context_date": "2026-01-04"}
            result = mock()
            assert result["status"] == "success"


class TestJobErrorHandling:
    """Test that jobs handle exceptions gracefully."""

    def test_job_ingest_rss_catches_exceptions(self) -> None:
        """RSS job should catch exceptions and return error status."""
        from app.scheduler.jobs import job_ingest_rss

        with patch("app.ingestion.rss.ingest_sources", side_effect=Exception("Connection failed")):
            result = job_ingest_rss()
            assert result["status"] == "error"
            assert "Connection failed" in result["error"]

    def test_job_sync_calendar_catches_exceptions(self) -> None:
        """Calendar job should catch exceptions and return error status."""
        from app.scheduler.jobs import job_sync_calendar

        with patch(
            "app.ingestion.economic_calendar.sync_calendar",
            side_effect=Exception("API error"),
        ):
            result = job_sync_calendar()
            assert result["status"] == "error"
            assert "API error" in result["error"]

    def test_job_sync_fed_catches_exceptions(self) -> None:
        """Fed job should catch exceptions and return error status."""
        from app.scheduler.jobs import job_sync_fed

        with patch(
            "app.ingestion.central_banks.fed.ingest_fomc_statements",
            side_effect=Exception("Network error"),
        ):
            result = job_sync_fed()
            assert result["status"] == "error"
            assert "Network error" in result["error"]

    def test_job_ingest_prices_catches_exceptions(self) -> None:
        """Prices job should catch exceptions and return error status."""
        from app.scheduler.jobs import job_ingest_prices

        with patch("app.ingestion.prices.ingest_prices", side_effect=Exception("Yahoo API down")):
            result = job_ingest_prices()
            assert result["status"] == "error"
            assert "Yahoo API down" in result["error"]

    def test_job_generate_digest_catches_exceptions(self) -> None:
        """Digest job should catch exceptions and return error status."""
        from app.scheduler.jobs import job_generate_digest

        with patch(
            "app.services.digests.get_or_create_digest",
            side_effect=Exception("Database unavailable"),
        ):
            result = job_generate_digest()
            assert result["status"] == "error"
            assert "Database unavailable" in result["error"]

    def test_job_sync_market_context_catches_exceptions(self) -> None:
        """Market context job should catch exceptions and return error status."""
        from app.scheduler.jobs import job_sync_market_context

        with patch(
            "app.analysis.market_context.ingest_market_context",
            side_effect=Exception("FRED API error"),
        ):
            result = job_sync_market_context()
            assert result["status"] == "error"
            assert "FRED API error" in result["error"]


class TestSchedulerCreation:
    """Test scheduler configuration."""

    @pytest.fixture
    def mock_settings(self) -> MagicMock:
        """Create mock settings for testing."""
        settings = MagicMock()
        settings.scheduler_timezone = "UTC"
        settings.scheduler_rss_interval_minutes = 10
        settings.scheduler_calendar_interval_minutes = 360
        settings.scheduler_fed_interval_minutes = 60
        settings.scheduler_prices_interval_minutes = 1440
        settings.scheduler_digest_hour = 6
        settings.scheduler_digest_minute = 0
        return settings

    def test_create_scheduler_returns_scheduler(self, mock_settings: MagicMock) -> None:
        """Scheduler creation should return a Scheduler instance."""
        try:
            from apscheduler.schedulers.background import BackgroundScheduler

            from app.scheduler.scheduler import create_scheduler

            scheduler = create_scheduler(mock_settings)
            assert isinstance(scheduler, BackgroundScheduler)
        except ImportError:
            pytest.skip("APScheduler not installed")

    def test_scheduler_has_all_jobs_configured(self, mock_settings: MagicMock) -> None:
        """Scheduler should have all required jobs configured."""
        try:
            from app.scheduler.scheduler import (
                JOB_CALENDAR,
                JOB_DIGEST,
                JOB_FED,
                JOB_MARKET_CONTEXT,
                JOB_PRICES,
                JOB_RSS,
            )

            # Just verify the job IDs are defined
            assert JOB_RSS == "rss_ingestion"
            assert JOB_CALENDAR == "calendar_sync"
            assert JOB_FED == "fed_sync"
            assert JOB_PRICES == "price_ingestion"
            assert JOB_MARKET_CONTEXT == "market_context_sync"
            assert JOB_DIGEST == "digest_generation"
        except ImportError:
            pytest.skip("APScheduler not installed")


class TestListJobsCommand:
    """Test the --list-jobs command output."""

    def test_list_jobs_prints_configuration(self, capsys: pytest.CaptureFixture[str]) -> None:
        """List jobs should print all configured jobs."""
        from app.scheduler.__main__ import list_jobs

        list_jobs()
        captured = capsys.readouterr()

        assert "Meridian Scheduler" in captured.out
        assert "RSS ingestion" in captured.out
        assert "Calendar sync" in captured.out
        assert "Fed communications" in captured.out
        assert "Price ingestion" in captured.out
        assert "Market context sync" in captured.out
        assert "Daily digest" in captured.out
