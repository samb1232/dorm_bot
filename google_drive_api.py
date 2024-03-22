import logging
import config
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import utils

logger = logging.getLogger(__name__)


class GoogleDriveAPI:
    SCOPES = ["https://www.googleapis.com/auth/drive"]
    SERVICE_ACCOUNT_FILE = "google_drive_key.json"
    PARENT_FOLDER_ID = config.GD_PARENT_FOLDER_ID

    @staticmethod
    def _authenticate():
        try:
            credentials = service_account.Credentials.from_service_account_file(
                GoogleDriveAPI.SERVICE_ACCOUNT_FILE,
                scopes=GoogleDriveAPI.SCOPES)
            return credentials
        except Exception as e:
            logging.error(f"Error authenticating: {e}")
            return None

    @staticmethod
    def upload_file(file_path, file_name):
        creds = GoogleDriveAPI._authenticate()
        service = build("drive", "v3", credentials=creds)

        try:
            file_metadata = {
                'name': file_name,
                'parents': [GoogleDriveAPI.PARENT_FOLDER_ID]}
            service.files().create(
                body=file_metadata,
                media_body=file_path
            ).execute()
            logging.info(f"File {file_name} uploaded successfully")
        except HttpError as error:
            logging.error(f"An error occurred: {error}")
        except Exception as e:
            logging.error(f"Error uploading file: {e}")


