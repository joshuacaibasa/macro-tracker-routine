import os
import json
import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def get_sheet():
    creds_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(os.environ["SHEET_ID"])

def append_daily_log_rows(rows):
    """rows: list of [date, food_item, calories, protein, fat]. food_item
    should already include quantity, e.g. "1 banana" or "100g banana"."""
    ws = get_sheet().worksheet("Daily Log")
    ws.append_rows(rows, value_input_option="USER_ENTERED")

def upsert_daily_summary(date, totals):
    """totals: dict with calories/protein/fat. Updates the row for `date` if
    it exists, else appends one."""
    ws = get_sheet().worksheet("Daily Summary")
    records = ws.get_all_values()
    for i, row in enumerate(records):
        if row and row[0] == date:
            ws.update(f"A{i+1}:D{i+1}", [[date, totals["calories"], totals["protein"], totals["fat"]]])
            return
    ws.append_row([date, totals["calories"], totals["protein"], totals["fat"]], value_input_option="USER_ENTERED")
