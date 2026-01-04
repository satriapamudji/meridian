"""Tests for app.analysis.market_context module."""

from __future__ import annotations

from datetime import date

import pytest

from app.analysis.market_context import (
    MarketContextRecord,
    RegimeClassification,
    calculate_position_multiplier,
    classify_credit_regime,
    classify_curve_regime,
    classify_dollar_regime,
    classify_regimes,
    classify_volatility_regime,
    format_context_for_llm,
)
from app.ingestion.market_context import MarketSnapshot


class TestVolatilityRegimeClassification:
    """Tests for volatility regime classification based on VIX."""

    def test_none_returns_unknown(self):
        """None VIX value returns unknown."""
        assert classify_volatility_regime(None) == "unknown"

    def test_vix_below_15_is_calm(self):
        """VIX below 15 is calm regime."""
        assert classify_volatility_regime(10) == "calm"
        assert classify_volatility_regime(12.5) == "calm"
        assert classify_volatility_regime(14.99) == "calm"

    def test_vix_15_to_20_is_normal(self):
        """VIX 15-20 is normal regime."""
        assert classify_volatility_regime(15) == "normal"
        assert classify_volatility_regime(17.5) == "normal"
        assert classify_volatility_regime(19.99) == "normal"

    def test_vix_20_to_30_is_elevated(self):
        """VIX 20-30 is elevated regime."""
        assert classify_volatility_regime(20) == "elevated"
        assert classify_volatility_regime(25) == "elevated"
        assert classify_volatility_regime(29.99) == "elevated"

    def test_vix_30_to_40_is_fear(self):
        """VIX 30-40 is fear regime."""
        assert classify_volatility_regime(30) == "fear"
        assert classify_volatility_regime(35) == "fear"
        assert classify_volatility_regime(39.99) == "fear"

    def test_vix_above_40_is_crisis(self):
        """VIX above 40 is crisis regime."""
        assert classify_volatility_regime(40) == "crisis"
        assert classify_volatility_regime(50) == "crisis"
        assert classify_volatility_regime(80) == "crisis"


class TestDollarRegimeClassification:
    """Tests for dollar regime classification based on DXY."""

    def test_none_returns_unknown(self):
        """None DXY value returns unknown."""
        assert classify_dollar_regime(None) == "unknown"

    def test_dxy_below_95_is_weak(self):
        """DXY below 95 is weak dollar regime."""
        assert classify_dollar_regime(90) == "weak"
        assert classify_dollar_regime(95) == "weak"  # 95 and below is weak

    def test_dxy_95_to_105_is_neutral(self):
        """DXY between 95 and 105 (exclusive bounds) is neutral regime."""
        assert classify_dollar_regime(95.01) == "neutral"
        assert classify_dollar_regime(100) == "neutral"
        assert classify_dollar_regime(104.99) == "neutral"

    def test_dxy_above_105_is_strong(self):
        """DXY above 105 is strong dollar regime."""
        assert classify_dollar_regime(105) == "strong"
        assert classify_dollar_regime(110) == "strong"


class TestCurveRegimeClassification:
    """Tests for yield curve regime classification based on 2s10s spread."""

    def test_none_returns_unknown(self):
        """None spread value returns unknown."""
        assert classify_curve_regime(None) == "unknown"

    def test_negative_spread_is_inverted(self):
        """Negative spread is inverted curve."""
        assert classify_curve_regime(-0.5) == "inverted"
        assert classify_curve_regime(-0.01) == "inverted"

    def test_zero_to_025_is_flat(self):
        """0 to 0.25 spread is flat curve."""
        assert classify_curve_regime(0) == "flat"
        assert classify_curve_regime(0.1) == "flat"
        assert classify_curve_regime(0.24) == "flat"

    def test_025_to_1_is_normal(self):
        """0.25 to 1.0 spread is normal curve."""
        assert classify_curve_regime(0.25) == "normal"
        assert classify_curve_regime(0.5) == "normal"
        assert classify_curve_regime(0.99) == "normal"

    def test_above_1_is_steep(self):
        """Spread above 1.0 is steep curve."""
        assert classify_curve_regime(1.0) == "steep"
        assert classify_curve_regime(1.5) == "steep"
        assert classify_curve_regime(2.0) == "steep"


