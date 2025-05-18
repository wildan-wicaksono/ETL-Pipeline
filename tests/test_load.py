from unittest.mock import patch, Mock, MagicMock
from utils.load import store_to_postgre, store_to_google_sheet, store_to_csv
from utils.transform import transform_to_df, transform_data
import pandas as pd
import os

sample_data = [
    {"Title": "Product A", "Price": "$100.0", "Rating": "4.5", "Colors": "2", "Size": "M", "Gender": "Unisex", "Timestamp": "2025-05-14T17:22:04.282749"},
    {"Title": "Product B", "Price": "$200.0", "Rating": "3.0", "Colors": "1", "Size": "L", "Gender": "Male", "Timestamp": "2025-05-14T17:22:04.387612"}
]

df = transform_to_df(sample_data) 
df = transform_data(df, 16000)


# ==================================== TESTING Store To CSV ====================================

class Test_StoreToCSV:
    def test_StoreToCSV(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        filename = "output.csv"
        store_to_csv(df, filename)

        saved_df = pd.read_csv(filename)

        assert os.path.exists(filename)
        assert saved_df.shape == df.shape 
        assert list(saved_df.columns) == list(df.columns)

    @patch("pandas.DataFrame.to_csv", side_effect=Exception("Mocked error"))
    def test_store_to_csv_exception(self, mock_to_csv):
        store_to_csv(df, "anyfile.csv") 
        assert mock_to_csv.called

# ==================================== TESTING Store To Postgre ====================================

class Test_StoreToPostgre:
    @patch("utils.load.create_engine")
    def test_store_to_postgre_success(self, mock_create_engine):
        mock_engine = MagicMock()
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection

        mock_create_engine.return_value = mock_engine

        store_to_postgre(df, "postgresql://dummy_url")

        assert mock_create_engine.called
        assert mock_connection is not None

    @patch("utils.load.create_engine", side_effect=Exception("Mocked DB error"))
    def test_store_to_postgre_exception(self, mock_create_engine):
        store_to_postgre(df, "postgresql://dummy_url")
        assert mock_create_engine.called


# ==================================== TESTING Store To Google Sheets ====================================
class Test_StoreToGoogleSheets:
    @patch("utils.load.build")
    def test_store_to_google_sheet_success(self, mock_build):
        mock_service = MagicMock()
        mock_sheet = MagicMock()
        mock_update = MagicMock()

        mock_build.return_value = mock_service
        mock_service.spreadsheets.return_value = mock_sheet
        mock_sheet.values.return_value.update.return_value.execute.return_value = {"updatedCells": 7}

        store_to_google_sheet(df)

        assert mock_build.called
        assert mock_sheet.values.return_value.update.called

    @patch("utils.load.build", side_effect=Exception("Google API failure"))
    def test_store_to_google_sheet_failure(self, mock_build):
        store_to_google_sheet(df)
        assert mock_build.called    
