from flask import Blueprint, request, jsonify, current_app, send_from_directory
from mcp_server.rules_engine import loader as rules_loader
from mcp_server.app import scheduler # Import scheduler from app.py
import uuid
import datetime
from datetime import timezone # Import timezone
import os # For send_from_directory and path joining

# In-memory store for requests and their statuses
_filing_requests = {}

# Lock for controlling access to file deletion, if needed (simple approach first)
# from threading import Lock
# _download_lock = Lock() # For more complex scenarios

bp = Blueprint('api', __name__, url_prefix='/')

@bp.route('/forms/available', methods=['GET'])
def available_forms():
    entity_type = request.args.get('entity_type')
    if not entity_type:
        return jsonify({"error": "entity_type query parameter is required"}), 400
    try:
        rules_loader.load_rules() # Ensure rules are loaded
        applicable_forms = rules_loader.get_forms_by_entity_type(entity_type)
        current_app.logger.info(f"Applicable forms for {entity_type}: {applicable_forms}")
        return jsonify(applicable_forms), 200
    except Exception as e:
        current_app.logger.error(f"Error getting available forms: {e}", exc_info=True)
        return jsonify({"error": "Failed to retrieve forms"}), 500

def process_filing_request_task_runner(request_id_for_task):
    app = scheduler.app
    with app.app_context():
        current_app.logger.info(f"Background task runner started for request_id: {request_id_for_task}")
        try:
            from mcp_server.fetcher.tasks import execute_filing_request
            execute_filing_request(request_id_for_task, _filing_requests)
            current_app.logger.info(f"Background task via runner finished for request_id: {request_id_for_task}")
        except Exception as e:
            current_app.logger.error(f"Exception in background task runner for {request_id_for_task}: {e}", exc_info=True)
            if request_id_for_task in _filing_requests:
                _filing_requests[request_id_for_task]['status'] = 'error'
                _filing_requests[request_id_for_task]['error_message'] = f'Background task failed: {str(e)}'

@bp.route('/filings/request', methods=['POST'])
def request_filings():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    company_identifier = data.get('company_identifier')
    requests_list = data.get('requests')

    if not company_identifier or not requests_list:
        return jsonify({"error": "Missing company_identifier or requests list"}), 400
    if not isinstance(requests_list, list):
        return jsonify({"error": "'requests' must be a list"}), 400
    for req_item in requests_list:
        if not isinstance(req_item, dict) or 'form_type' not in req_item or 'date_range' not in req_item:
            return jsonify({"error": "Each item in 'requests' must be an object with 'form_type' and 'date_range'"}), 400
        if not isinstance(req_item['date_range'], list) or len(req_item['date_range']) != 2:
            return jsonify({"error": "'date_range' must be a list of two dates [start, end]"}), 400

    request_id = str(uuid.uuid4())
    _filing_requests[request_id] = {
        "status": "pending",
        "submitted_at": datetime.datetime.now(timezone.utc).isoformat(),
        "details": data,
        "results": []
    }

    try:
        scheduler.add_job(
            id=f"process_request_{request_id}",
            func=process_filing_request_task_runner,
            args=[request_id],
            trigger='date',
            run_date=datetime.datetime.now(timezone.utc) + datetime.timedelta(seconds=1)
        )
        current_app.logger.info(f"Scheduled background task for request_id: {request_id}")
    except Exception as e:
        current_app.logger.error(f"Error scheduling task for {request_id}: {e}", exc_info=True)
        _filing_requests[request_id]["status"] = "error"
        _filing_requests[request_id]["error_message"] = "Failed to schedule processing task"
        return jsonify({"error": "Failed to schedule processing task"}), 500

    status_url = request.url_root + f"filings/status/{request_id}"
    return jsonify({"request_id": request_id, "status_url": status_url}), 202

@bp.route('/filings/status/<string:request_id>', methods=['GET'])
def filing_status(request_id):
    current_app.logger.info(f"Status request for request_id: {request_id}")
    request_info = _filing_requests.get(request_id)

    if not request_info:
        current_app.logger.warning(f"Request ID {request_id} not found.")
        return jsonify({"error": "Request ID not found"}), 404

    response_data = {"status": request_info["status"]}
    if request_info["status"] == "complete":
        response_data["results"] = request_info.get("results", [])
    elif request_info["status"] == "error":
        response_data["message"] = request_info.get("error_message", "An unknown error occurred.")

    return jsonify(response_data), 200

@bp.route('/filings/download/<string:file_id>', methods=['GET'])
def download_filing(file_id):
    # Construct the path to the storage directory
    # current_app.root_path is the path to the 'mcp_server' directory
    storage_path = os.path.join(current_app.root_path, 'storage')
    file_path = os.path.join(storage_path, file_id)

    current_app.logger.info(f"Download request for file_id: {file_id}. Attempting to serve from: {file_path}")

    if not os.path.isfile(file_path): # Check if the specific file exists
        current_app.logger.warning(f"File not found at path: {file_path}")
        return jsonify({"error": "File not found or access expired"}), 404

    try:
        # Serve the file for download
        response = send_from_directory(storage_path, file_id, as_attachment=True)
        current_app.logger.info(f"Successfully prepared {file_id} for download.")

        # Attempt to delete the file after serving
        # This requires the response to be fully sent first.
        # @response.call_on_close decorator is a good way to handle this.
        @response.call_on_close
        def remove_file_after_download():
            # Create an app context for logging within this deferred function
            app = scheduler.app # Get the app instance from the scheduler (or pass it if not using scheduler)
            with app.app_context():
                try:
                    os.remove(file_path)
                    current_app.logger.info(f"Successfully deleted {file_id} from storage after download.")
                except Exception as e:
                    current_app.logger.error(f"Error deleting file {file_id} after download: {e}", exc_info=True)

        return response

    except Exception as e:
        current_app.logger.error(f"Error during download process for {file_id}: {e}", exc_info=True)
        return jsonify({"error": "Could not process file download"}), 500
