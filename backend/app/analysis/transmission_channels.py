"""Transmission channel definitions for macro event analysis.

This module defines the causal pathways through which macro events transmit
to tradeable assets. Each channel type represents a specific mechanism:

1. COMMODITY SUPPLY: Supply disruptions affecting physical commodity prices
2. CURRENCY/FX: Dollar strength, carry trades, EM currency impacts
3. RATES/LIQUIDITY: Central bank policy, yield curve, credit conditions
4. RISK SENTIMENT: Risk-on/off flows, flight to safety
5. SANCTIONS/CONTROLS: Capital controls, trade restrictions, sanction impacts
6. INFLATION: CPI, PPI, wage pressures, inflation expectations

Each channel includes:
- Primary and secondary affected assets
- Search queries for discovering related tickers
- Typical magnitude and time horizon guidance

Usage:
    from app.analysis.transmission_channels import (
        get_channel_by_type,
        get_channels_for_event_type,
        TransmissionChannel,
    )

    channel = get_channel_by_type("oil_supply_disruption")
    assets = channel.primary_assets + channel.secondary_assets
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ChannelType(Enum):
    """Types of transmission channels."""

    # Commodity supply channels
    OIL_SUPPLY_DISRUPTION = "oil_supply_disruption"
    OIL_DEMAND_SHOCK = "oil_demand_shock"
    NATURAL_GAS_SUPPLY = "natural_gas_supply"
    METALS_SUPPLY = "metals_supply"
    AGRICULTURAL_SUPPLY = "agricultural_supply"

    # Currency/FX channels
    DOLLAR_STRENGTH = "dollar_strength"
    DOLLAR_WEAKNESS = "dollar_weakness"
    EM_CURRENCY_STRESS = "em_currency_stress"
    CARRY_TRADE_UNWIND = "carry_trade_unwind"
    YUAN_DEVALUATION = "yuan_devaluation"

    # Rates/Liquidity channels
    FED_HAWKISH = "fed_hawkish"
    FED_DOVISH = "fed_dovish"
    YIELD_CURVE_INVERSION = "yield_curve_inversion"
    CREDIT_TIGHTENING = "credit_tightening"
    LIQUIDITY_CRISIS = "liquidity_crisis"

    # Risk sentiment channels
    RISK_OFF_FLIGHT = "risk_off_flight"
    RISK_ON_RALLY = "risk_on_rally"
    VIX_SPIKE = "vix_spike"

    # Sanctions/Controls channels
    TRADE_SANCTIONS = "trade_sanctions"
    CAPITAL_CONTROLS = "capital_controls"
    EXPORT_RESTRICTIONS = "export_restrictions"

    # Inflation channels
    INFLATION_SPIKE = "inflation_spike"
    DEFLATION_RISK = "deflation_risk"
    WAGE_PRESSURE = "wage_pressure"


class TimeHorizon(Enum):
    """Expected time horizon for channel effects."""

    IMMEDIATE = "immediate"  # 1-5 days
    SHORT_TERM = "short_term"  # 2-8 weeks
    MEDIUM_TERM = "medium_term"  # 2-6 months
    LONG_TERM = "long_term"  # 6+ months


@dataclass(frozen=True)
class TransmissionChannel:
    """Definition of a macro-to-asset transmission channel."""

    channel_type: ChannelType
    name: str
    description: str
    primary_assets: tuple[str, ...]
    secondary_assets: tuple[str, ...] = ()
    search_queries: tuple[str, ...] = ()
    typical_magnitude: str = ""  # e.g., "5-15% move in primary assets"
    time_horizon: TimeHorizon = TimeHorizon.SHORT_TERM
    keywords: tuple[str, ...] = ()  # For matching events to channels

    def all_assets(self) -> list[str]:
        """Return all assets (primary + secondary)."""
        return list(self.primary_assets) + list(self.secondary_assets)


# =============================================================================
# COMMODITY SUPPLY CHANNELS
# =============================================================================

OIL_SUPPLY_DISRUPTION = TransmissionChannel(
    channel_type=ChannelType.OIL_SUPPLY_DISRUPTION,
    name="Oil Supply Disruption",
    description=(
        "Physical supply disruption from production outages, pipeline issues, "
        "OPEC cuts, or geopolitical events affecting oil-producing regions."
    ),
    primary_assets=("CL=F", "BZ=F", "USO", "XLE"),
    secondary_assets=("OXY", "CVX", "XOM", "SLB", "HAL", "DVN", "PXD"),
    search_queries=(
        "oil stocks affected by supply disruption",
        "oil E&P companies Middle East exposure",
        "oil tanker stocks sanctions",
        "refinery stocks supply shortage",
    ),
    typical_magnitude="$5-20/barrel move; 10-30% in E&P stocks",
    time_horizon=TimeHorizon.IMMEDIATE,
    keywords=("oil", "crude", "opec", "pipeline", "production cut", "supply disruption"),
)

OIL_DEMAND_SHOCK = TransmissionChannel(
    channel_type=ChannelType.OIL_DEMAND_SHOCK,
    name="Oil Demand Shock",
    description=(
        "Demand-driven oil price move from economic slowdown, lockdowns, "
        "or sudden demand recovery. Affects refining margins differently than supply."
    ),
    primary_assets=("CL=F", "BZ=F", "XLE", "VDE"),
    secondary_assets=("PSX", "VLO", "MPC", "DAL", "UAL", "LUV"),
    search_queries=(
        "airline stocks oil price correlation",
        "refinery stocks demand shock",
        "transportation stocks fuel costs",
    ),
    typical_magnitude="$10-40/barrel move; airlines move inverse 2-3x oil",
    time_horizon=TimeHorizon.SHORT_TERM,
    keywords=("oil demand", "gasoline demand", "jet fuel", "refining", "lockdown"),
)

NATURAL_GAS_SUPPLY = TransmissionChannel(
    channel_type=ChannelType.NATURAL_GAS_SUPPLY,
    name="Natural Gas Supply",
    description=(
        "Natural gas supply disruption from pipeline issues, LNG terminal problems, "
        "or geopolitical events affecting gas-producing/transit regions."
    ),
    primary_assets=("NG=F", "UNG", "LNG", "GLNG"),
    secondary_assets=("EQT", "RRC", "AR", "SWN", "TELL", "NEXT"),
    search_queries=(
        "natural gas stocks Europe exposure",
        "LNG shipping stocks",
        "gas utility stocks price spike",
    ),
    typical_magnitude="20-50% in gas futures; 15-40% in producers",
    time_horizon=TimeHorizon.IMMEDIATE,
    keywords=("natural gas", "lng", "pipeline", "nord stream", "gazprom"),
)

METALS_SUPPLY = TransmissionChannel(
    channel_type=ChannelType.METALS_SUPPLY,
    name="Metals Supply Disruption",
    description=(
        "Supply disruption in industrial or precious metals from mine closures, "
        "export bans, or logistics issues. Includes copper, aluminum, nickel, rare earths."
    ),
    primary_assets=("HG=F", "GC=F", "SI=F", "COPX", "CPER"),
    secondary_assets=("FCX", "SCCO", "TECK", "AA", "NEM", "GOLD", "WPM"),
    search_queries=(
        "copper mining stocks supply disruption",
        "rare earth stocks China export",
        "nickel stocks Indonesia ban",
        "aluminum stocks sanctions",
    ),
    typical_magnitude="10-25% in futures; 15-40% in miners",
    time_horizon=TimeHorizon.SHORT_TERM,
    keywords=("copper", "aluminum", "nickel", "rare earth", "mining", "export ban"),
)

AGRICULTURAL_SUPPLY = TransmissionChannel(
    channel_type=ChannelType.AGRICULTURAL_SUPPLY,
    name="Agricultural Supply Disruption",
    description=(
        "Supply disruption in agricultural commodities from weather, export bans, "
        "or conflict affecting major producing regions."
    ),
    primary_assets=("ZW=F", "ZC=F", "ZS=F", "DBA"),
    secondary_assets=("ADM", "BG", "CTVA", "MOS", "NTR", "CF"),
    search_queries=(
        "grain stocks Ukraine exports",
        "fertilizer stocks sanctions",
        "agricultural stocks drought",
    ),
    typical_magnitude="15-40% in grains; 20-50% in fertilizers",
    time_horizon=TimeHorizon.SHORT_TERM,
    keywords=("wheat", "corn", "grain", "fertilizer", "drought", "export ban"),
)


# =============================================================================
# CURRENCY/FX CHANNELS
# =============================================================================

DOLLAR_STRENGTH = TransmissionChannel(
    channel_type=ChannelType.DOLLAR_STRENGTH,
    name="Dollar Strength",
    description=(
        "Broad dollar appreciation from Fed hawkishness, safe haven flows, or "
        "relative growth differentials. Headwind for commodities and EM assets."
    ),
    primary_assets=("UUP", "DX=F", "EURUSD=X"),
    secondary_assets=("EEM", "VWO", "GLD", "SLV", "FXE", "FXY"),
    search_queries=(
        "EM stocks dollar strength exposure",
        "commodity stocks dollar correlation",
        "multinationals dollar headwind",
    ),
    typical_magnitude="5-10% DXY move; inverse 0.5-1x in EM/commodities",
    time_horizon=TimeHorizon.MEDIUM_TERM,
    keywords=("dollar", "dxy", "fed", "hawkish", "safe haven", "flight to quality"),
)

DOLLAR_WEAKNESS = TransmissionChannel(
    channel_type=ChannelType.DOLLAR_WEAKNESS,
    name="Dollar Weakness",
    description=(
        "Broad dollar depreciation from Fed dovishness, risk-on sentiment, or "
        "twin deficit concerns. Tailwind for commodities, EM, and exporters."
    ),
    primary_assets=("UDN", "DX=F", "GLD", "EEM"),
    secondary_assets=("FXE", "FXA", "SLV", "COPX", "VWO"),
    search_queries=(
        "gold stocks dollar weakness",
        "EM stocks dollar depreciation",
        "commodity exporters weak dollar",
    ),
    typical_magnitude="5-10% DXY move; 1-1.5x in gold/commodities",
    time_horizon=TimeHorizon.MEDIUM_TERM,
    keywords=("dollar weak", "fed dovish", "twin deficit", "inflation", "debasement"),
)

EM_CURRENCY_STRESS = TransmissionChannel(
    channel_type=ChannelType.EM_CURRENCY_STRESS,
    name="EM Currency Stress",
    description=(
        "Emerging market currency crisis from capital flight, debt concerns, or "
        "contagion. Often triggers broader EM selloff and safe haven flows."
    ),
    primary_assets=("EEM", "VWO", "EMB", "EMLC"),
    secondary_assets=("TUR", "EWZ", "EWW", "RSX", "EZA", "INDA"),
    search_queries=(
        "EM stocks currency crisis exposure",
        "frontier market ETFs stress",
        "EM bond funds selloff",
    ),
    typical_magnitude="20-40% in affected currencies; 15-30% in equity",
    time_horizon=TimeHorizon.SHORT_TERM,
    keywords=("emerging market", "em currency", "capital flight", "crisis", "contagion"),
)

CARRY_TRADE_UNWIND = TransmissionChannel(
    channel_type=ChannelType.CARRY_TRADE_UNWIND,
    name="Carry Trade Unwind",
    description=(
        "Rapid unwinding of yen or CHF-funded carry trades. Causes sharp yen "
        "appreciation and cascading risk-off across global risk assets."
    ),
    primary_assets=("USDJPY=X", "EWJ", "FXY"),
    secondary_assets=("^VIX", "SPY", "QQQ", "EEM", "HYG"),
    search_queries=(
        "stocks exposed to yen carry trade",
        "risk assets carry trade correlation",
        "Japan stocks yen strength impact",
    ),
    typical_magnitude="5-10% yen move in days; 5-15% equity drawdown",
    time_horizon=TimeHorizon.IMMEDIATE,
    keywords=("yen", "carry trade", "boj", "japan", "unwind", "deleveraging"),
)

YUAN_DEVALUATION = TransmissionChannel(
    channel_type=ChannelType.YUAN_DEVALUATION,
    name="Yuan Devaluation",
    description=(
        "Chinese yuan devaluation from PBOC policy shift or capital outflows. "
        "Signals competitive devaluation risk, deflation export, or stress."
    ),
    primary_assets=("CNH=X", "FXI", "KWEB", "MCHI"),
    secondary_assets=("EEM", "ASHR", "GXC", "CQQQ"),
    search_queries=(
        "China ADR stocks yuan devaluation",
        "Asian stocks competitive devaluation",
        "commodity stocks China demand",
    ),
    typical_magnitude="2-5% CNH move; 10-20% in China equities",
    time_horizon=TimeHorizon.SHORT_TERM,
    keywords=("yuan", "cnh", "pboc", "china", "devaluation", "rmb"),
)


# =============================================================================
# RATES/LIQUIDITY CHANNELS
# =============================================================================

FED_HAWKISH = TransmissionChannel(
    channel_type=ChannelType.FED_HAWKISH,
    name="Fed Hawkish Shift",
    description=(
        "Federal Reserve signals more restrictive policy via dot plot, statement, "
        "or speeches. Reprices rate expectations, strengthens dollar, pressures duration."
    ),
    primary_assets=("^TNX", "TLT", "IEF", "SHY"),
    secondary_assets=("XLF", "KRE", "SPY", "QQQ", "ARKK"),
    search_queries=(
        "rate-sensitive stocks Fed hawkish",
        "growth stocks rising rates impact",
        "bank stocks higher rates benefit",
    ),
    typical_magnitude="10-30bps 10Y move; 5-10% in long duration",
    time_horizon=TimeHorizon.IMMEDIATE,
    keywords=("fed", "fomc", "hawkish", "rate hike", "tightening", "dot plot"),
)

FED_DOVISH = TransmissionChannel(
    channel_type=ChannelType.FED_DOVISH,
    name="Fed Dovish Shift",
    description=(
        "Federal Reserve signals more accommodative policy. Reprices rate "
        "expectations, weakens dollar, supports duration and risk assets."
    ),
    primary_assets=("TLT", "IEF", "GLD", "QQQ"),
    secondary_assets=("ARKK", "XLK", "SMH", "EEM", "HYG"),
    search_queries=(
        "growth stocks Fed dovish benefit",
        "rate-sensitive REITs Fed pivot",
        "gold stocks Fed pause",
    ),
    typical_magnitude="10-30bps 10Y move; 5-15% in growth/tech",
    time_horizon=TimeHorizon.IMMEDIATE,
    keywords=("fed", "fomc", "dovish", "rate cut", "pause", "pivot"),
)

YIELD_CURVE_INVERSION = TransmissionChannel(
    channel_type=ChannelType.YIELD_CURVE_INVERSION,
    name="Yield Curve Inversion",
    description=(
        "Inversion of the 2s10s yield curve signaling recession expectations. "
        "Pressures bank NIMs, signals growth concerns, historically leads recessions."
    ),
    primary_assets=("^TNX", "TLT", "XLF", "KRE"),
    secondary_assets=("SPY", "XLY", "XLI", "HYG"),
    search_queries=(
        "bank stocks inverted yield curve",
        "recession stocks historical performance",
        "defensive stocks curve inversion",
    ),
    typical_magnitude="Banks -10-20%; defensive rotation",
    time_horizon=TimeHorizon.MEDIUM_TERM,
    keywords=("yield curve", "inversion", "2s10s", "recession", "curve"),
)

CREDIT_TIGHTENING = TransmissionChannel(
    channel_type=ChannelType.CREDIT_TIGHTENING,
    name="Credit Tightening",
    description=(
        "Widening credit spreads from bank stress, defaults, or risk aversion. "
        "HY and leveraged loans lead equities. Watch HY spread vs VIX divergences."
    ),
    primary_assets=("HYG", "JNK", "LQD", "BKLN"),
    secondary_assets=("XLF", "KRE", "SPY", "IWM"),
    search_queries=(
        "high yield stocks credit spread",
        "leveraged loan exposure stocks",
        "bank stocks credit tightening",
    ),
    typical_magnitude="100-300bps HY spread widening; 10-25% equity",
    time_horizon=TimeHorizon.SHORT_TERM,
    keywords=("credit", "spread", "high yield", "default", "tightening", "stress"),
)

LIQUIDITY_CRISIS = TransmissionChannel(
    channel_type=ChannelType.LIQUIDITY_CRISIS,
    name="Liquidity Crisis",
    description=(
        "Systemic liquidity stress from repo market dysfunction, bank runs, or "
        "collateral issues. Forces deleveraging across all risk assets."
    ),
    primary_assets=("^VIX", "TLT", "GLD", "BIL"),
    secondary_assets=("SPY", "HYG", "EMB", "XLF"),
    search_queries=(
        "safe haven stocks liquidity crisis",
        "bank stocks liquidity stress",
        "money market funds flight to safety",
    ),
    typical_magnitude="VIX 40+; 15-30% equity drawdown",
    time_horizon=TimeHorizon.IMMEDIATE,
    keywords=("liquidity", "repo", "bank run", "collateral", "margin call", "crisis"),
)


# =============================================================================
# RISK SENTIMENT CHANNELS
# =============================================================================

RISK_OFF_FLIGHT = TransmissionChannel(
    channel_type=ChannelType.RISK_OFF_FLIGHT,
    name="Risk-Off Flight",
    description=(
        "Broad flight to safety from geopolitical shock, growth scare, or systemic "
        "concerns. Treasuries, gold, yen, CHF bid; equities, credit, EM sold."
    ),
    primary_assets=("TLT", "GLD", "FXY", "UUP"),
    secondary_assets=("^VIX", "VIXY", "XLU", "XLP"),
    search_queries=(
        "safe haven stocks risk-off",
        "defensive stocks flight to safety",
        "gold miners risk-off rally",
    ),
    typical_magnitude="10Y yield -20-50bps; gold +5-10%; SPX -5-15%",
    time_horizon=TimeHorizon.IMMEDIATE,
    keywords=("risk-off", "flight to safety", "safe haven", "fear", "panic"),
)

RISK_ON_RALLY = TransmissionChannel(
    channel_type=ChannelType.RISK_ON_RALLY,
    name="Risk-On Rally",
    description=(
        "Broad risk appetite from positive surprise, trade deal, or dovish Fed. "
        "Equities, HY, EM bid; Treasuries, gold, yen sold."
    ),
    primary_assets=("SPY", "QQQ", "HYG", "EEM"),
    secondary_assets=("IWM", "ARKK", "XLF", "SMH"),
    search_queries=(
        "high beta stocks risk-on rally",
        "EM stocks risk appetite",
        "cyclical stocks risk-on rotation",
    ),
    typical_magnitude="SPX +3-10%; HY spreads -50-100bps",
    time_horizon=TimeHorizon.IMMEDIATE,
    keywords=("risk-on", "rally", "relief", "trade deal", "stimulus"),
)

VIX_SPIKE = TransmissionChannel(
    channel_type=ChannelType.VIX_SPIKE,
    name="VIX Spike",
    description=(
        "Sharp volatility spike from shock event. Creates vol-of-vol cascade, "
        "forced deleveraging, and option dealer hedging flows."
    ),
    primary_assets=("^VIX", "VIXY", "UVXY", "VXX"),
    secondary_assets=("SPY", "QQQ", "IWM", "HYG"),
    search_queries=(
        "vol stocks VIX spike",
        "short vol ETF liquidation",
        "options dealer hedging stocks",
    ),
    typical_magnitude="VIX +50-200%; SPX -5-15% rapid",
    time_horizon=TimeHorizon.IMMEDIATE,
    keywords=("vix", "volatility", "spike", "panic", "fear"),
)


# =============================================================================
# SANCTIONS/CONTROLS CHANNELS
# =============================================================================

TRADE_SANCTIONS = TransmissionChannel(
    channel_type=ChannelType.TRADE_SANCTIONS,
    name="Trade Sanctions",
    description=(
        "Trade sanctions targeting specific countries, sectors, or companies. "
        "Disrupts supply chains, creates winners (alternatives) and losers (exposed)."
    ),
    primary_assets=("SPY", "EEM", "SMH"),
    secondary_assets=("XLE", "XLI", "KWEB", "FXI"),
    search_queries=(
        "stocks affected by Russia sanctions",
        "China sanctions exposure stocks",
        "semiconductor sanctions beneficiaries",
        "defense stocks sanctions beneficiary",
    ),
    typical_magnitude="Targeted stocks -30-70%; alternatives +20-50%",
    time_horizon=TimeHorizon.MEDIUM_TERM,
    keywords=("sanction", "tariff", "trade war", "embargo", "ban"),
)

CAPITAL_CONTROLS = TransmissionChannel(
    channel_type=ChannelType.CAPITAL_CONTROLS,
    name="Capital Controls",
    description=(
        "Capital controls imposed by countries facing currency pressure or "
        "geopolitical isolation. Creates trapped capital, premium for exit."
    ),
    primary_assets=("EEM", "EMB", "EMLC"),
    secondary_assets=("BTC-USD", "ETH-USD", "GLD"),
    search_queries=(
        "EM stocks capital controls exposure",
        "frontier market ETFs capital flight",
        "crypto stocks capital controls demand",
    ),
    typical_magnitude="Affected country -20-50%; stablecoin premium",
    time_horizon=TimeHorizon.SHORT_TERM,
    keywords=("capital control", "currency control", "blocked", "frozen", "seized"),
)

EXPORT_RESTRICTIONS = TransmissionChannel(
    channel_type=ChannelType.EXPORT_RESTRICTIONS,
    name="Export Restrictions",
    description=(
        "Export bans or restrictions on critical materials or technology. "
        "Creates shortages for importers, benefits for alternative suppliers."
    ),
    primary_assets=("SMH", "COPX", "XME"),
    secondary_assets=("INTC", "AMD", "NVDA", "MU", "ASML"),
    search_queries=(
        "semiconductor stocks export restrictions",
        "rare earth alternatives companies",
        "chip equipment stocks export ban",
    ),
    typical_magnitude="Affected sectors ±20-40%",
    time_horizon=TimeHorizon.MEDIUM_TERM,
    keywords=("export ban", "export restriction", "technology ban", "chip war"),
)


# =============================================================================
# INFLATION CHANNELS
# =============================================================================

INFLATION_SPIKE = TransmissionChannel(
    channel_type=ChannelType.INFLATION_SPIKE,
    name="Inflation Spike",
    description=(
        "Sharp increase in inflation readings or expectations. Reprices Fed, "
        "pressures duration, benefits TIPS, commodities, and pricing power."
    ),
    primary_assets=("TIP", "VTIP", "GLD", "DJP"),
    secondary_assets=("XLE", "XLB", "PDBC", "XLP"),
    search_queries=(
        "inflation beneficiary stocks",
        "pricing power stocks inflation",
        "TIPS stocks inflation hedge",
    ),
    typical_magnitude="10Y +20-50bps; TIP +2-5%; gold +5-10%",
    time_horizon=TimeHorizon.SHORT_TERM,
    keywords=("inflation", "cpi", "ppi", "hot", "sticky", "expectations"),
)

DEFLATION_RISK = TransmissionChannel(
    channel_type=ChannelType.DEFLATION_RISK,
    name="Deflation Risk",
    description=(
        "Signs of deflation from demand collapse or overcapacity. Benefits long "
        "duration; pressures commodities, banks, and cyclicals."
    ),
    primary_assets=("TLT", "EDV", "ZROZ"),
    secondary_assets=("XLU", "XLP", "VNQ"),
    search_queries=(
        "deflation beneficiary stocks",
        "long duration stocks deflation",
        "utility stocks deflation hedge",
    ),
    typical_magnitude="10Y -50-100bps; TLT +10-20%",
    time_horizon=TimeHorizon.MEDIUM_TERM,
    keywords=("deflation", "disinflation", "collapse", "overcapacity"),
)

WAGE_PRESSURE = TransmissionChannel(
    channel_type=ChannelType.WAGE_PRESSURE,
    name="Wage Pressure",
    description=(
        "Rising wage pressures from tight labor markets. Compresses margins for "
        "labor-intensive businesses; benefits worker-friendly sectors."
    ),
    primary_assets=("XLY", "XRT", "EATS"),
    secondary_assets=("XLI", "XLF", "XLP"),
    search_queries=(
        "labor intensive stocks wage pressure",
        "automation stocks labor shortage",
        "retail stocks labor costs",
    ),
    typical_magnitude="Margin compression 1-3pp; sector rotation",
    time_horizon=TimeHorizon.MEDIUM_TERM,
    keywords=("wage", "labor", "employment", "jobs", "hiring"),
)


# =============================================================================
# CHANNEL REGISTRY AND LOOKUP
# =============================================================================

ALL_CHANNELS: tuple[TransmissionChannel, ...] = (
    # Commodity supply
    OIL_SUPPLY_DISRUPTION,
    OIL_DEMAND_SHOCK,
    NATURAL_GAS_SUPPLY,
    METALS_SUPPLY,
    AGRICULTURAL_SUPPLY,
    # Currency/FX
    DOLLAR_STRENGTH,
    DOLLAR_WEAKNESS,
    EM_CURRENCY_STRESS,
    CARRY_TRADE_UNWIND,
    YUAN_DEVALUATION,
    # Rates/Liquidity
    FED_HAWKISH,
    FED_DOVISH,
    YIELD_CURVE_INVERSION,
    CREDIT_TIGHTENING,
    LIQUIDITY_CRISIS,
    # Risk sentiment
    RISK_OFF_FLIGHT,
    RISK_ON_RALLY,
    VIX_SPIKE,
    # Sanctions/Controls
    TRADE_SANCTIONS,
    CAPITAL_CONTROLS,
    EXPORT_RESTRICTIONS,
    # Inflation
    INFLATION_SPIKE,
    DEFLATION_RISK,
    WAGE_PRESSURE,
)

_CHANNEL_BY_TYPE: dict[ChannelType, TransmissionChannel] = {
    channel.channel_type: channel for channel in ALL_CHANNELS
}

# Mapping from event types (from significance.py) to likely channels
EVENT_TYPE_TO_CHANNELS: dict[str, tuple[ChannelType, ...]] = {
    "geopolitical": (
        ChannelType.OIL_SUPPLY_DISRUPTION,
        ChannelType.RISK_OFF_FLIGHT,
        ChannelType.TRADE_SANCTIONS,
        ChannelType.CAPITAL_CONTROLS,
    ),
    "monetary_policy": (
        ChannelType.FED_HAWKISH,
        ChannelType.FED_DOVISH,
        ChannelType.DOLLAR_STRENGTH,
        ChannelType.DOLLAR_WEAKNESS,
    ),
    "fiscal_policy": (
        ChannelType.INFLATION_SPIKE,
        ChannelType.RISK_ON_RALLY,
    ),
    "financial_crisis": (
        ChannelType.CREDIT_TIGHTENING,
        ChannelType.LIQUIDITY_CRISIS,
        ChannelType.RISK_OFF_FLIGHT,
        ChannelType.VIX_SPIKE,
    ),
    "trade_policy": (
        ChannelType.TRADE_SANCTIONS,
        ChannelType.EXPORT_RESTRICTIONS,
        ChannelType.YUAN_DEVALUATION,
    ),
    "pandemic": (
        ChannelType.OIL_DEMAND_SHOCK,
        ChannelType.LIQUIDITY_CRISIS,
        ChannelType.RISK_OFF_FLIGHT,
    ),
    "election": (
        ChannelType.RISK_ON_RALLY,
        ChannelType.RISK_OFF_FLIGHT,
    ),
    "regulatory": (
        ChannelType.EXPORT_RESTRICTIONS,
        ChannelType.TRADE_SANCTIONS,
    ),
    "commodity_supply": (
        ChannelType.OIL_SUPPLY_DISRUPTION,
        ChannelType.NATURAL_GAS_SUPPLY,
        ChannelType.METALS_SUPPLY,
        ChannelType.AGRICULTURAL_SUPPLY,
    ),
    "inflation": (
        ChannelType.INFLATION_SPIKE,
        ChannelType.FED_HAWKISH,
        ChannelType.WAGE_PRESSURE,
    ),
    "other": (
        ChannelType.RISK_OFF_FLIGHT,
        ChannelType.RISK_ON_RALLY,
    ),
}


def get_channel_by_type(channel_type: ChannelType | str) -> TransmissionChannel | None:
    """
    Look up a transmission channel by its type.

    Args:
        channel_type: ChannelType enum or string value

    Returns:
        TransmissionChannel if found, None otherwise
    """
    if isinstance(channel_type, str):
        try:
            channel_type = ChannelType(channel_type)
        except ValueError:
            return None
    return _CHANNEL_BY_TYPE.get(channel_type)


def get_channels_for_event_type(event_type: str) -> list[TransmissionChannel]:
    """
    Get likely transmission channels for a given event type.

    Args:
        event_type: Normalized event type from significance.py

    Returns:
        List of relevant TransmissionChannel objects
    """
    channel_types = EVENT_TYPE_TO_CHANNELS.get(event_type, ())
    return [_CHANNEL_BY_TYPE[ct] for ct in channel_types if ct in _CHANNEL_BY_TYPE]


def match_channels_by_keywords(text: str) -> list[TransmissionChannel]:
    """
    Match transmission channels based on keywords in text.

    Args:
        text: Event headline or description

    Returns:
        List of matching TransmissionChannel objects, sorted by match count
    """
    text_lower = text.lower()
    matches: list[tuple[int, TransmissionChannel]] = []

    for channel in ALL_CHANNELS:
        match_count = sum(1 for kw in channel.keywords if kw in text_lower)
        if match_count > 0:
            matches.append((match_count, channel))

    # Sort by match count descending
    matches.sort(key=lambda x: x[0], reverse=True)
    return [channel for _, channel in matches]


def get_all_search_queries(channels: list[TransmissionChannel]) -> list[str]:
    """
    Collect all search queries from a list of channels.

    Args:
        channels: List of TransmissionChannel objects

    Returns:
        Deduplicated list of search queries
    """
    queries: list[str] = []
    seen: set[str] = set()
    for channel in channels:
        for query in channel.search_queries:
            if query not in seen:
                seen.add(query)
                queries.append(query)
    return queries


def get_all_assets(channels: list[TransmissionChannel]) -> list[str]:
    """
    Collect all assets from a list of channels.

    Args:
        channels: List of TransmissionChannel objects

    Returns:
        Deduplicated list of asset symbols (primary first, then secondary)
    """
    primary: list[str] = []
    secondary: list[str] = []
    seen: set[str] = set()

    for channel in channels:
        for asset in channel.primary_assets:
            if asset not in seen:
                seen.add(asset)
                primary.append(asset)
        for asset in channel.secondary_assets:
            if asset not in seen:
                seen.add(asset)
                secondary.append(asset)

    return primary + secondary
