from utils.extract import extract_product, scrape_fashion
from utils.transform import transform_to_df, transform_data
from utils.load import store_to_postgre, store_to_csv, store_to_google_sheet
import psycopg2

def main():
    # URL fashion
    BASE_URL = 'https://fashion-studio.dicoding.dev/page{}'
    all_fashion_data = scrape_fashion(BASE_URL)

    # merubah ke df 
    if all_fashion_data:
        try:
            df = transform_to_df(all_fashion_data)
            df = transform_data(df, 16000)
            
            db_url = 'postgresql+psycopg2://developer:supersecretpassword@localhost:5432/fashiondb'
            store_to_postgre(df, db_url)

            store_to_csv(df, 'products.csv')
            store_to_google_sheet(df)

        except Exception as e:
            print(f"[ERROR] Terjadi kesalahan dalam proses:{e}")
    else:
        print("Scraping gagal.")
    

if __name__ == "__main__":
    main()