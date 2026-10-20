"""Constantes e enumerações do domínio da Fórmula 1."""

from enum import Enum, IntEnum


class DRSStatus(IntEnum):
    """Códigos de status do DRS (Drag Reduction System)."""

    OFF = 0
    OFF_ALT = 1
    UNKNOWN_2 = 2
    UNKNOWN_3 = 3
    DETECTED = 8
    UNKNOWN_9 = 9
    ON_10 = 10
    ON_12 = 12
    ON_14 = 14

    @property
    def is_eligible(self) -> bool:
        """Verifica se o piloto é elegível para abertura do DRS."""
        return self == DRSStatus.DETECTED

    @property
    def is_active(self) -> bool:
        """Verifica se o DRS está ativado/aberto."""
        return self in (DRSStatus.ON_10, DRSStatus.ON_12, DRSStatus.ON_14)


class TyreCompound(str, Enum):
    """Compostos de pneus utilizados."""

    SOFT = "SOFT"
    MEDIUM = "MEDIUM"
    HARD = "HARD"
    INTERMEDIATE = "INTERMEDIATE"
    WET = "WET"
    UNKNOWN = "UNKNOWN"


class FlagType(str, Enum):
    """Tipos de bandeiras emitidas pela Direção de Prova."""

    GREEN = "GREEN"
    YELLOW = "YELLOW"
    DOUBLE_YELLOW = "DOUBLE YELLOW"
    RED = "RED"
    CHEQUERED = "CHEQUERED"
    BLACK_AND_WHITE = "BLACK AND WHITE"
    BLUE = "BLUE"
    CLEAR = "CLEAR"


class SessionType(str, Enum):
    """Tipos de sessões oficiais de um final de semana."""

    PRACTICE = "Practice"
    QUALIFYING = "Qualifying"
    SPRINT_QUALIFYING = "Sprint Qualifying"
    SPRINT_SHOOTOUT = "Sprint Shootout"
    SPRINT = "Sprint"
    RACE = "Race"


class CircuitType(str, Enum):
    """Classificação do tipo de traçado do circuito."""

    PERMANENT = "Permanent"
    TEMPORARY_STREET = "Temporary - Street"
    TEMPORARY_ROAD = "Temporary - Road"