class TestCreditRegimeClassification:
    """Tests for credit regime classification based on HY spread."""

    def test_none_returns_unknown(self):
        """None spread value returns unknown."""
        assert classify_credit_regime(None) == "unknown"

    def test_below_300_is_tight(self):
        """HY spread below 300bps is tight credit."""
        assert classify_credit_regime(200) == "tight"
        assert classify_credit_regime(299) == "tight"

    def test_300_to_400_is_normal(self):
        """HY spread 300-400bps is normal credit."""
        assert classify_credit_regime(300) == "normal"
        assert classify_credit_regime(350) == "normal"
        assert classify_credit_regime(399) == "normal"

    def test_400_to_500_is_wide(self):
        """HY spread 400-500bps is wide credit."""
        assert classify_credit_regime(400) == "wide"
        assert classify_credit_regime(450) == "wide"
        assert classify_credit_regime(499) == "wide"

    def test_500_to_800_is_stressed(self):
        """HY spread 500-800bps is stressed credit."""
        assert classify_credit_regime(500) == "stressed"
        assert classify_credit_regime(650) == "stressed"
        assert classify_credit_regime(799) == "stressed"

    def test_above_800_is_crisis(self):
        """HY spread above 800bps is credit crisis."""
        assert classify_credit_regime(800) == "crisis"
        assert classify_credit_regime(1000) == "crisis"


class TestRegimeClassificationFromSnapshot:
    """Tests for classify_regimes with MarketSnapshot."""

    def test_classify_regimes_with_full_data(self):
        """Classification works with complete snapshot data."""
        snapshot = MarketSnapshot(
            snapshot_date=date(2026, 1, 4),
            yahoo_prices={
                "^VIX": 22.5,
                "DX=F": 102.0,
            },
            fred_values={
                "T10Y2Y": 0.5,
                "BAMLH0A0HYM2": 350,
            },
            calculated_ratios={},
            errors=[],
        )
        regimes = classify_regimes(snapshot)

        assert regimes.volatility_regime == "elevated"
        assert regimes.dollar_regime == "neutral"
        assert regimes.curve_regime == "normal"
        assert regimes.credit_regime == "normal"

    def test_classify_regimes_handles_missing_data(self):
        """Classification returns unknown for missing data."""
        snapshot = MarketSnapshot(
            snapshot_date=date(2026, 1, 4),
            yahoo_prices={},
            fred_values={},
            calculated_ratios={},
            errors=[],
        )
        regimes = classify_regimes(snapshot)

        # All regimes should be unknown when data is missing
        assert regimes.volatility_regime == "unknown"
        assert regimes.dollar_regime == "unknown"
        assert regimes.curve_regime == "unknown"
        assert regimes.credit_regime == "unknown"


