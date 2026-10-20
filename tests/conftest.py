"""Fixtures compartilhadas e geradores de mock data para a suíte de testes do pytest."""

from typing import Any
from unittest.mock import MagicMock

import pytest
import requests

from f1.clients.openf1 import OpenF1Client

# Payloads de exemplo fieis à especificação da OpenF1 API (doc.api.md)
SAMPLE_CAR_DATA = {
    "brake": 0,
    "date": "2023-09-15T13:08:19.923000+00:00",
    "driver_number": 55,
    "drs": 12,
    "meeting_key": 1219,
    "n_gear": 8,
    "rpm": 11141,
    "session_key": 9159,
    "speed": 315,
    "throttle": 99,
}

SAMPLE_CHAMPIONSHIP_DRIVER = {
    "driver_number": 4,
    "meeting_key": 1276,
    "points_current": 423.0,
    "points_start": 408.0,
    "position_current": 1,
    "position_start": 1,
    "session_key": 9839,
}

SAMPLE_CHAMPIONSHIP_TEAM = {
    "meeting_key": 1276,
    "points_current": 833.0,
    "points_start": 800.0,
    "position_current": 1,
    "position_start": 1,
    "session_key": 9839,
    "team_name": "McLaren",
}

SAMPLE_DRIVER = {
    "broadcast_name": "M VERSTAPPEN",
    "country_code": "NED",
    "driver_number": 1,
    "first_name": "Max",
    "full_name": "Max VERSTAPPEN",
    "headshot_url": "https://www.formula1.com/maxver01.png",
    "last_name": "Verstappen",
    "meeting_key": 1219,
    "name_acronym": "VER",
    "session_key": 9158,
    "team_colour": "3671C6",
    "team_name": "Red Bull Racing",
}

SAMPLE_INTERVAL = {
    "date": "2023-09-17T13:31:02.395000+00:00",
    "driver_number": 1,
    "gap_to_leader": 41.019,
    "interval": 0.003,
    "meeting_key": 1219,
    "session_key": 9165,
}

SAMPLE_LAP = {
    "date_start": "2023-09-16T13:59:07.606000+00:00",
    "driver_number": 63,
    "duration_sector_1": 26.966,
    "duration_sector_2": 38.657,
    "duration_sector_3": 26.12,
    "i1_speed": 307,
    "i2_speed": 277,
    "is_pit_out_lap": False,
    "lap_duration": 91.743,
    "lap_number": 8,
    "meeting_key": 1219,
    "segments_sector_1": [2049, 2049, 2049, 2051],
    "segments_sector_2": [2049, 2049, 2049, 2049],
    "segments_sector_3": [2048, 2048, 2048, 2064],
    "session_key": 9161,
    "st_speed": 298,
}

SAMPLE_LOCATION = {
    "date": "2023-09-16T13:03:35.292000+00:00",
    "driver_number": 81,
    "meeting_key": 1219,
    "session_key": 9161,
    "x": 567,
    "y": 3195,
    "z": 187,
}

SAMPLE_MEETING = {
    "circuit_key": 61,
    "circuit_image": "https://media.formula1.com/singapore.png",
    "circuit_info_url": "https://api.multiviewer.app/circuit/61",
    "circuit_short_name": "Singapore",
    "circuit_type": "Temporary - Street",
    "country_code": "SGP",
    "country_flag": "https://media.formula1.com/singapore-flag.png",
    "country_key": 157,
    "country_name": "Singapore",
    "date_end": "2024-09-22T14:00:00+00:00",
    "date_start": "2024-09-20T09:30:00+00:00",
    "gmt_offset": "08:00:00",
    "is_cancelled": False,
    "location": "Marina Bay",
    "meeting_key": 1246,
    "meeting_name": "Singapore Grand Prix",
    "meeting_official_name": "FORMULA 1 SINGAPORE AIRLINES SINGAPORE GRAND PRIX 2024",
    "year": 2024,
}

SAMPLE_OVERTAKE = {
    "date": "2024-11-03T15:50:07.565000+00:00",
    "meeting_key": 1249,
    "overtaken_driver_number": 4,
    "overtaking_driver_number": 63,
    "position": 1,
    "session_key": 9636,
}

