from unittest.mock import patch, Mock
from utils.transform import transform_to_df, transform_data 
from bs4 import BeautifulSoup
import requests, re
import pandas as pd

# ==================================== TESTING TRANSFROM TO DF ====================================

class Test_TransformToDF:
    def test_transform_to_df_valid(self):
        data = [
            # complete
            {"Title": "Product A", "Price": "$100.0", "Rating": "4.5", "Colors": "2", "Size": "M", "Gender": "Unisex", "Timestamp": "2025-05-14T17:22:04.282749"},

            # missing title
            {"Title": "Unknown Product", "Price": "$200.0", "Rating": "3.0", "Colors": "1", "Size": "L", "Gender": "Male", "Timestamp": "2025-05-14T17:22:04.387612"},

            # not rated
            {"Title": "Product C", "Price": "$165.23", "Rating": "0", "Colors": "5", "Size": "XL", "Gender": "Female", "Timestamp": "2025-05-14T17:22:05.187622"},

            # invalid rating, price unavailable
            {"Title": "Product D", "Price": "Price Unavailable", "Rating": None, "Colors": "2", "Size": "XXL", "Gender": "Female", "Timestamp": "2025-05-14T17:22:05.567219"},      
        ]
        df = transform_to_df(data)
        assert isinstance(df, pd.DataFrame)
        assert set(["Title", "Price", "Rating", "Colors", "Size", "Gender", "Timestamp"]).issubset(df.columns)
        assert "Title" in df.columns

    def test_transform_to_df_empty(self):
        df = transform_to_df([])
        assert df is None 

# ==================================== TESTING TRANSFROM DF ====================================

class Test_Transform:
    def test_transform_complete(self):
        data = [
            {"Title": "Product A", "Price": "$100.0", "Rating": "4.5", "Colors": "2", "Size": "M", "Gender": "Unisex", "Timestamp": "2025-05-14T17:22:04.282749"},
        ]
        df = transform_to_df(data)
        result = transform_data(df, exchange_rate=16000)

        assert isinstance(result, pd.DataFrame)
        assert "Price" in result.columns
        assert "Title" in result.columns
        assert result.shape == (1, 7)
        assert result['Price'].iloc[0] == 100.0 * 16000
        assert result['Colors'].dtype == 'int64'
        assert result['Rating'].dtype == 'float64'

    def test_transform_MissingTitle_Duplicate(self):
        data = [
            {"Title": "Unknown Product", "Price": "$100.0", "Rating": "4.5", "Colors": "2", "Size": "M", "Gender": "Unisex", "Timestamp": "2025-05-14T17:22:04.282749"},
            {"Title": "Product A", "Price": "$100.0", "Rating": "4.5", "Colors": "2", "Size": "M", "Gender": "Unisex", "Timestamp": "2025-05-14T17:22:04.282749"},
            {"Title": "Product A", "Price": "$100.0", "Rating": "4.5", "Colors": "2", "Size": "M", "Gender": "Unisex", "Timestamp": "2025-05-14T17:22:04.282749"},
        ]
        df = transform_to_df(data)
        result = transform_data(df, exchange_rate=16000)

        assert isinstance(result, pd.DataFrame)
        assert result.shape == (1,7) # dropna dan duplicate

    def test_empty_data(self):
        data = []
        df = transform_to_df(data)
        result = transform_data(df, exchange_rate=16000)

        assert result is None
        