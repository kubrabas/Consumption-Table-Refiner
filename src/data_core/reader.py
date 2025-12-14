import pandas as pd
import os
import csv

class DataReader:
    """
    Responsibility: To safely read the raw Excel data file (XLSX/XLS),
    detect its format, and return a Pandas DataFrame.
    CSV support added with automatic separator detection.
    """
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_extension = os.path.splitext(file_path)[1].lower()
        self.table = None

    def _detect_csv_separator(self, sample_bytes: int = 65536) -> str:
        """
        Detect CSV delimiter by sampling the file content.
        Tries csv.Sniffer first; falls back to common delimiters.
        """
        # Try common encodings for robust detection
        encodings_to_try = ["utf-8-sig", "utf-8", "cp1252", "latin1"]

        for enc in encodings_to_try:
            try:
                with open(self.file_path, "r", encoding=enc, newline="") as f:
                    sample = f.read(sample_bytes)

                # If file is extremely small or empty, Sniffer may fail
                if not sample.strip():
                    return ","

                try:
                    dialect = csv.Sniffer().sniff(sample, delimiters=[",", ";", "\t", "|"])
                    return dialect.delimiter
                except Exception:
                    # Fallback: choose the delimiter that appears most consistently
                    candidates = [",", ";", "\t", "|"]
                    counts = {d: sample.count(d) for d in candidates}
                    best = max(counts, key=counts.get)
                    return best if counts[best] > 0 else ","
            except Exception:
                continue

        # Final fallback
        return ","

    def read_data(self):
        """
        Reads the data using the appropriate Pandas function based on file extension.
        Supports XLSX/XLS and CSV (with auto separator detection).
        """
        if self.file_extension in [".xlsx", ".xls"]:
            self.table = pd.read_excel(
                self.file_path,
                skiprows=0,
                header=None
            )

        elif self.file_extension == ".csv":
            sep = self._detect_csv_separator()

            # Try a couple of encodings to be resilient
            encodings_to_try = ["utf-8-sig", "utf-8", "cp1252", "latin1"]
            last_err = None
            for enc in encodings_to_try:
                try:
                    self.table = pd.read_csv(
                        self.file_path,
                        sep=sep,
                        header=None,
                        encoding=enc,
                        engine="python"  # more tolerant for odd CSVs
                    )
                    last_err = None
                    break
                except Exception as e:
                    last_err = e

            if last_err is not None:
                raise ValueError(f"CSV could not be read. Detected sep='{sep}'. Last error: {last_err}")

        else:
            raise ValueError(
                f"Unsupported file type: {self.file_extension}. Only XLSX/XLS/CSV formats are accepted."
            )

        if self.table is None or self.table.empty:
            raise ValueError("Data failed to load or the file is empty after reading.")

        return self.table
