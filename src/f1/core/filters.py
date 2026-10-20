"""Mecanismos de construção e parsing de filtros para a OpenF1 API."""

from collections.abc import Iterable
from datetime import date, datetime
from typing import Any
from urllib.parse import urlencode

OPERATOR_MAP = {
    "__gte": ">=",
    "__gt": ">",
    "__lte": "<=",
    "__lt": "<",
    "__eq": "",
}


def serialize_value(val: Any) -> str:
    """Serializa tipos Python primitivos para formatos compatíveis com a OpenF1 API.

    Args:
        val: Valor a ser serializado (bool, datetime, int, float, str, etc.).

    Returns:
        Representação em string adequada para a URL.
    """
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, (datetime, date)):
        return val.isoformat()
    return str(val)


def build_filter_params(**kwargs: Any) -> list[tuple[str, str]]:
    """Constrói uma lista de pares chave-valor para parâmetros de query string.

    Suporta:
    - Sufixos de operadores: `__gte`, `__gt`, `__lte`, `__lt`, `__eq`
      Exemplo: `speed__gte=315` -> `("speed>=", "315")`
    - Chaves que já contenham operadores diretos:
      Exemplo: `**{"speed>=": 315}` -> `("speed>=", "315")`
    - Valores múltiplos (listas/tuplas/conjuntos):
      Exemplo: `driver_number=[4, 81]` -> `[("driver_number", "4"), ("driver_number", "81")]`
    - Valores `None` são ignorados.

    Args:
        **kwargs: Parâmetros de filtro nomeados.

    Returns:
        Lista de tuplas (chave_parametro, valor_parametro).
    """
    params: list[tuple[str, str]] = []

    for key, raw_value in kwargs.items():
        if raw_value is None:
            continue

        param_key = key
        for suffix, op in OPERATOR_MAP.items():
            if key.endswith(suffix):
                param_key = key[: -len(suffix)] + op
                break

        if isinstance(raw_value, (list, tuple, set)) and not isinstance(
            raw_value, (str, bytes)
        ):
            values: Iterable[Any] = raw_value
        else:
            values = [raw_value]

        for val in values:
            if val is not None:
                params.append((param_key, serialize_value(val)))

    return params


def encode_query_string(params: list[tuple[str, str]] | dict[str, Any]) -> str:
    """Codifica parâmetros para query string preservando operadores de comparação.

    A OpenF1 aceita operadores literais como `>=`, `<=`, `>`, `<`.
    Esta função utiliza `safe=">=<,"` para manter legibilidade e conformidade
    com a especificação técnica da API.

    Args:
        params: Lista de tuplas ou dicionário com os parâmetros.

    Returns:
        Query string formatada (sem a interrogação inicial).
    """
    if isinstance(params, dict):
        param_list = build_filter_params(**params)
    else:
        param_list = params

    return urlencode(param_list, safe=">=<,")

