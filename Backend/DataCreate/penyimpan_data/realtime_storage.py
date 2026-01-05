import mysql.connector
from config import DB_CON

def get_db_connection():
    """Membuat koneksi ke database LuxGrow"""
    return mysql.connector.connect(**DB_CON)

def simpan_data_lux(lux_value):
    """
    Menyimpan data sensor Lux ke database secara realtime
    """
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = "INSERT INTO lux (lux) VALUES (%s)"
        cur.execute(query, (lux_value,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving Lux data: {e}")
        return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def simpan_data_dht(temperature, humidity):
    """
    Menyimpan data sensor DHT (Suhu & Kelembaban) ke database secara realtime
    """
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = "INSERT INTO dht (temperature, humidity) VALUES (%s, %s)"
        cur.execute(query, (temperature, humidity))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving DHT data: {e}")
        return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
