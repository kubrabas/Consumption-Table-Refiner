from typing import List
import pandas as pd

from .base import BaseColumnDetector


class TimeColumnDetector(BaseColumnDetector):
    """
    Detect time-related columns based on column names only.
    """

    TIME_KEYWORDS = [
        "time",
        "date",
        "datum",
        "timestamp",
        "zeit",
        "uhrzeit",
        "datetime",
        "from",
        "to",
        "von",
        "bis",
        "ab"
    ]

    def __init__(self, table: pd.DataFrame) -> None:
        super().__init__(table)

    def _has_time_keyword(self, name: str) -> bool:
        n = self._norm(name)
        return any(keyword in n for keyword in self.TIME_KEYWORDS)

    def detect_time_columns(self) -> List[str]:
        return [col for col in self.columns if self._has_time_keyword(col)]
