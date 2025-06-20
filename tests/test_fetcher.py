import pytest
from unittest.mock import patch, MagicMock, mock_open
from mcp_server.fetcher import tasks
from mcp_server.api.routes import _filing_requests # To inject test data
import os # For path manipulation
import uuid # For patching uuid in amendment test

# This fixture is to ensure that current_app.logger and current_app.root_path are available
# as they are used in the tasks module.
@pytest.fixture
def mock_app_context(app): # Use the app fixture from conftest
    with app.app_context():
        # Additionally, ensure the storage directory exists for tasks that write files
        storage_dir = os.path.join(app.root_path, 'storage')
        os.makedirs(storage_dir, exist_ok=True)
        yield

def test_execute_filing_request_success(mock_app_context, monkeypatch):
    request_id = "fetcher_test_success_id"
    _filing_requests[request_id] = {
        "status": "pending",
        "details": {
            "company_identifier": {"ticker": "FETCHCO"},
            "requests": [{"form_type": "10-K_TEST", "date_range": ["2023-01-01", "2023-12-31"]}]
        },
        "results": []
    }

    # Mock rules loader to return specific rules
    mock_rules_data = { # Renamed from mock_rules to avoid conflict
        "10-K_TEST": {
            "source_api": "SEC-EDGAR",
            "issuance_interval": "Annual",
            "amendment_process": "10-K/A for full amendment",
            "relevant_entity_types": ["US Public Company"]
        }
    }
    monkeypatch.setattr(tasks.rules_loader, 'load_rules', lambda: mock_rules_data)

    # Mock file creation
    m = mock_open()
    with patch('mcp_server.fetcher.tasks.open', m):
        # Patch time.sleep to speed up the test
        with patch('time.sleep', return_value=None):
            tasks.execute_filing_request(request_id, _filing_requests)

    assert _filing_requests[request_id]["status"] == "complete"
    assert len(_filing_requests[request_id]["results"]) == 1
    result = _filing_requests[request_id]["results"][0]
    assert result["form_type"] == "10-K_TEST"
    assert "filing_url" in result
    m.assert_called()

def test_execute_filing_request_rule_not_found(mock_app_context, monkeypatch):
    request_id = "fetcher_test_no_rule_id"
    _filing_requests[request_id] = {
        "status": "pending",
        "details": {
            "company_identifier": {"ticker": "NORULECO"},
            "requests": [{"form_type": "NO-RULE-FORM", "date_range": ["2023-01-01", "2023-12-31"]}]
        },
        "results": []
    }
    monkeypatch.setattr(tasks.rules_loader, 'load_rules', lambda: {}) # No rules

    with patch('time.sleep', return_value=None): # Patch sleep here too
        tasks.execute_filing_request(request_id, _filing_requests)

    assert _filing_requests[request_id]["status"] == "complete"
    assert len(_filing_requests[request_id]["results"]) == 1
    result = _filing_requests[request_id]["results"][0]
    assert result["form_type"] == "NO-RULE-FORM"
    assert "error" in result
    assert "Rules not found" in result["error"]

@patch('mcp_server.fetcher.tasks.simulate_sec_edgar_fetch', side_effect=Exception("EDGAR Sim Down"))
def test_execute_filing_request_fetch_exception(mock_simulate_fetch_fails, mock_app_context, monkeypatch):
    request_id = "fetcher_test_sim_fail_id"
    _filing_requests[request_id] = {
        "status": "pending",
        "details": {
            "company_identifier": {"ticker": "SIMFAILCO"},
            "requests": [{"form_type": "10-K_TEST", "date_range": ["2023-01-01", "2023-12-31"]}]
        },
        "results": []
    }
    mock_rules_data = {"10-K_TEST": {"amendment_process": "test"}}
    monkeypatch.setattr(tasks.rules_loader, 'load_rules', lambda: mock_rules_data)

    with patch('time.sleep', return_value=None):
        tasks.execute_filing_request(request_id, _filing_requests)

    assert _filing_requests[request_id]["status"] == "error"
    assert "error_message" in _filing_requests[request_id]
    assert "EDGAR Sim Down" in _filing_requests[request_id]["error_message"]

@patch('mcp_server.fetcher.tasks.open', new_callable=mock_open)
@patch('time.sleep', return_value=None) # Patch time.sleep globally for this test
def test_simulate_sec_edgar_fetch_creates_files(mock_sleep, mock_file_open, app):
    with app.app_context():
        form_type = "SIM-TEST"
        # Ensure date_range_str is a list of strings as expected by the function
        date_range_str = ["2023-01-01", "2023-12-31"]
        company_id = {"ticker": "SIMTESTCO"}
        rules = {"amendment_process": "None"}

        results = tasks.simulate_sec_edgar_fetch(form_type, date_range_str, company_id, rules)

    assert len(results) == 1
    result = results[0]
    assert result["form_type"] == form_type
    assert result["is_amended"] == False
    assert "filing_url" in result

    mock_file_open.assert_called()
    args_list = mock_file_open.call_args_list
    written_file_path = args_list[0][0][0]
    assert form_type.replace('-', '') in written_file_path
    # mock_filing_date is date_range_str[1] which is "2023-12-31"
    assert date_range_str[1].replace('-', '') in written_file_path

    # Test amendment simulation
    rules_amend = {"amendment_process": "Can be amended", "relevant_entity_types": ["Test"]}
    # Patching uuid.uuid4 specifically where it's used in the tasks module.
    with patch('mcp_server.fetcher.tasks.uuid.uuid4') as mock_uuid_call:
        mock_uuid_instance = MagicMock()
        mock_uuid_instance.int = 0 # Standard way to force the modulo condition
        mock_uuid_call.return_value = mock_uuid_instance

        with app.app_context():
             results_amended = tasks.simulate_sec_edgar_fetch(form_type, date_range_str, company_id, rules_amend)

    assert len(results_amended) == 1
    result_amended = results_amended[0]
    assert result_amended["is_amended"] == True, "The 'is_amended' flag should be True when uuid mock forces amendment."
    assert "amendment_url" in result_amended, "An amendment_url should be present when amended."

    # Reset mock_file_open to specifically check calls for the amendment part
    mock_file_open.reset_mock()
    with patch('mcp_server.fetcher.tasks.uuid.uuid4') as mock_uuid_call_again: # Use a new mock name for clarity
        mock_uuid_instance_again = MagicMock()
        mock_uuid_instance_again.int = 0 # Standard way
        mock_uuid_call_again.return_value = mock_uuid_instance_again

        with app.app_context():
            # This call should result in an amendment and thus 2 file writes
            tasks.simulate_sec_edgar_fetch(form_type, date_range_str, company_id, rules_amend)
        # This specific call should make two writes: one for main, one for amendment.
        assert mock_file_open.call_count == 2, "Expected 2 file writes (main + amendment) for this call."

    # Clean up any created files in storage (though mock_open prevents actual file writes)
    storage_dir = os.path.join(app.root_path, 'storage')
    for item in os.listdir(storage_dir): # This loop might not be needed with mock_open
        item_path = os.path.join(storage_dir, item)
        if "SIM-TEST" in item and os.path.isfile(item_path): # Only remove files from this test
             os.remove(item_path)
