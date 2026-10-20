"""OpenF1 Python SDK - Biblioteca cliente para dados e telemetria da Fórmula 1."""

from f1.clients.base import BaseHTTPClient
from f1.clients.openf1 import OpenF1Client
from f1.core.constants import (
    CircuitType,
    DRSStatus,
    FlagType,
    SessionType,
    TyreCompound,
)
from f1.core.filters import build_filter_params, encode_query_string
from f1.core.models import (
    CarData,
    CarLocation,
    ChampionshipDriver,
    ChampionshipTeam,
    Driver,
    Interval,
    Lap,
    Meeting,
    OpenF1BaseModel,
    Overtake,
    PitStop,
    Position,
    RaceControlMessage,
    Session,
    SessionResult,
    StartingGrid,
    Stint,
    TeamRadio,
    Weather,
)
from f1.exceptions import (
    OpenF1APIError,
    OpenF1ConnectionError,
    OpenF1Exception,
    OpenF1ValidationError,
)
from f1.utils.dataframe import to_dataframe
from f1.utils.datetime import format_utc_iso, parse_iso_datetime

__version__ = "0.1.0"

__all__ = [
    "BaseHTTPClient",
    "CarData",
    "CarLocation",
    "ChampionshipDriver",
    "ChampionshipTeam",
    "CircuitType",
    "DRSStatus",
    "Driver",
    "FlagType",
    "Interval",
    "Lap",
    "Meeting",
    "OpenF1APIError",
    "OpenF1BaseModel",
    "OpenF1Client",
    "OpenF1ConnectionError",
    "OpenF1Exception",
    "OpenF1ValidationError",
    "Overtake",
    "PitStop",
    "Position",
    "RaceControlMessage",
    "Session",
    "SessionResult",
    "SessionType",
    "StartingGrid",
    "Stint",
    "TeamRadio",
    "TyreCompound",
    "Weather",
    "__version__",
    "build_filter_params",
    "encode_query_string",
    "format_utc_iso",
    "parse_iso_datetime",
    "to_dataframe",
]

