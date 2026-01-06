import json
import pytest

from backend.ingestion import parser


def test_parse_brd_splits_headings_and_extracts_markers(tmp_path):
    content = """
    # Login
    AC: User can login with valid creds
    Risk: Brute force attempts

    ## Payments
    AC: Supports UPI payments
    Risk: Payment gateway downtime
    """
    file_path = tmp_path / "brd_sample.txt"
    file_path.write_text(content)

    records = parser.parse_brd_document(str(file_path), default_priority="p1", feature_area="auth")

    assert len(records) == 2
    first, second = records

    assert first["id"].endswith("-1")
    assert first["title"].lower().startswith("login")
    assert first["priority"] == "P1"
    assert first["feature_area"] == "auth"
    assert first["acceptance_criteria"] == ["User can login with valid creds"]
    assert first["risks"] == ["Brute force attempts"]

    assert second["title"].lower().startswith("payments")
    assert second["acceptance_criteria"] == ["Supports UPI payments"]
    assert second["risks"] == ["Payment gateway downtime"]


def test_parse_api_excel_normalizes_and_parses(tmp_path):
    pd = pytest.importorskip("pandas")
    pytest.importorskip("openpyxl")

    df = pd.DataFrame(
        [
            {
                "service": "ledger",
                "path": "/v1/transfer",
                "method": "post",
                "version": "v1",
                "auth": "oauth2",
                "rate_limit": "100/m",
                "request_schema": json.dumps({"amount": "number"}),
                "response_schema": json.dumps({"status": "string"}),
                "errors": "400, 500",
                "tests": "smoke, regression",
            }
        ]
    )

    excel_path = tmp_path / "apis.xlsx"
    df.to_excel(excel_path, index=False)

    records = parser.parse_api_excel(str(excel_path))
    assert len(records) == 1
    rec = records[0]

    assert rec["method"] == "POST"
    assert rec["path"] == "/v1/transfer"
    assert rec["errors"] == ["400", "500"]
    assert rec["tests"] == ["smoke", "regression"]
    assert rec["request_schema"] == {"amount": "number"}
    assert rec["response_schema"] == {"status": "string"}
    assert rec["source"].endswith("apis.xlsx")
