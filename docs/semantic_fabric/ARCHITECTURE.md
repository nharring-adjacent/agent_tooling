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

## Security Model

- **Container-Based Isolation**: The application runs in a Docker container with a `/workspace` volume mount
- **Input Validation**: All user inputs are validated and sanitized before processing
- **Path Constraints**: Operations are restricted to the mounted `/workspace` directory
- **Error Handling**: Detailed errors are logged but sanitized before returning to clients
- **Version Control Safety**: Relies on Git as the primary safety mechanism for code modifications

## Future Extensions

The architecture is designed to be extensible, with planned integration of additional static and dynamic analysis tools:

### Static Analysis

- **Tree-sitter**: For syntax-aware code navigation and manipulation
- **Semgrep**: For semantic pattern matching across codebases

### Dynamic Analysis

- **Causal Profiling (coz)**: For identifying performance optimization opportunities
- **Memory Profiling (DHAT)**: For analyzing memory usage patterns and inefficiencies

## Technical Constraints

- **Stateless Operation**: No persistent storage between requests
- **Local Execution**: Designed to run on developer machines
- **Resource Limiting**: Long-running operations can be terminated via timeouts
- **Performance**: Uses caching strategies to minimize repeated analysis
