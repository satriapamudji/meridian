# Data

Seed data used for cold start and local development.

## Layout (planned)
- `metals/`: metals knowledge base (YAML/JSON).
- `cases/`: historical case library (YAML/JSON).
- `calendar/`: optional seed events or mappings.

## Metals seed format

Each JSON file in `data/metals/` represents one metal with required categories.

```
{
  "metal": "gold",
  "categories": {
    "supply_chain": {},
    "use_cases": {},
    "patterns": [],
    "correlations": {},
    "actors": {}
  }
}
```

## Historical cases seed format

Each JSON file in `data/cases/` is a single historical case aligned to Appendix B:

```
{
  "event_name": "2020 COVID Shock",
  "date_range": "2020-02 to 2020-08",
  "event_type": "pandemic",
  "significance_score": 90,
  "structural_drivers": ["..."],
  "metal_impacts": {
    "gold": {"direction": "up", "magnitude": "+25%", "driver": "..."},
    "silver": {"direction": "up", "magnitude": "+100%", "driver": "..."},
    "copper": {"direction": "down_then_up", "magnitude": "...", "driver": "..."}
  },
  "traditional_market_reaction": ["..."],
  "crypto_reaction": ["..."],
  "crypto_transmission": {"exists": true, "path": "...", "strength": "moderate"},
  "time_delays": ["..."],
  "lessons": ["..."],
  "counter_examples": ["..."]
}
```

Embeddings are optional; when ready, apply them via the CLI in `backend/app/db/embeddings.py`
using a JSON list of `{event_name, date_range, embedding}` entries.

## Calendar seed format

Each JSON file in `data/calendar/` contains a list of upcoming events.

```
{
  "source": "sample",
  "events": [
    {
      "event_name": "US CPI (YoY)",
      "event_date": "2026-02-05T13:30:00Z",
      "region": "US",
      "impact_level": "high",
      "expected": "3.1%",
      "actual": "3.0%",
      "previous": "3.2%"
    }
  ]
}
```
