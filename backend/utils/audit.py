import hmac
import hashlib
import json
import os
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from db import AuditLog

# Secret key for HMAC signing
AUDIT_SECRET = os.getenv("AUDIT_SECRET", "audit-secret-key-change-this")

def calculate_hmac(log_data: dict) -> str:
    """Calculate HMAC signature for audit log to ensure tamper evidence"""
    # Create a canonical representation of the log data
    canonical_data = json.dumps(log_data, sort_keys=True, separators=(',', ':'))
    
    # Calculate HMAC
    signature = hmac.new(
        AUDIT_SECRET.encode('utf-8'),
        canonical_data.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return signature

async def log_audit(
    db: Session,
    user_id: Optional[int],
    action: str,
    resource_type: str,
    resource_id: Optional[str],
    ip_address: str,
    status: str,
    details: Optional[str] = None,
    user_agent: Optional[str] = None
):
    """Log an audit event with tamper-evident signature"""
    timestamp = datetime.utcnow()
    
    # Create log data for HMAC calculation
    log_data = {
        "user_id": user_id,
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "ip_address": ip_address,
        "status": status,
        "details": details,
        "user_agent": user_agent,
        "timestamp": timestamp.isoformat()
    }
    
    # Calculate HMAC signature
    hmac_signature = calculate_hmac(log_data)
    
    # Create audit log entry
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=ip_address,
        user_agent=user_agent,
        status=status,
        details=details,
        hmac_signature=hmac_signature,
        timestamp=timestamp
    )
    
    db.add(audit_log)
    db.commit()

def verify_audit_log(log: AuditLog) -> bool:
    """Verify the integrity of an audit log entry"""
    log_data = {
        "user_id": log.user_id,
        "action": log.action,
        "resource_type": log.resource_type,
        "resource_id": log.resource_id,
        "ip_address": log.ip_address,
        "status": log.status,
        "details": log.details,
        "user_agent": log.user_agent,
        "timestamp": log.timestamp.isoformat()
    }
    
    expected_signature = calculate_hmac(log_data)
    return hmac.compare_digest(expected_signature, log.hmac_signature)