"""Tests for app.data.core_watchlist module."""

from __future__ import annotations

import pytest

from app.data.core_watchlist import (
    ALL_INSTRUMENTS,
    BREADTH,
    CALCULATED_RATIOS,
    COMMODITIES,
    CREDIT,
    CREDIT_REGIME_THRESHOLDS,
    CURVE_REGIME_THRESHOLDS,
    FX,
    POSITION_SIZE_MULTIPLIERS,
    RATES,
    VITAL_SIGNS,
    VOLATILITY,
    VOLATILITY_REGIME_THRESHOLDS,
    AlertThresholds,
    Category,
    DataSource,
    get_all_by_category,
    get_fred_series,
    get_instrument_by_name,
    get_instrument_by_symbol,
    get_yahoo_symbols,
)


class TestWatchlistInstrument:
    """Tests for WatchlistInstrument dataclass."""

    def test_instrument_is_frozen(self):
        """Verify instruments are immutable."""
        inst = VITAL_SIGNS[0]
        with pytest.raises(AttributeError):
            inst.name = "changed"  # type: ignore[misc]

    def test_all_instruments_have_required_fields(self):
        """Verify all instruments have name, symbol, source, category, interpretation."""
        for inst in ALL_INSTRUMENTS:
            assert inst.name, f"Instrument missing name: {inst}"
            assert inst.symbol, f"Instrument missing symbol: {inst}"
            assert isinstance(inst.source, DataSource), f"Invalid source: {inst.source}"
            assert isinstance(inst.category, Category), f"Invalid category: {inst.category}"
            assert inst.interpretation, f"Instrument missing interpretation: {inst.name}"


class TestAlertThresholds:
    """Tests for AlertThresholds threshold detection."""

    def test_get_alert_level_no_thresholds(self):
        """Returns None when no thresholds defined."""
        alert = AlertThresholds(levels={})
        assert alert.get_alert_level(50) is None

    def test_get_alert_level_below_all(self):
        """Returns None when value is below all thresholds."""
        alert = AlertThresholds(levels={"elevated": 20, "fear": 30, "crisis": 40})
        assert alert.get_alert_level(15) is None

    def test_get_alert_level_single_breach(self):
        """Returns the breached level when one threshold is crossed."""
        alert = AlertThresholds(levels={"elevated": 20, "fear": 30, "crisis": 40})
        assert alert.get_alert_level(25) == "elevated"

    def test_get_alert_level_multiple_breaches(self):
        """Returns the highest breached level when multiple thresholds are crossed."""
        alert = AlertThresholds(levels={"elevated": 20, "fear": 30, "crisis": 40})
        assert alert.get_alert_level(35) == "fear"
        assert alert.get_alert_level(50) == "crisis"

    def test_get_alert_level_exact_threshold(self):
        """Returns the level when value exactly matches threshold."""
        alert = AlertThresholds(levels={"elevated": 20, "fear": 30})
        assert alert.get_alert_level(20) == "elevated"
        assert alert.get_alert_level(30) == "fear"

    def test_vix_thresholds_from_vital_signs(self):
        """VIX instrument has proper alert thresholds."""
        vix = get_instrument_by_name("VIX")
        assert vix is not None
        assert vix.alert_thresholds is not None

        # Test actual VIX regime thresholds
        assert vix.alert_thresholds.get_alert_level(12) is None  # Below calm
        assert vix.alert_thresholds.get_alert_level(17) == "normal"
        assert vix.alert_thresholds.get_alert_level(25) == "elevated"
        assert vix.alert_thresholds.get_alert_level(32) == "fear"
        assert vix.alert_thresholds.get_alert_level(45) == "crisis"


