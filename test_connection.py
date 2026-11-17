import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db_connection

def cek_struktur_tph():
    conn = get_db_connection()
    if conn is None:
        print("❌ Gagal terhubung ke database.")
        return

    cursor = conn.cursor()
    print("=" * 65)
    print("STRUKTUR KOLOM TABEL: TPH_TRANSACTION")
    print("=" * 65)

    cursor.execute("""
        SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'TPH_TRANSACTION'
        ORDER BY ORDINAL_POSITION
    """)
    kolom_list = cursor.fetchall()

    for col in kolom_list:
        nama = col[0]
        tipe = col[1]
        panjang = f"({col[2]})" if col[2] else ""
        nullable = "BISA NULL" if col[3] == "YES" else "WAJIB ISI"
        print(f"  • Kolom: {nama.ljust(22)} | Tipe: {tipe}{panjang}".ljust(48) + f" | {nullable}")

    print("=" * 65)
    cursor.close()
    conn.close()

if __name__ == "__main__":
    cek_struktur_tph()