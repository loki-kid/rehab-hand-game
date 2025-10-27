"""
Player progress logging and data persistence.

Responsibilities:
- Append session metrics (score, level, timestamps) to a storage format
- Provide simple APIs for exporting/loading progress for future analytics
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, List

# Placeholder import note (uncomment when implementing):
# import pandas as pd


class DataLogger:
    """Stub for writing and reading player progress data."""

    def __init__(self, output_dir: Path | str = "data") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.records: List[Dict[str, Any]] = []

    def log(self, payload: Dict[str, Any]) -> None:
        """Buffer a record for later flush to disk."""
        self.records.append(payload)

    def flush(self) -> None:
        """Persist buffered records to disk (implement CSV/Parquet later)."""
        # Placeholder: write a minimal marker file when records exist
        if self.records:
            (self.output_dir / "LOG.TXT").write_text("records buffered: " + str(len(self.records)))
