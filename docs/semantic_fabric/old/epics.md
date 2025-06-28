You are absolutely right. My apologies for staying at the sprint-plan level. For effective agentic coding, we need to move from "epics" to "stories," breaking down each task into its smallest logical, testable unit. The goal is a set of PRs so focused that the code changes themselves are the clearest possible specification of the work done.

Let's do this properly. Here is the nitty-gritty, project-manager-style breakdown of the implementation plan, designed for maximum clarity and minimal scope per task.

---
### **Detailed Implementation Plan (Pass 3.1)**

**Methodology:** The following tasks are ordered by dependency. Each task is designed to be a single, atomic Pull Request (PR). The "Test Requirements" are the definitive checklist for the reviewing agent.

---
### **Epic 1: Project Scaffolding**

* **1.1: Initialize Project and Dependencies**
    * **PR Title:** `build: initialize pyproject.toml with core dependencies`
    * **Description:** Create the `pyproject.toml` file to formally define the project, its dependencies, and lock them.
    * **File(s) to Create/Modify:** `pyproject.toml`, `poetry.lock` (or `pdm.lock`, etc.)
    * **Deliverable:** A `pyproject.toml` file specifying Python 3.11+ and adding `fastapi`, `uvicorn[standard]`, and `pydantic` as dependencies.
    * **Test Requirements:**
        * \[ ] Does the project successfully initialize and install dependencies using the package manager (e.g., `poetry install`) in a clean environment?
        * \[ ] Are the specified libraries (`fastapi`, `uvicorn`, `pydantic`) present in the lock file?

* **1.2: Create Application Directory Structure**
    * **PR Title:** `chore: create initial application directory structure`
    * **Description:** Lay out the empty directories and Python module initializers for the entire application.
    * **File(s) to Create/Modify:** `mcp_server/__init__.py`, `mcp_server/api/__init__.py`, `mcp_server/services/__init__.py`, `mcp_server/models/__init__.py`
    * **Deliverable:** A set of directories and `__init__.py` files creating the basic module structure.
    * **Test Requirements:**
        * \[ ] Does the directory structure exactly match the specification (`mcp_server/api`, `mcp_server/services`, `mcp_server/models`)?
        * \[ ] Is the project root still a valid Python package (i.e., can it be imported)?

* **1.3: Create Multi-Stage Dockerfile**
    * **PR Title:** `build: create multi-stage Dockerfile for production`
    * **Description:** Implement the production `Dockerfile`, including the `comby` installation, dependency management, and non-root user setup.
    * **File(s) to Create/Modify:** `Dockerfile`
    * **Deliverable:** A complete, buildable `Dockerfile`.
    * **Test Requirements:**
        * \[ ] Does the command `docker build .` complete successfully?
        * \[ ] Does the `Dockerfile` contain at least two stages (e.g., a `builder` and a final stage)?
        * \[ ] Does the final stage copy the `comby` binary from a source like `comby/comby`?
        * \[ ] Does the final stage create and switch to a non-root user (e.g., `USER appuser`)?
        * \[ ] Does the final stage define a `VOLUME /workspace`?
        * \[ ] Can a container be run from the image, and does `which comby` inside the container return a valid path?

---
### **Epic 2: Core Data Structures**

* **2.1: Implement API Request Models**
    * **PR Title:** `feat(models): implement pydantic request models`
    * **Description:** Define the Pydantic models for all incoming API request bodies.
    * **File(s) to Create/Modify:** `mcp_server/models/comby_models.py`
    * **Deliverable:** Pydantic classes for `IdeateRequest`, `ExecuteRequest`, and `ScanRequest`.
    * **Test Requirements:**
        * \[ ] Does each model in `comby_models.py` have fields and types that exactly match the "Pass 2 (Final)" specification for requests?
        * \[ ] Is there a unit test file (e.g., `tests/test_models.py`)?
        * \[ ] Does the test suite validate that creating a model with correct data succeeds?
        * \[ ] Does the test suite assert that `pydantic.ValidationError` is raised when a required field (e.g., `match_template`) is missing?

* **2.2: Implement API Response Models**
    * **PR Title:** `feat(models): implement pydantic response models`
    * **Description:** Define the Pydantic models for all API responses, including success and error cases.
    * **File(s) to Create/Modify:** `mcp_server/models/comby_models.py`
    * **Deliverable:** Pydantic classes for `IdeateSuccessResponse`, `ExecuteSuccessResponse`, `ScanSuccessResponse`, and `ErrorResponse`.
    * **Test Requirements:**
        * \[ ] Does each model in `comby_models.py` have fields and types that exactly match the "Pass 2 (Final)" specification for responses?
        * \[ ] Does the `ErrorResponse` model contain `success: bool`, `error_type: str`, and `details: str | object`?
        * \[ ] Does the unit test suite include tests that successfully create instances of each response model?

---
### **Epic 3: Ideate Endpoint Implementation**

