"""Corpus repository for Wang Zengqi quotes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class CorpusRepository:
    """Load and summarize the local corpus under ``data/corpus``."""

    def __init__(self, corpus_dir: Path | None = None) -> None:
        project_root = Path(__file__).resolve().parents[2]
        self.corpus_dir = corpus_dir or project_root / "data" / "corpus"
        self.raw_quotes_path = self.corpus_dir / "wangzengqi_quotes.txt"
        self.structured_quotes_path = self.corpus_dir / "wangzengqi_quotes.json"

    def load_raw_quotes(self) -> list[str]:
        """Load raw quotes, one line per quote."""
        if not self.raw_quotes_path.exists():
            return []

        lines = self._read_text_with_fallback(self.raw_quotes_path).splitlines()
        return [line.strip() for line in lines if line.strip() and not line.startswith("#")]

    def load_structured_quotes(self) -> list[dict[str, Any]]:
        """Load structured quotes from JSON."""
        if not self.structured_quotes_path.exists():
            return []

        data = json.loads(self._read_text_with_fallback(self.structured_quotes_path))
        if not isinstance(data, list):
            return []

        cleaned_quotes: list[dict[str, Any]] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            if not item.get("text"):
                continue
            cleaned_quotes.append(item)
        return cleaned_quotes

    def get_corpus_stats(self) -> dict[str, Any]:
        """Return a compact corpus summary for planner decisions."""
        raw_quotes = self.load_raw_quotes()
        structured_quotes = self.load_structured_quotes()

        themes = sorted(
            {
                theme
                for item in structured_quotes
                for theme in item.get("theme", [])
                if isinstance(theme, str) and theme
            }
        )

        return {
            "corpus_dir": str(self.corpus_dir),
            "raw_quote_count": len(raw_quotes),
            "structured_quote_count": len(structured_quotes),
            "themes": themes,
            "ready": bool(raw_quotes or structured_quotes),
        }

    def _read_text_with_fallback(self, path: Path) -> str:
        """Read corpus files with a small encoding fallback set."""
        for encoding in ("utf-8", "utf-8-sig", "gbk", "gb18030"):
            try:
                return path.read_text(encoding=encoding)
            except UnicodeDecodeError:
                continue
        return path.read_text(encoding="utf-8", errors="ignore")
