"""Testes unitários para utilitários de datetime e pandas DataFrame."""

from datetime import UTC, datetime, timezone

import pandas as pd

from f1.core.models import Driver
from f1.utils.dataframe import to_dataframe
from f1.utils.datetime import format_utc_iso, parse_iso_datetime
from tests.conftest import SAMPLE_DRIVER


class TestDataframeUtils:
    """Valida a conversão de coleções e payloads para pandas DataFrame."""

    def test_to_dataframe_from_models(self):
        driver = Driver.model_validate(SAMPLE_DRIVER)
        df = to_dataframe([driver])
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert df["name_acronym"].iloc[0] == "VER"
        assert df["driver_number"].iloc[0] == 1

    def test_to_dataframe_from_dicts(self):
        df = to_dataframe([SAMPLE_DRIVER])
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert df["full_name"].iloc[0] == "Max VERSTAPPEN"

    def test_to_dataframe_empty_list(self):
        df = to_dataframe([])
        assert isinstance(df, pd.DataFrame)
        assert df.empty

    def test_to_dataframe_from_csv_string(self):
        csv_data = "driver_number,name_acronym,team_name\n1,VER,Red Bull\n44,HAM,Mercedes\n"
        df = to_dataframe(csv_data)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert list(df["driver_number"]) == [1, 44]

    def test_to_dataframe_from_empty_csv_string(self):
        df = to_dataframe("   \n  ")
        assert isinstance(df, pd.DataFrame)
        assert df.empty


class TestDatetimeUtils:
    """Valida funções de parsing e formatação temporal."""

    def test_parse_iso_datetime_with_utc_offset(self):
        iso_str = "2023-09-15T13:08:19.923000+00:00"
        dt = parse_iso_datetime(iso_str)
        assert dt.year == 2023
        assert dt.month == 9
        assert dt.day == 15
        assert dt.tzinfo is not None

    def test_parse_iso_datetime_with_z_suffix(self):
        iso_str = "2023-09-15T13:08:19.923000Z"
        dt = parse_iso_datetime(iso_str)
        assert dt.year == 2023
        assert dt.tzinfo == UTC

    def test_parse_iso_datetime_naive(self):
        iso_str = "2023-09-15T13:08:19"
        dt = parse_iso_datetime(iso_str)
        assert dt.tzinfo == UTC

    def test_format_utc_iso_naive(self):
        dt = datetime(2023, 9, 15, 13, 8, 19)
        formatted = format_utc_iso(dt)
        assert "+00:00" in formatted or "Z" in formatted

    def test_format_utc_iso_aware(self):
        dt = datetime(2023, 9, 15, 13, 8, 19, tzinfo=timezone.utc)
        formatted = format_utc_iso(dt)
        assert formatted == "2023-09-15T13:08:19+00:00"

