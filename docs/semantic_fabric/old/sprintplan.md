Excellent. This is the final and most crucial pass: breaking the architectural blueprint into a concrete, sequential project plan. The goal is to create a series of tasks so well-defined that they can be executed independently, minimizing coordination and ambiguity.

Here is Pass 3: The implementation plan, broken down into discrete tasks with clear deliverables and test requirements, project-manager style.

---

### **Project Plan: Comby MCP Server - Pass 3 (Implementation Tasks)**

**Methodology:** The following tasks are presented in a logical dependency order. Each task should be handled on a separate feature branch. The "Test Requirements" for each PR serve as the explicit checklist for the reviewing agent.

---

### **Task 1: Project Scaffolding and Initial Docker Setup**

* **Title:** `feat: initial project structure and Dockerfile`
* **Description:** Create the basic directory structure for a Python web application and a multi-stage `Dockerfile` to build and run the server. This task does *not* include any web server logic, only the setup.
* **Deliverables:**
    1.  A `pyproject.toml` file defining project metadata and dependencies (e.g., `fastapi`, `uvicorn`, `pydantic`).
    2.  A main application directory (e.g., `mcp_server/`) with empty `__init__.py` files and subdirectories for `api`, `services`, and `models`.
    3.  A `Dockerfile` with at least two stages:
        * A `builder` stage to install Python dependencies.
        * A final, minimal runtime stage that copies dependencies from the `builder` and includes the `comby` binary. It should define a non-root user and set up the `/workspace` volume.
* **Test Requirements (PR Review Checklist):**
    * \[ ] Does the `Dockerfile` successfully build a container image using `docker build .`?
    * \[ ] Does the `Dockerfile` use a specific Python version (e.g., `python:3.11-slim`)?
    * \[ ] Is there a non-root user created and used in the final stage (`USER appuser`)?
    * \[ ] Does the `Dockerfile` define a `VOLUME /workspace`?
    * \[ ] Does the final image contain the `comby` binary in its `PATH`? (Verify with `docker run <image> which comby`).

---

### **Task 2: Implement Core Data Structures and Request Models**

* **Title:** `feat: define core API request and response models`
* **Description:** Implement all JSON data structures as defined in the Pass 2 document using Pydantic. This provides a single source of truth for all API contracts before the API itself is built.
* **Dependencies:** Task 1
* **Deliverables:**
    1.  A new file, `mcp_server/models/comby_models.py`.
    2.  Pydantic classes for all request bodies: `IdeateRequest`, `ExecuteRequest`, `ScanRequest`.
    3.  Pydantic classes for all success responses: `IdeateSuccessResponse`, `ExecuteSuccessResponse`, `ScanSuccessResponse`.
    4.  A Pydantic class for the standard `ErrorResponse`.
* **Test Requirements (PR Review Checklist):**
    * \[ ] Do all Pydantic models in `comby_models.py` exactly match the fields and data types specified in the "Pass 2 (Final)" document?
    * \[ ] Do all fields marked as `required` in the spec lack an `Optional` type hint or a default value?
    * \[ ] Do all fields marked as `optional` have an `Optional` type hint or a default value?
    * \[ ] Does the code include unit tests that validate the models with both correct and incorrect data payloads, checking that `pydantic.ValidationError` is raised appropriately?

---

### **Task 3: Implement the `/ideate` Endpoint**

* **Title:** `feat: implement the /api/v1/ideate endpoint`
* **Description:** Build the first functional endpoint. This involves setting up the FastAPI server, creating the Comby execution logic for a single snippet, and wiring everything together for the `ideate` use case.
* **Dependencies:** Task 1, Task 2
* **Deliverables:**
    1.  `mcp_server/main.py` file to initialize and configure the FastAPI app.
    2.  `mcp_server/api/comby_routes.py` file with a router and the `POST /api/v1/ideate` route.
    3.  `mcp_server/services/comby_runner.py` file with a function `run_comby_on_snippet(source: str, ...) -> str`. This function will perform the `subprocess.run` call for a snippet.
    4.  Integration tests for the `/ideate` endpoint.
