from __future__ import annotations
from typing import Any, Dict, List
from types import SimpleNamespace


def _get(attr_obj: Any, key: str, default: str = "") -> str:
    if isinstance(attr_obj, dict):
        return attr_obj.get(key, default) or default
    if hasattr(attr_obj, key):
        return getattr(attr_obj, key) or default
    return default


def _normalize_path(path: str) -> str:
    return (path or "").strip("/").lower()


def _paths_match(a: str, b: str) -> bool:
    a_norm, b_norm = _normalize_path(a), _normalize_path(b)
    return a_norm == b_norm or a_norm in b_norm or b_norm in a_norm


def compute_gap_report(
    *,
    api_contracts: List[Any],
    backend_endpoints: List[Any],
    flutter_calls: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Compare contracts vs. backend endpoints vs. Flutter calls.

    Returns dict with missing_backend_endpoints, backend_without_contract,
    contracts_not_used_in_flutter, and method_mismatches.
    """
    missing_backend = []
    backend_without_contract = []
    contracts_not_used_in_flutter = []
    method_mismatches = []

    # Index backend endpoints by path for quick method checks
    backend_by_path = {}
    for ep in backend_endpoints:
        path = _get(ep, "path")
        method = _get(ep, "method").upper()
        backend_by_path.setdefault(_normalize_path(path), set()).add(method)

    for contract in api_contracts:
        meta = contract.metadata if hasattr(contract, "metadata") else getattr(contract, "meta", {})
        path = _get(meta, "path")
        method = _get(meta, "method").upper()

        # Find matching backend endpoint
        match = next(
            (
                ep
                for ep in backend_endpoints
                if _paths_match(path, _get(ep, "path")) and method == _get(ep, "method").upper()
            ),
            None,
        )
        if not match:
            # If path exists but method differs, record a method mismatch
            if _normalize_path(path) in backend_by_path:
                method_mismatches.append({
                    "path": path,
                    "contract_method": method,
                    "backend_methods": sorted(backend_by_path[_normalize_path(path)]),
                    "reason": "Method differs between contract and backend",
                })
            else:
                missing_backend.append({
                    "path": path,
                    "method": method,
                    "reason": "No matching FastAPI endpoint",
                })

        # Flutter usage check
        used = any(_paths_match(path, call.get("endpoint", "")) for call in flutter_calls)
        if not used:
            contracts_not_used_in_flutter.append({
                "path": path,
                "method": method,
                "reason": "Not called from Flutter",
            })

    for ep in backend_endpoints:
        ep_path = _get(ep, "path")
        ep_method = _get(ep, "method").upper()
        has_contract = any(
            _paths_match(_get(contract.metadata if hasattr(contract, "metadata") else {}, "path"), ep_path)
            and _get(contract.metadata if hasattr(contract, "metadata") else {}, "method").upper() == ep_method
            for contract in api_contracts
        )
        if not has_contract:
            backend_without_contract.append({
                "path": ep_path,
                "method": ep_method,
                "reason": "Endpoint not covered by contract",
            })

    return {
        "missing_backend_endpoints": missing_backend,
        "backend_without_contract": backend_without_contract,
        "contracts_not_used_in_flutter": contracts_not_used_in_flutter,
        "method_mismatches": method_mismatches,
    }