class TestPositionMultiplierCalculation:
    """Tests for position sizing multiplier calculation."""

    def test_normal_regimes_full_size(self):
        """Normal volatility and credit allows full position size."""
        regimes = RegimeClassification(
            volatility_regime="normal",
            dollar_regime="neutral",
            curve_regime="normal",
            credit_regime="normal",
        )
        assert calculate_position_multiplier(regimes) == 1.0

    def test_calm_regimes_full_size(self):
        """Calm volatility and tight credit allows full position size."""
        regimes = RegimeClassification(
            volatility_regime="calm",
            dollar_regime="neutral",
            curve_regime="normal",
            credit_regime="tight",
        )
        assert calculate_position_multiplier(regimes) == 1.0

    def test_elevated_volatility_reduces_size(self):
        """Elevated volatility reduces position size to 0.75."""
        regimes = RegimeClassification(
            volatility_regime="elevated",
            dollar_regime="neutral",
            curve_regime="normal",
            credit_regime="normal",
        )
        assert calculate_position_multiplier(regimes) == 0.75

    def test_fear_volatility_reduces_size(self):
        """Fear volatility reduces position size to 0.50."""
        regimes = RegimeClassification(
            volatility_regime="fear",
            dollar_regime="neutral",
            curve_regime="normal",
            credit_regime="normal",
        )
        assert calculate_position_multiplier(regimes) == 0.50

    def test_crisis_volatility_reduces_size(self):
        """Crisis volatility reduces position size to 0.25."""
        regimes = RegimeClassification(
            volatility_regime="crisis",
            dollar_regime="neutral",
            curve_regime="normal",
            credit_regime="normal",
        )
        assert calculate_position_multiplier(regimes) == 0.25

    def test_wide_credit_reduces_size(self):
        """Wide credit reduces position size to 0.75."""
        regimes = RegimeClassification(
            volatility_regime="normal",
            dollar_regime="neutral",
            curve_regime="normal",
            credit_regime="wide",
        )
        assert calculate_position_multiplier(regimes) == 0.75

    def test_stressed_credit_reduces_size(self):
        """Stressed credit reduces position size to 0.50."""
        regimes = RegimeClassification(
            volatility_regime="normal",
            dollar_regime="neutral",
            curve_regime="normal",
            credit_regime="stressed",
        )
        assert calculate_position_multiplier(regimes) == 0.50

    def test_crisis_credit_reduces_size(self):
        """Credit crisis reduces position size to 0.25."""
        regimes = RegimeClassification(
            volatility_regime="normal",
            dollar_regime="neutral",
            curve_regime="normal",
            credit_regime="crisis",
        )
        assert calculate_position_multiplier(regimes) == 0.25

    def test_takes_minimum_of_vol_and_credit(self):
        """Position size is minimum of volatility and credit adjustments."""
        regimes = RegimeClassification(
            volatility_regime="elevated",  # 0.75
            dollar_regime="neutral",
            curve_regime="normal",
            credit_regime="stressed",  # 0.50
        )
        assert calculate_position_multiplier(regimes) == 0.50

        regimes2 = RegimeClassification(
            volatility_regime="fear",  # 0.50
            dollar_regime="neutral",
            curve_regime="normal",
            credit_regime="wide",  # 0.75
        )
        assert calculate_position_multiplier(regimes2) == 0.50

    def test_unknown_regimes_default_to_full_size(self):
        """Unknown regimes default to 1.0 multiplier."""
        regimes = RegimeClassification(
            volatility_regime="unknown",
            dollar_regime="unknown",
            curve_regime="unknown",
            credit_regime="unknown",
        )
        assert calculate_position_multiplier(regimes) == 1.0


class TestRegimeClassificationDataclass:
    """Tests for RegimeClassification dataclass."""

    def test_to_dict_returns_all_regimes(self):
        """to_dict returns all four regime values."""
        regimes = RegimeClassification(
            volatility_regime="elevated",
            dollar_regime="strong",
            curve_regime="inverted",
            credit_regime="wide",
        )
        d = regimes.to_dict()

        assert d["volatility_regime"] == "elevated"
        assert d["dollar_regime"] == "strong"
        assert d["curve_regime"] == "inverted"
        assert d["credit_regime"] == "wide"
        assert len(d) == 4


