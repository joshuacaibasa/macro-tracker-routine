import os
import json
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
DATE_FMT = "%Y-%m-%d"

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

def fill_missing_days(new_date_str):
    """Inserts an N/A row for every date strictly between the latest
    existing Daily Summary date and new_date_str. No-op if there's no prior
    data, or if new_date_str isn't chronologically after the latest one."""
    ws = get_sheet().worksheet("Daily Summary")
    records = ws.get_all_values()
    existing_dates = []
    for row in records[1:]:  # skip header row
        if row and row[0]:
            try:
                existing_dates.append(datetime.strptime(row[0], DATE_FMT))
            except ValueError:
                continue
    if not existing_dates:
        return
    latest = max(existing_dates)
    new_date = datetime.strptime(new_date_str, DATE_FMT)
    gap_rows = []
    current = latest + timedelta(days=1)
    while current < new_date:
        gap_rows.append([current.strftime(DATE_FMT), "N/A", "N/A", "N/A"])
        current += timedelta(days=1)
    if gap_rows:
        ws.append_rows(gap_rows, value_input_option="USER_ENTERED")

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
