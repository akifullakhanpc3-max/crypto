from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import os
from dotenv import load_dotenv

from db import create_tables
from routers import auth, keys, encrypt, audit
from utils.jwt_auth import verify_token

load_dotenv()

app = FastAPI(
    title="Cryptographic Key Management System",
    description="A secure web application for managing cryptographic keys",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(keys.router, prefix="/api/keys", tags=["key management"])
app.include_router(encrypt.router, prefix="/api", tags=["encryption"])
app.include_router(audit.router, prefix="/api/audit", tags=["audit logs"])

@app.on_event("startup")
async def startup():
    create_tables()

@app.get("/")
async def root():
    return {"message": "KMS API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)