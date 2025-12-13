from __future__ import annotations

from typing import List
import pandas as pd

from .base import BaseColumnDetector


# ==============================================================================
# 1) Detector
# ==============================================================================
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
        "ab",
    ]

    def __init__(self, table: pd.DataFrame) -> None:
        super().__init__(table)

    def _has_time_keyword(self, name: str) -> bool:
        n = self._norm(name)
        return any(keyword in n for keyword in self.TIME_KEYWORDS)

    def detect_time_columns(self) -> List[str]:
        return [col for col in self.columns if self._has_time_keyword(col)]


# ==============================================================================
# 2) Date + Hour -> Single timestamp
# ==============================================================================
class Preference_Date_And_Hour:
    """
    User selected two columns: one is DATE (day-month-year),
    the other is Hour/minute/seconds.
    """

    def __init__(self, table: pd.DataFrame, date_col: str):
        self.table = table
        self.date_col = date_col

    def detect_date_dtype(self) -> str:
        """
        Returns: "string"

        Behavior:
        - If DATE column is datetime-like: drop time part and convert to YYYY-MM-DD (string)
        - If DATE column is string/object: parse -> drop time part -> YYYY-MM-DD (string)
        """
        if self.date_col not in self.table.columns:
            raise KeyError(f"Date column not found: {self.date_col}")

        s = self.table[self.date_col]

        # Case 1: datetime-like -> drop time, convert to date string
        if pd.api.types.is_datetime64_any_dtype(s):
            norm = s.dt.normalize()
            self.table[self.date_col] = norm.dt.strftime("%Y-%m-%d").astype("string")
            return "string"

        # Case 2: string/object -> parse -> drop time -> convert to date string
        if pd.api.types.is_string_dtype(s) or pd.api.types.is_object_dtype(s):
            parsed = pd.to_datetime(s, errors="coerce")  # istersek dayfirst ekleriz sonra
            if parsed.notna().sum() == 0 and s.dropna().shape[0] > 0:
                raise ValueError(
                    f"Could not parse any values in DATE column '{self.date_col}' as datetime."
                )

            norm = parsed.dt.normalize()
            self.table[self.date_col] = norm.dt.strftime("%Y-%m-%d").astype("string")
            return "string"

        raise TypeError(
            f"Preference_Date_And_Hour expects DATE column to be datetime or string/object, "
            f"but got dtype={s.dtype} for column '{self.date_col}'."
        )
