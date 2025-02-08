import logging

import apiclient.discovery
import httplib2
from oauth2client.service_account import ServiceAccountCredentials

import config
from database.db_operations import DbHelper

logger = logging.getLogger(__name__)


class GoogleSheetsAPI:
    CREDENTIALS_FILE = 'google_drive_key.json'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SPREADSHEETS_ID = config.GS_SPREADSHEETS_ID

    LIST_A = "ДОЛГ 5а"
    LIST_B = "ДОЛГ 5б"

    RANGE = "A2:C500"

    @staticmethod
    def _authenticate():
        try:
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                GoogleSheetsAPI.CREDENTIALS_FILE,
                GoogleSheetsAPI.SCOPES)
            return credentials
        except Exception as e:
            logging.error(f"Error authenticating: {e}")
            return None

    @staticmethod
    def get_debtors_table():
        debtors = {}
        credentials = GoogleSheetsAPI._authenticate()

        httpAuth = credentials.authorize(httplib2.Http())
        service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)

        values_a = service.spreadsheets().values().get(
            spreadsheetId=config.GS_SPREADSHEETS_ID,
            range=f'{GoogleSheetsAPI.LIST_A}!{GoogleSheetsAPI.RANGE}',
            majorDimension='ROWS'
        ).execute()

        values_b = service.spreadsheets().values().get(
            spreadsheetId=config.GS_SPREADSHEETS_ID,
            range=f'{GoogleSheetsAPI.LIST_B}!{GoogleSheetsAPI.RANGE}',
            majorDimension='ROWS'
        ).execute()

        values_ab = values_a["values"] + values_b["values"]

        for row in values_ab:
            if len(row) != 2:
                continue
            if row[1] == "" or row[0] == "":
                continue

            cleaned_string = ''.join([char for char in row[1] if char.isdigit() or char in ['.', ',', '-']]).replace(
                ',', '.')

            debtors[row[0].lower().replace("ё", "е")] = float(cleaned_string)

        return debtors

    @staticmethod
    def batch_debtors_from_sheets():
        DbHelper.update_debtors_table(GoogleSheetsAPI.get_debtors_table())
