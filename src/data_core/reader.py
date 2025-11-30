import pandas as pd
import os

class DataReader:
    """
    Responsibility: To safely read the raw Excel data file (XLSX/XLS), 
    detect its format, and return a Pandas DataFrame. 
    CSV support has been explicitly removed.
    """
    def __init__(self, file_path):
        self.file_path = file_path
        # Automatically determine file type upon initialization
        self.file_extension = os.path.splitext(file_path)[1].lower()
        self.df = None
        
        # skiprows is set to 0 (Excel usually handles headers well)
        self.skiprows = 0

    # The CSV-specific "_determine_csv_params" method has been REMOVED entirely.

    def read_data(self):
        """
        Reads the data using the appropriate Pandas function based on file extension.
        Only XLSX and XLS formats are supported.
        """
        if self.file_extension in ['.xlsx', '.xls']:
            # Read the Excel file 
            # Note: skiprows=0 is the default, but explicitly kept for clarity
            self.df = pd.read_excel(self.file_path, skiprows=self.skiprows)
            
        else:
            # Only accept Excel formats.
            raise ValueError(f"Unsupported file type: {self.file_extension}. Only XLSX/XLS formats are accepted.")

        if self.df is None or self.df.empty:
            raise ValueError("Data failed to load or the file is empty after reading.")
            
        return self.df

    def clean_dataframe(self):
        """
        Drop columns and rows that are completely NaN.
        """
        self.df = self.df.dropna(axis=1, how='all')
        self.df = self.df.dropna(axis=0, how='all')

        return self.df
    

    def drop_unnamed(self):
        """
        If all column names start with 'Unnamed', treat the first row as data,
        use the second row as the header, and drop the original header row.
        """

        # Convert column names to strings and check them
        col_names = [str(c) for c in self.df.columns]

        # If all column names start with 'Unnamed'
        if all(name.startswith("Unnamed") or name == "nan" for name in col_names):
        # Use the first row as the new header
            new_header = self.df.iloc[0]   # row 0
            self.df = self.df[1:]          # drop the first row
            self.df.columns = new_header   # set new column names
            self.df = self.df.reset_index(drop=True)  # reset the index
            return self.df

