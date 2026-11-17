import sys
import os
import shutil
import crud

from fastapi import FastAPI, HTTPException, status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from schemas import (
    LoginRequest, 
    EstateItem, 
    AfdelingItem, 
    BlockItem, 
    TphTransactionCreate, 
    TransactionResponse
)

app = FastAPI(
    title="SPECTRA Backend API",
    description="API Server SPECTRA - Sensus & Grading Panen Sawit terintegrasi SSMS SPECTRA_DB",
    version="1.0.0"
)

# 1. Folder uploads
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# 2. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["General"])
def root():
    return {
        "status": "online",
        "service": "SPECTRA BACKEND API",
        "database": "SPECTRA_DB",
        "version": "1.0.0"
    }

# 1. Endpoint Login Kerani Panen (Menyediakan payload fleksibel untuk Android)
@app.post("/api/auth/login", tags=["Authentication"])
def login(payload: LoginRequest):
    clean_nik = payload.nik.strip() if payload.nik else ""
    employee = crud.get_employee_by_nik(clean_nik)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NIK '{clean_nik}' tidak terdaftar di sistem SPECTRA"
        )
    if not employee.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akun karyawan ini berstatus tidak aktif"
        )
    
    # Mengembalikan kedua key "data" dan "user" agar kompatibel dengan model Android
    return {
        "status": "success",
        "message": f"Selamat datang, {employee['full_name']}",
        "data": employee,
        "user": employee
    }

# 2. Endpoint Master Estate
@app.get("/api/master/estates", response_model=List[EstateItem], tags=["Master Data"])
def get_estates():
    return crud.get_all_estates()

# 3. Endpoint Master Afdeling
@app.get("/api/master/afdelings", response_model=List[AfdelingItem], tags=["Master Data"])
def get_afdelings():
    return crud.get_all_afdelings()

# 4. Endpoint Master Blok
@app.get("/api/master/blocks", response_model=List[BlockItem], tags=["Master Data"])
def get_blocks(afdeling_code: Optional[str] = None):
    return crud.get_all_blocks(afdeling_code)

# Endpoint Upload Foto TBS
@app.post("/api/transactions/upload-photo", tags=["Transactions"])
async def upload_tph_photo(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {
            "status": "success",
            "message": "Foto TBS berhasil diunggah ke server",
            "photo_path": f"uploads/{file.filename}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengunggah foto: {str(e)}"
        )

# 5. Endpoint Input Transaksi Sensus TPH
@app.post("/api/transactions/tph", response_model=TransactionResponse, tags=["Transactions"])
def submit_tph_transaction(payload: TphTransactionCreate):
    inserted_id = crud.create_tph_transaction(payload)
    if not inserted_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal menyimpan transaksi TPH ke database SPECTRA_DB"
        )
    return {
        "status": "success",
        "message": "Data grading TPH berhasil disimpan",
        "inserted_id": inserted_id
    }

# 6. Endpoint Riwayat Transaksi TPH
@app.get("/api/transactions/recent", tags=["Transactions"])
def get_recent_transactions(limit: int = 20):
    return crud.get_recent_transactions(limit=limit)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5005, reload=True)
