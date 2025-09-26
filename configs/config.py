import os
from dotenv import load_dotenv


load_dotenv()


class Config:
    API_TOKEN = os.getenv("API_TOKEN", "")
    GD_PARENT_FOLDER_ID = os.getenv("GD_PARENT_FOLDER_ID", "")
    GS_SPREADSHEETS_ID = os.getenv("GS_SPREADSHEETS_ID", "")
    
    @staticmethod
    def get_google_credentials():
        return {
            "type": "service_account",
            "project_id": os.getenv("GOOGLE_PROJECT_ID"),
            "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace('\\n', '\n'),
            "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{os.getenv('GOOGLE_CLIENT_EMAIL').replace('@', '%40')}",
            "universe_domain": "googleapis.com"
        }