* **3.1: Basic Health Check Endpoint**
    * **PR Title:** `feat(api): create basic FastAPI app with /health endpoint`
    * **Description:** Set up the main application entrypoint and a simple `/health` route to confirm the web server works.
    * **File(s) to Create/Modify:** `mcp_server/main.py`
    * **Deliverable:** A `main.py` file with a FastAPI app instance and a `GET /health` route that returns `{"status": "ok"}`.
    * **Test Requirements:**
        * \[ ] When the server is run via `uvicorn`, does a `GET` request to `/health` return a `200 OK` status?
        * \[ ] Is the response body of `/health` exactly `{"status":"ok"}`?

* **3.2: Implement Comby Snippet Runner Logic**
    * **PR Title:** `feat(services): implement comby snippet runner`
    * **Description:** Create the core, isolated logic for running `comby` on an in-memory string of code.
    * **File(s) to Create/Modify:** `mcp_server/services/comby_runner.py`
    * **Deliverable:** A function `run_comby_on_snippet(source: str, match: str, rewrite: str, lang: str) -> str`.
    * **Test Requirements:**
        * \[ ] Is there a `tests/test_comby_runner.py` file?
        * \[ ] Does the unit test for `run_comby_on_snippet` mock `subprocess.run`?
        * \[ ] Does the test assert that the mocked `subprocess.run` is called with a command list that includes `-stdin` and `-stdout`?
        * \[ ] Does the test assert that the mocked `subprocess.run` is called with a `timeout` argument (e.g., `timeout=15`)?
        * \[ ] Does the test assert that if the mock `subprocess` returns an error (`stderr`), a custom exception (e.g., `CombyExecutionError`) is raised?

* **3.3: Wire and Test the `/ideate` API Endpoint**
    * **PR Title:** `feat(api): implement /api/v1/ideate endpoint`
    * **Description:** Create the public API endpoint for `/ideate` and connect it to the `comby_runner` service.
    * **File(s) to Create/Modify:** `mcp_server/api/comby_routes.py`, `mcp_server/main.py`
    * **Deliverable:** A `POST /api/v1/ideate` route that takes an `IdeateRequest`, calls the service from 3.2, and returns an `IdeateSuccessResponse`.
    * **Test Requirements:**
        * \[ ] Is there an integration test file (e.g., `tests/test_api.py`)?
        * \[ ] Does a `POST` request to `/api/v1/ideate` with a valid payload return `200 OK` and a response matching the `IdeateSuccessResponse` schema?
        * \[ ] Does the `rewritten_code` field in the response show the correct code transformation?
        * \[ ] Does a request with a syntactically invalid `match_template` cause `comby` to error, resulting in a `422 Unprocessable Entity` response from the API?

*(The breakdowns for Epics 4, 5, and 6 would follow this same granular pattern, each focusing on separating the core service logic from the API wiring and having distinct unit and integration tests.)*You got it. I'm glad this level of detail is hitting the mark. Let's continue with the same nitty-gritty, project-manager style for the remaining epics.

Here is the rest of the detailed implementation plan.

---
### **Epic 4: Scan Endpoint Implementation**

* **4.1: Implement Comby Scan Runner Logic**
    * **PR Title:** `feat(services): implement comby scan runner for project-wide matching`
    * **Description:** Create the core, isolated logic for running a read-only `comby` scan across the `/workspace` directory.
    * **Dependencies:** Epic 3
    * **File(s) to Create/Modify:** `mcp_server/services/comby_runner.py`
    * **Deliverable:** A new function `run_comby_scan(match_template: str, file_filters: list[str], rule: str) -> list[dict]`. This function will parse the JSON output from `comby`.
    * **Test Requirements:**
        * \[ ] Does the unit test for `run_comby_scan` in `tests/test_comby_runner.py` mock `subprocess.run`?
        * \[ ] Does the test assert that the mocked `subprocess.run` is called with a command list that includes the `/workspace` directory as the target?
        * \[ ] Does the test assert the command includes the `-json-lines` and `-match-only` flags?
        * \[ ] Does the test assert that the `file_filters` are correctly passed as arguments to the command?
        * \[ ] Does the test simulate `comby` returning valid JSON lines to `stdout` and assert that the function correctly parses and returns a list of dictionaries?
        * \[ ] Does the test assert that a path traversal attempt in `file_filters` (e.g., `../..`) raises a `ValueError`?

* **4.2: Wire and Test the `/scan` API Endpoint**
    * **PR Title:** `feat(api): implement /api/v1/scan endpoint`
    * **Description:** Create the public API endpoint for `/scan` and connect it to the `comby_runner` scan service.
    * **Dependencies:** Task 4.1
    * **File(s) to Create/Modify:** `mcp_server/api/comby_routes.py`
    * **Deliverable:** A `POST /api/v1/scan` route that accepts a `ScanRequest`, calls the service from 4.1, and returns a `ScanSuccessResponse`.
    * **Test Requirements:**
        * \[ ] Does the integration test in `tests/test_api.py` create a temporary directory with a nested structure and at least three files?
        * \[ ] Does the test run the server container with this directory bind-mounted to `/workspace`?
        * \[ ] Does a `POST` request to `/api/v1/scan` with a valid payload return a `200 OK` status?
        * \[ ] Does the response body match the `ScanSuccessResponse` schema?
        * \[ ] Does the `matches_by_file` array in the response contain entries for the correct files?
        * \[ ] Does a request targeting a specific file extension (e.g., `file_filters: [".py"]`) only return results from `.py` files in the test directory?

