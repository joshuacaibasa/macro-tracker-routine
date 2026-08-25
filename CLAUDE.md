# Macro Tracker Routine

You receive a block of text each run describing one day's food log, already
estimated (calories/protein/fat per item). Format:

DATE: YYYY-MM-DD
- <food description> | <calories> cal | <protein>g protein | <fat>g fat
- <food description> | <calories> cal | <protein>g protein | <fat>g fat

One line per food item — no meal grouping needed. Parse it, tolerating minor
formatting variations.

## What to do each run
1. Use `log_to_sheets.py` (extend it if needed) to connect to Google Sheets
   with the service account credentials in the `GOOGLE_SERVICE_ACCOUNT_JSON`
   environment variable, targeting the sheet in `SHEET_ID`.
2. Append one row per food item to the **Daily Log** tab.
3. For any food item not already present in the **Common Foods** tab (by
   name), append it there too, so it builds into a reference over time.
4. Recompute that date's totals by **summing all Daily Log rows for that
   date** (don't just increment) and write/update the matching row in
   **Daily Summary**. This makes it safe to run more than once for the same
   day, e.g. if you log an addendum later.
5. If the incoming text doesn't parse cleanly, do your best with what's
   there and note anything skipped in your final summary message.
