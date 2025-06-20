import datetime
from datetime import timezone # Import timezone
import time
import uuid
import os
from flask import current_app # To access logger and app config like root_path

# To access _filing_requests, we need to import it from the api.routes module.
# This creates a dependency, which is acceptable for this project size.
# In larger apps, a dedicated state management module or service might be used.
from mcp_server.api.routes import _filing_requests
from mcp_server.rules_engine import loader as rules_loader

def generate_mock_filename(form_type, date_str, is_amendment=False):
    """Generates a unique-ish filename and file_id."""
    ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    suffix = "_amended" if is_amendment else ""
    # file_id will be the filename for simplicity in this mock setup
    file_id = f"{form_type.replace('-', '')}_{date_str.replace('-', '')}{suffix}_{ts}.txt"
    return file_id

def simulate_sec_edgar_fetch(form_type, date_range_str, company_identifier, rules):
    """
    Simulates fetching data from SEC EDGAR.
    Generates mock filing data.
    """
    current_app.logger.info(f"Simulating fetch for {form_type} for {company_identifier} in range {date_range_str}")
    time.sleep(1) # Simulate network delay

    # Mock data generation
    # For simplicity, let's assume one filing per request, possibly amended.
    # Use a fixed date or derive one from date_range for mock purposes
    mock_filing_date = date_range_str[1] # e.g., use end of range
    if isinstance(mock_filing_date, list): # Ensure it's not a list if passed directly
        mock_filing_date = mock_filing_date[0]


    # Ensure STORAGE_PATH is correctly determined using app's root_path
    # current_app might not be available if this module is imported before app context is pushed
    # However, execute_filing_request is called within an app_context.
    storage_path = os.path.join(current_app.root_path, 'storage')
    if not os.path.exists(storage_path):
        os.makedirs(storage_path, exist_ok=True)
        current_app.logger.info(f"Created storage directory: {storage_path}")

    filing_result = {
        "form_type": form_type,
        "date": mock_filing_date, # This should be the actual filing date found
        "is_amended": False,
        "filing_url": None,
        "amendment_url": None
    }

    # Create mock main filing
    main_file_id = generate_mock_filename(form_type, mock_filing_date)
    main_file_path = os.path.join(storage_path, main_file_id)
    with open(main_file_path, 'w') as f:
        f.write(f"Mock content for {form_type} filed by {company_identifier.get('ticker', 'UnknownTicker')} on {mock_filing_date}\n")
        f.write(f"File ID: {main_file_id}\n")
    filing_result["filing_url"] = f"/filings/download/{main_file_id}"
    current_app.logger.info(f"Mocked main filing: {main_file_path}")


    # Simulate amendment based on rules
    amendment_rules = rules.get("amendment_process", "")
    # Simple check: if "amendment" is in the string, assume it can be amended.
    # And for mock, let's say 50% chance of being amended.
    if "amendment" in amendment_rules.lower() and uuid.uuid4().int % 2 == 0:
        filing_result["is_amended"] = True
        amendment_file_id = generate_mock_filename(form_type, mock_filing_date, is_amendment=True)
        amendment_file_path = os.path.join(storage_path, amendment_file_id)
        with open(amendment_file_path, 'w') as f:
            f.write(f"Mock AMENDED content for {form_type} ({rules.get('amendment_process')}) by {company_identifier.get('ticker', 'UnknownTicker')} on {mock_filing_date}\n")
            f.write(f"File ID: {amendment_file_id}\nOriginal File ID: {main_file_id}\n")
        filing_result["amendment_url"] = f"/filings/download/{amendment_file_id}"
        current_app.logger.info(f"Mocked amendment: {amendment_file_path}")

    return [filing_result] # Return as a list, as a form_type request could yield multiple actual filings in reality


def execute_filing_request(request_id, requests_store):
    """
    The main logic for processing a filing request.
    This function is called by the background task runner.
    `requests_store` is the shared dictionary _filing_requests from api.routes.
    """
    current_app.logger.info(f"Executing filing request for ID: {request_id}")
    request_job = requests_store.get(request_id)

    if not request_job:
        current_app.logger.error(f"Request ID {request_id} not found in store. Cannot process.")
        return

    if request_job["status"] != "pending":
        current_app.logger.warn(f"Request ID {request_id} is not pending (status: {request_job['status']}). Skipping.")
        return

    try:
        original_request_details = request_job["details"]
        company_identifier = original_request_details["company_identifier"]
        requested_forms = original_request_details["requests"] # list of {"form_type": "...", "date_range": ["...", "..."]}

        all_results = []
        rules_data = rules_loader.load_rules() # Load all rules once

        for form_req in requested_forms:
            form_type = form_req["form_type"]
            date_range = form_req["date_range"] # ["YYYY-MM-DD", "YYYY-MM-DD"]

            form_rules = rules_data.get(form_type)
            if not form_rules:
                current_app.logger.warn(f"No rules found for form type {form_type}. Skipping this form.")
                # Optionally add an error note to results for this specific form
                all_results.append({
                    "form_type": form_type,
                    "error": f"Rules not found for form type {form_type}"
                })
                continue

            # Simulate fetching
            # In a real scenario, this would involve API calls to SEC EDGAR, parsing, etc.
            # It would also handle pagination and multiple filings within the date range.
            # For now, one mock result per requested form_type.
            mock_results_for_form = simulate_sec_edgar_fetch(form_type, date_range, company_identifier, form_rules)
            all_results.extend(mock_results_for_form)
            current_app.logger.info(f"Processed mock fetch for {form_type}. Results: {len(mock_results_for_form)}")

        # Update the request store with the results
        requests_store[request_id]["status"] = "complete"
        requests_store[request_id]["results"] = all_results
        requests_store[request_id]["completed_at"] = datetime.datetime.now(timezone.utc).isoformat()
        current_app.logger.info(f"Request ID {request_id} processing complete. Results: {len(all_results)} items.")

    except Exception as e:
        current_app.logger.error(f"Unhandled exception processing request ID {request_id}: {e}", exc_info=True)
        requests_store[request_id]["status"] = "error"
        requests_store[request_id]["error_message"] = str(e)
        requests_store[request_id]["completed_at"] = datetime.datetime.now(timezone.utc).isoformat()

if __name__ == '__main__':
    # This part is for standalone testing of this module, if needed.
    # Requires a mock Flask app context.
    class MockApp:
        def __init__(self):
            self.root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) # Simulates 'mcp_server' dir
            # self.logger = logging.getLogger(__name__) # This would require importing logging
            # logging.basicConfig(level=logging.INFO) # This would require importing logging
            pass # Minimal mock

    # To run this effectively, you'd need to mock current_app or run within Flask context
    print("Fetcher tasks module. Run within Flask app context or with mocks.")
    # Example of how you might test (very basic):
    # import logging # Required for the commented out test code
    # mock_app_instance = MockApp()
    # # This is conceptual for a standalone mock:
    # # with mock_app_instance.app_context():
    # rules_loader.RULES_FILE = os.path.join(mock_app_instance.root_path, 'rules_engine', 'rules.json')
    # _filing_requests['test-req-123'] = {
    #     "status": "pending",
    #     "details": {
    #         "company_identifier": {"ticker": "TEST"},
    #         "requests": [{"form_type": "10-K", "date_range": ["2022-01-01", "2022-12-31"]}]
    #     }
    # }
    # # current_app needs to be available for execute_filing_request to run,
    # # or the logger and path logic needs to be refactored to not depend on it directly.
    # # execute_filing_request('test-req-123', _filing_requests)
    # # print(_filing_requests['test-req-123'])
