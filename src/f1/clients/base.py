"""Cliente HTTP base com retry exponencial, timeouts e tratamento defensivo."""

from typing import Any
from urllib.parse import urlencode

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from f1.core.filters import build_filter_params
from f1.exceptions import (
    OpenF1APIError,
    OpenF1ConnectionError,
)

DEFAULT_TIMEOUT = 15.0
DEFAULT_BASE_URL = "https://api.openf1.org/v1"


class BaseHTTPClient:
    """Cliente HTTP com pool de conexões resiliente e retries automáticos."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        session: requests.Session | None = None,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
    ) -> None:
        """Inicializa o cliente HTTP.

        Args:
            base_url: URL base dos serviços da API.
            timeout: Tempo limite de espera para requisições em segundos.
            session: Sessão requests existente (opcional).
            max_retries: Quantidade máxima de tentativas em erros transitórios.
            backoff_factor: Fator de multiplicação para espera exponencial entre retries.
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or self._create_resilient_session(
            max_retries=max_retries,
            backoff_factor=backoff_factor,
        )

    def _create_resilient_session(
        self,
        max_retries: int,
        backoff_factor: float,
    ) -> requests.Session:
        """Cria e configura uma sessão requests com retries em códigos de erro transitórios."""
        session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": "OpenF1-Python-SDK/0.1.0",
            }
        )
        return session

    def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        as_csv: bool = False,
    ) -> Any:
        """Executa uma chamada HTTP GET contra um endpoint da API.

        Args:
            endpoint: Caminho relativo do endpoint (ex: '/car_data' ou 'car_data').
            params: Dicionário de filtros e parâmetros de busca.
            as_csv: Se True, requisita formato CSV e retorna o texto puro.

        Returns:
            Lista de dicionários (JSON) ou string (CSV).

        Raises:
            OpenF1APIError: Se o servidor retornar status 4xx ou 5xx.
            OpenF1ConnectionError: Se houver timeout ou erro de conexão de rede.
        """
        clean_endpoint = endpoint.lstrip("/")
        url = f"{self.base_url}/{clean_endpoint}"

        query_params = build_filter_params(**(params or {}))
        if as_csv:
            query_params.append(("csv", "true"))

        # Montagem de query string com suporte a caracteres literais (>=, <=)
        query_string = urlencode(query_params, safe=">=<,")
        full_url = f"{url}?{query_string}" if query_string else url

        headers: dict[str, str] = {}
        if as_csv:
            headers["Accept"] = "text/csv, text/plain; q=0.9, */*; q=0.8"

        try:
            response = self.session.get(
                full_url,
                timeout=self.timeout,
                headers=headers if headers else None,
            )
        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
        ) as exc:
            raise OpenF1ConnectionError(
                f"Falha de conexão ao acessar {url}: {exc}"
            ) from exc
        except requests.exceptions.RequestException as exc:
            raise OpenF1ConnectionError(
                f"Erro na requisição HTTP para {url}: {exc}"
            ) from exc

        if response.status_code >= 400:
            raise OpenF1APIError(
                status_code=response.status_code,
                message=f"Falha na requisição para {url}: {response.reason}",
                response_body=response.text,
            )

        if as_csv:
            return response.text

        try:
            return response.json()
        except Exception as exc:
            raise OpenF1APIError(
                status_code=response.status_code,
                message=f"Falha ao decodificar JSON retornado de {url}: {exc}",
                response_body=response.text,
            ) from exc

    def close(self) -> None:
        """Fecha a sessão HTTP subjacente liberando conexões de rede."""
        self.session.close()

    def __enter__(self) -> "BaseHTTPClient":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

