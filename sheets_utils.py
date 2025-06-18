# sheets_utils.py
import gspread
from google.oauth2.service_account import Credentials

def get_sheet():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        'askmedix-credentials.json',
        scopes=SCOPES
    )

    client = gspread.authorize(creds)

    # Replace with your actual Google Sheet name
    sheet = client.open("AskMediX Patient Records").sheet1
    return sheet
