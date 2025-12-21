import os 
from dotenv import load_dotenv 

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME') 
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

DB_CON={
    'host': DB_HOST,
    'database': DB_NAME,
    'port': DB_PORT,
    'user': DB_USER,
    'password': DB_PASSWORD
}

