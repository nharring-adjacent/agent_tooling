import pytest
import json
from unittest.mock import patch, MagicMock
from mcp_server.api.routes import _filing_requests # To inspect or set state
import os
from mcp_server.app import scheduler # To mock its methods
# from mcp_server.api import routes as api_routes_module # For more specific patching if needed

# Test /forms/available endpoint
def test_forms_available_success(client, mock_rules_file, monkeypatch, app): # Added app for context
    # Point the loader to our mock rules file for this test
    monkeypatch.setattr('mcp_server.rules_engine.loader.RULES_FILE', mock_rules_file)
    monkeypatch.setattr('mcp_server.rules_engine.loader._rules_cache', None) # Reset cache

    with app.app_context(): # For current_app.logger in loader
        response = client.get('/forms/available?entity_type=Test%20Entity')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "TEST-FORM" in data
    assert "10-K_TEST" in data

def test_forms_available_missing_param(client, app): # Added app for context
    with app.app_context():  # For current_app.logger in loader (though not strictly for this error path)
        response = client.get('/forms/available')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
    assert "entity_type query parameter is required" in data["error"]

# Test /filings/request endpoint
@patch.object(scheduler, 'add_job') # Mock the scheduler's add_job
def test_filings_request_success(mock_add_job, client):
    payload = {
        "company_identifier": {"ticker": "TEST"},
        "requests": [
            {"form_type": "10-K", "date_range": ["2022-01-01", "2023-12-31"]}
        ]
    }
    response = client.post('/filings/request', json=payload)
    assert response.status_code == 202 # Accepted
    data = json.loads(response.data)
    assert "request_id" in data
    assert "status_url" in data
    request_id = data["request_id"]
    assert request_id in _filing_requests
    assert _filing_requests[request_id]["status"] == "pending"
    mock_add_job.assert_called_once() # Check that scheduler.add_job was called

def test_filings_request_invalid_payload(client):
    response = client.post('/filings/request', json={"wrong_payload": True})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data

@patch.object(scheduler, 'add_job', side_effect=Exception("Scheduler down"))
def test_filings_request_scheduler_failure(mock_add_job_fails, client):
    payload = {
        "company_identifier": {"ticker": "FAIL"},
        "requests": [{"form_type": "8-K", "date_range": ["2023-01-01", "2023-01-31"]}]
    }
    response = client.post('/filings/request', json=payload)
    assert response.status_code == 500
    data = json.loads(response.data)
    assert "error" in data
    assert "Failed to schedule processing task" in data["error"]
    # Check if request was marked as error in store
    # This requires finding the request_id, which isn't returned on 500.
    # A robust way is to check the _filing_requests store for any entry with status 'error' and matching details.
    found_error_request = False
    for req_id, req_data in _filing_requests.items():
        if req_data.get("details", {}).get("company_identifier", {}).get("ticker") == "FAIL":
            if req_data["status"] == "error" and "Failed to schedule processing task" in req_data.get("error_message", ""):
                found_error_request = True
                break
    assert found_error_request, "Request should be in store and marked as error with specific message"


# Test /filings/status/{request_id}
def test_filing_status_pending(client):
    request_id = "test_pending_id"
    _filing_requests[request_id] = {"status": "pending"}
    response = client.get(f'/filings/status/{request_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "pending"

def test_filing_status_complete(client):
    request_id = "test_complete_id"
    results = [{"form_type": "10-K", "date": "2023-10-27", "filing_url": "/filings/download/file1"}]
    _filing_requests[request_id] = {"status": "complete", "results": results}
    response = client.get(f'/filings/status/{request_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "complete"
    assert data["results"] == results

def test_filing_status_not_found(client):
    response = client.get('/filings/status/non_existent_id')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert "error" in data
    assert "Request ID not found" in data["error"]

import sys # Import sys for sys.modules patch

# Test /filings/download/{file_id}
def test_filing_download_success_and_delete(client, app): # Changed test name and removed mock
    storage_dir = os.path.join(app.root_path, 'storage')
    # conftest.py should ensure storage_dir exists

    file_id = "test_download_and_delete.txt" # Changed filename for clarity
    file_path = os.path.join(storage_dir, file_id)

    with open(file_path, 'w') as f:
        f.write("Test content for download and delete.")

    assert os.path.exists(file_path), "File should exist before download"

    response = client.get(f'/filings/download/{file_id}')
    assert response.status_code == 200
    assert response.data == b"Test content for download and delete."
    assert response.headers["Content-Disposition"].startswith(f"attachment; filename={file_id}")

    # Ensure call_on_close callbacks are triggered for the test client
    # It's important that the test client fully processes the response,
    # which usually includes calling close() on the response object internally or when the 'with' block exits if used.
    if hasattr(response, 'close') and callable(response.close):
        response.close()
    # else:
        # If no close method, consuming response.data should be sufficient for test client
        # to trigger cleanup like @response.call_on_close for non-streaming responses.
        # For streaming, response. épuiser_stream() or similar might be needed.
        # Flask's test client typically handles this well enough.

    import time; time.sleep(0.1) # Add a small delay for call_on_close

    # Check that the file has actually been deleted
    assert not os.path.exists(file_path), "File should be deleted after download"


def test_filing_download_not_found(client, app): # Added app for context
    # Ensure storage dir exists for current_app.root_path reference
    # storage_dir = os.path.join(app.root_path, 'storage')
    # os.makedirs(storage_dir, exist_ok=True) # conftest should handle this

    response = client.get('/filings/download/non_existent_file.txt')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert "error" in data
    assert "File not found" in data["error"]