* **Test Requirements (PR Review Checklist):**
    * \[ ] Does the `POST /ideate` endpoint accept a valid `IdeateRequest` and return a `200 OK` status?
    * \[ ] Does the response body match the `IdeateSuccessResponse` schema?
    * \[ ] Does the `rewritten_code` in the response reflect the correct `comby` transformation? (Test with a simple swap, e.g., `a(b)` -> `b(a)`).
    * \[ ] Does sending a request with missing required fields (e.g., no `source_code`) return a `422 Unprocessable Entity` status and an `ErrorResponse` body?
    * \[ ] Does the `comby_runner.py` module use `subprocess.run` with a `timeout` argument?
    * \[ ] Are there unit tests for `run_comby_on_snippet` that mock `subprocess.run`?

---

### **Task 4: Implement the `/scan` Endpoint**

* **Title:** `feat: implement the /api/v1/scan endpoint`
* **Description:** Implement the read-only, project-wide search functionality. This extends the `CombyRunner` to operate on a directory and adds the corresponding API route.
* **Dependencies:** Task 3
* **Deliverables:**
    1.  A new `POST /api/v1/scan` route in `comby_routes.py`.
    2.  A new function `run_comby_scan(file_filters: list, ...)` in `comby_runner.py`. This function will construct and execute a `comby` command that runs on `/workspace` and outputs JSON (`-json-lines`).
    3.  Integration tests that use a bind-mounted directory to test the `/scan` endpoint.
* **Test Requirements (PR Review Checklist):**
    * \[ ] Does the `POST /scan` endpoint accept a valid `ScanRequest` and return a `200 OK` status?
    * \[ ] Does the response body match the `ScanSuccessResponse` schema?
    * \[ ] Does the test suite create a temporary directory with at least two subdirectories and multiple files?
    * \[ ] Does the integration test run the server container with this temporary directory bind-mounted to `/workspace`?
    * \[ ] Does the `matches_by_file` array in the response contain the correct file paths (relative to `/workspace`) and match data for a known pattern in the test files?
    * \[ ] Does the `comby_runner.py` module sanitize the `file_filters` to prevent directory traversal (`../`)?
    * \[ ] Does the `comby` command in `run_comby_scan` use the `-json-lines` flag to get structured output?

---

### **Task 5: Implement the `/execute` Endpoint**

* **Title:** `feat: implement the /api/v1/execute endpoint`
* **Description:** Implement the primary stateful functionality: in-place, project-wide refactoring. This is the final core feature.
* **Dependencies:** Task 4
* **Deliverables:**
    1.  A new `POST /api/v1/execute` route in `comby_routes.py`.
    2.  A new function `run_comby_execute(file_filters: list, ...)` in `comby_runner.py`. This will execute `comby` with the `-in-place` flag.
    3.  Integration tests for the `/execute` endpoint.
* **Test Requirements (PR Review Checklist):**
    * \[ ] Does the `POST /execute` endpoint accept a valid `ExecuteRequest` and return a `200 OK` status?
    * \[ ] Does the response body match the `ExecuteSuccessResponse` schema?
    * \[ ] Does the integration test use a temporary directory initialized as a `git` repository?
    * \[ ] After the API call, does the test verify that the files on the host filesystem have been physically modified as expected?
    * \[ ] Does the test verify this change using `git status` or `git diff` on the host-side temporary directory?
    * \[ ] Does the `modified_files` array in the JSON response accurately list the files that were changed?
    * \[ ] Does the `comby` command in `run_comby_execute` use the `-in-place` flag?
    * \[ ] Does the command also use a flag to get stats (`-stats`)?

---

### **Task 6: Finalize Error Handling and Logging**

* **Title:** `refactor: implement global error handling and structured logging`
* **Description:** Solidify the server by adding centralized exception handlers and structured (JSON) logging for better observability.
* **Dependencies:** Task 5
* **Deliverables:**
    1.  A global exception handler in `main.py` to catch custom exceptions (e.g., `CombyTimeoutError`) and return the standard `ErrorResponse`.
    2.  Integration of a structured logging library to output all logs (requests, errors, etc.) as JSON.
* **Test Requirements (PR Review Checklist):**
    * \[ ] Does an API call that causes a `comby` timeout return a `500 Internal Server Error` and a well-formed `ErrorResponse` body?
    * \[ ] When running the server, are logs written to `stdout` formatted as JSON objects (not plain text)?
    * \[ ] Do request logs include the request path, method, and response status code?
