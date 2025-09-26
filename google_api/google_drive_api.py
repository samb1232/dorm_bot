from config.config import Config
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from configs.my_logger import get_logger


logger = get_logger(__name__)


class GoogleDriveAPI:
    SCOPES = ["https://www.googleapis.com/auth/drive"]
    PARENT_FOLDER_ID = Config.GD_PARENT_FOLDER_ID

    @staticmethod
    def _authenticate():
        try:
            credentials_dict = Config.get_google_credentials()
            if not credentials_dict:
                logger.error("Google credentials not found in configuration")
                return None
                
            credentials = service_account.Credentials.from_service_account_info(
                credentials_dict,
                scopes=GoogleDriveAPI.SCOPES
            )
            return credentials
        except Exception as e:
            logger.error(f"Error authenticating: {e}")
            return None

    @staticmethod
    def upload_file(file_path, file_name):
        creds = GoogleDriveAPI._authenticate()
        if not creds:
            logger.error("Failed to authenticate, aborting upload.")
            return False

        try:
            service = build("drive", "v3", credentials=creds)

            file_metadata = {
                'name': file_name,
                'parents': [GoogleDriveAPI.PARENT_FOLDER_ID]
            }

            mime_type = GoogleDriveAPI._get_mime_type(file_path)
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)

            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            logger.info(f"File '{file_name}' uploaded successfully with ID: {file.get('id')}")
            return file.get('id')
            
        except HttpError as error:
            logger.error(f"Google API error occurred: {error}")
            return False
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return False

    @staticmethod
    def _get_mime_type(file_path):
        mime_types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.txt': 'text/plain',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.zip': 'application/zip',
            '.rar': 'application/x-rar-compressed',
        }
        
        for ext, mime_type in mime_types.items():
            if file_path.lower().endswith(ext):
                return mime_type
                
        return 'application/octet-stream'  # default MIME type

    @staticmethod
    def create_folder(folder_name, parent_folder_id=None):
        creds = GoogleDriveAPI._authenticate()
        if not creds:
            logger.error("Failed to authenticate, aborting folder creation.")
            return None

        try:
            service = build("drive", "v3", credentials=creds)
            
            parent_id = parent_folder_id or GoogleDriveAPI.PARENT_FOLDER_ID
            
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_id]
            }

            folder = service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
            
            logger.info(f"Folder '{folder_name}' created successfully with ID: {folder.get('id')}")
            return folder.get('id')
            
        except HttpError as error:
            logger.error(f"Google API error occurred: {error}")
            return None
        except Exception as e:
            logger.error(f"Error creating folder: {e}")
            return None

    @staticmethod
    def list_files(folder_id=None, query=None):
        creds = GoogleDriveAPI._authenticate()
        if not creds:
            logger.error("Failed to authenticate, aborting file listing.")
            return []

        try:
            service = build("drive", "v3", credentials=creds)
            
            target_folder_id = folder_id or GoogleDriveAPI.PARENT_FOLDER_ID
            base_query = f"'{target_folder_id}' in parents and trashed=false"
            
            if query:
                full_query = f"{base_query} and {query}"
            else:
                full_query = base_query

            results = service.files().list(
                q=full_query,
                pageSize=100,
                fields="nextPageToken, files(id, name, mimeType, createdTime, modifiedTime)"
            ).execute()
            
            files = results.get('files', [])
            logger.info(f"Found {len(files)} files in folder {target_folder_id}")
            return files
            
        except HttpError as error:
            logger.error(f"Google API error occurred: {error}")
            return []
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return []
        