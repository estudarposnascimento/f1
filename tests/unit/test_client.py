"""Testes unitários para BaseHTTPClient e OpenF1Client."""

from unittest.mock import MagicMock

import pytest
import requests

from f1.clients.base import BaseHTTPClient
from f1.clients.openf1 import OpenF1Client
from f1.core.models import (
    CarData,
    CarLocation,
    ChampionshipDriver,
    ChampionshipTeam,
    Driver,
    Interval,
    Lap,
    Meeting,
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
from f1.exceptions import OpenF1APIError, OpenF1ConnectionError
from tests.conftest import (
    SAMPLE_CAR_DATA,
    SAMPLE_CHAMPIONSHIP_DRIVER,
    SAMPLE_CHAMPIONSHIP_TEAM,
    SAMPLE_DRIVER,
    SAMPLE_INTERVAL,
    SAMPLE_LAP,
    SAMPLE_LOCATION,
    SAMPLE_MEETING,
    SAMPLE_OVERTAKE,
    SAMPLE_PIT,
    SAMPLE_POSITION,
    SAMPLE_RACE_CONTROL,
    SAMPLE_SESSION,
    SAMPLE_SESSION_RESULT,
    SAMPLE_STARTING_GRID,
    SAMPLE_STINT,
    SAMPLE_TEAM_RADIO,
    SAMPLE_WEATHER,
)


class TestBaseHTTPClient:
    """Valida resiliência, montagem de requisição e tratamento de erros do cliente base."""

    def test_context_manager_and_close(self, mock_session):
        with BaseHTTPClient(session=mock_session) as client:
            assert client.timeout == 15.0
        mock_session.close.assert_called_once()

    def test_http_error_raises_openf1_api_error(
        self, mock_session, mock_response_builder
    ):
        mock_session.get.return_value = mock_response_builder(
            status_code=404, text="Not Found", reason="Not Found"
        )
        client = BaseHTTPClient(session=mock_session)
        with pytest.raises(OpenF1APIError) as exc_info:
            client.get("unknown_endpoint")
        assert exc_info.value.status_code == 404
        assert "Not Found" in str(exc_info.value)

    def test_connection_error_raises_openf1_connection_error(self, mock_session):
        mock_session.get.side_effect = requests.exceptions.ConnectionError(
            "Connection failed"
        )
        client = BaseHTTPClient(session=mock_session)
        with pytest.raises(OpenF1ConnectionError) as exc_info:
            client.get("drivers")
        assert "Falha de conexão" in str(exc_info.value)

    def test_timeout_raises_openf1_connection_error(self, mock_session):
        mock_session.get.side_effect = requests.exceptions.Timeout("Request timed out")
        client = BaseHTTPClient(session=mock_session)
        with pytest.raises(OpenF1ConnectionError) as exc_info:
            client.get("drivers")
        assert "Falha de conexão" in str(exc_info.value)

    def test_invalid_json_raises_openf1_api_error(
        self, mock_session, mock_response_builder
    ):
        mock_session.get.return_value = mock_response_builder(
            status_code=200, json_data=None, text="<html>Invalid JSON</html>"
        )
        client = BaseHTTPClient(session=mock_session)
        with pytest.raises(OpenF1APIError) as exc_info:
            client.get("drivers")
        assert "Falha ao decodificar JSON" in str(exc_info.value)

    def test_csv_mode_returns_string(self, mock_session, mock_response_builder):
        csv_content = "driver_number,name_acronym\n1,VER\n44,HAM"
        mock_session.get.return_value = mock_response_builder(
            status_code=200, text=csv_content
        )
        client = BaseHTTPClient(session=mock_session)
        result = client.get("drivers", as_csv=True)
        assert result == csv_content

    def test_default_session_creation(self):
        client = BaseHTTPClient()
        assert client.session is not None
        assert client.base_url == "https://api.openf1.org/v1"
        client.close()


class TestOpenF1ClientEndpoints:
    """Valida as chamadas tipadas para todos os 18 endpoints da OpenF1 API."""

    def test_get_car_data(self, client, mock_session, mock_response_builder):
        mock_session.get.return_value = mock_response_builder(
            json_data=[SAMPLE_CAR_DATA]
        )
        res = client.get_car_data(session_key=9159, driver_number=55)
        assert len(res) == 1
        assert isinstance(res[0], CarData)
        assert res[0].speed == 315

    def test_get_championship_drivers(
        self, client, mock_session, mock_response_builder
    ):
        mock_session.get.return_value = mock_response_builder(
            json_data=[SAMPLE_CHAMPIONSHIP_DRIVER]
        )
        res = client.get_championship_drivers(session_key="latest")
        assert len(res) == 1
        assert isinstance(res[0], ChampionshipDriver)
        assert res[0].points_current == 423.0

    def test_get_championship_teams(self, client, mock_session, mock_response_builder):
        mock_session.get.return_value = mock_response_builder(
            json_data=[SAMPLE_CHAMPIONSHIP_TEAM]
        )
        res = client.get_championship_teams(session_key="latest")
        assert len(res) == 1
        assert isinstance(res[0], ChampionshipTeam)
        assert res[0].team_name == "McLaren"

    def test_get_drivers(self, client, mock_session, mock_response_builder):
        mock_session.get.return_value = mock_response_builder(json_data=[SAMPLE_DRIVER])
        res = client.get_drivers(driver_number=1)
        assert len(res) == 1
        assert isinstance(res[0], Driver)
        assert res[0].name_acronym == "VER"

    def test_get_intervals(self, client, mock_session, mock_response_builder):
        mock_session.get.return_value = mock_response_builder(
            json_data=[SAMPLE_INTERVAL]
        )
        res = client.get_intervals(session_key=9165)
        assert len(res) == 1
        assert isinstance(res[0], Interval)
        assert res[0].gap_to_leader == 41.019

    def test_get_laps(self, client, mock_session, mock_response_builder):
        mock_session.get.return_value = mock_response_builder(json_data=[SAMPLE_LAP])
        res = client.get_laps(session_key=9161, driver_number=63)
        assert len(res) == 1
        assert isinstance(res[0], Lap)
        assert res[0].lap_number == 8

    def test_get_location(self, client, mock_session, mock_response_builder):
        mock_session.get.return_value = mock_response_builder(
            json_data=[SAMPLE_LOCATION]
        )
        res = client.get_location(session_key=9161, driver_number=81)
        assert len(res) == 1
        assert isinstance(res[0], CarLocation)
        assert res[0].x == 567

    def test_get_meetings(self, client, mock_session, mock_response_builder):
        mock_session.get.return_value = mock_response_builder(
            json_data=[SAMPLE_MEETING]
        )
        res = client.get_meetings(year=2024)
        assert len(res) == 1
        assert isinstance(res[0], Meeting)
        assert res[0].circuit_short_name == "Singapore"

    def test_get_overtakes(self, client, mock_session, mock_response_builder):
        mock_session.get.return_value = mock_response_builder(
            json_data=[SAMPLE_OVERTAKE]
        )
        res = client.get_overtakes(session_key=9636)
        assert len(res) == 1
        assert isinstance(res[0], Overtake)
        assert res[0].overtaking_driver_number == 63

    def test_get_pit(self, client, mock_session, mock_response_builder):
        mock_session.get.return_value = mock_response_builder(json_data=[SAMPLE_PIT])
        res = client.get_pit(session_key=9877)
        assert len(res) == 1
        assert isinstance(res[0], PitStop)
        assert res[0].stop_duration == 2.2

    def test_get_position(self, client, mock_session, mock_response_builder):
        mock_session.get.return_value = mock_response_builder(
            json_data=[SAMPLE_POSITION]
        )
        res = client.get_position(meeting_key=1217)
        assert len(res) == 1
        assert isinstance(res[0], Position)
        assert res[0].position == 2

    def test_get_race_control(self, client, mock_session, mock_response_builder):
        mock_session.get.return_value = mock_response_builder(
            json_data=[SAMPLE_RACE_CONTROL]
        )
        res = client.get_race_control(session_key=9102)
        assert len(res) == 1
        assert isinstance(res[0], RaceControlMessage)
        assert res[0].flag == "BLACK AND WHITE"

    def test_get_sessions(self, client, mock_session, mock_response_builder):
        mock_session.get.return_value = mock_response_builder(
            json_data=[SAMPLE_SESSION]
        )
        res = client.get_sessions(year=2023)
        assert len(res) == 1
        assert isinstance(res[0], Session)
        assert res[0].session_name == "Sprint Qualifying"

    def test_get_session_results(self, client, mock_session, mock_response_builder):
        mock_session.get.return_value = mock_response_builder(
            json_data=[SAMPLE_SESSION_RESULT]
        )
        res = client.get_session_results(session_key=7782)
        assert len(res) == 1
        assert isinstance(res[0], SessionResult)
        assert res[0].duration == 77.565

    def test_get_starting_grid(self, client, mock_session, mock_response_builder):
        mock_session.get.return_value = mock_response_builder(
            json_data=[SAMPLE_STARTING_GRID]
        )
        res = client.get_starting_grid(session_key=7783)
        assert len(res) == 1
        assert isinstance(res[0], StartingGrid)
        assert res[0].lap_duration == 76.732

    def test_get_stints(self, client, mock_session, mock_response_builder):
        mock_session.get.return_value = mock_response_builder(json_data=[SAMPLE_STINT])
        res = client.get_stints(session_key=9165)
        assert len(res) == 1
        assert isinstance(res[0], Stint)
        assert res[0].compound == "SOFT"

    def test_get_team_radio(self, client, mock_session, mock_response_builder):
        mock_session.get.return_value = mock_response_builder(
            json_data=[SAMPLE_TEAM_RADIO]
        )
        res = client.get_team_radio(session_key=9158)
        assert len(res) == 1
        assert isinstance(res[0], TeamRadio)
        assert "radio.mp3" in res[0].recording_url

    def test_get_weather(self, client, mock_session, mock_response_builder):
        mock_session.get.return_value = mock_response_builder(
            json_data=[SAMPLE_WEATHER]
        )
        res = client.get_weather(session_key=9078)
        assert len(res) == 1
        assert isinstance(res[0], Weather)
        assert res[0].track_temperature == 52.5

    def test_csv_flag_on_endpoints(self, client, mock_session, mock_response_builder):
        csv_data = "meeting_key,meeting_name\n1246,Singapore Grand Prix"
        mock_session.get.return_value = mock_response_builder(
            status_code=200, text=csv_data
        )
        res = client.get_meetings(year=2024, csv=True)
        assert isinstance(res, str)
        assert "Singapore Grand Prix" in res

    def test_single_object_response_wrapped_in_list(
        self, client, mock_session, mock_response_builder
    ):
        # Caso a API retorne um único dicionário em vez de lista
        mock_session.get.return_value = mock_response_builder(json_data=SAMPLE_DRIVER)
        res = client.get_drivers(driver_number=1)
        assert len(res) == 1
        assert isinstance(res[0], Driver)
        assert res[0].name_acronym == "VER"
