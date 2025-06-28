# Semantic Fabric Project

## Project Overview

The Semantic Fabric project creates a Model Context Protocol (MCP) server for structural code search and replace operations using Comby. This server provides a secure, reliable, and atomic API to enable AI agents to perform precise code transformations.

### Purpose and Goals

1. **Enhance Agent Accuracy**: Provide agents with rich, precise, and structurally-aware context about codebases
2. **Improve Agent Efficiency**: Reduce cost and latency by minimizing tokens sent to LLMs
3. **Enable Safe Refactoring**: Allow agents to perform atomic, project-wide code transformations

### Core Philosophy

- **Stateless**: No data storage between requests; all information provided in request payloads
- **Secure**: All incoming requests treated as untrusted; execution in sandboxed environment
- **Structured I/O**: JSON-based API for machine-readable requests and responses
- **Atomicity**: Operations succeed or fail cleanly with no partial changes
- **Safety via SCM**: Git as primary safety net, with operations on clean branches

## Key Resources

- [Architecture](ARCHITECTURE.md): System design, components, and data flow
- [Implementation Plan](IMPLEMENTATION_PLAN.md): Detailed task breakdown for incremental development
- [Development Workflow](DEVELOPMENT_WORKFLOW.md): Process for feature development and code review
- [API Specification](API_SPECIFICATION.md): Endpoint definitions and request/response formats

## Technology Stack

- **Backend**: Python 3.11+, FastAPI, Pydantic
- **Deployment**: Docker containerization
- **Core Tools**: Comby (primary), Tree-sitter, Semgrep
- **Testing**: pytest for unit and integration testing
- **Code Quality**: ruff for linting, formatting, and type checking
- **Package Management**: uv for Python dependency management

## Local Development

### Prerequisites

- Python 3.11+
- Docker
- Git
- uv (Python package manager)

### Quick Start

```bash
# Clone repository
git clone <repository-url>
cd semantic-fabric

# Install dependencies
uv pip install -e .

# Run tests
pytest

# Start server locally
uvicorn mcp_server.main:app --reload
```

## Project Structure

```
semantic-fabric/
├── mcp_server/           # Main application package
│   ├── api/              # API endpoints
│   ├── services/         # Business logic
│   ├── models/           # Pydantic models
│   ├── utils/            # Utility functions
│   └── main.py           # Application entry point
├── tests/                # Test suite
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── docs/                 # Documentation
├── Dockerfile            # Container definition
└── pyproject.toml        # Project definition and dependencies
```

"""## Roadmap

The Semantic Fabric is designed to evolve in three distinct phases, moving from foundational analysis to autonomous code generation and optimization.

- **V1 (The Analysis Engine):** The initial version establishes the foundation by understanding code as a structure. It focuses on providing tools for precise, structural search and transformation, answering the question: *"What does this code mean?"*

- **V2 (The Generative Leap):** The second phase will introduce a fine-tuned model capable of generating code as a structured Abstract Syntax Tree (AST) rather than raw text. This leap in generative technology aims to eliminate syntax errors and ensure code correctness by design, answering the question: *"How do I build this logic flawlessly?"*

- **V3 (The Optimization & Autonomy Engine):** The final phase evolves the platform into an autonomous system that can proactively optimize and maintain a codebase. By integrating performance and security feedback loops (including fuzzing), it will be able to identify, fix, and verify improvements automatically, answering the question: *"How do I make this code better, faster, and more secure?"*

## License and Contribution

This project is licensed under [LICENSE]. For contribution guidelines, see [DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md).
""
