# FD Agent System - AI-Powered Change Request Handler

A complete production-ready MVP system for an AI agent that **reads your codebase (Flutter + FastAPI), stores a graph of what exists, and plans changes for new requirements without breaking what’s there**.

## What the Agent Actually Does (plain words)

- Scans the code statically (no need to “tap” or run the app) to list screens, blocs, routes, API calls, endpoints, models, and validators.
- Builds a memory graph (SQLite + Chroma) so it knows what exists and how pieces connect.
- When you give a new requirement, it checks what’s missing, what conflicts, and suggests changes that fit safely.
- Produces two core outputs:
	- **Feature graph**: counts and maps of widgets/blocs/routes/API calls/endpoints/models.
	- **Gap report**: contracts vs backend vs client API calls, flagging missing or mismatched methods/paths.

## At-a-Glance Mindmap (text version)

```
[Codebase]
	|-- mobile/ (Flutter)
	|     |-- widgets, blocs, routes, API calls
	|
	|-- backend/ (FastAPI)
				|-- endpoints, models, services, validators

[Agent Scanner]
	|-- parses Flutter + Python
	|-- extracts structure
	|-- builds feature graph

[Memory]
	|-- SQLite (structured facts)
	|-- Chroma (semantic search)

[Outputs]
	|-- Feature graph → what exists today
	|-- Gap report → what’s missing/mismatched
	|-- CR plan → how a new requirement fits without breakage
```

## Visual Story (Padam Parthu Kadhai Sollu)

```
[CODE]  Flutter + FastAPI
	 |
	 |  (static scan)
	 v
[AGENT] Extracts widgets/blocs/routes/endpoints/models
	 |
	 |  (stores)
	 v
[MEMORY] SQLite + Chroma knowledge graph
	 |
	 |  (answers)
	 v
[YOU] Ask: feature graph? gap report? new CR plan?
```

## How It Feels to Use

- Tap in the mobile app → API call hits FastAPI → agent understands screens, APIs, and data models.
- Ask for a feature graph → agent returns counts of widgets/blocs/endpoints/models.
- Ask for a gap report → agent flags missing or mismatched APIs between docs, backend, and Flutter.

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