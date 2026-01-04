"""Tests for app.analysis.time_horizons module."""

from app.analysis.conviction import ConvictionLevel
from app.analysis.time_horizons import (
    DEFAULT_INSTRUMENTS,
    ENTRY_APPROACHES,
    HORIZON_LABELS,
    LONG_TERM_INSTRUMENTS,
    MEDIUM_TERM_INSTRUMENTS,
    RISK_MANAGEMENT,
    SHORT_TERM_INSTRUMENTS,
    HorizonAnalysis,
    HorizonRecommendation,
    TradeDirection,
    TradeHorizon,
    analyze_time_horizons,
    build_rationale,
    determine_direction_from_behavior,
    determine_magnitude_from_behavior,
    format_horizons_for_prompt,
    get_instruments_for_horizon,
)


class TestTradeHorizonEnum:
    """Tests for TradeHorizon enum values."""

    def test_short_term_value(self) -> None:
        assert TradeHorizon.SHORT_TERM.value == "short_term"

    def test_medium_term_value(self) -> None:
        assert TradeHorizon.MEDIUM_TERM.value == "medium_term"

    def test_long_term_value(self) -> None:
        assert TradeHorizon.LONG_TERM.value == "long_term"


class TestTradeDirectionEnum:
    """Tests for TradeDirection enum values."""

    def test_long_value(self) -> None:
        assert TradeDirection.LONG.value == "long"

    def test_short_value(self) -> None:
        assert TradeDirection.SHORT.value == "short"

    def test_neutral_value(self) -> None:
        assert TradeDirection.NEUTRAL.value == "neutral"


class TestHorizonRecommendation:
    """Tests for HorizonRecommendation dataclass."""

    def test_to_dict_includes_all_fields(self) -> None:
        rec = HorizonRecommendation(
            horizon=TradeHorizon.SHORT_TERM,
            instruments=["CL=F", "USO"],
            direction=TradeDirection.LONG,
            rationale="Oil supply disruption expected",
            conviction=ConvictionLevel.HIGH,
            entry_approach="Enter immediately",
            risk_management="Stop at -5%",
            expected_magnitude="+15% in oil futures",
        )
        result = rec.to_dict()

        assert result["horizon"] == "short_term"
        assert result["horizon_label"] == HORIZON_LABELS[TradeHorizon.SHORT_TERM]
        assert result["instruments"] == ["CL=F", "USO"]
        assert result["direction"] == "long"
        assert result["conviction"] == "high"
        assert "entry_approach" in result
        assert "risk_management" in result

    def test_default_values(self) -> None:
        rec = HorizonRecommendation(horizon=TradeHorizon.MEDIUM_TERM)
        assert rec.instruments == []
        assert rec.direction == TradeDirection.NEUTRAL
        assert rec.conviction == ConvictionLevel.INSUFFICIENT


class TestHorizonAnalysis:
    """Tests for HorizonAnalysis dataclass."""

    def test_all_recommendations_returns_non_none(self) -> None:
        short = HorizonRecommendation(horizon=TradeHorizon.SHORT_TERM)
        long = HorizonRecommendation(horizon=TradeHorizon.LONG_TERM)
        analysis = HorizonAnalysis(short_term=short, long_term=long)

        recs = analysis.all_recommendations()
        assert len(recs) == 2
        assert short in recs
        assert long in recs

    def test_to_dict_includes_all_horizons(self) -> None:
        analysis = HorizonAnalysis(
            event_summary="Test event",
            short_term=HorizonRecommendation(horizon=TradeHorizon.SHORT_TERM),
            warnings=["Low conviction"],
        )
        result = analysis.to_dict()

        assert result["event_summary"] == "Test event"
        assert result["short_term"] is not None
        assert result["medium_term"] is None
        assert result["long_term"] is None
        assert "Low conviction" in result["warnings"]


class TestInstrumentMapping:
    """Tests for instrument mapping by horizon and channel."""

    def test_short_term_has_oil_instruments(self) -> None:
        instruments = SHORT_TERM_INSTRUMENTS.get("oil_supply_disruption", [])
        assert "CL=F" in instruments
        assert "BZ=F" in instruments

    def test_medium_term_has_sector_etfs(self) -> None:
        instruments = MEDIUM_TERM_INSTRUMENTS.get("oil_supply_disruption", [])
        assert "XLE" in instruments
        assert "OXY" in instruments or "CVX" in instruments

    def test_long_term_has_equity_positions(self) -> None:
        instruments = LONG_TERM_INSTRUMENTS.get("oil_supply_disruption", [])
        assert "XOM" in instruments or "CVX" in instruments

    def test_all_channels_have_instruments(self) -> None:
        """Verify all channels defined in short-term have instruments."""
        for channel in SHORT_TERM_INSTRUMENTS.keys():
            assert len(SHORT_TERM_INSTRUMENTS[channel]) > 0

    def test_default_instruments_defined_for_all_horizons(self) -> None:
        for horizon in TradeHorizon:
            assert horizon in DEFAULT_INSTRUMENTS
            assert len(DEFAULT_INSTRUMENTS[horizon]) > 0


