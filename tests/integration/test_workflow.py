"""Testes de integração do fluxo completo de ponta a ponta (E2E workflow)."""

from unittest.mock import MagicMock

import pandas as pd

from f1.clients.openf1 import OpenF1Client
from f1.utils.dataframe import to_dataframe
from tests.conftest import (
    SAMPLE_CAR_DATA,
    SAMPLE_DRIVER,
    SAMPLE_LAP,
    SAMPLE_SESSION,
)


class TestE2EWorkflow:
    """Simula o ciclo analítico completo: Sessão -> Pilotos -> Voltas -> Telemetria -> DataFrame."""

    def test_complete_telemetry_analysis_flow(self, mock_response_builder):
        # Configura as respostas sequenciais da API
        session_mock = MagicMock()

        car_telemetry_point_1 = dict(SAMPLE_CAR_DATA)
        car_telemetry_point_1["speed"] = 310
        car_telemetry_point_1["rpm"] = 11000

        car_telemetry_point_2 = dict(SAMPLE_CAR_DATA)
        car_telemetry_point_2["speed"] = 320
        car_telemetry_point_2["rpm"] = 11200

        # Respostas em sequência para chamadas sucessivas
        session_mock.get.side_effect = [
            mock_response_builder(json_data=[SAMPLE_SESSION]),
            mock_response_builder(json_data=[SAMPLE_DRIVER]),
            mock_response_builder(json_data=[SAMPLE_LAP]),
            mock_response_builder(
                json_data=[car_telemetry_point_1, car_telemetry_point_2]
            ),
        ]

        client = OpenF1Client(session=session_mock)

        # 1. Obter informações da sessão de 2023
        sessions = client.get_sessions(year=2023, session_name="Sprint Qualifying")
        assert len(sessions) == 1
        active_session = sessions[0]
        assert active_session.session_key == 9140

        # 2. Obter pilotos participantes
        drivers = client.get_drivers(session_key=active_session.session_key)
        assert len(drivers) == 1
        driver = drivers[0]
        assert driver.driver_number == 1
        assert driver.name_acronym == "VER"

        # 3. Consultar voltas do piloto
        laps = client.get_laps(
            session_key=active_session.session_key,
            driver_number=driver.driver_number,
        )
        assert len(laps) == 1
        assert laps[0].lap_number == 8

        # 4. Obter telemetria em alta frequência
        telemetry = client.get_car_data(
            session_key=active_session.session_key,
            driver_number=driver.driver_number,
            speed__gte=300,
        )
        assert len(telemetry) == 2

        # 5. Converter telemetria em DataFrame e calcular agregações
        df = to_dataframe(telemetry)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert "speed" in df.columns
        assert "rpm" in df.columns

        mean_speed = df["speed"].mean()
        max_rpm = df["rpm"].max()

        assert mean_speed == 315.0
        assert max_rpm == 11200

