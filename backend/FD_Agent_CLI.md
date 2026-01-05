# FD Agent System - Interactive CLI

This document provides an overview of the **FD Agent System** and its interactive CLI for analyzing codebases and handling change requests.

---

## 🚀 Overview

The **FD Agent System** is an AI-powered tool designed to:
- Analyze codebases (Flutter and Python).
- Process change requests (CRs) with detailed analysis and planning.
- Provide implementation suggestions, effort estimates, and test scenarios.

---

## 🛠️ Features

### How It Works (Agent Flow)
- **Orchestrator**: Coordinates analysis, memory, and CR handling (see agents/orchestrator.py).
- **Analyzers**: Flutter analyzer extracts widgets/BLoCs/routes/API calls; Python analyzer extracts FastAPI endpoints, Pydantic models, services, validators.
- **Memory**: ChromaDB (vector) for semantic search + SQLite (structured) for entities, relationships, API mappings, and CR history.
- **CR Handler**: Detects CR patterns, pulls context, suggests Flutter/Python changes, effort, tests, compliance notes.
- **CLI**: `run_agent.py` exposes `--analyze`, `--cr`, `--search`, `--interactive`, `--demo` for end-to-end runs.

### Planning Flow (BRD → Plan → Implementation)
1) **Analyze the codebase** (Flutter + Python) and store entities/relations in memory.
2) **Ingest BRD / CR docs + API sheets** (planned): parse text (DOCX/PDF) and Excel API definitions; normalize into requirements and API contracts.
3) **Map requirements to code**: match features/APIs to existing widgets, blocs, endpoints, models, validators; identify gaps.
4) **Impact & scope**: list affected files/modules; flag cross-layer touchpoints (UI → BLoC → API → DB/validators).
5) **Plan tasks**: decompose into frontend/backend/testing tasks with owners, dependencies, estimates, and acceptance criteria.
6) **Compliance & risk**: note RBI/PCI/PII, auth flows, limits, audit/logging, rate limits.
7) **Test strategy**: unit/widget/integration/api tests to add/update; coverage goals; regression focus areas.
8) **Execution**: implement changes with logic comments; keep existing behavior intact; prefer additive changes; migrate safely.
9) **Validate**: run linters/formatters/tests; sanity QA flows; update docs/BRD traceability.

**Planned automation** (future):
- Parsers for BRD (DOCX/PDF) and API Excel → structured requirements.
- Task plan export (Jira-ready) with dependencies and estimates.
- Impact matrix (requirements ↔ code artifacts ↔ tests).
- Test skeleton generation and CI hooks (pytest/flutter test).

### Flutter Coverage Depth (Clean Architecture / DI / TDD)
- **Entry points**: Parse `main.dart` and `app.dart` to find app init, router setup, and top-level providers.
- **Routing**: Extract named routes, `RouteGenerator`, `GoRouter`/`Navigator` usage to map screens and flows.
- **Feature slices**: Traverse `lib/features/**` to map Data/Domain/Presentation layers (data sources, repositories, usecases, blocs/cubits, widgets/pages).
- **DI container**: Read `injection_container.dart` (and other `di/` files) to list registrations, lifetimes, and feature-specific injectables.
- **Config & constants**: Index `core/constants/`, `core/config/`, `env` loaders, theming, localization, and feature flags.
- **Utilities**: Collect helpers in `core/utils/` and `shared/utils/` (validators, formatters, error mappers) and link them to call sites.
- **State management**: Detect Bloc/Cubit classes, events/states, and where they’re provided/consumed; map blocs to screens.
- **API contracts**: Extract Dio/HTTP calls, endpoints, methods, payload shapes, and tie them to repositories/usecases and blocs/screens.
- **Assets & theme**: Note fonts, colors, theme configs, and where applied.
- **Testing hooks**: Locate existing `test/` (unit/widget/golden/integration) and planned spots for new tests per feature slice.