class TestCategoryGrouping:
    """Tests for instrument category grouping."""

    def test_all_categories_represented(self):
        """All Category enum values are represented in instruments."""
        grouped = get_all_by_category()
        for category in Category:
            assert category in grouped, f"Category {category} has no instruments"
            assert len(grouped[category]) > 0

    def test_category_tuples_match_all_instruments(self):
        """All tier tuples combine to ALL_INSTRUMENTS."""
        tier_count = (
            len(VITAL_SIGNS)
            + len(VOLATILITY)
            + len(RATES)
            + len(FX)
            + len(CREDIT)
            + len(COMMODITIES)
            + len(BREADTH)
        )
        assert len(ALL_INSTRUMENTS) == tier_count

    def test_vital_signs_count(self):
        """Vital signs tier has 8 instruments."""
        assert len(VITAL_SIGNS) == 8

    def test_no_duplicate_symbols(self):
        """No duplicate symbols in ALL_INSTRUMENTS."""
        symbols = [inst.symbol for inst in ALL_INSTRUMENTS]
        assert len(symbols) == len(set(symbols)), "Duplicate symbols found"

    def test_no_duplicate_names(self):
        """No duplicate names in ALL_INSTRUMENTS."""
        names = [inst.name for inst in ALL_INSTRUMENTS]
        assert len(names) == len(set(names)), "Duplicate names found"


class TestSymbolLists:
    """Tests for get_yahoo_symbols and get_fred_series."""

    def test_get_yahoo_symbols_not_empty(self):
        """Yahoo symbols list is not empty."""
        symbols = get_yahoo_symbols()
        assert len(symbols) > 0

    def test_get_yahoo_symbols_excludes_fred(self):
        """Yahoo symbols list excludes FRED series."""
        symbols = get_yahoo_symbols()
        fred_series = get_fred_series()
        for fred_id in fred_series:
            assert fred_id not in symbols, f"FRED series {fred_id} in Yahoo list"

    def test_get_fred_series_not_empty(self):
        """FRED series list is not empty."""
        series = get_fred_series()
        assert len(series) > 0

    def test_get_fred_series_expected_ids(self):
        """FRED series contains expected IDs."""
        series = get_fred_series()
        expected = {"T10Y2Y", "DGS2", "DGS10", "DGS30", "T5YIE", "BAMLH0A0HYM2"}
        for expected_id in expected:
            assert expected_id in series, f"Expected FRED series {expected_id} not found"

    def test_yahoo_symbols_sorted(self):
        """Yahoo symbols are sorted."""
        symbols = get_yahoo_symbols()
        assert symbols == sorted(symbols)

    def test_fred_series_sorted(self):
        """FRED series are sorted."""
        series = get_fred_series()
        assert series == sorted(series)

    def test_yahoo_symbols_includes_ratio_components(self):
        """Yahoo symbols include ratio numerator/denominator symbols."""
        symbols = get_yahoo_symbols()
        # Check some key ratio components
        assert "GC=F" in symbols  # Gold for gold/silver ratio
        assert "SI=F" in symbols  # Silver for gold/silver ratio
        assert "^VIX" in symbols  # VIX for VIX/VIX3M ratio
        assert "SPY" in symbols  # SPY for SPY/RSP ratio
        assert "RSP" in symbols  # RSP for SPY/RSP ratio


class TestCalculatedRatios:
    """Tests for calculated ratio definitions."""

    def test_calculated_ratios_not_empty(self):
        """Calculated ratios list is not empty."""
        assert len(CALCULATED_RATIOS) > 0

    def test_calculated_ratios_have_unique_names(self):
        """Calculated ratios have unique names."""
        names = [r.name for r in CALCULATED_RATIOS]
        assert len(names) == len(set(names)), "Duplicate ratio names found"

    def test_calculated_ratios_have_interpretations(self):
        """All calculated ratios have interpretations."""
        for ratio in CALCULATED_RATIOS:
            assert ratio.interpretation, f"Ratio {ratio.name} missing interpretation"

    def test_expected_ratios_defined(self):
        """Expected ratios are defined."""
        ratio_names = {r.name for r in CALCULATED_RATIOS}
        expected = {
            "gold_silver_ratio",
            "copper_gold_ratio",
            "vix_term_structure",
            "spy_rsp_ratio",
        }
        for name in expected:
            assert name in ratio_names, f"Expected ratio {name} not found"


