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
        self.table = self.table.dropna(axis=1, how='all')

        # Drop rows that are completely NaN
        self.table = self.table.dropna(axis=0, how='all')

        # Update columns after cleaning
        self.columns = list(self.table.columns)

        return self.table
