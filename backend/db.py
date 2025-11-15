from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://kms_user:kms_password@localhost:5432/kms_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")  # admin or user
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class CryptoKey(Base):
    __tablename__ = "crypto_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    key_type = Column(String)  # AES256GCM or RSA
    encrypted_key = Column(LargeBinary)  # Encrypted with master key
    key_version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    is_revoked = Column(Boolean, default=False)
    created_by = Column(Integer, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    rotated_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    action = Column(String)
    resource_type = Column(String)
    resource_id = Column(String, nullable=True)
    ip_address = Column(String)
    user_agent = Column(String, nullable=True)
    status = Column(String)  # success or failure
    details = Column(Text, nullable=True)
    hmac_signature = Column(String)  # For tamper evidence
    timestamp = Column(DateTime, default=datetime.utcnow)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()