import pandas as pd


class TableRefiner:
    def __init__(self, table: pd.DataFrame):
        """
        Initialize the TableRefiner with a pandas DataFrame.

        Parameters
        ----------
        table : pd.DataFrame
            The table to be refined.
        """
        self.table = table
        self.columns = list(table.columns)

    def clean_table(self) -> pd.DataFrame:
        """
        Remove columns and rows that are entirely NaN.

        Returns
        -------
        pd.DataFrame
            The cleaned DataFrame.
        """
        # Drop columns that are completely NaN
        self.table = self.table.dropna(axis=1, how="all")

        # Drop rows that are completely NaN
        self.table = self.table.dropna(axis=0, how="all")

        # Update columns after cleaning
        self.columns = list(self.table.columns)

        return self.table

    def keep_only_moment_and_consumption(
        self,
        *,
        moment_col: str = "moment",
        consumption_col: str = "consumption_kwh",
    ) -> pd.DataFrame:
        """
        Keep only `moment_col` and `consumption_col` in the table.
        Drops all other columns (in-place) and updates `self.columns`.

        Returns
        -------
        pd.DataFrame
            The reduced DataFrame containing only [moment_col, consumption_col].
        """
        missing = [c for c in (moment_col, consumption_col) if c not in self.table.columns]
        if missing:
            raise KeyError(f"Missing required columns: {missing}")

        self.table = self.table[[moment_col, consumption_col]].copy()
        self.columns = list(self.table.columns)
        return self.table
    
        def drop_trailing_empty_rows(self) -> pd.DataFrame:
           """
           Drop rows at the very bottom of the table that are entirely NaN.
           (Only trims trailing empty rows; does not touch empty rows in the middle.)

           Returns
           -------
            pd.DataFrame
            The trimmed DataFrame.
            """
        if self.table.empty:
            return self.table

        # rows that are fully NaN
        fully_empty = self.table.isna().all(axis=1)

        if not fully_empty.any():
            return self.table

        # find last non-empty row index (position)
        non_empty_positions = (~fully_empty).to_numpy().nonzero()[0]
        if len(non_empty_positions) == 0:
            # everything is empty -> return empty df with same columns
            self.table = self.table.iloc[0:0].copy()
            self.columns = list(self.table.columns)
            return self.table

        last_keep_pos = non_empty_positions[-1]
        self.table = self.table.iloc[: last_keep_pos + 1].copy()

        self.columns = list(self.table.columns)
        return self.table

