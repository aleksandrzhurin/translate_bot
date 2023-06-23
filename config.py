import os

from dotenv import load_dotenv


load_dotenv()

TOKEN_API = os.getenv('TOKEN_API', default='')
IAM_TOKEN = os.getenv('IAM_TOKEN', default='')
folder_id = os.getenv('folder_id', default='')
target_language = os.getenv('target_language', default='ru')
