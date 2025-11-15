# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a **Cryptographic Key Management System (KMS)** - a full-stack web application for secure key management built with:
- **Backend**: FastAPI (Python 3.11) with PostgreSQL
- **Frontend**: React 18 + TypeScript with Tailwind CSS
- **Infrastructure**: Docker Compose for development

## Common Development Commands

### Full Stack Development
```bash
# Start all services (recommended for development)
docker-compose up --build

# Start in background
docker-compose up --build -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f [backend|frontend|db]
```

### Backend Development
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run backend server with hot reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest

# Run tests with coverage
pytest --cov=.
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Run tests
npm test

# Build for production
npm run build
```

### Database Operations
```bash
# Connect to PostgreSQL (when running via Docker)
docker exec -it kms-webapp-db-1 psql -U kms_user -d kms_db

# Reset database (caution: destroys all data)
docker-compose down -v
docker-compose up --build
```

### Single Service Testing
```bash
# Test single backend endpoint
curl -X GET "http://localhost:8000/health"

# Test frontend connectivity
curl -X GET "http://localhost:3000"
```

## Architecture Overview

### High-Level Structure
```
Frontend (React) ←→ Backend (FastAPI) ←→ Database (PostgreSQL)
     ↓                    ↓                    ↓
  - UI Components    - API Endpoints      - User data
  - Authentication   - Business logic     - Crypto keys (encrypted)
  - State management - Crypto operations  - Audit logs
```

### Security Architecture
- **Master Key Encryption**: All cryptographic keys are encrypted at rest using AES-256-GCM with a master key
- **Envelope Encryption**: User keys encrypt data, master key encrypts user keys
- **JWT Authentication**: Role-based access (Admin/User) with token expiry
- **Audit Logging**: HMAC-signed tamper-evident logs for all operations

### Key Backend Modules

**Core Application (`main.py`)**
- FastAPI app initialization with CORS middleware
- Router registration for auth, keys, encrypt, and audit endpoints
- Database table creation on startup

**Database Models (`db.py`)**
- `User`: Authentication and role management
- `CryptoKey`: Encrypted key storage with lifecycle management
- `AuditLog`: Tamper-evident operation logging

**Router Architecture (`routers/`)**
- `auth.py`: User registration, login, JWT token management
- `keys.py`: CRUD operations for cryptographic keys (Admin only)
- `encrypt.py`: Data encryption/decryption using managed keys
- `audit.py`: Audit log retrieval and analysis (Admin only)

**Cryptographic Operations (`utils/crypto.py`)**
- Key generation (AES-256-GCM, RSA-2048)
- Master key encryption/decryption
- Data encryption/decryption with envelope encryption
- Secure key serialization and storage

**Authentication (`utils/jwt_auth.py`)**
- JWT token creation and verification
- Role-based access control
- Token expiry and refresh logic

### Frontend Architecture

**Component Structure**
- `App.jsx`: Main router with authentication state management
- `pages/`: Main application views (Dashboard, Login, EncryptTool, AuditLogs)
- `components/`: Reusable UI components (Navbar, KeyCard)
- `api/`: HTTP client functions for backend communication

**Authentication Flow**
1. JWT token stored in localStorage
2. Token decoded client-side for user info and role
3. Protected routes enforce role-based access
4. Automatic redirect on token expiry

### Security Considerations

**Environment Variables**
- `MASTER_KEY`: 64-character hex string for key encryption
- `JWT_SECRET`: Long random string for JWT signing
- `AUDIT_SECRET`: HMAC secret for audit log integrity

**Role-Based Access**
- **Admin**: Full CRUD on keys, view audit logs, manage users
- **User**: Encrypt/decrypt data with existing keys only

**Key Lifecycle**
- **Active**: Available for encryption and decryption
- **Revoked**: Decryption only (for legacy data)
- **Rotated**: New version created, old version marked for eventual removal

## Development Patterns

### Adding New Endpoints
1. Create route handler in appropriate router file
2. Add database models if needed in `db.py`
3. Implement business logic in `utils/` if complex
4. Add corresponding frontend API call in `api/`
5. Update frontend components to use new endpoint

### Cryptographic Operations
- Always use the crypto utilities in `utils/crypto.py`
- Never store raw keys - always encrypt with master key
- Log all crypto operations to audit trail
- Handle key rotation through `utils/rotation.py`

### Testing Strategy
- Backend: pytest with database fixtures
- Frontend: React Testing Library with user event simulation
- Integration: Full stack tests via Docker compose

### Environment Setup
- Copy `.env.example` to `.env` and update values
- Generate secure keys using `openssl rand -hex 32` (master key) and `openssl rand -base64 64` (JWT/audit secrets)
- Never commit real secrets to version control