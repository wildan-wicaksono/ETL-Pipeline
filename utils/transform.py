import pandas as pd 


# mengubah ke dataframe
def transform_to_df(data):
    try:
        if not data:
            raise ValueError("Data tidak boleh kosong")
        df = pd.DataFrame(data)
        
        return df 
    except Exception as e:
        print(f"[ERROR] Gagal mengoversi ke DataFrame: {e}")
        return None 

# transform data 
def transform_data(data, exchange_rate):
    try:
        # konversi Unknown -> None
        data['Title'] = data['Title'].replace('Unknown Product', None)
        data['Price'] = data['Price'].replace('Price Unavailable', None)

        # membuang data null dan duplikat
        data = data.dropna()
        data = data.drop_duplicates()

        # konversi ke RP
        data['Price'] = data['Price'].astype(str).str.replace('$', '', regex=False)
        data['Price'] = pd.to_numeric(data['Price'], errors='coerce')
        data['Price'] = (data['Price'] * exchange_rate).astype(float)
        # data = data.drop(columns=['Price'])

        # Merubah tipe data
        data['Rating'] = data['Rating'].astype(float)
        data['Colors'] = data['Colors'].astype('int64')

        # memindahkan kolom
        col = data.pop('Price')
        data.insert(1, 'Price', col)

        return data 
    except Exception as e:
        print(f"[ERROR] Gagal transform data: {e}")
        return None 