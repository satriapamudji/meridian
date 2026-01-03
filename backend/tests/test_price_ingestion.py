from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
import json

from app.ingestion.prices import PriceBar, build_ratio_series, parse_yahoo_chart

_TIMESTAMP_1 = int(datetime(2026, 2, 1, tzinfo=timezone.utc).timestamp())
_TIMESTAMP_2 = int(datetime(2026, 2, 2, tzinfo=timezone.utc).timestamp())
_TIMESTAMP_3 = int(datetime(2026, 2, 3, tzinfo=timezone.utc).timestamp())

SAMPLE_CHART = json.dumps(
    {
        "chart": {
            "result": [
                {
                    "timestamp": [_TIMESTAMP_1, _TIMESTAMP_2, _TIMESTAMP_3],
                    "indicators": {
                        "quote": [
                            {
                                "open": [100, None, 102],
                                "high": [110, 112, 113],
                                "low": [90, 92, 91],
                                "close": [105, 106, None],
                                "volume": [1000, 1001, 1002],
                            }
                        ],
                        "adjclose": [{"adjclose": [105, 106, None]}],
                    },
                }
            ],
            "error": None,
        }
    }
)


def test_parse_yahoo_chart_filters_bad_rows() -> None:
    bars = parse_yahoo_chart(SAMPLE_CHART, "GC=F")

    assert len(bars) == 2
    assert bars[0].price_date == date(2026, 2, 1)
    assert bars[0].close == Decimal("105")
    assert bars[1].price_date == date(2026, 2, 2)
    assert bars[1].open is None


def test_build_ratio_series_uses_shared_dates() -> None:
    gold_bars = [
        PriceBar(
            symbol="GC=F",
            price_date=date(2026, 2, 1),
            open=None,
            high=None,
            low=None,
            close=Decimal("100"),
            adj_close=None,
            volume=None,
        ),
        PriceBar(
            symbol="GC=F",
            price_date=date(2026, 2, 2),
            open=None,
            high=None,
            low=None,
            close=Decimal("110"),
            adj_close=None,
            volume=None,
        ),
    ]
    silver_bars = [
        PriceBar(
            symbol="SI=F",
            price_date=date(2026, 2, 2),
            open=None,
            high=None,
            low=None,
            close=Decimal("10"),
            adj_close=None,
            volume=None,
        ),
        PriceBar(
            symbol="SI=F",
            price_date=date(2026, 2, 3),
            open=None,
            high=None,
            low=None,
            close=Decimal("11"),
            adj_close=None,
            volume=None,
        ),
    ]

    ratios = build_ratio_series("GC=F", "SI=F", gold_bars, silver_bars)

    assert [entry.price_date for entry in ratios] == [date(2026, 2, 2)]
    assert ratios[0].value == Decimal("11")
