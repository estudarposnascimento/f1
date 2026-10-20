"""Testes unitários para o construtor e serializador de filtros."""

from datetime import date, datetime, timezone

from f1.core.filters import (
    build_filter_params,
    encode_query_string,
    serialize_value,
)


class TestFilters:
    """Valida a conversão e formatação de parâmetros de consulta da OpenF1."""

    def test_serialize_value(self):
        assert serialize_value(True) == "true"
        assert serialize_value(False) == "false"
        assert serialize_value(123) == "123"
        assert serialize_value(45.67) == "45.67"
        assert serialize_value("latest") == "latest"

        dt = datetime(2023, 9, 15, 13, 8, 19, tzinfo=timezone.utc)
        assert serialize_value(dt) == "2023-09-15T13:08:19+00:00"

        d = date(2023, 9, 15)
        assert serialize_value(d) == "2023-09-15"

    def test_build_filter_params_operators(self):
        params = build_filter_params(
            speed__gte=315,
            rpm__gt=11000,
            throttle__lte=90,
            lap_duration__lt=92.5,
            driver_number__eq=44,
        )
        assert ("speed>=", "315") in params
        assert ("rpm>", "11000") in params
        assert ("throttle<=", "90") in params
        assert ("lap_duration<", "92.5") in params
        assert ("driver_number", "44") in params

    def test_build_filter_params_direct_operators(self):
        params = build_filter_params(**{"speed>=": 300, "date_start<=": "2024-01-01"})
        assert ("speed>=", "300") in params
        assert ("date_start<=", "2024-01-01") in params

    def test_build_filter_params_multi_values(self):
        params = build_filter_params(driver_number=[4, 81])
        assert ("driver_number", "4") in params
        assert ("driver_number", "81") in params
        assert len(params) == 2

    def test_build_filter_params_none_values_ignored(self):
        params = build_filter_params(session_key="latest", driver_number=None)
        assert params == [("session_key", "latest")]

    def test_encode_query_string(self):
        params = [("speed>=", "315"), ("driver_number", "55")]
        qs = encode_query_string(params)
        # Verifica que o operador >= foi preservado sem urlencode (%3E%3D)
        assert "speed>=315" in qs
        assert "driver_number=55" in qs

    def test_encode_query_string_from_dict(self):
        data = {"speed__gte": 315, "session_key": "latest"}
        qs = encode_query_string(data)
        assert "speed>=315" in qs
        assert "session_key=latest" in qs

