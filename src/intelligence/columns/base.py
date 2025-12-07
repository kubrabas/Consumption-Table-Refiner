import re
import pandas as pd


class BaseColumnDetector:
    """
    Base class for column detectors.

    Holds a reference to the table and provides shared helpers.
    """

    def __init__(self, table: pd.DataFrame):
        self.table = table
        self.columns = list(table.columns)

    @staticmethod
    def _norm(name: str) -> str:
        """
        Normalize a column name for comparison.

        - Convert to lowercase
        - Replace common separators with spaces
        - Collapse multiple spaces into a single space
        - Strip leading and trailing spaces
        """
        s = str(name).lower()

        # Replace common separators with spaces
        for ch in ["/", "-", "_", ".", ",", "|", "\\"]:
            s = s.replace(ch, " ")

        # Collapse multiple whitespace characters into a single space
        s = re.sub(r"\s+", " ", s).strip()

        return s