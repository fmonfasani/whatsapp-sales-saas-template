"""Ingestion layer: multimodal preprocessing → Hindsight RAG."""

from __future__ import annotations

from sample.ingestion.extractors import (
    CsvExtractor,
    DocxExtractor,
    ExtractedChunk,
    ExtractorPort,
    MockAudioExtractor,
    MockImageExtractor,
    MockVideoExtractor,
    PdfExtractor,
    UnsupportedFormatError,
)
from sample.ingestion.hindsight import HindsightPort, InMemoryHindsight, PostgresHindsight
from sample.ingestion.preprocessor import Preprocessor, default_extractors

__all__ = [
    "CsvExtractor",
    "DocxExtractor",
    "ExtractedChunk",
    "ExtractorPort",
    "HindsightPort",
    "InMemoryHindsight",
    "MockAudioExtractor",
    "MockImageExtractor",
    "MockVideoExtractor",
    "PdfExtractor",
    "PostgresHindsight",
    "Preprocessor",
    "UnsupportedFormatError",
    "default_extractors",
]