class TestInstrumentLookup:
    """Tests for instrument lookup functions."""

    def test_get_instrument_by_symbol_found(self):
        """Can find instrument by symbol."""
        inst = get_instrument_by_symbol("^VIX")
        assert inst is not None
        assert inst.name == "VIX"

    def test_get_instrument_by_symbol_not_found(self):
        """Returns None for unknown symbol."""
        inst = get_instrument_by_symbol("UNKNOWN")
        assert inst is None

    def test_get_instrument_by_name_found(self):
        """Can find instrument by name."""
        inst = get_instrument_by_name("Gold")
        assert inst is not None
        assert inst.symbol == "GC=F"

    def test_get_instrument_by_name_not_found(self):
        """Returns None for unknown name."""
        inst = get_instrument_by_name("Unknown Instrument")
        assert inst is None


class TestRegimeThresholds:
    """Tests for regime threshold definitions."""

    def test_volatility_regime_thresholds_complete(self):
        """Volatility regime has all expected levels."""
        expected = {"crisis", "fear", "elevated", "normal", "calm"}
        assert set(VOLATILITY_REGIME_THRESHOLDS.keys()) == expected

    def test_volatility_regime_thresholds_descending(self):
        """Volatility thresholds are in descending order."""
        thresholds = [
            VOLATILITY_REGIME_THRESHOLDS["crisis"]["vix_min"],
            VOLATILITY_REGIME_THRESHOLDS["fear"]["vix_min"],
            VOLATILITY_REGIME_THRESHOLDS["elevated"]["vix_min"],
            VOLATILITY_REGIME_THRESHOLDS["normal"]["vix_min"],
            VOLATILITY_REGIME_THRESHOLDS["calm"]["vix_min"],
        ]
        assert thresholds == sorted(thresholds, reverse=True)

    def test_curve_regime_thresholds_complete(self):
        """Curve regime has all expected levels."""
        expected = {"steep", "normal", "flat", "inverted"}
        assert set(CURVE_REGIME_THRESHOLDS.keys()) == expected

    def test_credit_regime_thresholds_complete(self):
        """Credit regime has all expected levels."""
        expected = {"crisis", "stressed", "wide", "normal", "tight"}
        assert set(CREDIT_REGIME_THRESHOLDS.keys()) == expected


class TestPositionSizeMultipliers:
    """Tests for position sizing multiplier definitions."""

    def test_volatility_multipliers_complete(self):
        """Volatility multipliers cover all regimes."""
        expected = {"crisis", "fear", "elevated", "normal", "calm"}
        assert set(POSITION_SIZE_MULTIPLIERS["volatility"].keys()) == expected

    def test_credit_multipliers_complete(self):
        """Credit multipliers cover all regimes."""
        expected = {"crisis", "stressed", "wide", "normal", "tight"}
        assert set(POSITION_SIZE_MULTIPLIERS["credit"].keys()) == expected

    def test_multipliers_in_valid_range(self):
        """All multipliers are between 0.25 and 1.0."""
        for regime_type, multipliers in POSITION_SIZE_MULTIPLIERS.items():
            for regime, value in multipliers.items():
                assert 0.25 <= value <= 1.0, (
                    f"Multiplier {regime_type}/{regime} = {value} out of range"
                )

    def test_crisis_multipliers_are_minimum(self):
        """Crisis regimes have minimum (0.25) multipliers."""
        assert POSITION_SIZE_MULTIPLIERS["volatility"]["crisis"] == 0.25
        assert POSITION_SIZE_MULTIPLIERS["credit"]["crisis"] == 0.25

    def test_calm_normal_multipliers_are_one(self):
        """Calm/normal regimes have full (1.0) multipliers."""
        assert POSITION_SIZE_MULTIPLIERS["volatility"]["calm"] == 1.0
        assert POSITION_SIZE_MULTIPLIERS["volatility"]["normal"] == 1.0
        assert POSITION_SIZE_MULTIPLIERS["credit"]["tight"] == 1.0
        assert POSITION_SIZE_MULTIPLIERS["credit"]["normal"] == 1.0