SAMPLE_PIT = {
    "date": "2025-10-26T20:46:37.358000+00:00",
    "driver_number": 16,
    "lane_duration": 22.215,
    "lap_number": 31,
    "meeting_key": 1272,
    "pit_duration": 22.215,
    "session_key": 9877,
    "stop_duration": 2.2,
}

SAMPLE_POSITION = {
    "date": "2023-08-26T09:30:47.199000+00:00",
    "driver_number": 40,
    "meeting_key": 1217,
    "position": 2,
    "session_key": 9144,
}

SAMPLE_RACE_CONTROL = {
    "category": "Flag",
    "date": "2023-06-04T14:21:01+00:00",
    "driver_number": 1,
    "flag": "BLACK AND WHITE",
    "lap_number": 59,
    "meeting_key": 1211,
    "message": "BLACK AND WHITE FLAG FOR CAR 1 (VER) - TRACK LIMITS",
    "qualifying_phase": None,
    "scope": "Driver",
    "sector": None,
    "session_key": 9102,
}

SAMPLE_SESSION = {
    "circuit_key": 7,
    "circuit_short_name": "Spa-Francorchamps",
    "country_code": "BEL",
    "country_key": 16,
    "country_name": "Belgium",
    "date_end": "2023-07-29T15:35:00+00:00",
    "date_start": "2023-07-29T15:05:00+00:00",
    "gmt_offset": "02:00:00",
    "is_cancelled": False,
    "location": "Spa-Francorchamps",
    "meeting_key": 1216,
    "session_key": 9140,
    "session_name": "Sprint Qualifying",
    "session_type": "Sprint Qualifying",
    "year": 2023,
}

SAMPLE_SESSION_RESULT = {
    "dnf": False,
    "dns": False,
    "dsq": False,
    "driver_number": 1,
    "duration": 77.565,
    "gap_to_leader": 0.0,
    "number_of_laps": 24,
    "meeting_key": 1143,
    "position": 1,
    "session_key": 7782,
}

SAMPLE_STARTING_GRID = {
    "position": 1,
    "driver_number": 1,
    "lap_duration": 76.732,
    "meeting_key": 1143,
    "session_key": 7783,
}

SAMPLE_STINT = {
    "compound": "SOFT",
    "driver_number": 16,
    "lap_end": 20,
    "lap_start": 1,
    "meeting_key": 1219,
    "session_key": 9165,
    "stint_number": 1,
    "tyre_age_at_start": 3,
}

SAMPLE_TEAM_RADIO = {
    "date": "2023-09-15T09:40:43.005000+00:00",
    "driver_number": 11,
    "meeting_key": 1219,
    "recording_url": "https://livetiming.formula1.com/radio.mp3",
    "session_key": 9158,
}

SAMPLE_WEATHER = {
    "air_temperature": 27.8,
    "date": "2023-05-07T18:42:25.233000+00:00",
    "humidity": 58.0,
    "meeting_key": 1208,
    "pressure": 1018.7,
    "rainfall": 0,
    "session_key": 9078,
    "track_temperature": 52.5,
    "wind_direction": 136,
    "wind_speed": 2.4,
}


@pytest.fixture
def mock_response_builder():
    """Factory fixture para criar objetos Mock Response do requests."""

    def _builder(
        status_code: int = 200,
        json_data: Any = None,
        text: str = "",
        reason: str = "OK",
    ) -> MagicMock:
        mock_resp = MagicMock(spec=requests.Response)
        mock_resp.status_code = status_code
        mock_resp.reason = reason
        mock_resp.text = text
        if json_data is not None:
            mock_resp.json.return_value = json_data
        else:
            mock_resp.json.side_effect = ValueError("No JSON")
        return mock_resp

    return _builder


@pytest.fixture
def mock_session(mock_response_builder):
    """Sessão requests mockada com resposta JSON padrão."""
    session = MagicMock(spec=requests.Session)
    session.get.return_value = mock_response_builder(json_data=[SAMPLE_DRIVER])
    return session


@pytest.fixture
def client(mock_session):
    """Instância do OpenF1Client injetando a sessão mockada."""
    return OpenF1Client(session=mock_session)
