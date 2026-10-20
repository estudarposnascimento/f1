"""Exceções de domínio do OpenF1 SDK."""


class OpenF1Exception(Exception):
    """Exceção base para todos os erros da biblioteca f1."""


class OpenF1APIError(OpenF1Exception):
    """Exceção levantada quando a API da OpenF1 retorna um status de erro HTTP (4xx ou 5xx)."""

    def __init__(
        self,
        status_code: int,
        message: str,
        response_body: str | None = None,
    ) -> None:
        self.status_code = status_code
        self.message = message
        self.response_body = response_body
        super().__init__(f"OpenF1 API Error [{status_code}]: {message}")


class OpenF1ConnectionError(OpenF1Exception):
    """Exceção levantada em falhas de rede, conexões recusadas ou timeouts."""


class OpenF1ValidationError(OpenF1Exception):
    """Exceção levantada quando parâmetros ou dados de resposta são inválidos."""