---
### **Epic 5: Execute Endpoint Implementation**

* **5.1: Implement Comby Execute Runner Logic**
    * **PR Title:** `feat(services): implement comby execute runner for in-place refactoring`
    * **Description:** Create the core logic for running `comby` to modify files directly within the `/workspace` directory.
    * **Dependencies:** Epic 4
    * **File(s) to Create/Modify:** `mcp_server/services/comby_runner.py`
    * **Deliverable:** A new function `run_comby_execute(match_template: str, rewrite_template: str, file_filters: list[str], rule: str) -> dict`. This function will parse the statistics output from `comby`.
    * **Test Requirements:**
        * \[ ] Does the unit test for `run_comby_execute` mock `subprocess.run`?
        * \[ ] Does the test assert that the mocked `subprocess.run` is called with a command list that includes the `-in-place` flag?
        * \[ ] Does the test assert the command also includes the `-stats` flag to generate machine-readable statistics?
        * \[ ] Does the test simulate `comby` returning valid stats JSON to `stdout` and assert that the function correctly parses it into a dictionary?
        * \[ ] Does the test assert that a path traversal attempt in `file_filters` raises a `ValueError`?

* **5.2: Wire and Test the `/execute` API Endpoint**
    * **PR Title:** `feat(api): implement /api/v1/execute endpoint`
    * **Description:** Create the public API endpoint for `/execute`, connecting it to the `comby_runner` service that performs direct file modification.
    * **Dependencies:** Task 5.1
    * **File(s) to Create/Modify:** `mcp_server/api/comby_routes.py`
    * **Deliverable:** A `POST /api/v1/execute` route that accepts an `ExecuteRequest`, calls the service from 5.1, and returns an `ExecuteSuccessResponse`.
    * **Test Requirements:**
        * \[ ] Does the integration test create a temporary directory, initialize it as a `git` repository, and add several files?
        * \[ ] Does the test run the server container with this directory bind-mounted to `/workspace`?
        * \[ ] Does a `POST` request to `/api/v1/execute` return `200 OK` and a response matching the `ExecuteSuccessResponse` schema?
        * \[ ] After the API call, does the test check the contents of the files on the host filesystem to confirm they have been modified correctly?
        * \[ ] Does the test run `git status --porcelain` on the temporary directory and assert that the output shows the expected files as modified?
        * \[ ] Does the `modified_files` array in the JSON response accurately list all files that were changed?

---
### **Epic 6: Production Hardening**

* **6.1: Implement Custom Exception Classes**
    * **PR Title:** `refactor(services): define custom exceptions for error handling`
    * **Description:** Create specific exception classes for known failure modes to enable fine-grained error handling.
    * **Dependencies:** Epic 5
    * **File(s) to Create/Modify:** `mcp_server/services/exceptions.py`
    * **Deliverable:** A new file containing custom exception classes like `CombyExecutionError`, `CombyTimeoutError`, and `InvalidPathError`.
    * **Test Requirements:**
        * \[ ] Does the file `mcp_server/services/exceptions.py` exist?
        * \[ ] Does it define custom exceptions that inherit from Python's base `Exception`?
        * \[ ] Do the unit tests for `comby_runner.py` get updated to raise these specific exceptions instead of generic ones?

* **6.2: Implement Global Exception Handler**
    * **PR Title:** `feat(api): implement global exception handler for clean error responses`
    * **Description:** Add a centralized handler to the FastAPI app to catch all custom exceptions and return a standardized `ErrorResponse`.
    * **Dependencies:** Task 6.1
    * **File(s) to Create/Modify:** `mcp_server/main.py`
    * **Deliverable:** A FastAPI exception handler function registered with the app that catches `CombyExecutionError` (and others) and returns the correct `ErrorResponse` model with an appropriate HTTP status code (e.g., 422, 500).
    * **Test Requirements:**
        * \[ ] Does the integration test suite include a test that intentionally triggers a `comby` error (e.g., by providing a bad rule)?
        * \[ ] Does that test assert that the server returns the correct status code (e.g., `422 Unprocessable Entity`)?
        * \[ ] Does the test assert that the response body matches the `ErrorResponse` schema, including a descriptive `error_type` and `details`?

* **6.3: Configure Structured Logging**
    * **PR Title:** `refactor: configure structured JSON logging for observability`
    * **Description:** Replace the default Uvicorn logger with a structured logger to make server output machine-readable for monitoring.
    * **Dependencies:** Task 6.2
    * **File(s) to Create/Modify:** `mcp_server/main.py` (or a new `mcp_server/logging_config.py`)
    * **Deliverable:** Configuration that makes Uvicorn access logs and application logs output as JSON.
    * **Test Requirements:**
        * \[ ] When running an integration test, is the log output captured from the server container a series of valid JSON objects?
        * \[ ] Does a log line for a successful request contain keys such as `level`, `timestamp`, `message`, `path`, `method`, and `status_code`?
        * \[ ] Does a log line for an error also include an `error` or `exception` key?
