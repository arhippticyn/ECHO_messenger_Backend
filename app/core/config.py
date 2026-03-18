import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv('DB_URL')
ALGORITM = os.getenv('ALGORITM')
SECRET_KEY = os.getenv('SECRET_KEY')