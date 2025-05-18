from sqlalchemy import create_engine
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# menyimpan ke postgreSQL
def store_to_postgre(data, db_url):
    try: 
        engine = create_engine(db_url)
        with engine.connect() as con:
            data.to_sql('fashiontoscrape', con=con, if_exists='replace', index=False)
            print('Data berhasil ditambahkan!')
    
    except Exception as e:
        print(f"Eror saat menyimpan data: {e}")

# menyimpan ke csv
def store_to_csv(data, filename):
    try:
        data.to_csv(filename, index=False)
        print(f"Data berhasil disimpan ke {filename}")
    except Exception as e:
        print(f"Error saat menyimpan data ke CSV: {e}")

# menyimpan ke google sheet

SERVICE_ACCOUNT_FILE  = './google-sheets-api.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

credential = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

SPREADSHEET_ID = '----PROHOBITED-----'
RANGE_NAME = 'Sheet1!A2:G1500'

def store_to_google_sheet(data):
    try:
        service = build('sheets', 'v4', credentials=credential)
        sheet = service.spreadsheets()
        values = data.values.tolist()
        body = {
            'values': values
        }

        result = sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption='RAW',
            body=body
        ).execute()

        print("Data berhasil disimpan ke Google Sheets")
    except Exception as e:
        print(f"Error saat menyimpan data ke Google Sheets: {e}")

