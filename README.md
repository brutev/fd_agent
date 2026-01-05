# FD Agent System - AI-Powered Change Request Handler

A complete production-ready MVP system for an AI agent that maintains persistent memory across conversations for handling Change Requests (CRs) in a Financial Domain (FD) application.

## Architecture

- **Frontend**: Flutter (Android + iOS)
- **Backend**: Python (FastAPI)
- **Agent System**: Python-based with persistent memory
- **Database**: SQLite + Chroma Vector DB
- **Testing**: Comprehensive unit, widget, integration tests

## Quick Start

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m pytest tests/ -v --cov=. --cov-report=html
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Flutter Setup

```bash
cd mobile
flutter pub get
flutter test --coverage
flutter run
```

### Agent System

```bash
cd backend
python -c "from agents.orchestrator import AgentOrchestrator; agent = AgentOrchestrator(); agent.analyze_codebase('/path/to/project')"
```

## Features

### Flutter App (Indian Banking)
- Mobile OTP + Biometric Authentication
- Account Management (Balance, Statements)
- Transactions (NEFT, RTGS, IMPS, UPI)
- KYC (Aadhaar e-KYC, PAN verification)
- Loans (Application, EMI Calculator)
- Bill Payments, Cards Management

### Python Backend
- JWT Authentication with refresh tokens
- Banking APIs with Indian compliance
- Validators (IFSC, PAN, Aadhaar, UPI)
- Rate limiting and security middleware
- Comprehensive error handling

### AI Agent System
- Persistent memory across conversations
- Flutter + Python code analysis
- Smart context retrieval for CRs
- BRD document parsing
- Dependency mapping

## Testing Coverage

- **Backend**: 90%+ code coverage
- **Flutter**: 85%+ code coverage
- **Validators**: 100% coverage
- All user flows tested
- All error scenarios covered

## API Documentation

Visit `http://localhost:8000/docs` after starting the backend server.

## Test Coverage Reports

```bash
# Backend
cd backend && python -m pytest --cov=. --cov-report=html
open htmlcov/index.html

# Flutter
cd mobile && flutter test --coverage
genhtml coverage/lcov.info -o coverage/html
open coverage/html/index.html
```