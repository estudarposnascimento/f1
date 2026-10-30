"""Catálogo e utilitários compartilhados pelas camadas do pipeline."""

import json
from dataclasses import dataclass
from datetime import date, datetime
from hashlib import sha256
from typing import Any, get_args, get_origin

from pydantic import BaseModel

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


@dataclass(frozen=True)
class EndpointDefinition:
    model: type[OpenF1BaseModel]
    raw_table: str
    refined_tables: tuple[str, ...]


@dataclass(frozen=True)
class IngestionResult:
    id_execucao: str
    id_extracao: str
    status: str
    records_written: int
    hash_conteudo: str | None


@dataclass(frozen=True)
class TransformationResult:
    id_execucao: str
    endpoint: str
    status: str
    records_processed: int
    records_rejected: int


ENDPOINTS = {
    "meetings": EndpointDefinition(
        Meeting, "grandes_premios", ("dim_grandes_premios", "dim_circuitos")
    ),
    "sessions": EndpointDefinition(Session, "sessoes", ("dim_sessoes",)),
    "drivers": EndpointDefinition(Driver, "pilotos", ("dim_pilotos", "dim_equipes")),
    "car_data": EndpointDefinition(CarData, "telemetria_carros", ("fato_telemetria",)),
    "laps": EndpointDefinition(Lap, "voltas", ("fato_voltas",)),
    "location": EndpointDefinition(
        CarLocation, "localizacao_carros", ("fato_localizacao",)
    ),
    "position": EndpointDefinition(Position, "posicoes", ("fato_posicoes",)),
    "intervals": EndpointDefinition(Interval, "intervalos", ("fato_intervalos",)),
    "stints": EndpointDefinition(Stint, "stints_pneus", ("fato_stints",)),
    "pit": EndpointDefinition(PitStop, "paradas_box", ("fato_pit_stops",)),
    "weather": EndpointDefinition(Weather, "clima", ("fato_clima",)),
    "race_control": EndpointDefinition(
        RaceControlMessage, "controle_corrida", ("fato_controle_corrida",)
    ),
    "session_result": EndpointDefinition(
        SessionResult, "resultados_sessao", ("fato_resultados",)
    ),
    "starting_grid": EndpointDefinition(
        StartingGrid, "grid_largada", ("fato_grid_largada",)
    ),
    "overtakes": EndpointDefinition(
        Overtake, "ultrapassagens", ("fato_ultrapassagens",)
    ),
    "team_radio": EndpointDefinition(
        TeamRadio, "radio_equipes", ("fato_radio_equipes",)
    ),
    "championship_drivers": EndpointDefinition(
        ChampionshipDriver, "campeonato_pilotos", ("fato_campeonato_pilotos",)
    ),
    "championship_teams": EndpointDefinition(
        ChampionshipTeam, "campeonato_equipes", ("fato_campeonato_equipes",)
    ),
}


def json_default(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    return str(value)


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=json_default,
        allow_nan=False,
    )


def canonical_json_hash(value: Any) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


def duckdb_type(annotation: Any) -> str:
    origin = get_origin(annotation)
    arguments = [item for item in get_args(annotation) if item is not type(None)]

    if origin in (list, tuple, dict, set) or len(arguments) > 1:
        return "JSON"
    if arguments:
        annotation = arguments[0]
        origin = get_origin(annotation)
    if origin in (list, tuple, dict, set):
        return "JSON"
    if annotation is bool:
        return "BOOLEAN"
    if annotation is int:
        return "BIGINT"
    if annotation is float:
        return "DOUBLE"
    if annotation is str:
        return "VARCHAR"
    return "JSON"


def refined_type(name: str, annotation: Any) -> str:
    if name in {"date", "date_start", "date_end"}:
        return "TIMESTAMPTZ"
    if name in {"meeting_key", "session_key"}:
        return "VARCHAR"
    return duckdb_type(annotation)


def sql_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'
