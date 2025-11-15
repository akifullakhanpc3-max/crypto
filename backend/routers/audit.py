from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Union

from db import get_db, AuditLog
from utils.jwt_auth import verify_token, require_role

router = APIRouter()
security = HTTPBearer()

class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    resource_type: str
    resource_id: Optional[str]
    ip_address: str
    user_agent: Optional[str]
    status: str
    details: Optional[str]
    timestamp: datetime

@router.get("/logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    user_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    status: Optional[str] = Query(None)
):
    token_data = verify_token(credentials.credentials)
    user_role = token_data.get("role")
    
    # Only admins can view audit logs
    require_role(user_role, ["admin"])
    
    query = db.query(AuditLog)
    
    # Apply filters (handle empty strings as None)
    if user_id and user_id.strip():
        try:
            user_id_int = int(user_id.strip())
            query = query.filter(AuditLog.user_id == user_id_int)
        except ValueError:
            pass  # Ignore invalid user_id values
    if action and action.strip():
        query = query.filter(AuditLog.action == action.strip())
    if status and status.strip():
        query = query.filter(AuditLog.status == status.strip())
    
    # Order by timestamp descending (most recent first)
    query = query.order_by(AuditLog.timestamp.desc())
    
    # Apply pagination
    logs = query.offset(offset).limit(limit).all()
    
    return [
        AuditLogResponse(
            id=log.id,
            user_id=log.user_id,
            action=log.action,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
            status=log.status,
            details=log.details,
            timestamp=log.timestamp
        )
        for log in logs
    ]

@router.get("/logs/summary")
async def get_audit_summary(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token_data = verify_token(credentials.credentials)
    user_role = token_data.get("role")
    
    # Only admins can view audit summary
    require_role(user_role, ["admin"])
    
    # Get counts by action
    action_counts = db.query(
        AuditLog.action,
        func.count(AuditLog.id).label('count')
    ).group_by(AuditLog.action).all()
    
    # Get counts by status
    status_counts = db.query(
        AuditLog.status,
        func.count(AuditLog.id).label('count')
    ).group_by(AuditLog.status).all()
    
    # Get total logs count
    total_logs = db.query(AuditLog).count()
    
    return {
        "total_logs": total_logs,
        "actions": [{"action": action, "count": count} for action, count in action_counts],
        "statuses": [{"status": status, "count": count} for status, count in status_counts]
    }