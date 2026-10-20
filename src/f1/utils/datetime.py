"""Utilitários para parsing, normalização e formatação de datas e fusos horários."""

from datetime import UTC, datetime


def parse_iso_datetime(date_str: str) -> datetime:
    """Converte uma string ISO 8601 em um objeto datetime timezone-aware (UTC).

    Args:
        date_str: String de data no formato ISO 8601 (ex: '2023-09-15T13:08:19.923000+00:00').

    Returns:
        Objeto datetime correspondente no fuso horário UTC.
    """
    clean_str = date_str.replace("Z", "+00:00")
    dt = datetime.fromisoformat(clean_str)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def format_utc_iso(dt: datetime) -> str:
    """Formata um objeto datetime em string ISO 8601 no padrão esperado pela OpenF1.

    Args:
        dt: Objeto datetime a ser formatado.

    Returns:
        String ISO 8601 compatível com a API.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    else:
        dt = dt.astimezone(UTC)
    return dt.isoformat()

