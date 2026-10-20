"""Testes unitários para todos os 18 modelos Pydantic v2 e enums."""

import pytest
from pydantic import ValidationError

from f1.core.constants import (
    CircuitType,
    DRSStatus,
    FlagType,
    SessionType,
    TyreCompound,
)
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


class TestConstants:
    """Valida enums e constantes de domínio."""

    def test_drs_status_properties(self):
        assert DRSStatus.DETECTED.is_eligible is True
        assert DRSStatus.OFF.is_eligible is False
        assert DRSStatus.ON_10.is_active is True
        assert DRSStatus.ON_12.is_active is True
        assert DRSStatus.ON_14.is_active is True
        assert DRSStatus.OFF.is_active is False

    def test_enums_membership(self):
        assert TyreCompound.SOFT == "SOFT"
        assert FlagType.BLACK_AND_WHITE == "BLACK AND WHITE"
        assert SessionType.RACE == "Race"
        assert CircuitType.PERMANENT == "Permanent"


class TestModelsValidation:
    """Valida instanciação, tipagem e serialização dos 18 modelos."""

    def test_car_data_valid(self):
        obj = CarData.model_validate(SAMPLE_CAR_DATA)
        assert obj.driver_number == 55
        assert obj.speed == 315
        assert obj.brake == 0
        assert obj.session_key == 9159

    def test_car_data_invalid(self):
        with pytest.raises(ValidationError):
            CarData.model_validate({"speed": "fast"})

    def test_championship_driver_valid(self):
        obj = ChampionshipDriver.model_validate(SAMPLE_CHAMPIONSHIP_DRIVER)
        assert obj.driver_number == 4
        assert obj.points_current == 423.0
        assert obj.position_current == 1

    def test_championship_team_valid(self):
        obj = ChampionshipTeam.model_validate(SAMPLE_CHAMPIONSHIP_TEAM)
        assert obj.team_name == "McLaren"
        assert obj.points_current == 833.0

    def test_driver_valid_and_optional_fields(self):
        obj = Driver.model_validate(SAMPLE_DRIVER)
        assert obj.full_name == "Max VERSTAPPEN"
        assert obj.name_acronym == "VER"
        assert obj.team_name == "Red Bull Racing"

        # Com campos opcionais ausentes
        minimal = {
            "driver_number": 44,
            "full_name": "Lewis HAMILTON",
            "name_acronym": "HAM",
            "meeting_key": "latest",
            "session_key": "latest",
        }
        min_obj = Driver.model_validate(minimal)
        assert min_obj.broadcast_name is None
        assert min_obj.headshot_url is None

    def test_interval_valid_and_null_gap(self):
        obj = Interval.model_validate(SAMPLE_INTERVAL)
        assert obj.gap_to_leader == 41.019
        assert obj.interval == 0.003

        # Líder com gap nulo
        leader_interval = {
            "date": "2023-09-17T13:31:02.395000+00:00",
            "driver_number": 55,
            "gap_to_leader": None,
            "interval": None,
            "meeting_key": 1219,
            "session_key": 9165,
        }
        leader_obj = Interval.model_validate(leader_interval)
        assert leader_obj.gap_to_leader is None
        assert leader_obj.interval is None

    def test_lap_valid_and_segments(self):
        obj = Lap.model_validate(SAMPLE_LAP)
        assert obj.lap_number == 8
        assert obj.lap_duration == 91.743
        assert len(obj.segments_sector_1) == 4
        assert obj.st_speed == 298

    def test_location_valid(self):
        obj = CarLocation.model_validate(SAMPLE_LOCATION)
        assert obj.x == 567
        assert obj.y == 3195
        assert obj.z == 187

    def test_meeting_valid(self):
        obj = Meeting.model_validate(SAMPLE_MEETING)
        assert obj.meeting_name == "Singapore Grand Prix"
        assert obj.year == 2024
        assert obj.is_cancelled is False

    def test_overtake_valid(self):
        obj = Overtake.model_validate(SAMPLE_OVERTAKE)
        assert obj.overtaken_driver_number == 4
        assert obj.overtaking_driver_number == 63
        assert obj.position == 1

    def test_pit_valid(self):
        obj = PitStop.model_validate(SAMPLE_PIT)
        assert obj.lane_duration == 22.215
        assert obj.stop_duration == 2.2
        assert obj.lap_number == 31

    def test_position_valid(self):
        obj = Position.model_validate(SAMPLE_POSITION)
        assert obj.driver_number == 40
        assert obj.position == 2

    def test_race_control_valid(self):
        obj = RaceControlMessage.model_validate(SAMPLE_RACE_CONTROL)
        assert obj.category == "Flag"
        assert obj.flag == "BLACK AND WHITE"
        assert obj.lap_number == 59

    def test_session_valid(self):
        obj = Session.model_validate(SAMPLE_SESSION)
        assert obj.session_name == "Sprint Qualifying"
        assert obj.circuit_short_name == "Spa-Francorchamps"
        assert obj.year == 2023

    def test_session_result_valid_single_and_array_durations(self):
        obj = SessionResult.model_validate(SAMPLE_SESSION_RESULT)
        assert obj.position == 1
        assert obj.duration == 77.565
        assert obj.number_of_laps == 24

        # Teste com lista de tempos (formato de Qualifying)
        quali_result = {
            "dnf": False,
            "dns": False,
            "dsq": False,
            "driver_number": 1,
            "duration": [78.1, 77.8, 77.2],
            "gap_to_leader": [0.0, 0.0, 0.0],
            "number_of_laps": 18,
            "meeting_key": 1143,
            "position": 1,
            "session_key": 7782,
        }
        quali_obj = SessionResult.model_validate(quali_result)
        assert isinstance(quali_obj.duration, list)
        assert len(quali_obj.duration) == 3

    def test_starting_grid_valid(self):
        obj = StartingGrid.model_validate(SAMPLE_STARTING_GRID)
        assert obj.position == 1
        assert obj.driver_number == 1
        assert obj.lap_duration == 76.732

    def test_stint_valid(self):
        obj = Stint.model_validate(SAMPLE_STINT)
        assert obj.compound == "SOFT"
        assert obj.stint_number == 1
        assert obj.tyre_age_at_start == 3

    def test_team_radio_valid(self):
        obj = TeamRadio.model_validate(SAMPLE_TEAM_RADIO)
        assert obj.driver_number == 11
        assert "radio.mp3" in obj.recording_url

    def test_weather_valid(self):
        obj = Weather.model_validate(SAMPLE_WEATHER)
        assert obj.air_temperature == 27.8
        assert obj.track_temperature == 52.5
        assert obj.rainfall == 0
        assert obj.wind_speed == 2.4