class TestGetInstrumentsForHorizon:
    """Tests for get_instruments_for_horizon function."""

    def test_returns_instruments_for_known_channel(self) -> None:
        instruments = get_instruments_for_horizon(
            TradeHorizon.SHORT_TERM,
            ["oil_supply_disruption"],
        )
        assert len(instruments) > 0
        assert "CL=F" in instruments

    def test_respects_max_instruments(self) -> None:
        instruments = get_instruments_for_horizon(
            TradeHorizon.SHORT_TERM,
            ["oil_supply_disruption"],
            max_instruments=3,
        )
        assert len(instruments) <= 3

    def test_returns_defaults_for_unknown_channel(self) -> None:
        instruments = get_instruments_for_horizon(
            TradeHorizon.SHORT_TERM,
            ["unknown_channel"],
        )
        assert len(instruments) > 0  # Falls back to defaults

    def test_combines_multiple_channels(self) -> None:
        instruments = get_instruments_for_horizon(
            TradeHorizon.SHORT_TERM,
            ["oil_supply_disruption", "risk_off_flight"],
        )
        # Should have instruments from both channels
        assert len(instruments) > len(SHORT_TERM_INSTRUMENTS.get("oil_supply_disruption", []))


class TestDetermineDirectionFromBehavior:
    """Tests for determine_direction_from_behavior function."""

    def test_oil_up_returns_long_for_commodity_channel(self) -> None:
        behavior = {"short_term_1_5d": {"oil_direction": "up"}}
        direction = determine_direction_from_behavior(
            TradeHorizon.SHORT_TERM,
            behavior,
            ["oil_supply_disruption"],
        )
        assert direction == TradeDirection.LONG

    def test_oil_down_returns_short_for_commodity_channel(self) -> None:
        behavior = {"long_term_6m_plus": {"oil_direction": "down"}}
        direction = determine_direction_from_behavior(
            TradeHorizon.LONG_TERM,
            behavior,
            ["oil_supply_disruption"],
        )
        assert direction == TradeDirection.SHORT

    def test_bearish_channel_defaults_to_short(self) -> None:
        direction = determine_direction_from_behavior(
            TradeHorizon.SHORT_TERM,
            None,
            ["risk_off_flight"],
        )
        assert direction == TradeDirection.SHORT

    def test_bullish_channel_defaults_to_long(self) -> None:
        direction = determine_direction_from_behavior(
            TradeHorizon.SHORT_TERM,
            None,
            ["risk_on_rally"],
        )
        assert direction == TradeDirection.LONG


class TestDetermineMagnitudeFromBehavior:
    """Tests for determine_magnitude_from_behavior function."""

    def test_uses_behavior_data_when_available(self) -> None:
        behavior = {"short_term_1_5d": {"oil_magnitude_pct": 15, "gold_magnitude_pct": 2}}
        magnitude = determine_magnitude_from_behavior(
            TradeHorizon.SHORT_TERM,
            behavior,
            None,
        )
        assert "Oil" in magnitude
        assert "15" in magnitude

    def test_falls_back_to_quantitative_impacts(self) -> None:
        impacts = {"peak_price_impact_pct": 50}
        magnitude = determine_magnitude_from_behavior(
            TradeHorizon.MEDIUM_TERM,
            None,
            impacts,
        )
        assert "50" in magnitude

    def test_returns_default_when_no_data(self) -> None:
        magnitude = determine_magnitude_from_behavior(
            TradeHorizon.SHORT_TERM,
            None,
            None,
        )
        assert "5-15%" in magnitude or "primary instruments" in magnitude.lower()


class TestBuildRationale:
    """Tests for build_rationale function."""

    def test_includes_horizon_context(self) -> None:
        rationale = build_rationale(TradeHorizon.SHORT_TERM, [], None)
        assert "Immediate" in rationale or "reaction" in rationale.lower()

    def test_includes_channel_names(self) -> None:
        rationale = build_rationale(
            TradeHorizon.SHORT_TERM,
            ["oil_supply_disruption"],
            None,
        )
        assert "Oil Supply Disruption" in rationale or "Channels:" in rationale

    def test_includes_primary_driver_from_behavior(self) -> None:
        behavior = {"short_term_1_5d": {"primary_driver": "Supply shock headlines"}}
        rationale = build_rationale(
            TradeHorizon.SHORT_TERM,
            ["oil_supply_disruption"],
            behavior,
        )
        assert "Supply shock headlines" in rationale