**Planned enhancements to make this airtight**:
- Add deeper parsers for DI registrations and route graphs (including nested/navigation stacks).
- Build a feature graph (widgets ↔ blocs ↔ usecases ↔ repositories ↔ data sources ↔ endpoints) to drive impact analysis.
- Surface missing links: unregistered injectables, unused blocs, orphaned routes, or dead widgets.
- Generate test skeletons per layer (widget, bloc, usecase, repository) with placeholders for assertions and fixtures.

### Enterprise Roadmap (Next-Level Capabilities)
- **Docs/APIs ingestion**: Parse BRD/CR (PDF/DOCX) and API Excel into structured requirements/contracts.
- **Feature graph + impact**: Maintain graph across Flutter/Python; auto scope changes and regressions.
- **Planning engine**: Tasks with dependencies, estimates, AC, risks; export to Jira/Trello.
- **Test automation**: Generate test skeletons per layer; enforce `flutter test`, `dart analyze`, `pytest` in CI.
- **Compliance/security**: RBI/PII checks, rate limits, audit logs, input validation, dependency scanning.
- **Telemetry**: Trace agent runs; detect drift between BRD/API and code; surface missing/mismatched contracts.

### Requirement & API Schema (for parsers)
- Requirement: `id`, `title`, `description`, `priority`, `acceptance_criteria`, `feature_area`, `risk`, `compliance_tags` (e.g., PII/RBI), `dependencies`.
- API: `service`, `path`, `method`, `request_schema`, `response_schema`, `auth`, `rate_limit`, `errors`, `version`, `owner`, `tests`.

### Feature Graph Model (cross-stack)
- Nodes: `widget`, `bloc/cubit`, `usecase`, `repository`, `data_source`, `endpoint`, `validator`, `model`, `route`, `di_binding`, `test`.
- Edges: `uses`, `provides`, `calls`, `validates`, `navigates`, `injects`, `tested_by`.
- Uses: impact analysis, regression selection, missing-link detection (e.g., route without widget, DI without binding).

### Task Template (per change)
- **Frontend**: screens/widgets, bloc wiring, routes, theme/assets, localization, DI registrations.
- **Backend**: endpoints, models/validators, services/repos, DB/transactions, auth/rate limits, logging/audit.
- **Tests**: widget/bloc/usecase/repo/API; fixtures/mocks; golden/regression where needed.
- **Compliance/Risk**: PII handling, limits, audit, error handling, fallback/rollback.
- **Docs**: changelog/ADR/update BRD traceability.

### CI / Quality Gates
- `dart analyze`, `flutter test`, `pytest -q`, formatters.
- Block merges if coverage/regression suites fail; run critical-path smoke (auth/payments/kyc/navigation).

### Safe Implementation Workflow (Flutter)
1) **Plan diff-first**: derive impact (widgets ↔ blocs ↔ usecases ↔ repositories ↔ data sources ↔ endpoints). Prefer additive changes; avoid rewiring unless required.
2) **Guard rails**: keep existing routes and DI registrations intact; introduce new feature flags or screen entries instead of replacing flows.
3) **Scoped coding**:
  - UI: add/extend widgets/pages; keep navigation intact; wire new blocs via DI.
  - State: create new Bloc/Cubit + events/states; avoid altering shared blocs unless necessary.
  - Domain: add usecases and repositories; preserve existing contracts.
  - Data: add data sources/API calls; do not break existing models; version endpoints if needed.
4) **Config/DI**: register new injectables in `injection_container.dart`; keep lifetimes consistent; avoid removing existing bindings.
5) **Tests first (or alongside)**:
  - Widget tests for new screens/widgets.
  - Bloc tests for event→state logic.
  - Usecase/repo tests with mocks for data sources.
  - API contract tests (golden payloads) if touching network layer.
