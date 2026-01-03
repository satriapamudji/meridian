from __future__ import annotations

from app.analysis.historical import HistoricalCase, extract_keywords, rank_cases


def test_extract_keywords_filters_stopwords_and_short_tokens() -> None:
    keywords = extract_keywords("The Fed hikes rates in the US and in Europe")

    assert "fed" in keywords
    assert "hikes" in keywords
    assert "rates" in keywords
    assert "the" not in keywords
    assert "us" not in keywords


def test_rank_cases_prefers_event_type_and_keywords() -> None:
    cases = [
        HistoricalCase(
            event_name="Fed Hiking Cycle",
            date_range="2022-2023",
            event_type="monetary_policy",
            significance_score=80,
            structural_drivers=["Rate hikes", "tightening"],
            lessons=["liquidity stress"],
            counter_examples=[],
            traditional_market_reaction=[],
        ),
        HistoricalCase(
            event_name="SVB Banking Crisis",
            date_range="2023",
            event_type="financial_crisis",
            significance_score=90,
            structural_drivers=["bank run", "liquidity"],
            lessons=["liquidity stress"],
            counter_examples=[],
            traditional_market_reaction=[],
        ),
    ]

    matches = rank_cases(
        cases,
        event_text="Fed hikes spark liquidity stress",
        event_type="monetary_policy",
        limit=2,
    )

    assert matches[0].event_name == "Fed Hiking Cycle"
    assert matches[0].match_method == "fallback"


def test_rank_cases_orders_by_significance_when_no_context() -> None:
    cases = [
        HistoricalCase(
            event_name="Lower Impact",
            date_range="2010",
            event_type=None,
            significance_score=40,
        ),
        HistoricalCase(
            event_name="Higher Impact",
            date_range="2020",
            event_type=None,
            significance_score=80,
        ),
    ]

    matches = rank_cases(cases, event_text=None, event_type=None, limit=2)

    assert [match.event_name for match in matches] == ["Higher Impact", "Lower Impact"]