class TestAnalyzeTimeHorizons:
    """Tests for analyze_time_horizons main function."""

    def test_returns_analysis_with_all_horizons(self) -> None:
        analysis = analyze_time_horizons(
            event_headline="Russia threatens oil pipeline cutoff",
            channel_types=["oil_supply_disruption"],
        )
        assert analysis.short_term is not None
        assert analysis.medium_term is not None
        assert analysis.long_term is not None

    def test_includes_event_summary(self) -> None:
        headline = "Fed announces rate hike"
        analysis = analyze_time_horizons(
            event_headline=headline,
            channel_types=["fed_hawkish"],
        )
        assert analysis.event_summary == headline

    def test_uses_historical_behavior_for_direction(self) -> None:
        historical_cases = [
            {
                "event_name": "Venezuela Strike",
                "time_horizon_behavior": {
                    "short_term_1_5d": {"oil_direction": "up", "oil_magnitude_pct": 15},
                    "medium_term_2_8w": {"oil_direction": "up", "oil_magnitude_pct": 50},
                    "long_term_6m_plus": {"oil_direction": "down", "oil_magnitude_pct": -30},
                },
            }
        ]
        analysis = analyze_time_horizons(
            event_headline="Oil supply disruption",
            channel_types=["oil_supply_disruption"],
            historical_cases=historical_cases,
        )
        # Short/medium should be LONG, long-term should be SHORT
        assert analysis.short_term.direction == TradeDirection.LONG
        assert analysis.medium_term.direction == TradeDirection.LONG
        assert analysis.long_term.direction == TradeDirection.SHORT

    def test_adds_warnings_for_missing_data(self) -> None:
        analysis = analyze_time_horizons(
            event_headline="Unknown event",
            channel_types=[],
        )
        assert any("historical" in w.lower() for w in analysis.warnings)
        assert any("quantitative" in w.lower() for w in analysis.warnings)

    def test_adds_warning_for_low_conviction(self) -> None:
        analysis = analyze_time_horizons(
            event_headline="Test event",
            conviction_level=ConvictionLevel.LOW,
        )
        assert any("conviction" in w.lower() for w in analysis.warnings)


class TestFormatHorizonsForPrompt:
    """Tests for format_horizons_for_prompt function."""

    def test_includes_header(self) -> None:
        analysis = analyze_time_horizons(
            event_headline="Test event",
            channel_types=["oil_supply_disruption"],
        )
        formatted = format_horizons_for_prompt(analysis)
        assert "TIME HORIZON ANALYSIS" in formatted

    def test_includes_all_horizon_sections(self) -> None:
        analysis = analyze_time_horizons(
            event_headline="Test event",
            channel_types=["oil_supply_disruption"],
        )
        formatted = format_horizons_for_prompt(analysis)
        assert "Short-Term" in formatted
        assert "Medium-Term" in formatted
        assert "Long-Term" in formatted

    def test_includes_direction_and_instruments(self) -> None:
        analysis = analyze_time_horizons(
            event_headline="Test event",
            channel_types=["oil_supply_disruption"],
        )
        formatted = format_horizons_for_prompt(analysis)
        assert "Direction:" in formatted
        assert "Instruments:" in formatted

    def test_includes_warnings(self) -> None:
        analysis = analyze_time_horizons(
            event_headline="Test event",
            channel_types=[],
        )
        formatted = format_horizons_for_prompt(analysis)
        assert "WARNINGS:" in formatted


class TestEntryAndRiskApproaches:
    """Tests for entry and risk management guidance."""

    def test_entry_approaches_defined_for_all_horizons(self) -> None:
        for horizon in TradeHorizon:
            assert horizon in ENTRY_APPROACHES
            assert len(ENTRY_APPROACHES[horizon]) > 0

    def test_risk_management_defined_for_all_horizons(self) -> None:
        for horizon in TradeHorizon:
            assert horizon in RISK_MANAGEMENT
            assert len(RISK_MANAGEMENT[horizon]) > 0

    def test_short_term_has_tight_stops(self) -> None:
        risk = RISK_MANAGEMENT[TradeHorizon.SHORT_TERM]
        assert any("3-5%" in r or "tight" in r.lower() for r in risk)

    def test_long_term_has_wider_stops(self) -> None:
        risk = RISK_MANAGEMENT[TradeHorizon.LONG_TERM]
        assert any("15-20%" in r or "wide" in r.lower() for r in risk)
