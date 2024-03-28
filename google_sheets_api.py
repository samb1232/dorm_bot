import logging

import httplib2
import apiclient.discovery

from oauth2client.service_account import ServiceAccountCredentials

import config

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

        for row in values_a["values"]:
            if len(row) != 3:
                continue
            if row[2] == "" or row[0] == "":
                continue
            debtors[row[0]] = row[2]

        for row in values_b["values"]:
            if len(row) != 3:
                continue
            if row[2] == "" or row[0] == "":
                continue
            debtors[row[0]] = row[2]

        return debtors
