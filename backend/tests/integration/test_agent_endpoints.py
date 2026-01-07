from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient
from jose import jwt

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.main import app
from api.routes.agent import get_orchestrator
from config import settings


class DummyOrchestrator:
    def __init__(self):
        self.feature_graph_response = {
            "flutter": {"widgets": 1, "blocs": 2, "api_calls": 3, "routes": 4},
            "python": {"endpoints": 5, "models": 6, "services": 7},
            "timestamp": "now",
        }
        self.gap_report_response = {
            "missing_backend_endpoints": [],
            "backend_without_contract": [],
            "contracts_not_used_in_flutter": [],
            "method_mismatches": [],
            "timestamp": "now",
        }
        self.initialized = 0

    async def initialize(self):
        self.initialized += 1

    async def build_feature_graph(self, project_path: str):
        return {"project_path": project_path, **self.feature_graph_response}

    async def generate_gap_report(self, project_path: str):
        return {"project_path": project_path, **self.gap_report_response}


class FailingOrchestrator(DummyOrchestrator):
    async def build_feature_graph(self, project_path: str):
        raise RuntimeError("boom")


@pytest.fixture
def auth_headers():
    token = jwt.encode({"sub": "test-user"}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client_with_dummy_orchestrator():
    orch = DummyOrchestrator()
    app.dependency_overrides[get_orchestrator] = lambda: orch
    with TestClient(app) as client:
        yield client, orch
    app.dependency_overrides.clear()


def test_feature_graph_success(client_with_dummy_orchestrator, auth_headers):
    client, orch = client_with_dummy_orchestrator
    response = client.get("/api/v1/feature-graph", params={"path": "/tmp/project"}, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["project_path"] == "/tmp/project"
    assert data["flutter"]["widgets"] == 1
    assert orch.initialized == 1


def test_gap_report_success(client_with_dummy_orchestrator, auth_headers):
    client, orch = client_with_dummy_orchestrator
    response = client.get("/api/v1/gap-report", params={"path": "/tmp/project"}, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["project_path"] == "/tmp/project"
    assert data["method_mismatches"] == []
    assert orch.initialized == 1


def test_feature_graph_failure_returns_500(auth_headers):
    app.dependency_overrides[get_orchestrator] = FailingOrchestrator
    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.get("/api/v1/feature-graph", headers=auth_headers)
            assert response.status_code == 500
    finally:
        app.dependency_overrides.clear()
