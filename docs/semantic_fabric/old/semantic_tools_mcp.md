# System Implementation Plan: Model Context Protocol Suite

## 1. System Goal

The primary objective is to build a local server that acts as a "Model Context Protocol Suite". This suite will serve as an intelligent intermediary between a human developer and an agentic coding partner (LLM). It has two main goals:

1.  **Enhance Agent Accuracy:** Provide the agent with rich, precise, and structurally-aware context about the codebase. This allows the agent to move beyond simple text-based analysis and understand the code's architecture, dependencies, and patterns, enabling it to provide more human-like, accurate assistance.
2.  **Improve Agent Efficiency:** Reduce the cost and latency of agentic interactions by minimizing the number of tokens sent to the LLM. This is achieved by extracting only the most relevant information and by offloading tasks that LLMs are poorly suited for (e.g., precise counting, finding unique sets) to more efficient, deterministic tools.

The entire suite must be designed to run on a local developer machine without requiring cloud resources.

## 2. Core Components and Architecture

The system will be built around a core of three specialized code analysis tools: **Tree-sitter**, **Semgrep**, and **Comby**. The server will expose an API that the agentic framework can query to get enriched context before presenting a prompt to the LLM.

### 2.1. Server Architecture: A Layered Context Approach

The server will process requests by generating a "layered context" payload. Instead of sending raw code files, the agent will receive a structured JSON object containing different layers of analysis.

#### **Layer 1: Structural Foundation (Tree-sitter Integration)**

* **Purpose:** To provide a foundational, syntax-aware understanding of the code.
* **Implementation:**
    * Integrate Tree-sitter parsers for common programming languages (Python, JavaScript, TypeScript, Go, Rust, etc.).
    * Implement a file-caching mechanism for Abstract Syntax Trees (ASTs). The server should only re-parse a file if its content has changed.
    * Create API endpoints for the following functionalities:
        * `getNodeAtPosition(filePath, lineNumber, columnNumber)`: Returns the AST node and its source code at a specific location.
        * `findNodesOfType(filePath, nodeType)`: Finds all nodes of a specific type (e.g., `function_definition`, `import_statement`, `class_declaration`) and returns their source code and locations.
        * `getFunctionSource(filePath, functionName)`: A specialized endpoint to quickly retrieve the source code of a specific function.
        * `getAST(filePath, format='json')`: Returns the full AST of a file in a simplified JSON format.

#### **Layer 2: Pattern Matching & Analysis (Semgrep Integration)**

* **Purpose:** To identify high-level patterns, vulnerabilities, and code quality issues.
* **Implementation:**
    * Integrate the Semgrep CLI. The server will execute Semgrep commands on the target files or directories.
    * Create an API endpoint:
        * `runSemgrepAnalysis(targetPath, ruleset)`: Executes Semgrep on a given file or directory using a specified ruleset (e.g., `p/security`, `p/python`, or custom project rules). The endpoint should return a summarized JSON output of the findings. This summary, not the raw Semgrep output, will be passed to the LLM. For example: `{"filePath": "app.py", "line": 42, "message": "Hardcoded secret detected."}`.

#### **Layer 3: Structural Refactoring (Comby Integration)**

* **Purpose:** To enable the agent to suggest and execute large-scale, syntactically-aware refactoring tasks.
* **Implementation:**
    * Integrate the Comby CLI.
    * The agent's role is not to *run* Comby directly, but to *generate* Comby commands.
    * Create an API endpoint to validate Comby syntax:
        * `validateCombyRule(matchTemplate, rewriteTemplate, language)`: Checks if a Comby rule is syntactically valid for a given language. This provides a feedback loop to the agent if it generates an invalid rule.
    * The workflow will be:
        1.  The agent determines a refactor is needed.
        2.  The agent generates a Comby match/rewrite template.
        3.  This template is presented to the human user for confirmation.
        4.  The human executes the Comby command in their terminal.

## 3. Additional Tool Integrations

To further enhance the context, implement the following capabilities.

### 3.1. Data-Flow and Call Graph Analysis

* **Goal:** Understand how data and execution flow through the application.
* **Implementation:**
    * Integrate a lightweight call graph generator (e.g., `pyan` for Python).
    * Create an endpoint `getCallGraph(filePath)` that returns a summary of functions called by each function within a file.
    * Example Summary: `{"function": "main", "calls": ["process_data", "make_api_call"]}`.

### 3.2. Offloading LLM-Unfriendly Tasks

* **Goal:** Use deterministic algorithms for tasks where LLMs are inefficient and inaccurate.
* **Implementation:**
    * Create a `utilities` API endpoint with the following functions:
        * `countNodes(filePath, nodeType)`: Uses Tree-sitter to get a precise count of a given node type.
        * `getUniqueImports(directoryPath)`: Parses all files in a directory to return a unique list of all imported libraries.
        * `findDuplicateBlocks(directoryPath, minLines=5)`: Implements a code deduplication algorithm (e.g., based on hashing content blocks) to find repeated code. The output should be a list of file paths and line ranges for each duplicate set.

## 4. Implementation Case Studies (Integration Tests)

The system's success will be measured by its ability to handle the following workflows. These should be treated as integration tests.

### 4.1. Test Case 1: Simple Feature Addition

* **Scenario:** A user wants to add an optional `timeout` parameter to a `make_request` function in `api.py`.
* **Expected Behavior:**
    1.  The agent framework calls the local server: `GET /api/getFunctionSource?filePath=api.py&functionName=make_request`.
    2.  The server uses Tree-sitter to find the function and returns its source code as a JSON response.
    3.  The agent framework constructs a prompt for the LLM containing only the function's source and the user's request.
    4.  The LLM provides the updated function code.

### 4.2. Test Case 2: Advanced Refactoring

* **Scenario:** A user wants to replace all uses of a deprecated `old_function(arg1, arg2)` with `new_function(arg2, arg1)`.
* **Expected Behavior:**
    1.  The agent framework first calls the local server to find all uses: `GET /api/runSemgrepAnalysis?targetPath=.&ruleset={"rules": [{"id": "find-old-func", "patterns": ["old_function(...)"], "languages": ["python"]}]}`.
    2.  The server returns a list of locations where `old_function` is used.
    3.  The agent framework prompts the LLM: "The user wants to refactor `old_function(arg1, arg2)` to `new_function(arg2, arg1)`. Generate a Comby command to perform this replacement."
    4.  The LLM responds with the Comby command string: `comby 'old_function(:[arg1], :[arg2])' 'new_function(:[arg2], :[arg1])' .py -i`.
    5.  This command is displayed to the user for execution.

## 5. Local Execution Constraints and Performance

* **Caching is critical:** Implement an in-memory or file-based cache for ASTs and analysis results to avoid re-computing on every request. Invalidate the cache only when a file's modification timestamp changes.
* **On-Demand Analysis:** All tools (Tree-sitter, Semgrep, Comby) should be executed on-demand in response to API calls, not as persistent background processes watching the filesystem.
* **Resource Limiting:** Ensure that long-running analyses can be terminated and do not consume unbounded CPU or memory.
