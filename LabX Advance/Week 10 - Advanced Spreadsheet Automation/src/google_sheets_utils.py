# agentic-spreadsheet-processor/src/google_sheets_utils.py
# Optional integration with the Google Sheets API using `gspread`.
# It only runs when "google_sheets": {"enabled": true} is set in the config and
# a Service Account key file is available. Otherwise the agent skips it.
import os
import logging

logger = logging.getLogger(__name__)


class GoogleSheetsUtils:
    """
    Helper class for interacting with Google Sheets.
    Requires the 'gspread' library (pip install gspread) and a Service Account JSON key.
    """
    def __init__(self, credentials_file):
        self.credentials_file = credentials_file
        self.gc = None

    def connect(self):
        """Authenticates with a Service Account. Returns True on success."""
        if not os.path.exists(self.credentials_file):
            logger.warning(f"Google credentials file not found: {self.credentials_file}. Skipping Google Sheets.")
            return False
        try:
            import gspread  # Imported here so the project runs without gspread installed
            self.gc = gspread.service_account(filename=self.credentials_file)
            logger.info("Connected to Google Sheets API.")
            return True
        except ImportError:
            logger.warning("gspread is not installed. Run 'pip install gspread' to enable Google Sheets.")
        except Exception as e:
            logger.error(f"Google Sheets authentication failed: {e}")
        return False

    def read_sheet(self, spreadsheet_id, sheet_name, range_name="A1:Z1000"):
        """Reads a range of values from a worksheet."""
        worksheet = self.gc.open_by_key(spreadsheet_id).worksheet(sheet_name)
        values = worksheet.get(range_name)
        logger.info(f"Read {len(values)} rows from Google Sheet '{sheet_name}'.")
        return values

    def write_sheet(self, spreadsheet_id, sheet_name, data, start_cell="A1"):
        """Writes a 2D list to a worksheet, creating the worksheet if needed."""
        spreadsheet = self.gc.open_by_key(spreadsheet_id)
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
        except Exception:
            worksheet = self.create_sheet(spreadsheet_id, sheet_name)
        worksheet.update(range_name=start_cell, values=data)
        logger.info(f"Wrote {len(data)} rows to Google Sheet '{sheet_name}'.")
        return True

    def create_sheet(self, spreadsheet_id, sheet_name, rows=100, cols=20):
        """Creates a new worksheet in a Google Sheet."""
        worksheet = self.gc.open_by_key(spreadsheet_id).add_worksheet(title=sheet_name, rows=rows, cols=cols)
        logger.info(f"Created worksheet '{sheet_name}'.")
        return worksheet

    def upload_worksheet(self, spreadsheet_id, openpyxl_sheet, target_sheet_name=None):
        """Uploads the values of an openpyxl worksheet to Google Sheets."""
        data = [["" if v is None else v for v in row] for row in openpyxl_sheet.iter_rows(values_only=True)]
        return self.write_sheet(spreadsheet_id, target_sheet_name or openpyxl_sheet.title, data)
