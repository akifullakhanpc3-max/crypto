from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from db import CryptoKey
from utils.crypto import generate_key, encrypt_key_with_master
import logging

logger = logging.getLogger(__name__)

def should_rotate_key(key: CryptoKey, rotation_days: int = 90) -> bool:
    """Check if a key should be rotated based on age"""
    if key.is_revoked or not key.is_active:
        return False
    
    # Use rotated_at if available, otherwise use created_at
    last_rotation = key.rotated_at if key.rotated_at else key.created_at
    rotation_threshold = datetime.utcnow() - timedelta(days=rotation_days)
    
    return last_rotation < rotation_threshold

def rotate_key_if_needed(db: Session, key: CryptoKey, rotation_days: int = 90) -> bool:
    """Rotate a key if it needs rotation"""
    if not should_rotate_key(key, rotation_days):
        return False
    
    try:
        # Generate new key
        raw_key = generate_key(key.key_type)
        encrypted_key = encrypt_key_with_master(raw_key)
        
        # Update the key
        key.encrypted_key = encrypted_key
        key.key_version += 1
        key.rotated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Rotated key {key.id} to version {key.key_version}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to rotate key {key.id}: {str(e)}")
        db.rollback()
        return False

def auto_rotate_keys(db: Session, rotation_days: int = 90):
    """Automatically rotate all keys that need rotation"""
    keys_to_rotate = db.query(CryptoKey).filter(
        CryptoKey.is_active == True,
        CryptoKey.is_revoked == False
    ).all()
    
    rotated_count = 0
    for key in keys_to_rotate:
        if rotate_key_if_needed(db, key, rotation_days):
            rotated_count += 1
    
    logger.info(f"Auto-rotated {rotated_count} keys")
    return rotated_count