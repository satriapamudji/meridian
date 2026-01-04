"""Dynamic asset discovery for macro event analysis.

This module discovers relevant tickers/assets based on transmission channels
and event context. It provides both static channel-based discovery and
dynamic web search-based discovery.

The discovery pipeline:
1. Match event to transmission channels (via keywords or event type)
2. Get primary/secondary assets from matched channels
3. Optionally run web searches to discover additional tickers
4. Validate and deduplicate discovered tickers

Usage:
    from app.analysis.asset_discovery import (
        discover_assets_for_event,
        DiscoveryResult,
    )

    result = discover_assets_for_event(
        headline="Russia threatens to cut oil pipeline to Europe",
        event_type="geopolitical",
    )
    print(result.primary_assets)  # ['CL=F', 'BZ=F', ...]
    print(result.channels)  # [OIL_SUPPLY_DISRUPTION, ...]
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

from app.analysis.transmission_channels import (
    ALL_CHANNELS,
    TransmissionChannel,
    get_channels_for_event_type,
    match_channels_by_keywords,
)

logger = logging.getLogger(__name__)


# Common ticker patterns for extraction from text
TICKER_PATTERN = re.compile(
    r"\b([A-Z]{1,5}(?:=[A-Z])?)\b"  # Match tickers like AAPL, CL=F, GC=F
)

# Known non-tickers that match the pattern
NON_TICKERS = frozenset(
    {
        "A",
        "I",
        "AND",
        "THE",
        "FOR",
        "WITH",
        "FROM",
        "THIS",
        "THAT",
        "THEY",
        "ARE",
        "WAS",
        "WERE",
        "BEEN",
        "HAVE",
        "HAS",
        "HAD",
        "DO",
        "DOES",
        "DID",
        "CAN",
        "COULD",
        "WOULD",
        "SHOULD",
        "MAY",
        "MIGHT",
        "MUST",
        "WILL",
        "IS",
        "IT",
        "BE",
        "TO",
        "OF",
        "IN",
        "ON",
        "AT",
        "BY",
        "AS",
        "OR",
        "AN",
        "IF",
        "SO",
        "NO",
        "YES",
        "NOT",
        "BUT",
        "ALL",
        "ANY",
        "NEW",
        "US",
        "UK",
        "EU",
        "FED",
        "ECB",
        "BOJ",
        "BOE",
        "PBOC",
        "OPEC",
        "GDP",
        "CPI",
        "PPI",
        "PMI",
        "NFP",
        "ISM",
        "FOMC",
        "RBI",
        "SNB",
        "CEO",
        "CFO",
        "COO",
        "IPO",
        "ETF",
        "NYSE",
        "NASDAQ",
        "DOW",
        "VS",
        "AM",
        "PM",
        "EST",
        "PST",
        "UTC",
        "GMT",
        "Q1",
        "Q2",
        "Q3",
        "Q4",
        "YTD",
        "YOY",
        "MOM",
        "QOQ",
        "BPS",
        "PCT",
        "MN",
        "BN",
        "TN",
        "MM",
        "K",
    }
)

# Valid ticker suffixes for futures/forex
VALID_SUFFIXES = frozenset({"=F", "=X"})


@dataclass
class DiscoveryResult:
    """Result of asset discovery for an event."""

    channels: list[TransmissionChannel] = field(default_factory=list)
    primary_assets: list[str] = field(default_factory=list)
    secondary_assets: list[str] = field(default_factory=list)
    discovered_assets: list[str] = field(default_factory=list)  # From search
    search_queries_used: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def all_assets(self) -> list[str]:
        """Return all assets in priority order (primary, secondary, discovered)."""
        seen: set[str] = set()
        result: list[str] = []
        for asset in self.primary_assets + self.secondary_assets + self.discovered_assets:
            if asset not in seen:
                seen.add(asset)
                result.append(asset)
        return result

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "channels": [c.name for c in self.channels],
            "channel_types": [c.channel_type.value for c in self.channels],
            "primary_assets": self.primary_assets,
            "secondary_assets": self.secondary_assets,
            "discovered_assets": self.discovered_assets,
            "all_assets": self.all_assets(),
            "search_queries_used": self.search_queries_used,
            "errors": self.errors,
        }


def discover_assets_for_event(
    headline: str,
    event_type: str | None = None,
    full_text: str | None = None,
    max_channels: int = 5,
    include_secondary: bool = True,
) -> DiscoveryResult:
    """
    Discover relevant assets for a macro event.

    This uses a multi-step process:
    1. Match channels by keywords in headline/text
    2. Match channels by event type
    3. Extract assets from matched channels
    4. Deduplicate and prioritize

    Args:
        headline: Event headline
        event_type: Normalized event type (from significance.py)
        full_text: Optional full event text for better matching
        max_channels: Maximum number of channels to match
        include_secondary: Whether to include secondary assets

    Returns:
        DiscoveryResult with matched channels and assets
    """
    result = DiscoveryResult()

    # Step 1: Match channels by keywords
    search_text = f"{headline} {full_text or ''}"
    keyword_matched = match_channels_by_keywords(search_text)

    # Step 2: Match channels by event type
    type_matched: list[TransmissionChannel] = []
    if event_type:
        type_matched = get_channels_for_event_type(event_type)

    # Step 3: Combine and deduplicate channels
    seen_types: set[str] = set()
    combined: list[TransmissionChannel] = []

    # Keyword matches first (more specific)
    for channel in keyword_matched:
        if channel.channel_type.value not in seen_types:
            seen_types.add(channel.channel_type.value)
            combined.append(channel)

    # Then type matches
    for channel in type_matched:
        if channel.channel_type.value not in seen_types:
            seen_types.add(channel.channel_type.value)
            combined.append(channel)

    # Limit to max_channels
    result.channels = combined[:max_channels]

    # Step 4: Extract assets from channels
    primary_seen: set[str] = set()
    secondary_seen: set[str] = set()

    for channel in result.channels:
        for asset in channel.primary_assets:
            if asset not in primary_seen:
                primary_seen.add(asset)
                result.primary_assets.append(asset)

        if include_secondary:
            for asset in channel.secondary_assets:
                if asset not in secondary_seen and asset not in primary_seen:
                    secondary_seen.add(asset)
                    result.secondary_assets.append(asset)

    # Step 5: Collect search queries for potential web search
    for channel in result.channels:
        result.search_queries_used.extend(channel.search_queries)

    return result


def discover_assets_by_channel_type(
    channel_type: str,
    include_secondary: bool = True,
) -> DiscoveryResult:
    """
    Discover assets for a specific channel type.

    Args:
        channel_type: Channel type value (e.g., "oil_supply_disruption")
        include_secondary: Whether to include secondary assets

    Returns:
        DiscoveryResult with the channel and its assets
    """
    result = DiscoveryResult()

    for channel in ALL_CHANNELS:
        if channel.channel_type.value == channel_type:
            result.channels = [channel]
            result.primary_assets = list(channel.primary_assets)
            if include_secondary:
                result.secondary_assets = list(channel.secondary_assets)
            result.search_queries_used = list(channel.search_queries)
            break

    if not result.channels:
        result.errors.append(f"Unknown channel type: {channel_type}")

    return result


def extract_tickers_from_text(text: str) -> list[str]:
    """
    Extract potential ticker symbols from text.

    This is a best-effort extraction that filters out common non-tickers.

    Args:
        text: Text to extract tickers from

    Returns:
        List of potential ticker symbols
    """
    matches = TICKER_PATTERN.findall(text)
    tickers: list[str] = []
    seen: set[str] = set()

    for match in matches:
        upper = match.upper()
        if upper in NON_TICKERS:
            continue
        if upper in seen:
            continue

        # Keep if it's a known pattern (futures, forex)
        if "=" in upper:
            if any(upper.endswith(suffix) for suffix in VALID_SUFFIXES):
                seen.add(upper)
                tickers.append(upper)
            continue

        # Keep if it's 2-5 uppercase letters (likely ticker)
        if 2 <= len(upper) <= 5:
            seen.add(upper)
            tickers.append(upper)

    return tickers


def validate_tickers(tickers: list[str]) -> list[str]:
    """
    Validate a list of tickers by checking format.

    This is a lightweight validation that doesn't hit external APIs.
    For full validation, use the Yahoo Finance API.

    Args:
        tickers: List of potential tickers

    Returns:
        List of tickers that pass format validation
    """
    valid: list[str] = []

    for ticker in tickers:
        # Basic format checks
        if not ticker:
            continue

        # Skip if in non-ticker list
        if ticker.upper() in NON_TICKERS:
            continue

        # Accept futures and forex
        if "=" in ticker:
            if any(ticker.upper().endswith(s) for s in VALID_SUFFIXES):
                valid.append(ticker)
            continue

        # Accept 1-5 letter tickers
        if re.match(r"^[A-Z]{1,5}$", ticker.upper()):
            valid.append(ticker.upper())
            continue

        # Accept tickers with dots (BRK.A, BRK.B)
        if re.match(r"^[A-Z]{1,4}\.[A-Z]$", ticker.upper()):
            valid.append(ticker.upper())
            continue

    return valid


def merge_discovery_results(*results: DiscoveryResult) -> DiscoveryResult:
    """
    Merge multiple discovery results into one.

    Args:
        *results: Discovery results to merge

    Returns:
        Merged DiscoveryResult
    """
    merged = DiscoveryResult()
    channel_seen: set[str] = set()
    primary_seen: set[str] = set()
    secondary_seen: set[str] = set()
    discovered_seen: set[str] = set()
    query_seen: set[str] = set()

    for result in results:
        for channel in result.channels:
            if channel.channel_type.value not in channel_seen:
                channel_seen.add(channel.channel_type.value)
                merged.channels.append(channel)

        for asset in result.primary_assets:
            if asset not in primary_seen:
                primary_seen.add(asset)
                merged.primary_assets.append(asset)

        for asset in result.secondary_assets:
            if asset not in secondary_seen and asset not in primary_seen:
                secondary_seen.add(asset)
                merged.secondary_assets.append(asset)

        for asset in result.discovered_assets:
            if (
                asset not in discovered_seen
                and asset not in primary_seen
                and asset not in secondary_seen
            ):
                discovered_seen.add(asset)
                merged.discovered_assets.append(asset)

        for query in result.search_queries_used:
            if query not in query_seen:
                query_seen.add(query)
                merged.search_queries_used.append(query)

        merged.errors.extend(result.errors)

    return merged


def format_discovery_for_prompt(result: DiscoveryResult) -> str:
    """
    Format discovery result as text for inclusion in LLM prompts.

    Args:
        result: Discovery result to format

    Returns:
        Formatted string for prompt injection
    """
    lines = ["=== DISCOVERED ASSETS ==="]

    if result.channels:
        lines.append("")
        lines.append("TRANSMISSION CHANNELS:")
        for channel in result.channels:
            lines.append(f"  • {channel.name}")
            lines.append(f"    {channel.description[:100]}...")

    if result.primary_assets:
        lines.append("")
        lines.append("PRIMARY ASSETS (high relevance):")
        lines.append(f"  {', '.join(result.primary_assets[:10])}")

    if result.secondary_assets:
        lines.append("")
        lines.append("SECONDARY ASSETS (related exposure):")
        lines.append(f"  {', '.join(result.secondary_assets[:10])}")

    if result.discovered_assets:
        lines.append("")
        lines.append("ADDITIONAL DISCOVERED:")
        lines.append(f"  {', '.join(result.discovered_assets[:10])}")

    lines.append("")
    lines.append("=" * 25)

    return "\n".join(lines)
