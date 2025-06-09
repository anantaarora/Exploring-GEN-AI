import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Define your sheet name
SHEET_NAME = "Job Tracker"

# Define Google Sheets access scope
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Lock Path to your credentials JSON file
CREDENTIALS_FILE = "config/google_service_account.json"

# Setup Google Sheets connection
def get_sheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).sheet1
    return sheet

# Append a row for job applications/referrals
def log_job_entry(company, title, referral_name, message, response, applied, passed):
    sheet = get_sheet()
    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        company,
        title,
        referral_name,
        message,
        response,
        applied,
        passed
    ]
    sheet.append_row(row)
