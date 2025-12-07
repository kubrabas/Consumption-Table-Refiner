from typing import Optional

import pandas as pd
from pandas.api.types import is_numeric_dtype

from .base import BaseColumnDetector


class ConsumptionColumnDetector(BaseColumnDetector):
    """
    Detect and normalize consumption-related columns in a table.
    """

    CONSUMPTION_KEYWORDS = [
        "consumption",
        "energy",
        "verbrauch",
        "power",
        "wirkleistung",
        "kw",
        "kwh",
    ]

    def __init__(self, table: pd.DataFrame):
        """
        Parameters
        ----------
        table : pd.DataFrame
            The input table that contains multiple columns, including
            consumption-related columns.
        """
        super().__init__(table)

        self.consumption_column: Optional[str] = None
        self.consumption_unit: Optional[str] = None  # "kwh", "kw", or None

    def _detect_consumption_unit_from_name(self, name: str) -> Optional[str]:
        """
        Try to infer the unit ("kwh" or "kw") from the column name.
        """
        n = self._norm(name)
        if "kwh" in n:
            return "kwh"
        elif "kw" in n:
            return "kw"
        return None

    def _has_consumption_keyword(self, name: str) -> bool:
        """
        Check if the column name looks consumption-related.
        """
        n = self._norm(name)
        return any(keyword in n for keyword in self.CONSUMPTION_KEYWORDS)

    def _numeric_likeness_score(self, series: pd.Series) -> int:
        """
        Score how numeric-like a column is.

        Returns
        -------
        int
            2 if the dtype is already numeric,
            1 if it is not numeric but can mostly be converted to numeric,
            0 otherwise.
        """
        if is_numeric_dtype(series):
            return 2

        coerced = pd.to_numeric(series, errors="coerce")
        non_na_ratio = coerced.notna().mean()

        if non_na_ratio >= 0.8:  # threshold can be tuned
            return 1

        return 0

    def detect_consumption_column(self) -> str:
        """
        Detect the most likely consumption-related column.

        Preference order:
        1. Column with kWh in its name
        2. Column with kW in its name
        3. Column without explicit unit but with consumption-related keywords

        Numeric or numeric-like columns are preferred.

        Returns
        -------
        str
            The name of the detected consumption column.

        Raises
        ------
        ValueError
            If no suitable consumption column can be found.
        """
        best_col: Optional[str] = None
        best_score = (-1, -1, -1)  # (has_keyword, unit_score, numeric_score)

        for col in self.columns:
            series = self.table[col]

            name_norm = self._norm(col)
            has_keyword = int(self._has_consumption_keyword(name_norm))
            unit = self._detect_consumption_unit_from_name(name_norm)
            unit_score = 2 if unit == "kwh" else 1 if unit == "kw" else 0
            numeric_score = self._numeric_likeness_score(series)

            score = (has_keyword, unit_score, numeric_score)

            if score > best_score:
                best_score = score
                best_col = col

        # Require at least some consumption signal (keyword or unit),
        # not just "numeric-looking".
        if best_col is None or (best_score[0] == 0 and best_score[1] == 0):
            raise ValueError("No suitable consumption column found.")

        self.consumption_column = best_col
        self.consumption_unit = self._detect_consumption_unit_from_name(best_col)

        return best_col

    def to_kwh(self, new_column_name: str = "consumption_kwh") -> pd.Series:
        """
        Return a consumption series in kWh and store it as a new column.

        If the detected unit is:
        - "kwh": values are used as-is.
        - "kw": values are divided by 4 (assuming quarter-hourly data).
        - None: values are assumed to be kWh and a warning is printed.

        Parameters
        ----------
        new_column_name : str, optional
            Name of the new column to store the kWh values in the table.

        Returns
        -------
        pd.Series
            The consumption series in kWh.

        Raises
        ------
        ValueError
            If the column cannot be converted to numeric.
        """
        if self.consumption_column is None:
            self.detect_consumption_column()

        col = self.consumption_column
        unit = self.consumption_unit

        series = pd.to_numeric(self.table[col], errors="coerce")

        if series.isna().all():
            raise ValueError(
                f"Column '{col}' cannot be converted to numeric values."
            )

        if unit == "kw":
            series = series / 4.0
        elif unit is None:
            print(
                f"Warning: No explicit unit found for column '{col}'. "
                "Assuming values are already in kWh."
            )

        # Store in the table as a standardized kWh column
        self.table[new_column_name] = series

        return series
