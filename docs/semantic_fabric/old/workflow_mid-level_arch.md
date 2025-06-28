# Project Plan: Comby MCP Server - Pass 2 (Final)

### **Objective**
To provide a detailed architectural blueprint for a Comby MCP server that enables an agent to perform **atomic, project-wide refactoring**. The server will operate directly on a user-provided directory, modifying files in-place to provide a simple and robust workflow for agentic coding.

---

### **1. Architectural Principles & Non-Goals**

#### **Architectural Principles**
* **Atomicity via In-Place Execution:** The server's primary function is to execute `comby` transformations that directly modify the files in the mounted `/workspace`. The `execute` endpoint is treated as a single, atomic operation that either succeeds or fails cleanly.
* **Trust in the Tool:** The agentic framework's contract is to trust the `execute` call. It issues the command and, upon success, assumes the filesystem state has been correctly updated. It does not try to verify or modify the result.
* **Safety via SCM:** The user's version control system (e.g., Git) is the primary safety net. All operations should be performed on a clean branch, allowing for easy review (`git diff`) and rollback (`git restore`).
* **Dual Operating Modes:**
    1.  **Ideate Mode:** For developing and testing a `comby` rule on an isolated code snippet without side effects.
    2.  **Execute Mode:** For applying a validated rule across the live directory structure.
* **Container-First:** The application is designed to run as a lightweight Docker container defining a `/workspace` volume to be bind-mounted from the host.
* **User-Context Execution:** The container should run as the host user (via UID/GID mapping) to ensure correct file permissions on the mounted volume.

#### **Non-Goals**
* Asynchronous/Batch Processing
* Authentication & Authorization
* Complex File Management (e.g., `git` operations)

---

### **2. Subsystem Definitions**

* **`APIServer`:** Manages HTTP routing for `/ideate`, `/execute`, and `/scan`.
* **`RequestModels`:** Defines the specific data structures for `IdeateRequest`, `ExecuteRequest`, `ScanRequest`, and their corresponding responses.
* **`CombyRunner`:** Encapsulates `comby` execution logic for all modes, ensuring `execute` runs `comby -in-place` against the `/workspace` directory.
* **`ResponseHandler`:** Transforms raw `comby` output (rewritten snippets, `in-place` stats, or JSON matches) into the correct structured response.
* **`ErrorHandler`:** Handles custom exceptions and translates them into consistent JSON error responses.

---

### **3. API Specification & Boundaries**

* **`POST /api/v1/ideate`**
    * **Purpose:** To test a `comby` rewrite rule on a single code snippet. The "unit test" for a refactor.
    * **Behavior:** Pure, side-effect-free operation.

* **`POST /api/v1/execute`**
    * **Purpose:** To apply a validated rewrite rule directly to the files in the `/workspace` directory.
    * **Behavior:** Modifies the filesystem in-place. This is a stateful operation.
    * **Success Response:** Reports which files were changed.

* **`POST /api/v1/scan`**
    * **Purpose:** To perform a read-only search across the `/workspace` directory to find all instances of a pattern.
    * **Behavior:** Read-only operation.

---

### **4. Key Data Structures (Final Schemas)**

#### **Requests**
* **`IdeateRequest`**
    ```json
    {
      "match_template": "string (required)",
      "rewrite_template": "string (required)",
      "source_code": "string (required)",
      "language": "string (optional)"
    }
    ```
* **`ExecuteRequest`**
    ```json
    {
      "match_template": "string (required)",
      "rewrite_template": "string (required)",
      "rule": "string (optional)",
      "file_filters": ["string (optional, e.g., '.py', 'src/')"]
    }
    ```
* **`ScanRequest`**
    ```json
    {
      "match_template": "string (required)",
      "rule": "string (optional)",
      "file_filters": ["string (optional)"]
    }
    ```

#### **Responses**
* **`IdeateSuccessResponse`**
    ```json
    {
      "success": true,
      "rewritten_code": "string"
    }
    ```
* **`ExecuteSuccessResponse`**
    ```json
    {
      "success": true,
      "message": "string (e.g., 'Execution successful. 3 matches found across 2 files.')",
      "modified_files": ["string"],
      "stats": {
        "match_count": "integer",
        "files_with_match": "integer"
      }
    }
    ```
* **`ScanSuccessResponse`**
    ```json
    {
      "success": true,
      "matches_by_file": [
        {
          "file_path": "string",
          "matches": [ /* Standard comby match object */ ]
        }
      ]
    }
    ```
* **`ErrorResponse`**
    ```json
    {
      "success": false,
      "error_type": "string (e.g., 'Validation Error', 'Comby Execution Error')",
      "details": "string or object with detailed error message"
    }
    ```

---

### **5. Test Strategy**

* **Unit Tests:** Each subsystem will be tested in isolation. `CombyRunner` will be tested by mocking the `subprocess.run` call.
* **Integration Tests:** The test suite will make live HTTP requests to a running instance. For the `/execute` endpoint, tests will create a temporary `git` repository, mount it, call the endpoint, and then use `git status` and file content assertions to verify that the in-place modifications were performed correctly.

---

### **6. Caveats & Security**

* **The Trust Boundary:** The user explicitly grants the server write access to the `/workspace` directory. This powerful capability must be handled with respect.
* **The Git Workflow is Mandatory:** The safety of the in-place execution model hinges on the user running this on a version-controlled project. The agent's operational procedures must treat this as a prerequisite. A recommended agent workflow is:
    1.  Confirm the `git` working directory is clean.
    2.  Call `/execute`.
    3.  Upon success, prompt the user: "I have applied the changes. Please review them with `git diff` before committing."
* **Path Sanitization:** All path and filter inputs must be rigorously sanitized to prevent directory traversal attacks. The `comby` execution must be constrained to the `/workspace` directory.
