# Agent Tooling Monorepo

This repository is a collection of tools and services designed to be used by AI agents. It serves as a central hub for developing, documenting, and managing a variety of tools, from simple callable Python functions to more complex, containerized MCP (Multi-Agent Communication Protocol) servers.

## Guiding Principles

* **Modularity:** Each tool should be self-contained within its own subdirectory.
* **Discoverability:** It should be easy for both humans and agents to find out what tools are available and how to use them.
* **Consistency:** Tools should follow a consistent structure and documentation format.

## Directory Structure

We recommend the following directory structure to keep the repository organized:
```
/
├── tools/
│   ├── tool_one/
│   │   ├── Dockerfile         # Optional: If it's a containerized service
│   │   ├── main.py            # Main entrypoint for the tool
│   │   ├── pyproject.toml     # Or requirements.txt, for dependencies
│   │   └── README.md          # Human-readable documentation for the tool
│   └── tool_two/
│       ├── ...
├── docs/                      # For overall project documentation
├── .gitignore
├── AGENTS.md                  # Instructions specifically for AI agents
└── README.md                  # This file
```

## Getting Started

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Explore the available tools:**
    Each tool is located in its own directory under `tools/`. Refer to the `README.md` inside each tool's directory for specific instructions on installation, configuration, and usage.

## Adding a New Tool

1.  Create a new subdirectory under `tools/`.
2.  Add your tool's code and a `pyproject.toml` managed with `uv`.
3.  **Crucially, create a `tool-spec.json` or `openapi.json` that clearly defines the tool's interface.**
4.  Add a `README.md` for human-readable context.
5.  Ensure all code passes `ruff` checks.

## Contribution Guidelines

1.  Fork the repository.
2.  Create a new branch for your feature (`git checkout -b feature/my-new-tool`).
3.  Commit your changes (`git commit -am 'Add some tool'`).
4.  Push to the branch (`git push origin feature/my-new-tool`).
5.  Create a new Pull Request.
