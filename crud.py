import pyodbc
from database import get_db_connection
from schemas import TphTransactionCreate

# 1. Autentikasi / Cek Profil Karyawan berdasarkan NIK (Dinamis dari SPM1)
def get_employee_by_nik(nik: str):
    conn = get_db_connection()
    if not conn:
        print("[DB ERROR] Gagal terhubung ke SPECTRA_DB di get_employee_by_nik")
        return None
    try:
        clean_nik = str(nik).strip()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                LTRIM(RTRIM(NIK)) AS NIK, 
                LTRIM(RTRIM(FULL_NAME)) AS FULL_NAME, 
                LTRIM(RTRIM(POSITION)) AS POSITION, 
                LTRIM(RTRIM(ESTATE_CODE)) AS ESTATE_CODE, 
                LTRIM(RTRIM(AFDELING_CODE)) AS AFDELING_CODE,
                IS_ACTIVE
            FROM dbo.MD_EMPLOYEE
            WHERE LTRIM(RTRIM(NIK)) = ?
        """, (clean_nik,))
        row = cursor.fetchone()
        if row:
            return {
                "nik": str(row[0]).strip(),
                "full_name": str(row[1]).strip(),
                "position": str(row[2]).strip(),
                "estate_code": str(row[3]).strip(),
                "afdeling_code": str(row[4]).strip(),
                "is_active": bool(row[5]) if row[5] is not None else True
            }
        return None
    except Exception as ex:
        print(f"[ERROR SQL get_employee_by_nik]: {ex}")
        return None
    finally:
        cursor.close()
        conn.close()

# 2. Ambil Semua Data Master Estate
def get_all_estates():
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT LTRIM(RTRIM(ESTATE_CODE)), LTRIM(RTRIM(ESTATE_NAME)) FROM MD_ESTATE ORDER BY ESTATE_CODE")
        rows = cursor.fetchall()
        return [{"estate_code": str(r[0]).strip(), "estate_name": str(r[1]).strip()} for r in rows]
    except Exception as ex:
        print(f"[ERROR get_all_estates]: {ex}")
        return []
    finally:
        cursor.close()
        conn.close()

# 3. Ambil Semua Data Master Afdeling
def get_all_afdelings():
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT LTRIM(RTRIM(AFDELING_CODE)), LTRIM(RTRIM(ESTATE_CODE)) FROM MD_AFDELING ORDER BY AFDELING_CODE")
        rows = cursor.fetchall()
        return [{"afdeling_code": str(r[0]).strip(), "estate_code": str(r[1]).strip()} for r in rows]
    except Exception as ex:
        print(f"[ERROR get_all_afdelings]: {ex}")
        return []
    finally:
        cursor.close()
        conn.close()

# 4. Ambil Semua Data Master Block (Satu fungsi bersih & aman, tanpa kolom IS_ACTIVE yang memicu error)
def get_all_blocks(afdeling_code: str = None):
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        if afdeling_code:
            cursor.execute("""
                SELECT LTRIM(RTRIM(BLOCK_ID)), LTRIM(RTRIM(AFDELING_CODE)), LTRIM(RTRIM(ESTATE_CODE)) 
                FROM MD_BLOCK 
                WHERE AFDELING_CODE = ? 
                ORDER BY BLOCK_ID ASC
            """, (str(afdeling_code).strip(),))
        else:
            cursor.execute("""
                SELECT LTRIM(RTRIM(BLOCK_ID)), LTRIM(RTRIM(AFDELING_CODE)), LTRIM(RTRIM(ESTATE_CODE)) 
                FROM MD_BLOCK 
                ORDER BY BLOCK_ID ASC
            """)
        rows = cursor.fetchall()
        blocks = []
        for r in rows:
            b_id = str(r[0]).strip()
            afd = str(r[1]).strip() if r[1] else ""
            est = str(r[2]).strip() if r[2] else ""
            blocks.append({
                "block_id": b_id,
                "block_name": f"{b_id} ({afd})" if afd else b_id,
                "afdeling_code": afd,
                "estate_code": est
            })
        return blocks
    except Exception as ex:
        print(f"[ERROR get_all_blocks]: {ex}")
        return []
    finally:
        cursor.close()
        conn.close()

# 5. Insert Transaksi Input TPH dari Form Android ke TPH_TRANSACTION
def create_tph_transaction(data: TphTransactionCreate):
    conn = get_db_connection()
    if not conn:
        print("[DB ERROR] Gagal koneksi database di create_tph_transaction")
        return None
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO TPH_TRANSACTION (
                ESTATE_CODE, AFDELING_CODE, BLOCK_ID, TPH_NUMBER,
                KRANI_NIK, HARVEST_DATE, MATANG_COUNT, MENTAH_COUNT,
                BUAH_BUSUK_COUNT, TANGKAI_PANJANG_COUNT, ABNORMAL_COUNT,
                TOTAL_BUAH, PHOTO_PATH, SYNC_STATUS, CREATED_AT
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE());
        """
        cursor.execute(query, (
            str(data.estate_code).strip() if data.estate_code else None,
            str(data.afdeling_code).strip() if data.afdeling_code else None,
            str(data.block_id).strip() if data.block_id else None,
            str(data.tph_number).strip() if data.tph_number else None,
            str(data.krani_nik).strip() if data.krani_nik else None,
            data.harvest_date,
            data.matang_count,
            data.mentah_count,
            data.buah_busuk_count,
            data.tangkai_panjang_count,
            data.abnormal_count,
            data.total_buah,
            data.photo_path,
            data.sync_status
        ))
        
        cursor.execute("SELECT SCOPE_IDENTITY()")
        row = cursor.fetchone()
        inserted_id = int(row[0]) if row and row[0] is not None else 1
        
        conn.commit()
        return inserted_id
    except Exception as ex:
        conn.rollback()
        print(f"\n[ERROR DETAIL SQL INSERT]: {ex}\n")
        return None
    finally:
        cursor.close()
        conn.close()

# 6. Ambil Riwayat Transaksi TPH Terbaru
def get_recent_transactions(limit: int = 20):
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT TOP ({limit}) 
                ID, ESTATE_CODE, AFDELING_CODE, BLOCK_ID, TPH_NUMBER, 
                KRANI_NIK, HARVEST_DATE, TOTAL_BUAH, SYNC_STATUS, CREATED_AT
            FROM TPH_TRANSACTION
            ORDER BY CREATED_AT DESC
        """)
        rows = cursor.fetchall()
        results = []
        for r in rows:
            results.append({
                "id": r[0],
                "estate_code": str(r[1]).strip() if r[1] else "",
                "afdeling_code": str(r[2]).strip() if r[2] else "",
                "block_id": str(r[3]).strip() if r[3] else "",
                "tph_number": str(r[4]).strip() if r[4] else "",
                "krani_nik": str(r[5]).strip() if r[5] else "",
                "harvest_date": str(r[6]) if r[6] else "",
                "total_buah": r[7],
                "sync_status": str(r[8]).strip() if r[8] else "SYNCED",
                "created_at": str(r[9]) if r[9] else None
            })
        return results
    except Exception as ex:
        print(f"[ERROR get_recent_transactions]: {ex}")
        return []
    finally:
        cursor.close()
        conn.close()