class TestFormatContextForLLM:
    """Tests for LLM prompt formatting."""

    @pytest.fixture
    def sample_record(self) -> MarketContextRecord:
        """Create a sample market context record."""
        return MarketContextRecord(
            context_date=date(2026, 1, 4),
            volatility_regime="elevated",
            dollar_regime="neutral",
            curve_regime="normal",
            credit_regime="normal",
            vix_level=22.5,
            dxy_level=102.3,
            us10y_level=4.25,
            us2y_level=4.10,
            gold_level=2650.0,
            oil_level=72.5,
            spx_level=5950.0,
            btc_level=98500.0,
            spread_2s10s=0.15,
            hy_spread=350.0,
            gold_silver_ratio=85.5,
            copper_gold_ratio=0.0015,
            vix_term_structure=0.95,
            spy_rsp_ratio=1.08,
            suggested_size_multiplier=0.75,
            raw_prices={},
            raw_fred={},
        )

    def test_format_contains_header(self, sample_record):
        """Format includes header line."""
        output = format_context_for_llm(sample_record)
        assert "=== CURRENT MARKET CONTEXT ===" in output

    def test_format_contains_date(self, sample_record):
        """Format includes context date."""
        output = format_context_for_llm(sample_record)
        assert "Date: 2026-01-04" in output

    def test_format_contains_regimes(self, sample_record):
        """Format includes regime classifications."""
        output = format_context_for_llm(sample_record)
        assert "Volatility: ELEVATED" in output
        assert "Dollar: NEUTRAL" in output
        assert "Yield Curve: NORMAL" in output
        assert "Credit: NORMAL" in output

    def test_format_contains_position_sizing(self, sample_record):
        """Format includes suggested position size."""
        output = format_context_for_llm(sample_record)
        assert "Suggested Position Size: 75%" in output

    def test_format_contains_key_levels(self, sample_record):
        """Format includes key market levels."""
        output = format_context_for_llm(sample_record)
        assert "VIX: 22.50" in output
        assert "DXY: 102.30" in output
        assert "US10Y: 4.25" in output
        assert "Gold: $2650.00" in output
        assert "Oil: $72.50" in output

    def test_format_contains_ratios(self, sample_record):
        """Format includes calculated ratios."""
        output = format_context_for_llm(sample_record)
        assert "Gold/Silver: 85.5" in output
        assert "SPY/RSP:" in output
        assert "narrow (mega-cap led)" in output

    def test_format_handles_none_values(self):
        """Format gracefully handles None values."""
        record = MarketContextRecord(
            context_date=date(2026, 1, 4),
            volatility_regime="unknown",
            dollar_regime="unknown",
            curve_regime="unknown",
            credit_regime="unknown",
            vix_level=None,
            dxy_level=None,
            us10y_level=None,
            us2y_level=None,
            gold_level=None,
            oil_level=None,
            spx_level=None,
            btc_level=None,
            spread_2s10s=None,
            hy_spread=None,
            gold_silver_ratio=None,
            copper_gold_ratio=None,
            vix_term_structure=None,
            spy_rsp_ratio=None,
            suggested_size_multiplier=1.0,
            raw_prices={},
            raw_fred={},
        )
        output = format_context_for_llm(record)

        # Should not raise, should contain header
        assert "=== CURRENT MARKET CONTEXT ===" in output
        # Should not contain None values
        assert "None" not in output

    def test_vix_term_structure_backwardation(self):
        """VIX term structure > 1 shows backwardation label."""
        record = MarketContextRecord(
            context_date=date(2026, 1, 4),
            volatility_regime="fear",
            dollar_regime="neutral",
            curve_regime="normal",
            credit_regime="normal",
            vix_level=35.0,
            dxy_level=None,
            us10y_level=None,
            us2y_level=None,
            gold_level=None,
            oil_level=None,
            spx_level=None,
            btc_level=None,
            spread_2s10s=None,
            hy_spread=None,
            gold_silver_ratio=None,
            copper_gold_ratio=None,
            vix_term_structure=1.15,  # Backwardation
            spy_rsp_ratio=None,
            suggested_size_multiplier=0.5,
            raw_prices={},
            raw_fred={},
        )
        output = format_context_for_llm(record)
        assert "backwardation (panic)" in output

    def test_spy_rsp_healthy_breadth(self):
        """SPY/RSP ratio <= 1.05 shows healthy breadth."""
        record = MarketContextRecord(
            context_date=date(2026, 1, 4),
            volatility_regime="normal",
            dollar_regime="neutral",
            curve_regime="normal",
            credit_regime="normal",
            vix_level=None,
            dxy_level=None,
            us10y_level=None,
            us2y_level=None,
            gold_level=None,
            oil_level=None,
            spx_level=None,
            btc_level=None,
            spread_2s10s=None,
            hy_spread=None,
            gold_silver_ratio=None,
            copper_gold_ratio=None,
            vix_term_structure=None,
            spy_rsp_ratio=1.02,  # Healthy
            suggested_size_multiplier=1.0,
            raw_prices={},
            raw_fred={},
        )
        output = format_context_for_llm(record)
        assert "healthy" in output
