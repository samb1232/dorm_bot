import logging
import config
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import utils

# usage
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
    def upload_file(file_path, file_new_name):
        creds = GoogleDriveAPI._authenticate()
        service = build("drive", "v3", credentials=creds)

        try:
            extension = utils.get_extension_from_file_name(file_path)
            file_metadata = {
                'name': file_new_name + "." + extension,
                'parents': [GoogleDriveAPI.PARENT_FOLDER_ID]}
            file = service.files().create(
                body=file_metadata,
                media_body=file_path
            ).execute()
            logging.info(f"File {file_new_name} uploaded successfully")
        except HttpError as error:
            logging.error(f"An error occurred: {error}")
        except ValueError as e:
            logging.error(f"Error finding file extension: {e}")
        except Exception as e:
            logging.error(f"Error uploading file: {e}")


