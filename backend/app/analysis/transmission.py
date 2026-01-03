from __future__ import annotations

from typing import Any, Iterable
import re

from app.analysis.significance import normalize_event_type

ALLOWED_STRENGTHS = {"strong", "moderate", "weak", "none"}
STRENGTH_ALIASES = {
    "high": "strong",
    "medium": "moderate",
    "low": "weak",
    "unknown": "none",
}

CRYPTO_ASSET_ALIASES = {
    "bitcoin": "BTC",
    "btc": "BTC",
    "ethereum": "ETH",
    "eth": "ETH",
    "solana": "SOL",
    "sol": "SOL",
    "stablecoin": "stablecoins",
    "stablecoins": "stablecoins",
    "usdt": "USDT",
    "tether": "USDT",
    "usdc": "USDC",
}

LIQUIDITY_TERMS = ("liquidity", "rates", "rate", "yield", "dollar", "tightening", "easing")
RISK_TERMS = ("risk-off", "risk on", "risk-on", "risk aversion", "risk appetite")
SANCTION_TERMS = ("sanction", "capital control", "controls", "restriction")

TOKEN_RE = re.compile(r"[a-z0-9]+")


def default_transmission() -> dict[str, Any]:
    return {"exists": False, "path": "", "strength": "none", "relevant_assets": []}


def normalize_crypto_transmission(payload: dict[str, Any] | None) -> dict[str, Any]:
    data = payload if isinstance(payload, dict) else {}
    exists = data.get("exists")
    normalized_exists = exists is True

    path = data.get("path")
    normalized_path = path.strip() if isinstance(path, str) else ""

    strength = data.get("strength")
    normalized_strength = _normalize_strength(strength)

    assets = normalize_relevant_assets(
        data.get("relevant_assets") or data.get("assets") or []
    )
    if normalized_exists and not assets:
        assets = extract_relevant_assets(normalized_path)

    return {
        "exists": normalized_exists,
        "path": normalized_path,
        "strength": normalized_strength,
        "relevant_assets": assets,
    }


def normalize_relevant_assets(value: object) -> list[str]:
    assets: list[str] = []
    if isinstance(value, str):
        assets = [item.strip() for item in value.split(",") if item.strip()]
    elif isinstance(value, list):
        assets = [item.strip() for item in value if isinstance(item, str) and item.strip()]
    normalized = [_normalize_asset(asset) for asset in assets]
    deduped: list[str] = []
    seen: set[str] = set()
    for asset in normalized:
        if asset not in seen:
            seen.add(asset)
            deduped.append(asset)
    return deduped


def extract_relevant_assets(text: str | None) -> list[str]:
    if not text:
        return []
    tokens = TOKEN_RE.findall(text.lower())
    assets = [_normalize_asset(token) for token in tokens if token in CRYPTO_ASSET_ALIASES]
    deduped: list[str] = []
    seen: set[str] = set()
    for asset in assets:
        if asset not in seen:
            seen.add(asset)
            deduped.append(asset)
    return deduped


def evaluate_transmission(event_text: str | None, event_type: str | None) -> dict[str, Any]:
    text = (event_text or "").lower()
    if not text:
        return default_transmission()

    assets = extract_relevant_assets(text)
    if assets:
        return normalize_crypto_transmission(
            {
                "exists": True,
                "path": "Direct crypto linkage referenced in the event.",
                "strength": "moderate",
                "relevant_assets": assets,
            }
        )

    normalized_event_type = normalize_event_type(event_type)
    if _contains_any(text, LIQUIDITY_TERMS) and normalized_event_type in {
        "monetary_policy",
        "financial_crisis",
    }:
        return normalize_crypto_transmission(
            {
                "exists": True,
                "path": "Liquidity and risk conditions can spill into crypto risk appetite.",
                "strength": "weak",
                "relevant_assets": ["BTC", "ETH"],
            }
        )

    if _contains_any(text, SANCTION_TERMS) and normalized_event_type == "geopolitical":
        return normalize_crypto_transmission(
            {
                "exists": True,
                "path": "Capital controls can raise stablecoin demand in affected regions.",
                "strength": "weak",
                "relevant_assets": ["stablecoins"],
            }
        )

    if _contains_any(text, RISK_TERMS):
        return normalize_crypto_transmission(
            {
                "exists": True,
                "path": "Risk sentiment shifts can influence crypto positioning.",
                "strength": "weak",
                "relevant_assets": ["BTC", "ETH"],
            }
        )

    return default_transmission()


def _normalize_strength(value: object) -> str:
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in ALLOWED_STRENGTHS:
            return normalized
        alias = STRENGTH_ALIASES.get(normalized)
        if alias:
            return alias
    return "none"


def _normalize_asset(value: str) -> str:
    normalized = value.strip().lower()
    return CRYPTO_ASSET_ALIASES.get(normalized, value.strip())


def _contains_any(text: str, terms: Iterable[str]) -> bool:
    return any(term in text for term in terms)
