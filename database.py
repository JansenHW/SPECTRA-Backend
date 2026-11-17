import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()

PORT = int(os.getenv("PORT", 5000))
DB_SERVER = os.getenv("DB_SERVER", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "64226")
DB_USER = os.getenv("DB_USER", "sa")
DB_PASSWORD = os.getenv("DB_PASSWORD", "D0d0lMssql")
DB_DATABASE = os.getenv("DB_DATABASE", "SPECTRA_DB")

def get_db_connection():
    try:
        connection_string = (
            f"DRIVER={{SQL Server}};"
            f"SERVER={DB_SERVER},{DB_PORT};"
            f"DATABASE={DB_DATABASE};"
            f"UID={DB_USER};"
            f"PWD={DB_PASSWORD};"
        )
        conn = pyodbc.connect(connection_string, timeout=10)
        return conn
    except Exception as ex:
        print(f"\n[KONEKSI GAGAL]")
        print(f"Server   : {DB_SERVER}:{DB_PORT}")
        print(f"Database : {DB_DATABASE}")
        print(f"Error    : {ex}\n")
        return None