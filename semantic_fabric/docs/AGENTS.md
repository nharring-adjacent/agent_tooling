# For Agents: How to Work on This Repository

This document provides the operational protocol for AI coding agents contributing to the Comby Model Context Protocol (MCP) server. Adherence to this protocol is mandatory for all contributions.

## 1. System Purpose

This repository contains the source code for the Comby MCP server. Its purpose is to provide a secure, reliable, and atomic API for performing structural code search and replace operations, intended to be used as a tool by other AI agents.

## 2. Agentic Development Workflow

All development must follow this precise, sequential workflow.

1.  **Consult the Plan:** The canonical source of truth for all tasks is the **Detailed Implementation Plan (Pass 3.1)**. Do not invent new tasks or deviate from the specified dependency order.

2.  **Select a Task:** Select the next available, unassigned task from the plan. Ensure all its dependencies are met by prior, merged pull requests.

3.  **Create a Branch:** Create a new branch from the `main` branch. The branch name MUST be derived from the `PR Title` specified in the task document.
    * **Example:** For a task with PR Title `feat(api): implement /api/v1/ideate endpoint`, a valid branch name is `feat/api-ideate-endpoint`.

4.  **Implement the Task:** Write or modify code to satisfy **only** the `Deliverable(s)` specified for the selected task. Do not expand the scope.

5.  **Write Tests:** Create or modify tests to satisfy **all** items listed under the `Test Requirements` for the selected task. Your implementation is not considered correct until it passes all specified tests.

6.  **Verify Locally:** Before submitting, run the entire test suite to ensure no regressions were introduced.
    * **Command:** `poetry run pytest`

7.  **Submit a Pull Request:**
    * The Pull Request title **MUST** exactly match the `PR Title` specified in the task document.
    * The Pull Request body **MUST** be left blank. The code, tests, and PR title are the complete specification of the change.

## 3. Codebase Structure

This is the map of the repository. Place new code in the correct location.

* `mcp_server/`: Main application source code.
* `mcp_server/api/`: API routing layer. Contains FastAPI routers and endpoint definitions.
* `mcp_server/models/`: Pydantic data structures. Defines all request and response schemas.
* `mcp_server/services/`: Core business logic.
    * `comby_runner.py`: The only module authorized to execute `comby` subprocesses.
    * `exceptions.py`: Custom exception classes for error handling.
* `tests/`: Unit and integration tests. The structure of this directory should mirror `mcp_server/`.
* `Dockerfile`: The container definition for the production service.
* `pyproject.toml`: Project definition, dependencies, and tooling configuration.

## 4. Key Commands

* **Install Dependencies:**
    ```bash
    poetry install
    ```
* **Run All Tests:**
    ```bash
    poetry run pytest
    ```
* **Run Server Locally for Manual Testing:**
    ```bash
    poetry run uvicorn mcp_server.main:app --reload
    ```
* **Build Docker Container:**
    ```bash
    docker build -t mcp-server .
    ```

## 5. Agentic PR Review Protocol

A reviewer agent MUST follow this protocol when evaluating a pull request submitted by a coder agent. Approval is contingent on all checks passing.

1.  **Verify Title:** Does the PR title exactly match the `PR Title` from the implementation plan for one specific task?

2.  **Verify Scope:** Do the `Files changed` in the PR align with the `File(s) to Create/Modify` for that task? Reject PRs that modify unrelated files.

3.  **Checkout and Test:** Check out the PR branch locally and run the entire test suite.
    * **Command:** `poetry run pytest`
    * **Condition:** The command must exit with code 0.

4.  **Validate Test Requirements:** This is the most critical step. For the specific task the PR addresses, act as a verifier for the `Test Requirements` checklist.
    * Read each item in the checklist from the implementation plan.
    * Examine the tests submitted in the PR.
    * Confirm that a specific test exists to satisfy each specific requirement. For example, if a requirement is "Assert that a timeout raises `CombyTimeoutError`," you must find a test case like `@pytest.mark.raises(CombyTimeoutError)` that validates this behavior.

5.  **Approve or Reject:**
    * **Approve:** If all checks and test requirements are verifiably met.
    * **Reject:** If any check fails. The rejection comment should specify which checklist item was not satisfied.
