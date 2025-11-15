# 🔐 Cryptographic Key Management System (KMS)

A secure full-stack web application for managing cryptographic keys, built with FastAPI, React, and PostgreSQL.

## 🎯 Features

- **Secure Key Management**: Generate, rotate, revoke, and delete AES-256-GCM and RSA-2048 keys
- **User Authentication**: JWT-based authentication with role-based access (Admin/User)
- **Encryption/Decryption**: Secure data encryption using managed keys with envelope encryption
- **Audit Logging**: Comprehensive tamper-evident audit logs for all operations
- **Dashboard UI**: Intuitive web interface for key management and operations
- **REST API**: Well-documented FastAPI with automatic OpenAPI/Swagger documentation
- **Docker Support**: Full containerization with Docker Compose

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │  FastAPI Backend│    │   PostgreSQL    │
│   (Port 3000)   │◄──►│   (Port 8000)   │◄──►│   (Port 5432)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Tech Stack

**Frontend:**
- React 18 + TypeScript
- Tailwind CSS for styling
- Axios for API communication
- React Router for navigation

**Backend:**
- FastAPI (Python 3.11)
- SQLAlchemy ORM with PostgreSQL
- Python Cryptography library (AES-256-GCM, RSA-2048)
- JWT authentication with role-based access
- HMAC-signed audit logs

**Infrastructure:**
- Docker + Docker Compose
- PostgreSQL 15
- Nginx (production ready)

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd kms-webapp
```

### 2. Environment Configuration

Create a `.env` file in the root directory:

```env
# Database Configuration
DATABASE_URL=postgresql://kms_user:kms_password@db:5432/kms_db
POSTGRES_DB=kms_db
POSTGRES_USER=kms_user
POSTGRES_PASSWORD=kms_password

# Security Keys (CHANGE THESE IN PRODUCTION!)
MASTER_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
JWT_SECRET=your-jwt-secret-key-change-this-in-production-make-it-long-and-random
AUDIT_SECRET=your-audit-secret-key-change-this-in-production-also-make-it-random

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000
```

**⚠️ IMPORTANT SECURITY NOTES:**
- Generate secure random keys for production
- Use a 64-character hex string for MASTER_KEY
- Keep these keys secure and never commit them to version control

### 3. Launch the Application

```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up --build -d
```

### 4. Access the Application

- **Web Interface**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health

### 5. Initial Setup

1. Create an admin account through the signup form
2. Login and start creating cryptographic keys
3. Use the Encryption Tool to test encryption/decryption
4. View audit logs in the Admin panel

## 📖 API Documentation

The API is fully documented with OpenAPI/Swagger. Access the interactive documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Authentication
- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info

#### Key Management
- `GET /api/keys` - List all keys
- `POST /api/keys` - Create new key (Admin only)
- `POST /api/keys/{id}/rotate` - Rotate key (Admin only)
- `POST /api/keys/{id}/revoke` - Revoke key (Admin only)
- `DELETE /api/keys/{id}` - Delete key (Admin only)

#### Encryption/Decryption
- `POST /api/encrypt` - Encrypt data with specified key
- `POST /api/decrypt` - Decrypt data with specified key

#### Audit Logs
- `GET /api/audit/logs` - Get audit logs (Admin only)
- `GET /api/audit/logs/summary` - Get audit summary (Admin only)

## 🔐 Security Features

### Encryption at Rest
- All cryptographic keys are encrypted using a master key (AES-256-GCM)
- Master key is derived from environment variables
- Database passwords and sensitive data are properly secured

### Audit Logging
- Every API operation is logged with HMAC signatures for tamper evidence
- Includes user ID, action, timestamp, IP address, and status
- Failed operations are also logged for security monitoring

### Access Control
- **Admin**: Can create, rotate, revoke, and delete keys; view audit logs
- **User**: Can encrypt/decrypt data using existing keys
- JWT tokens with role-based permissions

### Key Lifecycle Management
- **Active Keys**: Available for encryption and decryption
- **Revoked Keys**: Cannot encrypt but can decrypt legacy data
- **Rotation**: Generate new key versions while maintaining backward compatibility

## 🧪 Testing

### Backend Tests
```bash
cd backend
pip install -r requirements.txt
pytest
```

### Frontend Tests
```bash
cd frontend
npm install
npm test
```

## 🛠️ Development

### Running in Development Mode

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

#### Database
```bash
docker run --name kms-postgres \
  -e POSTGRES_DB=kms_db \
  -e POSTGRES_USER=kms_user \
  -e POSTGRES_PASSWORD=kms_password \
  -p 5432:5432 \
  -d postgres:15-alpine
```

## 📁 Project Structure

```
kms-webapp/
├── backend/                 # FastAPI backend
│   ├── main.py             # Application entry point
│   ├── db.py               # Database models and config
│   ├── requirements.txt    # Python dependencies
│   ├── routers/            # API route handlers
│   │   ├── auth.py         # Authentication endpoints
│   │   ├── keys.py         # Key management endpoints
│   │   ├── encrypt.py      # Encryption/decryption endpoints
│   │   └── audit.py        # Audit log endpoints
│   └── utils/              # Utility functions
│       ├── crypto.py       # Cryptographic operations
│       ├── jwt_auth.py     # JWT token handling
│       ├── audit.py        # Audit logging
│       └── rotation.py     # Key rotation logic
├── frontend/               # React frontend
│   ├── public/             # Static assets
│   ├── src/
│   │   ├── api/            # API client functions
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   └── App.jsx         # Main application component
│   ├── package.json        # Frontend dependencies
│   └── tailwind.config.js  # Tailwind CSS configuration
├── docker-compose.yml      # Docker services definition
├── .env.example           # Environment variables template
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `MASTER_KEY` | Master encryption key (hex) | Yes | - |
| `JWT_SECRET` | JWT signing secret | Yes | - |
| `AUDIT_SECRET` | HMAC signing secret for audit logs | Yes | - |
| `REACT_APP_API_URL` | Backend API URL | No | http://localhost:8000 |

### Key Rotation Schedule

By default, keys are recommended for rotation every 90 days. You can modify this in the `rotation.py` utility file.

## 🚨 Production Deployment

### Security Checklist

- [ ] Generate cryptographically secure random keys
- [ ] Use HTTPS in production
- [ ] Configure proper firewall rules
- [ ] Enable database SSL connections
- [ ] Set up monitoring and alerting
- [ ] Regular security updates
- [ ] Backup encryption keys securely
- [ ] Implement key escrow if required

### Environment-Specific Configurations

```bash
# Production example
MASTER_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -base64 64)
AUDIT_SECRET=$(openssl rand -base64 64)
```

## 📊 Monitoring

### Health Checks
- Database connectivity: `GET /health`
- API status: `GET /`

### Metrics to Monitor
- Key creation/rotation/revocation rates
- Encryption/decryption operation volumes
- Failed authentication attempts
- Audit log integrity checks

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the API documentation at http://localhost:8000/docs
2. Review the audit logs for troubleshooting
3. Open an issue in the project repository

---

**⚠️ Security Notice**: This is a demonstration KMS system. For production use, conduct a thorough security review and penetration testing.