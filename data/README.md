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
