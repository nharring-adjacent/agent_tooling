"""# Semantic Fabric

## Overview

The Semantic Fabric is a Model Context Protocol (MCP) server that provides a secure, reliable, and atomic API for performing structural code search and replace operations. It's designed to be used by AI agents for precise code transformations.

This project serves as the foundation for a long-term vision of autonomous software development, evolving from a powerful code analysis tool into a platform capable of generating, optimizing, and securing code with minimal human intervention.

## Features
"""

- **Structured Code Search**: Find code patterns with precise structural matching
- **Safe Transformations**: Perform atomic, project-wide code transformations
- **RESTful API**: Simple HTTP interface for integration with any client
- **Containerized**: Easy deployment using Docker

## Quick Start

### Prerequisites

- Python 3.11+
- Docker
- uv (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd semantic-fabric
   ```

2. Install dependencies:
   ```bash
   uv pip install -e .
   ```

3. Run tests:
   ```bash
   pytest
   ```

4. Start the server:
   ```bash
   uvicorn mcp_server.main:app --reload
   ```

### Docker

Build and run with Docker:

```bash
docker build -t mcp-server .
docker run -p 8000:8000 -v $(pwd):/workspace mcp-server
```

## API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

### Project Structure

```
semantic-fabric/
├── mcp_server/           # Main application package
│   ├── api/              # API endpoints
│   ├── services/         # Business logic
│   ├── models/          # Pydantic models
│   ├── utils/           # Utility functions
│   └── main.py          # Application entry point
├── tests/               # Test suite
│   ├── unit/           # Unit tests
│   └── integration/     # Integration tests
├── docs/               # Documentation
├── Dockerfile          # Container definition
└── pyproject.toml      # Project definition and dependencies
```

### Code Style

- Follow PEP 8
- Use type hints for all function signatures
- Document all public functions and classes with docstrings
- Run linter and formatter before committing:
  ```bash
  ruff check .
  ruff format .
  ```

## License

MIT
