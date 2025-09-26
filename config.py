import os
from dotenv import load_dotenv


load_dotenv()


class Config:
    API_TOKEN = os.getenv("API_TOKEN", "")
    GD_PARENT_FOLDER_ID = os.getenv("GD_PARENT_FOLDER_ID", "")
    GS_SPREADSHEETS_ID = os.getenv("GS_SPREADSHEETS_ID", "")
