"""Módulo de clientes de comunicação de rede para a OpenF1 API."""

from f1.clients.base import BaseHTTPClient
from f1.clients.openf1 import OpenF1Client

__all__ = [
    "BaseHTTPClient",
    "OpenF1Client",
]
