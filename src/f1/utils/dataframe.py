"""Utilitários de conversão e integração com pandas DataFrame."""

from collections.abc import Sequence
from io import StringIO
from typing import Any

import pandas as pd
from pydantic import BaseModel


def to_dataframe(
    data: Sequence[BaseModel | dict[str, Any]] | str,
) -> pd.DataFrame:
    """Converte modelos Pydantic, dicionários ou strings CSV em um pandas.DataFrame.

    Args:
        data: Sequência de modelos OpenF1/BaseModel, dicionários de resposta ou string CSV.

    Returns:
        pandas.DataFrame estruturado.
    """
    if isinstance(data, str):
        if not data.strip():
            return pd.DataFrame()
        return pd.read_csv(StringIO(data))

    if not data:
        return pd.DataFrame()

    records: list[dict[str, Any]] = []
    for item in data:
        if isinstance(item, BaseModel):
            records.append(item.model_dump())
        elif isinstance(item, dict):
            records.append(item)
        else:
            records.append(dict(item))

    return pd.DataFrame(records)
