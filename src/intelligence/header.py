import pandas as pd
from typing import Optional


class HeaderDetector:
    """
    Detect the most likely header row in a raw DataFrame and apply it as column names.

    The detector looks for rows that contain both time-related and
    consumption-related keywords and treats the best matching row as the header.
    """

    # Keywords used to identify time-related columns
    TIME_KEYS = ["time", "date", "datum", "timestamp", "zeit", "uhrzeit"]

    # Keywords used to identify consumption-related columns
    CONS_KEYS = [
        "consumption",
        "kw",
        "kwh",
        "energy",
        "verbrauch",
        "power",
        "wirkleistung",
    ]

    def __init__(self, table: pd.DataFrame) -> None:
        """
        Parameters
        ----------
        table : pd.DataFrame
            Raw table where the header row may not yet be set as column names.
        """
        self.table = table

    @staticmethod
    def _norm(x) -> str:
        """
        Normalize a cell value for comparison.

        - Convert NaN to an empty string
        - Strip leading/trailing whitespace
        - Convert to lowercase
        """
        if pd.isna(x):
            return ""
        return str(x).strip().lower()

    def find_header_row(self) -> int:
        """
        Scan all rows and return the index of the row
        that looks most like a header.

        A row is scored based on whether it contains any
        time-related and/or consumption-related keywords.

        Returns
        -------
        int
            Index of the detected header row.

        Raises
        ------
        ValueError
            If no suitable header row can be detected.
        """
        best_row: Optional[int] = None
        best_score = 0

        for i in range(len(self.table)):
            # Normalize all values in this row
            row_vals = [self._norm(v) for v in self.table.iloc[i]]

            # Join them into a single string for simple substring search
            row_text = " | ".join(row_vals)

            # Check if any time keyword appears anywhere in this row
            time_hit = any(k in row_text for k in self.TIME_KEYS)
            # Check if any consumption keyword appears anywhere in this row
            cons_hit = any(k in row_text for k in self.CONS_KEYS)

            score = int(time_hit) + int(cons_hit)

            if score > best_score:
                best_score = score
                best_row = i

        if best_row is None:
            raise ValueError("Header row could not be detected in the DataFrame.")

        return best_row

    def apply_header(self) -> pd.DataFrame:
        """
        Detect the header row, use that row as column names,
        update the internal table, and return the cleaned DataFrame.

        The detected header row is removed from the data; its values
        become the column names of the remaining rows.

        Returns
        -------
        pd.DataFrame
            A new DataFrame with:
            - the detected header row removed, and
            - normalized column names applied.

        Notes
        -----
        This method updates ``self.table`` in-place to the cleaned version.
        """
        hdr_idx = self.find_header_row()

        # New column names (normalized)
        new_cols = [self._norm(c) for c in self.table.iloc[hdr_idx]]

        # Data rows below the header
        new_table = self.table.iloc[hdr_idx + 1 :].copy()
        new_table.columns = new_cols
        new_table.reset_index(drop=True, inplace=True)

        # Update internal state
        self.table = new_table

        return new_table
