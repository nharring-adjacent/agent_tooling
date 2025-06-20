import pytest
from mcp_server.app import create_app, scheduler
from mcp_server.api.routes import _filing_requests
import os
import shutil
import json # Added for mock_rules_file

@pytest.fixture(scope='session')
def app():
    """Session-wide test Flask app."""
    # Ensure a clean state for _filing_requests before each session if needed,
    # but usually test functions should handle their own state.
    _filing_requests.clear()

    # Create a specific test config if needed, e.g. app.config['TESTING'] = True
    # For now, the default create_app should be fine.
    # Ensure scheduler doesn't actually start running jobs during tests,
    # or use a mock scheduler if background jobs interfere.
    # For now, we rely on mocking out the add_job part in API tests.

    app_instance = create_app() # Renamed to avoid conflict with fixture name
    app_instance.config.update({
        "TESTING": True,
        "SCHEDULER_API_ENABLED": False, # Disable scheduler's own API if not needed
        # "SCHEDULER_AUTOSTART": False # Could prevent scheduler from starting
    })

    # Clear storage before and after session if files are created
    storage_dir = os.path.join(app_instance.root_path, 'storage')
    if os.path.exists(storage_dir):
        shutil.rmtree(storage_dir)
    os.makedirs(storage_dir, exist_ok=True)

    yield app_instance #Flask client is derived from this

    # Clean up storage after tests
    if os.path.exists(storage_dir):
        shutil.rmtree(storage_dir)

@pytest.fixture()
def client(app): # app fixture is injected here
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(autouse=True)
def cleanup_filing_requests():
    """Clear the in-memory _filing_requests store before each test."""
    _filing_requests.clear()
    yield # This ensures cleanup happens after the test if needed, but clear() is usually enough before.

@pytest.fixture
def mock_rules_file(tmp_path):
    """ Creates a temporary rules.json file for testing the rules loader. """
    rules_content = {
        "TEST-FORM": {
            "source_api": "TEST-API",
            "issuance_interval": "TestInterval",
            "amendment_process": "TEST/A",
            "relevant_entity_types": ["Test Entity", "Another Entity"]
        },
        "10-K_TEST": {
            "source_api": "SEC-EDGAR",
            "issuance_interval": "Annual",
            "amendment_process": "10-K/A for full amendment",
            "relevant_entity_types": ["US Public Company", "Test Entity"]
        }
    }
    # Changed from rules_dir = tmp_path / "rules_engine" to just tmp_path for simplicity
    # as loader.RULES_FILE will be monkeypatched directly to the file path.
    rules_file = tmp_path / "rules.json"
    with open(rules_file, 'w') as f:
        json.dump(rules_content, f)
    return str(rules_file) # Return path to the file
