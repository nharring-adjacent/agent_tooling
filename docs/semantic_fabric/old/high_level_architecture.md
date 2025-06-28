Of course. Here is the project plan's first pass captured in a clean Markdown block, suitable for adding directly to your repository documentation.

````markdown
# Project Plan: Comby MCP Server - Pass 1

### **Objective**

To create a stateless web service that accepts structural search-and-replace requests, executes them using `comby`, and returns structured, machine-readable results. This server will act as a core component of the larger Model Context Protocol suite, providing a safe and reliable interface for an agentic coding platform to perform structural code manipulation.

### **Core Philosophy**

* **Stateless:** The server will not store any data between requests. All necessary information (code, match/rewrite templates) will be provided in the request payload.
* **Secure:** The server will treat all incoming requests as untrusted. It will operate within a sandboxed environment and will not execute arbitrary shell commands.
* **Structured I/O:** The server must speak JSON. It will accept structured requests and produce structured responses to be easily consumed by the LLM-based agentic framework.

---

### **1. Distinct System Components**

We can break the server down into four distinct, logical components.

* **Component A: The Public API Endpoint**
    * **Purpose:** This is the front door of our service. It's the only part of the system that communicates with the outside world.
    * **Boundary:** It is responsible for handling HTTP requests (e.g., POST), parsing the incoming request body, and routing the validated request to the appropriate internal component. It is also responsible for catching all errors and formatting them into a standard HTTP error response. It knows nothing about how `comby` works.

* **Component B: The Request Validator & Sanitizer**
    * **Purpose:** To ensure that incoming requests are well-formed and safe before any execution occurs.
    * **Boundary:** This component receives the deserialized request data from the API Endpoint. It checks for the presence of required fields (`match_template`, `rewrite_template`, `source_code`), validates the data types, and, most importantly, performs basic syntactic sanity checks on the `comby` templates to catch obvious errors early. It does not execute `comby`.

* **Component C: The Comby Execution Wrapper**
    * **Purpose:** This is the heart of the service. It is the sole component responsible for interfacing directly with the `comby` command-line tool.
    * **Boundary:** This component's interface accepts a validated `comby` command (match, rewrite, language, etc.) and a string of source code. It is responsible for creating a temporary file with the source code, invoking the `comby` process, capturing its `stdout` (the result) and `stderr` (any errors), and managing the subprocess's lifecycle (e.g., handling timeouts). It operates in a "black box" fashion; it runs a command and returns the result.

* **Component D: The Results Formatter**
    * **Purpose:** To translate the raw output from the `comby` process into a clean, structured JSON format that is useful for an LLM agent.
    * **Boundary:** This component receives the raw `stdout` from the Comby Execution Wrapper. Based on the type of request (e.g., a rewrite vs. a match-only), it formats the data into a predictable JSON structure, clearly indicating success, failure, the rewritten code, or a list of matches found.

### **2. Message Passing Flow**

Here is the step-by-step control flow for a typical "rewrite" request:

1.  **[Agent -> API Endpoint]**: The external agentic framework sends a `POST /rewrite` request. The JSON body contains:
    ```json
    {
      "language": ".py",
      "match_template": "old_function(:[args])",
      "rewrite_template": "new_function(:[args])",
      "source_code": "print(old_function(42))"
    }
    ```

2.  **[API Endpoint -> Validator]**: The API Endpoint deserializes the JSON and passes the data structure to the Request Validator.

3.  **[Validator -> API Endpoint]**: The Validator checks that all fields are present and that the templates don't contain obviously malicious characters. It returns `(isValid: true, error: null)` to the API Endpoint. (If validation failed, it would return `(isValid: false, error: "Missing source_code field")`, and the flow would stop, returning a 400 Bad Request error).

4.  **[API Endpoint -> Execution Wrapper]**: The API Endpoint, now confident the request is valid, calls the Comby Execution Wrapper with the validated parameters.

5.  **[Execution Wrapper -> System Shell]**:
    * The Wrapper writes the `source_code` string to a temporary file (e.g., `/tmp/comby_in_xyz.py`).
    * It constructs and executes the shell command: `comby 'old_function(:[args])' 'new_function(:[args])' /tmp/comby_in_xyz.py -stdout`
    * It captures the resulting `stdout` and `stderr` from the completed process. Let's say `stdout` is `"print(new_function(42))"`.

6.  **[Execution Wrapper -> Results Formatter]**: The Wrapper passes the raw `stdout` string to the Results Formatter.

7.  **[Results Formatter -> API Endpoint]**: The Formatter creates a structured JSON object from the raw string:
    ```json
    {
      "success": true,
      "rewritten_code": "print(new_function(42))",
      "matches": [
          // In a rewrite, this could be omitted or populated
      ],
      "error": null
    }
    ```

8.  **[API Endpoint -> Agent]**: The API Endpoint sends the final JSON object back to the agentic framework with a `200 OK` status code.
````
