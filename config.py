import os 
from dotenv import load_dotenv 
import mysql.connector

load_dotenv()

DB_CON = {
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'port': int(os.getenv('DB_PORT')),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}

# Debug print
print(f"DB Config: {DB_CON}")

# Test koneksi database
try:
    conn = mysql.connector.connect(**DB_CON)
    print("✓ Database connection successful")
    conn.close()
except Exception as e:
    print(f"✗ Database connection failed: {e}")
