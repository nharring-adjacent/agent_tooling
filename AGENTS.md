# For Agents: Your Development Environment and Responsibilities

Greetings, agent. This repository is designed for agents like you to be the primary code authors. This document provides the mandatory protocols and standards you must follow to contribute successfully.

## Primary Directive: Tool Creation

Your core function is to create and maintain the tools located in the `/tools` directory. Each tool you create must be self-contained, well-documented, and robustly tested.

## Protocol for Creating a New Tool

You must follow this protocol precisely for every new tool you create:

1.  **Create a Directory:** Create a new subdirectory for your tool under `/tools/`.
2.  **Write the Tool Code:** Develop the Python code for your tool.
3.  **Create the Specification File:** You MUST create a machine-readable `tool-spec.json` file. This is the canonical source of truth for your tool's interface, inputs, and outputs. This is non-negotiable.
4.  **Write Automated Tests:** You MUST write tests for your tool using the `pytest` framework. Create a file named `test_main.py` (or similar) and write functions that verify your tool's functionality. The tests must pass.
5.  **Ensure Code Quality:** Before committing, you MUST ensure your code passes all quality checks. Run the following commands on any file you create or modify:
    * `ruff format /path/to/your/file.py`
    * `ruff check --fix /path/to/your/file.py`
6.  **Commit Your Work:** Once your code is written, specified, tested, and formatted, you may commit it. The `pre-commit` system will run final checks automatically. If they fail, you must correct
