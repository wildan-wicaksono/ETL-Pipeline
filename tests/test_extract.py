from unittest.mock import patch, Mock
from utils.extract import fetching_content, extract_product, scrape_fashion
from bs4 import BeautifulSoup
import requests, re

# ==================================== TESTING FETCHING CONTENT ====================================

class Test_FetchingContent:
    
    @patch('utils.extract.requests.Session.get')
    def test_request_succes(self, mock_get):
        mock_response = Mock()
        mock_response.content = b"<html>OK</html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = fetching_content("https://example.com")
        assert result == b"<html>OK</html>"

    @patch('utils.extract.requests.Session.get')
    def test_request_connection_error(self, mock_get):
        mock_get.side_effect = Exception("Connection error")

        result = fetching_content("https://example.com")
        assert result is None


    @patch('utils.extract.requests.Session.get')
    def test_unexpected_failure(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Unexpected failure")
        result = fetching_content("https://example.com")
        assert result is None
#
#  ==================================== TESTING EXTRACT PRODUCT ====================================

class Test_ExtractProduct:
    def generate_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        return soup.find('div', class_='collection-card')
    
    def test_complete(self):
        html = """
            <div class="collection-card">
                <div class="product-details">
                    <h3>Product Test 1</h3>
                    <div class="price-container"><span class="price">$96.69</span></div>
                    <p>Rating: ⭐ 4.2 / 5</p>
                    <p>3 Colors</p>
                    <p>Size: M</p>
                    <p>Gender: Unisex</p>
                </div>
            </div>
        """

        product = self.generate_html(html)
        result = extract_product(product)
        assert result['Title'] == "Product Test 1"
        assert result['Price'] == "$96.69"
        assert result['Rating'] == "4.2"
        assert result['Colors'] == "3"
        assert result['Size'] == "M"
        assert result['Gender'] == "Unisex"
        assert result['Timestamp'] is not None
        
    def test_missing_price(self):
        html = """
            <div class="collection-card">
                <div class="product-details">
                    <h3>Product Test 2</h3>
                    <div class="price-container"><span class="price">Price Unavailable</span></div>
                    <p>Rating: ⭐ 4.2 / 5</p>
                    <p>1 Colors</p>
                    <p>Size: XXL</p>
                    <p>Gender: Male</p>
                </div>
            </div>
        """
        product = self.generate_html(html)
        result = extract_product(product)
        assert result['Title'] == "Product Test 2"
        assert result['Price'] == "Price Unavailable"
        assert result['Rating'] == "4.2"
        assert result['Colors'] == "1"
        assert result['Size'] == "XXL"
        assert result['Gender'] == "Male"
        assert result['Timestamp'] is not None

    def test_missing_title_NotRated(self):
        html = """
            <div class="collection-card">
                <div class="product-details">
                    <h3>Unknown Product</h3>
                    <div class="price-container"><span class="price">$89.21</span></div>
                    <p>Rating: Not Rated</p>
                    <p>4 Colors</p>
                    <p>Size: XL</p>
                    <p>Gender: Female</p>
                </div>
            </div>
        """
        product = self.generate_html(html)
        result = extract_product(product)
        assert result['Title'] == "Unknown Product"
        assert result['Price'] == "$89.21"
        assert result['Rating'] == "0"
        assert result['Colors'] == "4"
        assert result['Size'] == "XL"
        assert result['Gender'] == "Female"
        assert result['Timestamp'] is not None

    def test_InvalidRating(self):
        html = """
            <div class="collection-card">
                <div class="product-details">
                    <h3>Product Test 4</h3>
                    <div class="price-container"><span class="price">$243.21</span></div>
                    <p>Rating: ⭐ Invalid Rating / 5</p>
                    <p>8 Colors</p>
                    <p>Size: S</p>
                    <p>Gender: Unisex</p>
                </div>
            </div>
        """
        product = self.generate_html(html)
        result = extract_product(product)
        assert result['Title'] == "Product Test 4"
        assert result['Price'] == "$243.21"
        assert result['Rating'] == None
        assert result['Colors'] == "8"
        assert result['Size'] == "S"
        assert result['Gender'] == "Unisex"
        assert result['Timestamp'] is not None
    
    def test_missing_h3(self):
        html = """
            <div class="collection-card">
                <div class="product-details">
                    <div class="price-container"><span class="price">$99.99</span></div>
                </div>
            </div>
        """
        product = self.generate_html(html)
        result = extract_product(product)
        assert result is None

    def test_missing_price_container(self):
        html = """
            <div class="collection-card">
                <div class="product-details">
                    <h3>Product Test 5</h3>
                    <p>Rating: ⭐ 4.0 / 5</p>
                    <p>2 Colors</p>
                    <p>Size: M</p>
                    <p>Gender: Unisex</p>
                </div>
            </div>
        """
        product = self.generate_html(html)
        result = extract_product(product)
        assert result['Title'] == "Product Test 5"
        assert result['Price'] is None
        assert result['Rating'] == "4.0"
        assert result['Colors'] == "2"
        assert result['Size'] == "M"
        assert result['Gender'] == "Unisex"
        assert result['Timestamp'] is not None
# ==================================== TESTING SCRAPE FASHION ====================================

MOCK_HTML = """
<div class="collection-card">
    <div class="product-details">
        <h3>Product X</h3>
        <div class="price-container"><span class="price">$89.99</span></div>
        <p>Rating: ⭐ 4.7 / 5</p>
        <p>2 Colors</p>
        <p>Size: L</p>
        <p>Gender: Unisex</p>
    </div>
</div>
"""

class Test_ScrapeFashion:

    @patch('utils.extract.fetching_content')
    def test_scrape_single_page(self, mock_fetch):
        mock_fetch.return_value = f"<html><body>{MOCK_HTML}</body></html>".encode()

        result = scrape_fashion("https://dummy.url/page{}", start_page=1, delay=0)

        assert isinstance(result, list)
        assert len(result) > 0
        product = result[0]

        assert product['Title'] == "Product X"
        assert product['Price'] == "$89.99"
        assert product['Rating'] == "4.7"
        assert product['Colors'] == "2"
        assert product['Size'] == "L"
        assert product['Gender'] == "Unisex"
        assert product['Timestamp'] is not None

    @patch('utils.extract.fetching_content')
    def test_scrape_empty_page(self, mock_fetch):
        mock_fetch.return_value = "<html><body></body></html>".encode()

        result = scrape_fashion("https://dummy.url/page{}", start_page=1, delay=0)
        assert result == [] 

    @patch('utils.extract.fetching_content')
    def test_missing_tag_div(self, mock_fetch):
        mock_fetch.return_value = "<html><broken>".encode()

        result = scrape_fashion("https://dummy.url/page{}", start_page=1, delay=0)
        assert isinstance(result, list)

    @patch('utils.extract.fetching_content')
    def test_another_exception(self, mock_fetch):
        mock_fetch.side_effect = Exception("Fatal error")

        result = scrape_fashion("https://dummy.url/page{}", start_page=1, delay=0)
        assert result == []

    @patch('utils.extract.fetching_content')
    def test_scrape_fetching_none(self, mock_fetch):
        mock_fetch.return_value = None  # simulate failed request
        result = scrape_fashion("https://dummy.url/page{}", start_page=1, delay=0)
        assert result == []

    @patch('utils.extract.fetching_content')
    @patch('utils.extract.extract_product')
    def test_scrape_extract_product_error(self, mock_extract, mock_fetch):
        mock_fetch.return_value = f"<html><body>{MOCK_HTML}</body></html>".encode()
        mock_extract.side_effect = Exception("Simulated failure")

        result = scrape_fashion("https://dummy.url/page{}", start_page=1, delay=0)
        assert isinstance(result, list)
