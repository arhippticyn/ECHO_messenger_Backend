import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv('DB_URL')
ALGORITM = os.getenv('ALGORITM')
SECRET_KEY = os.getenv('SECRET_KEY')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
DEBUG = os.getenv('DEBUG')