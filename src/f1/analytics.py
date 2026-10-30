"""Facade pública para o pipeline analítico OpenF1."""

from f1.pipeline.common import IngestionResult, TransformationResult
from f1.pipeline.marts import MartsLayer

__all__ = ["F1AnalyticsPipeline", "IngestionResult", "TransformationResult"]


class F1AnalyticsPipeline(MartsLayer):
    """API compatível que compõe database, RAW, REFINED e marts."""
