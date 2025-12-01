import pandas as pd

class HeaderDetector:
    """
    Detects the most likely header row in a raw DataFrame and applies it as column names.
    """
    TIME_KEYS = ["time", "date", "datum", "timestamp", "zeit", "uhrzeit"]
    CONS_KEYS = ["consumption", "kw", "kwh", "energy", "verbrauch", "power", "wirkleistung"]

    def __init__(self, df):
        self.df = df

    @staticmethod
    def _norm(x):
        if pd.isna(x):
            return ""
        return str(x).strip().lower()

    def find_header_row(self):
        """
        Scan all rows and return the index of the row
        that looks most like a header (contains time + consumption keywords).
        """
        best_row = None
        best_score = 0

        for i in range(len(self.df)):
            # normalize all values in this row
            row_vals = [self._norm(v) for v in self.df.iloc[i]]
            # join them into a single string for simple substring search
            row_text = " | ".join(row_vals)

            # check if any time keyword appears anywhere in this row
            time_hit = any(k in row_text for k in self.TIME_KEYS)
            # check if any consumption keyword appears anywhere in this row
            cons_hit = any(k in row_text for k in self.CONS_KEYS)

            score = int(time_hit) + int(cons_hit)

            if score > best_score:
                best_score = score
                best_row = i

        if best_row is None:
            raise ValueError("Header row could not be detected in the DataFrame.")

        return best_row

    def apply_header(self):
        """
        Detect the header row, use that row as column names,
        and return the DataFrame with data rows only.
        """
        hdr_idx = self.find_header_row()

        # new column names (normalized)
        new_cols = [self._norm(c) for c in self.df.iloc[hdr_idx]]
        new_df = self.df.iloc[hdr_idx+1:].copy()
        new_df.columns = new_cols
        new_df.reset_index(drop=True, inplace=True)

        return new_df
