"""Cliente tipado de alto nível para todos os 18 endpoints da OpenF1 API."""

from collections.abc import Sequence
from typing import Any, TypeVar, overload

from f1.clients.base import BaseHTTPClient
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

M = TypeVar("M", bound=OpenF1BaseModel)


class OpenF1Client(BaseHTTPClient):
    """Cliente para a API OpenF1 com métodos fortemente tipados para cada endpoint."""

    def _fetch_entities(
        self,
        endpoint: str,
        model_cls: type[M],
        as_csv: bool = False,
        **filters: Any,
    ) -> list[M] | str:
        """Helper interno para obter e converter dados no modelo Pydantic correspondente."""
        raw_result = self.get(endpoint=endpoint, params=filters, as_csv=as_csv)
        if as_csv:
            return str(raw_result)
        if not isinstance(raw_result, Sequence):
            return [model_cls.model_validate(raw_result)]
        return [model_cls.model_validate(item) for item in raw_result]

    # 1. Car Data
    @overload
    def get_car_data(self, *, csv: bool = False, **filters: Any) -> list[CarData]: ...
    @overload
    def get_car_data(self, *, csv: bool = True, **filters: Any) -> str: ...
    def get_car_data(self, *, csv: bool = False, **filters: Any) -> list[CarData] | str:
        """Telemetria veicular de alta frequência (~3.7 Hz)."""
        return self._fetch_entities("car_data", CarData, as_csv=csv, **filters)

    # 2. Championship Drivers
    @overload
    def get_championship_drivers(
        self, *, csv: bool = False, **filters: Any
    ) -> list[ChampionshipDriver]: ...
    @overload
    def get_championship_drivers(self, *, csv: bool = True, **filters: Any) -> str: ...
    def get_championship_drivers(
        self, *, csv: bool = False, **filters: Any
    ) -> list[ChampionshipDriver] | str:
        """Classificação e pontuação do Campeonato Mundial de Pilotos."""
        return self._fetch_entities(
            "championship_drivers", ChampionshipDriver, as_csv=csv, **filters
        )

    # 3. Championship Teams
    @overload
    def get_championship_teams(
        self, *, csv: bool = False, **filters: Any
    ) -> list[ChampionshipTeam]: ...
    @overload
    def get_championship_teams(self, *, csv: bool = True, **filters: Any) -> str: ...
    def get_championship_teams(
        self, *, csv: bool = False, **filters: Any
    ) -> list[ChampionshipTeam] | str:
        """Classificação e pontuação do Campeonato Mundial de Construtores."""
        return self._fetch_entities(
            "championship_teams", ChampionshipTeam, as_csv=csv, **filters
        )

    # 4. Drivers
    @overload
    def get_drivers(self, *, csv: bool = False, **filters: Any) -> list[Driver]: ...
    @overload
    def get_drivers(self, *, csv: bool = True, **filters: Any) -> str: ...
    def get_drivers(self, *, csv: bool = False, **filters: Any) -> list[Driver] | str:
        """Informações cadastrais e metadados dos pilotos em uma sessão."""
        return self._fetch_entities("drivers", Driver, as_csv=csv, **filters)

    # 5. Intervals
    @overload
    def get_intervals(self, *, csv: bool = False, **filters: Any) -> list[Interval]: ...
    @overload
    def get_intervals(self, *, csv: bool = True, **filters: Any) -> str: ...
    def get_intervals(
        self, *, csv: bool = False, **filters: Any
    ) -> list[Interval] | str:
        """Intervalos de tempo em pista e gap para o líder da prova."""
        return self._fetch_entities("intervals", Interval, as_csv=csv, **filters)

    # 6. Laps
    @overload
    def get_laps(self, *, csv: bool = False, **filters: Any) -> list[Lap]: ...
    @overload
    def get_laps(self, *, csv: bool = True, **filters: Any) -> str: ...
    def get_laps(self, *, csv: bool = False, **filters: Any) -> list[Lap] | str:
        """Tempos de volta, setores, mini-setores e speed traps."""
        return self._fetch_entities("laps", Lap, as_csv=csv, **filters)

    # 7. Location
    @overload
    def get_location(
        self, *, csv: bool = False, **filters: Any
    ) -> list[CarLocation]: ...
    @overload
    def get_location(self, *, csv: bool = True, **filters: Any) -> str: ...
    def get_location(
        self, *, csv: bool = False, **filters: Any
    ) -> list[CarLocation] | str:
        """Coordenadas tridimensionais (X, Y, Z) dos carros no circuito."""
        return self._fetch_entities("location", CarLocation, as_csv=csv, **filters)

    # 8. Meetings
    @overload
    def get_meetings(self, *, csv: bool = False, **filters: Any) -> list[Meeting]: ...
    @overload
    def get_meetings(self, *, csv: bool = True, **filters: Any) -> str: ...
    def get_meetings(self, *, csv: bool = False, **filters: Any) -> list[Meeting] | str:
        """Finais de semana de Grandes Prêmios e testes."""
        return self._fetch_entities("meetings", Meeting, as_csv=csv, **filters)

    # 9. Overtakes
    @overload
    def get_overtakes(self, *, csv: bool = False, **filters: Any) -> list[Overtake]: ...
    @overload
    def get_overtakes(self, *, csv: bool = True, **filters: Any) -> str: ...
    def get_overtakes(
        self, *, csv: bool = False, **filters: Any
    ) -> list[Overtake] | str:
        """Registros cronológicos de ultrapassagens e trocas de posições."""
        return self._fetch_entities("overtakes", Overtake, as_csv=csv, **filters)

    # 10. Pit
    @overload
    def get_pit(self, *, csv: bool = False, **filters: Any) -> list[PitStop]: ...
    @overload
    def get_pit(self, *, csv: bool = True, **filters: Any) -> str: ...
    def get_pit(self, *, csv: bool = False, **filters: Any) -> list[PitStop] | str:
        """Dados de passagens pelo pit lane e duração das paradas de box."""
        return self._fetch_entities("pit", PitStop, as_csv=csv, **filters)

    # 11. Position
    @overload
    def get_position(self, *, csv: bool = False, **filters: Any) -> list[Position]: ...
    @overload
    def get_position(self, *, csv: bool = True, **filters: Any) -> str: ...
    def get_position(
        self, *, csv: bool = False, **filters: Any
    ) -> list[Position] | str:
        """Rastreamento de posições dos pilotos ao longo da prova."""
        return self._fetch_entities("position", Position, as_csv=csv, **filters)

    # 12. Race Control
    @overload
    def get_race_control(
        self, *, csv: bool = False, **filters: Any
    ) -> list[RaceControlMessage]: ...
    @overload
    def get_race_control(self, *, csv: bool = True, **filters: Any) -> str: ...
    def get_race_control(
        self, *, csv: bool = False, **filters: Any
    ) -> list[RaceControlMessage] | str:
        """Mensagens da Direção de Prova da FIA (bandeiras, investigações)."""
        return self._fetch_entities(
            "race_control", RaceControlMessage, as_csv=csv, **filters
        )

    # 13. Sessions
    @overload
    def get_sessions(self, *, csv: bool = False, **filters: Any) -> list[Session]: ...
    @overload
    def get_sessions(self, *, csv: bool = True, **filters: Any) -> str: ...
    def get_sessions(self, *, csv: bool = False, **filters: Any) -> list[Session] | str:
        """Sessões de pista de um final de semana."""
        return self._fetch_entities("sessions", Session, as_csv=csv, **filters)

    # 14. Session Results
    @overload
    def get_session_results(
        self, *, csv: bool = False, **filters: Any
    ) -> list[SessionResult]: ...
    @overload
    def get_session_results(self, *, csv: bool = True, **filters: Any) -> str: ...
    def get_session_results(
        self, *, csv: bool = False, **filters: Any
    ) -> list[SessionResult] | str:
        """Resultados e classificação oficial final homologada da sessão."""
        return self._fetch_entities(
            "session_result", SessionResult, as_csv=csv, **filters
        )

    # 15. Starting Grid
    @overload
    def get_starting_grid(
        self, *, csv: bool = False, **filters: Any
    ) -> list[StartingGrid]: ...
    @overload
    def get_starting_grid(self, *, csv: bool = True, **filters: Any) -> str: ...
    def get_starting_grid(
        self, *, csv: bool = False, **filters: Any
    ) -> list[StartingGrid] | str:
        """Grid de largada oficial para corrida ou sprint."""
        return self._fetch_entities(
            "starting_grid", StartingGrid, as_csv=csv, **filters
        )

    # 16. Stints
    @overload
    def get_stints(self, *, csv: bool = False, **filters: Any) -> list[Stint]: ...
    @overload
    def get_stints(self, *, csv: bool = True, **filters: Any) -> str: ...
    def get_stints(self, *, csv: bool = False, **filters: Any) -> list[Stint] | str:
        """Trechos contínuos com o mesmo conjunto de pneus."""
        return self._fetch_entities("stints", Stint, as_csv=csv, **filters)

    # 17. Team Radio
    @overload
    def get_team_radio(
        self, *, csv: bool = False, **filters: Any
    ) -> list[TeamRadio]: ...
    @overload
    def get_team_radio(self, *, csv: bool = True, **filters: Any) -> str: ...
    def get_team_radio(
        self, *, csv: bool = False, **filters: Any
    ) -> list[TeamRadio] | str:
        """Áudios de rádio entre equipe e piloto."""
        return self._fetch_entities("team_radio", TeamRadio, as_csv=csv, **filters)

    # 18. Weather
    @overload
    def get_weather(self, *, csv: bool = False, **filters: Any) -> list[Weather]: ...
    @overload
    def get_weather(self, *, csv: bool = True, **filters: Any) -> str: ...
    def get_weather(self, *, csv: bool = False, **filters: Any) -> list[Weather] | str:
        """Condições climáticas da pista minuto a minuto."""
        return self._fetch_entities("weather", Weather, as_csv=csv, **filters)
