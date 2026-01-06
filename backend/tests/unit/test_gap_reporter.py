from types import SimpleNamespace
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.gap_reporter import compute_gap_report


def test_compute_gap_report_matches_and_flags():
    contracts = [
        SimpleNamespace(metadata={"path": "/v1/foo", "method": "GET"}),
        SimpleNamespace(metadata={"path": "/v1/bar", "method": "POST"}),
        SimpleNamespace(metadata={"path": "/v1/baz", "method": "PUT"}),
    ]

    backend_endpoints = [
        SimpleNamespace(path="/v1/foo", method="GET"),
        SimpleNamespace(path="/v1/bar", method="GET"),  # method mismatch
        SimpleNamespace(path="/v1/qux", method="DELETE"),
    ]

    flutter_calls = [
        {"endpoint": "/v1/foo", "method": "GET"},
    ]

    gaps = compute_gap_report(
        api_contracts=contracts,
        backend_endpoints=backend_endpoints,
        flutter_calls=flutter_calls,
    )

    assert {("/v1/baz", "PUT")} == {
        (item["path"], item["method"])
        for item in gaps["missing_backend_endpoints"]
    }

    assert {("/v1/bar", "GET"), ("/v1/qux", "DELETE")} == {
        (item["path"], item["method"])
        for item in gaps["backend_without_contract"]
    }

    # bar (method mismatch) and baz (missing) are not used from Flutter
    assert {"/v1/bar", "/v1/baz"} == {item["path"] for item in gaps["contracts_not_used_in_flutter"]}

    # bar has a method mismatch
    assert {"/v1/bar"} == {item["path"] for item in gaps["method_mismatches"]}
