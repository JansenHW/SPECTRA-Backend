from pydantic import BaseModel
from typing import Optional, List

# Schema untuk Login Kerani Panen
class LoginRequest(BaseModel):
    nik: str

class LoginResponse(BaseModel):
    status: str
    message: str
    data: Optional[dict] = None
    user: Optional[dict] = None

# Schema Master Data untuk sinkronisasi ke Android
class EstateItem(BaseModel):
    estate_code: str
    estate_name: str

class AfdelingItem(BaseModel):
    afdeling_code: str
    estate_code: str

class BlockItem(BaseModel):
    block_id: str
    block_name: Optional[str] = None
    afdeling_code: Optional[str] = None
    estate_code: Optional[str] = None

# Schema Input Transaksi TPH dari Form Aplikasi Android
class TphTransactionCreate(BaseModel):
    estate_code: str
    afdeling_code: str
    block_id: str
    tph_number: str
    krani_nik: str
    harvest_date: str
    matang_count: Optional[int] = 0
    mentah_count: Optional[int] = 0
    buah_busuk_count: Optional[int] = 0
    tangkai_panjang_count: Optional[int] = 0
    abnormal_count: Optional[int] = 0
    total_buah: Optional[int] = 0
    photo_path: Optional[str] = None
    sync_status: Optional[str] = "SYNCED"

class TransactionResponse(BaseModel):
    status: str
    message: str
    inserted_id: Optional[int] = None