6) **Iterate safely**: run `flutter test` and `dart analyze` per slice; keep PRs small and vertical (UI→Bloc→Usecase→Repo→Data).
7) **Regression**: re-run critical flows (auth, navigation, payments) and existing widget/bloc suites to ensure no breakage.
8) **Review & docs**: add logic comments only where non-obvious; update routes/DI notes; link changes to BRD items.

### 1. **Codebase Analysis**
Analyze the codebase to extract key components:
- **Flutter Analysis**:
  - Widgets
  - BLoC patterns
  - API calls
  - Routes
- **Python Analysis**:
  - API endpoints
  - Pydantic models
  - Services
  - Validators
- **Memory Stats**:
  - Entities stored
  - Relationships between components

### 2. **Change Request (CR) Handling**
Process CRs to:
- Identify patterns and keywords.
- Analyze affected components.
- Suggest implementation steps.
- Estimate effort (complexity, total days, frontend/backend split).
- Generate test scenarios.
- Highlight compliance considerations.

### 3. **Contextual Search**
Search for relevant context in the codebase or memory database:
- Find specific files, components, or patterns.
- Retrieve related code or documentation.

### 4. **Interactive CLI**
Use the interactive CLI to:
- Analyze codebases.
- Process CRs.
- Search for context.
- Get help on available commands.

---

## 📋 Commands

### **Analyze Codebase**
Analyze the codebase at the specified path (default: current project).
```bash
python run_agent.py --analyze [path]
```

### **Process Change Request**
Process a CR by providing a description.
```bash
python run_agent.py --cr "Add UPI AutoPay mandate feature"
```

### **Search Context**
Search for relevant context in the codebase or memory.
```bash
python run_agent.py --search "UPI payment validation"
```

### **Interactive CLI**
Start the interactive CLI mode.
```bash
python run_agent.py --interactive
```

### **Demo Mode**
Run a quick demo of the agent's capabilities.
```bash
python run_agent.py --demo
```

### **Help**
Display help information.
```bash
python run_agent.py --help
```

---

## 🧑‍💻 Interactive CLI Usage

### Commands Available in CLI:
| Command         | Description                                      |
|-----------------|--------------------------------------------------|
| `analyze [path]`| Analyze the codebase (default: current project). |
| `cr <desc>`     | Process a change request.                       |
| `search <query>`| Search for relevant context.                    |
| `help`          | Show help information.                          |
| `quit/exit`     | Exit the CLI.                                   |

### Example CRs:
- "Add UPI AutoPay mandate feature for recurring payments."
- "Implement biometric authentication with fingerprint."
- "Add offline Aadhaar KYC verification."
- "Implement transaction limits based on KYC level."
- "Add annual tax statement generation feature."

---

## 🖥️ Demo Mode

The demo mode showcases the agent's capabilities:
1. **Analyze Codebase**: Analyze the FD Agent codebase.
2. **Process Sample CR**: Process a sample CR like "Add UPI AutoPay mandate feature."

Run the demo:
```bash
python run_agent.py --demo
```

---

## 📂 File Structure

### Main File
- **`run_agent.py`**: Entry point for the CLI.

### Key Modules
- **`agents/orchestrator.py`**: Coordinates all agents.
- **`agents/*`**: Individual agents for code analysis, CR handling, memory management, etc.

---

## 🛠️ Examples

### Analyze Codebase
```bash
python run_agent.py --analyze /path/to/project
```

### Process a Change Request
```bash
python run_agent.py --cr "Add UPI AutoPay mandate feature"
```

### Start Interactive CLI
```bash
python run_agent.py --interactive
```

### Run Demo
```bash
python run_agent.py --demo
```

---

## 📝 Notes
- Ensure all dependencies are installed before running the agent.
- Use the interactive CLI for a guided experience.
- For detailed logs, check the output of each command.

---

## 📖 Help
Run the following command to display help:
```bash
python run_agent.py --help
```

---

## 👋 Exit
To exit the CLI, type:
```bash
quit
```
or
```bash
exit
```