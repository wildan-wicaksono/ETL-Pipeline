from datetime import datetime
import time
import requests
import re
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    )
}

def fetching_content(url):
    try:
        session = requests.Session()
        response = session.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Gagal melakukan request: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] Unexpected failure: {e}")
        return None

def extract_product(product):
    try:
        product_details_element = product.find('div', class_='product-details')

        # judul produk
        product_title = product_details_element.find('h3').text.strip()
        
        # Harga produk
        product_element = product_details_element.find('div', class_='price-container')
        price = None
        if product_element:
            price_tag = product_element.find('span', class_='price')
            if price_tag:
                price = price_tag.text.strip()

        
        # Rating, colors, size, gender
        p_tags = product_details_element.find_all('p')
        rating, colors, size, gender = None, None, None, None
        for p in p_tags:
            element = p.text.strip()
            if 'Rating' in element:
                if element == 'Rating: Not Rated':
                    rating = '0'
                else:
                    rating = re.split(r':|\/|⭐', element)[2].strip()
                    if rating == 'Invalid Rating':
                        rating = None
            elif 'Colors' in element:
                colors = element.split()[0].strip()
            elif 'Size' in element:
                size = element.split(':')[1].strip()
            elif "Gender" in element:
                gender = element.split(':')[1].strip()
        

        fashion = {
            "Title": product_title,
            "Price": price,
            "Rating": rating,
            "Colors": colors,
            "Size": size,
            "Gender": gender,
            "Timestamp": datetime.now().isoformat()
        }

        return fashion 
    except Exception as e:
        print(f"[ERROR] Gagal extract data: {e}")

def scrape_fashion(base_url, start_page=1, delay=2):
    data = []
    page_number = start_page 

    while True:
        try:
            if page_number == 1:
                url =  base_url.replace('page{}', '')
            elif page_number <= 50:
                url = base_url.format(page_number)
            else:
                break
            print(f'[INFO] Scraping halaman {page_number}: {url}')

            content = fetching_content(url)
            if not content:
                print(f'[WARNING] Halaman gagal dimuat: {url}')
            
            try:
                soup = BeautifulSoup(content, 'html.parser')
                products_elements = soup.find_all('div', class_='collection-card')

                if not products_elements:
                    print(f'[INFO] Tidak ditemukan produk di halaman {page_number}')

                for product in products_elements:
                    fashion = extract_product(product)
                    data.append(fashion)

            except Exception as e:
                print(f"[ERROR] Gagal parsing halaman {page_number}: {e}")

            page_number += 1
            time.sleep(delay)
 
        except Exception as e:
            print(f'[CRITICAL] Gagal scraping halaman {page_number}: {e}')
            break 

    return data 

