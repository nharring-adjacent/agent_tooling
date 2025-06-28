# Semantic Fabric Architecture

## System Architecture Overview

The Semantic Fabric server is designed as a layered context provider that leverages structural code analysis tools to deliver precise insights and transformations. This document outlines the system's components, their interactions, and the guiding architectural principles.

## Core Components

### 1. API Layer

The API layer serves as the front door to the system, handling all external communications. It processes incoming HTTP requests, validates inputs, and routes to appropriate handlers.

**Responsibilities:**
- Request deserialization and validation
- Response serialization
- Error handling and HTTP status code mapping
- Routing to internal services

### 2. Service Layer

The service layer contains the business logic for executing code analysis operations and transformations. It's organized into distinct services by tool and responsibility.

**Key Services:**
- **CombyRunner**: Manages execution of Comby commands for code search and replace
- **TreeSitterService**: Handles syntax-aware code parsing (future extension)
- **SemgrepService**: Manages pattern-based code analysis (future extension)

### 3. Model Layer

The model layer defines structured data types for all requests, responses, and internal operations using Pydantic.

**Core Models:**
- **Request Models**: Define the schema for API requests
- **Response Models**: Define the schema for API responses
- **Internal Models**: Used for internal data processing

### 4. Utility Layer

The utility layer provides shared functionality and cross-cutting concerns.

**Key Utilities:**
- **Error Handling**: Custom exceptions and global handlers
- **Logging**: Structured JSON logging for observability
- **File Operations**: Safe file system interactions

## Operation Modes

### 1. Ideate Mode

Used for testing and developing transformations on isolated code snippets without side effects.

**Flow:**
1. Agent sends code snippet and transformation rules
2. Server validates inputs
3. Comby processes the transformation in-memory
4. Server returns the transformed code without modifying files

### 2. Execute Mode

Used for applying validated transformations across the project directory structure.

**Flow:**
1. Agent sends transformation rules and file filters
2. Server validates inputs
3. Comby processes the transformation with in-place file modifications
4. Server returns statistics on the transformation applied

### 3. Scan Mode

Used for analyzing code without modification to find matching patterns.

**Flow:**
1. Agent sends pattern to search for and file filters
2. Server validates inputs
3. Comby processes the search operation
4. Server returns match information organized by file

## Data Flow

```
┌───────────────┐     ┌──────────────────┐     ┌───────────────┐     ┌──────────────┐
│ API Endpoint  │ ─── │ Request Validator │ ─── │    Service    │ ─── │ Comby Process│
└───────────────┘     └──────────────────┘     └───────────────┘     └──────────────┘
        │                       │                      │                     │
        ▼                       ▼                      ▼                     ▼
┌───────────────┐     ┌──────────────────┐     ┌───────────────┐     ┌──────────────┐
│ HTTP Response │ ◄── │ Results Formatter│ ◄── │ Result Parser │ ◄── │ Command Output│
└───────────────┘     └──────────────────┘     └───────────────┘     └──────────────┘
```

"""## Security and Robustness Model

Security and robustness are foundational to the architecture, ensuring that all automated operations are safe, reliable, and do not introduce new vulnerabilities.

- **Container-Based Isolation**: The application runs in a Docker container with a `/workspace` volume mount to prevent access to the host filesystem.
- **Input Validation**: All user inputs are strictly validated and sanitized before processing to prevent injection or command manipulation.
- **Path Constraints**: Operations are restricted to the mounted `/workspace` directory.
- **Error Handling**: Detailed errors are logged for debugging but are sanitized before being returned to clients to avoid leaking internal state.
- **Version Control Safety**: The system relies on Git as the primary safety mechanism for code modifications, ensuring changes can be reviewed and reverted.
- **Fuzzing and Verification**: Future versions will integrate fuzzing as a mandatory verification step in the code generation and modification pipeline. This ensures that any AI-generated change is not only syntactically correct and performant but also robust against unexpected or malicious inputs.

## Future Extensions: The Path to Autonomous Development

The architecture is designed to be extensible, with a clear roadmap from advanced analysis to autonomous code generation and optimization.

### V1: Advanced Static Analysis

The initial extensions focus on deepening the system's understanding of code.

- **Tree-sitter**: For fine-grained, syntax-aware code navigation and manipulation.
- **Semgrep**: For semantic pattern matching that understands code logic beyond simple text patterns.

### V2: The Generative Leap

This phase moves from analyzing code to generating it with guaranteed correctness.

- **Fine-Tuned Generative Model**: A core goal is to develop a fine-tuned LLM that outputs a compact, structured Abstract Syntax Tree (AST) instead of raw text. This eliminates syntax, formatting, and indentation errors by design.
- **Deterministic "Pretty-Printer"**: A decoder will translate the model's AST output into perfectly formatted, human-readable code that adheres to project-specific style guides.

### V3: The Optimization & Autonomy Engine

This phase creates a closed-loop system for continuous code improvement.

- **Performance Optimization Workflow**: Agents will be able to hypothesize a performance improvement, use the V2 engine to generate a patch, and then use an integrated **Performance Measurement Service** to compile and benchmark the change. This provides a direct feedback loop to learn what changes yield real performance gains.
- **Autonomous Fuzzing and Security Hardening**: The system will use **fuzzing** not just for verification but for proactive vulnerability discovery. When a flaw is found, the V3 engine will be able to autonomously generate, test, and verify a patch before submitting it for human approval.
- **Proactive Code Health Monitoring**: Deployed as a service, the system will continuously scan for code smells, potential regressions, and complex security vulnerabilities using deep analysis tools like Code Property Graphs (CPGs), creating a "self-healing" codebase.

## Technical Constraints
"""

- **Stateless Operation**: No persistent storage between requests
- **Local Execution**: Designed to run on developer machines
- **Resource Limiting**: Long-running operations can be terminated via timeouts
- **Performance**: Uses caching strategies to minimize repeated analysis
