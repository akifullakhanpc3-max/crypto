from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import base64

from db import get_db, CryptoKey
from utils.jwt_auth import verify_token
from utils.crypto import encrypt_with_key, decrypt_with_key, decrypt_key_with_master
from utils.audit import log_audit

router = APIRouter()
security = HTTPBearer()

class EncryptRequest(BaseModel):
    key_id: int
    plaintext: str

class DecryptRequest(BaseModel):
    key_id: int
    ciphertext: str

class EncryptResponse(BaseModel):
    ciphertext: str
    key_id: int
    key_version: int

class DecryptResponse(BaseModel):
    plaintext: str
    key_id: int
    key_version: int

@router.post("/encrypt", response_model=EncryptResponse)
async def encrypt_data(
    request: EncryptRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token_data = verify_token(credentials.credentials)
    user_id = int(token_data.get("sub"))
    
    # Get the key from database
    db_key = db.query(CryptoKey).filter(CryptoKey.id == request.key_id).first()
    if not db_key:
        await log_audit(db, user_id, "encrypt", "data", str(request.key_id), "127.0.0.1", "failure")
        raise HTTPException(status_code=404, detail="Key not found")
    
    if not db_key.is_active or db_key.is_revoked:
        await log_audit(db, user_id, "encrypt", "data", str(request.key_id), "127.0.0.1", "failure")
        raise HTTPException(status_code=400, detail="Key is not active or has been revoked")
    
    try:
        # Decrypt the master-encrypted key
        raw_key = decrypt_key_with_master(db_key.encrypted_key)
        
        # Encrypt the plaintext with the key
        ciphertext = encrypt_with_key(request.plaintext, raw_key, db_key.key_type)
        
        await log_audit(db, user_id, "encrypt", "data", str(request.key_id), "127.0.0.1", "success")
        
        return EncryptResponse(
            ciphertext=base64.b64encode(ciphertext).decode('utf-8'),
            key_id=db_key.id,
            key_version=db_key.key_version
        )
        
    except Exception as e:
        await log_audit(db, user_id, "encrypt", "data", str(request.key_id), "127.0.0.1", "failure")
        raise HTTPException(status_code=500, detail=f"Encryption failed: {str(e)}")

@router.post("/decrypt", response_model=DecryptResponse)
async def decrypt_data(
    request: DecryptRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token_data = verify_token(credentials.credentials)
    user_id = int(token_data.get("sub"))
    
    # Get the key from database
    db_key = db.query(CryptoKey).filter(CryptoKey.id == request.key_id).first()
    if not db_key:
        await log_audit(db, user_id, "decrypt", "data", str(request.key_id), "127.0.0.1", "failure")
        raise HTTPException(status_code=404, detail="Key not found")
    
    # Allow decryption even for revoked keys (for legacy data)
    if not db_key.is_active and not db_key.is_revoked:
        await log_audit(db, user_id, "decrypt", "data", str(request.key_id), "127.0.0.1", "failure")
        raise HTTPException(status_code=400, detail="Key is not available")
    
    try:
        # Decrypt the master-encrypted key
        raw_key = decrypt_key_with_master(db_key.encrypted_key)
        
        # Decode the base64 ciphertext and decrypt
        ciphertext_bytes = base64.b64decode(request.ciphertext)
        plaintext = decrypt_with_key(ciphertext_bytes, raw_key, db_key.key_type)
        
        await log_audit(db, user_id, "decrypt", "data", str(request.key_id), "127.0.0.1", "success")
        
        return DecryptResponse(
            plaintext=plaintext,
            key_id=db_key.id,
            key_version=db_key.key_version
        )
        
    except Exception as e:
        await log_audit(db, user_id, "decrypt", "data", str(request.key_id), "127.0.0.1", "failure")
        raise HTTPException(status_code=500, detail=f"Decryption failed: {str(e)}")