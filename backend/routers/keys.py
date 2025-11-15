from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

from db import get_db, CryptoKey, User
from utils.jwt_auth import verify_token, require_role
from utils.crypto import generate_key, encrypt_key_with_master, decrypt_key_with_master
from utils.audit import log_audit

router = APIRouter()
security = HTTPBearer()

class KeyCreate(BaseModel):
    name: str
    key_type: str  # Supported key types: AES128GCM, AES256GCM, AES256CBC, ChaCha20Poly1305, RSA2048, RSA4096, ECC256, ECC384, Ed25519, HMAC256, HMAC512

class KeyResponse(BaseModel):
    id: int
    name: str
    key_type: str
    key_version: int
    is_active: bool
    is_revoked: bool
    created_by: int
    created_at: datetime
    rotated_at: Optional[datetime]
    revoked_at: Optional[datetime]

@router.post("/", response_model=KeyResponse)
async def create_key(
    key_data: KeyCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token_data = verify_token(credentials.credentials)
    user_id = int(token_data.get("sub"))
    user_role = token_data.get("role")
    
    # Only admins can create keys
    require_role(user_role, ["admin"])
    
    supported_key_types = [
        "AES128GCM", "AES256GCM", "AES256CBC", "ChaCha20Poly1305",
        "RSA", "RSA2048", "RSA4096", 
        "ECC256", "ECC384", "Ed25519",
        "HMAC256", "HMAC512"
    ]
    
    if key_data.key_type not in supported_key_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid key type. Supported types: {', '.join(supported_key_types)}"
        )
    
    try:
        # Generate the cryptographic key
        raw_key = generate_key(key_data.key_type)
        
        # Encrypt the key with the master key
        encrypted_key = encrypt_key_with_master(raw_key)
        
        # Store in database
        db_key = CryptoKey(
            name=key_data.name,
            key_type=key_data.key_type,
            encrypted_key=encrypted_key,
            created_by=user_id
        )
        
        db.add(db_key)
        db.commit()
        db.refresh(db_key)
        
        await log_audit(db, user_id, "create_key", "key", str(db_key.id), "127.0.0.1", "success")
        
        return KeyResponse(
            id=db_key.id,
            name=db_key.name,
            key_type=db_key.key_type,
            key_version=db_key.key_version,
            is_active=db_key.is_active,
            is_revoked=db_key.is_revoked,
            created_by=db_key.created_by,
            created_at=db_key.created_at,
            rotated_at=db_key.rotated_at,
            revoked_at=db_key.revoked_at
        )
        
    except Exception as e:
        await log_audit(db, user_id, "create_key", "key", None, "127.0.0.1", "failure")
        raise HTTPException(status_code=500, detail=f"Failed to create key: {str(e)}")

@router.get("/", response_model=List[KeyResponse])
async def list_keys(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token_data = verify_token(credentials.credentials)
    user_id = int(token_data.get("sub"))
    
    keys = db.query(CryptoKey).all()
    
    await log_audit(db, user_id, "list_keys", "key", None, "127.0.0.1", "success")
    
    return [
        KeyResponse(
            id=key.id,
            name=key.name,
            key_type=key.key_type,
            key_version=key.key_version,
            is_active=key.is_active,
            is_revoked=key.is_revoked,
            created_by=key.created_by,
            created_at=key.created_at,
            rotated_at=key.rotated_at,
            revoked_at=key.revoked_at
        )
        for key in keys
    ]

@router.post("/{key_id}/rotate", response_model=KeyResponse)
async def rotate_key(
    key_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token_data = verify_token(credentials.credentials)
    user_id = int(token_data.get("sub"))
    user_role = token_data.get("role")
    
    # Only admins can rotate keys
    require_role(user_role, ["admin"])
    
    db_key = db.query(CryptoKey).filter(CryptoKey.id == key_id).first()
    if not db_key:
        raise HTTPException(status_code=404, detail="Key not found")
    
    if db_key.is_revoked:
        raise HTTPException(status_code=400, detail="Cannot rotate a revoked key")
    
    try:
        # Generate new key
        raw_key = generate_key(db_key.key_type)
        encrypted_key = encrypt_key_with_master(raw_key)
        
        # Update the existing key
        db_key.encrypted_key = encrypted_key
        db_key.key_version += 1
        db_key.rotated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_key)
        
        await log_audit(db, user_id, "rotate_key", "key", str(key_id), "127.0.0.1", "success")
        
        return KeyResponse(
            id=db_key.id,
            name=db_key.name,
            key_type=db_key.key_type,
            key_version=db_key.key_version,
            is_active=db_key.is_active,
            is_revoked=db_key.is_revoked,
            created_by=db_key.created_by,
            created_at=db_key.created_at,
            rotated_at=db_key.rotated_at,
            revoked_at=db_key.revoked_at
        )
        
    except Exception as e:
        await log_audit(db, user_id, "rotate_key", "key", str(key_id), "127.0.0.1", "failure")
        raise HTTPException(status_code=500, detail=f"Failed to rotate key: {str(e)}")

@router.post("/{key_id}/revoke", response_model=KeyResponse)
async def revoke_key(
    key_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token_data = verify_token(credentials.credentials)
    user_id = int(token_data.get("sub"))
    user_role = token_data.get("role")
    
    # Only admins can revoke keys
    require_role(user_role, ["admin"])
    
    db_key = db.query(CryptoKey).filter(CryptoKey.id == key_id).first()
    if not db_key:
        raise HTTPException(status_code=404, detail="Key not found")
    
    # Mark as revoked
    db_key.is_revoked = True
    db_key.is_active = False
    db_key.revoked_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_key)
    
    await log_audit(db, user_id, "revoke_key", "key", str(key_id), "127.0.0.1", "success")
    
    return KeyResponse(
        id=db_key.id,
        name=db_key.name,
        key_type=db_key.key_type,
        key_version=db_key.key_version,
        is_active=db_key.is_active,
        is_revoked=db_key.is_revoked,
        created_by=db_key.created_by,
        created_at=db_key.created_at,
        rotated_at=db_key.rotated_at,
        revoked_at=db_key.revoked_at
    )

@router.delete("/{key_id}")
async def delete_key(
    key_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token_data = verify_token(credentials.credentials)
    user_id = int(token_data.get("sub"))
    user_role = token_data.get("role")
    
    # Only admins can delete keys
    require_role(user_role, ["admin"])
    
    db_key = db.query(CryptoKey).filter(CryptoKey.id == key_id).first()
    if not db_key:
        raise HTTPException(status_code=404, detail="Key not found")
    
    db.delete(db_key)
    db.commit()
    
    await log_audit(db, user_id, "delete_key", "key", str(key_id), "127.0.0.1", "success")
    
    return {"message": "Key deleted successfully"}