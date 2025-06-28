# Development Workflow

This document outlines the operational protocol for developing and contributing to the Semantic Fabric project. It defines a structured workflow for agentic development that ensures consistency, quality, and incremental progress.

## Development Principles

- **Task Atomicity**: Each task should be small, focused, and independently testable
- **Sequential Development**: Tasks are completed in dependency order
- **Test-Driven**: Tests are written alongside code to validate functionality
- **Consistent Process**: The same workflow applies to all contributions

## Agentic Development Workflow

All development must follow this precise, sequential workflow:

### 1. Task Selection

- Consult the [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) document - this is the canonical source of truth
- Select the next available, unassigned task from the plan
- Ensure all dependencies for the task are met by previously merged PRs

### 2. Branch Creation

- Create a new branch from the `main` branch
- Branch name MUST be derived from the PR Title specified in the task document
- Example: For PR Title `feat(api): implement /api/v1/ideate endpoint`, use branch name `feat/api-ideate-endpoint`

### 3. Implementation

- Implement code to satisfy **only** the deliverable(s) specified for the selected task
- Do not extend the scope beyond what's specified in the task
- Follow code style guidelines and project conventions
- Implement validation for edge cases and error handling

### 4. Testing

- Write tests to satisfy **all** items listed under the Test Requirements for the task
- Ensure all new code has appropriate unit test coverage
- Make sure all existing tests continue to pass
- For API endpoints, create both positive and negative test cases

### 5. Local Verification

- Before submitting, run the entire test suite to ensure no regressions:
  ```bash
  pytest
  ```
- Run the linter to ensure code quality:
  ```bash
  ruff check .
  ```
- Format the code:
  ```bash
  ruff format .
  ```

### 6. Pull Request Submission

- The Pull Request title **MUST** exactly match the PR Title specified in the task document
- Include a brief description of the changes if needed for context
- Link to any relevant issues or documentation

## PR Review Protocol

A reviewer MUST follow this protocol when evaluating a pull request:

### 1. Title Verification

- Does the PR title exactly match the PR Title from the implementation plan?

### 2. Scope Verification

- Do the Files changed in the PR align with the File(s) to Create/Modify for that task?
- Reject PRs that modify unrelated files without justification

### 3. Test Execution

- Check out the PR branch locally and run the test suite:
  ```bash
  pytest
  ```
- The command must exit with code 0 (all tests passing)

### 4. Test Requirements Validation

- For each item in the Test Requirements checklist in the implementation plan:
  - Examine the tests submitted in the PR
  - Confirm that a specific test exists to satisfy each specific requirement
  - If any requirement is not met, request changes

### 5. Code Quality Review

- Verify that the code follows project standards and best practices
- Check that error handling is appropriate
- Ensure code is well-documented

### 6. Approval or Rejection

- Approve if all checks and test requirements are verifiably met
- Reject if any check fails, with specific feedback on what needs to be fixed

## Key Commands

- **Install Dependencies:**
  ```bash
  uv pip install -e .
  ```
- **Run All Tests:**
  ```bash
  pytest
  ```
- **Run Server Locally:**
  ```bash
  uvicorn mcp_server.main:app --reload
  ```
- **Build Docker Container:**
  ```bash
  docker build -t mcp-server .
  ```
- **Run Docker Container:**
  ```bash
  docker run -p 8000:8000 -v $(pwd):/workspace mcp-server
  ```

## Git Workflow

1. **Start with a Clean State:**
   ```bash
   git checkout main
   git pull
   ```

2. **Create a Feature Branch:**
   ```bash
   git checkout -b feature/your-branch-name
   ```

3. **Make Regular Commits:**
   - Use conventional commit messages
   - Keep commits focused and logical

4. **Submit PR When Ready:**
   ```bash
   git push -u origin feature/your-branch-name
   ```

5. **Address Review Feedback:**
   - Make requested changes
   - Push additional commits to the same branch

6. **After Approval:**
   - Squash commits if necessary
   - Merge to main

## Code Standards

- Follow PEP 8 for Python code style
- Use type hints for function arguments and return values
- Write docstrings for all public functions, classes, and methods
- Keep functions small and focused on a single responsibility
- Use descriptive variable and function names
- Use appropriate error handling

## Documentation

- Update documentation when adding or changing functionality
- Document API endpoints with clear descriptions and examples
- Ensure code examples in documentation are accurate and tested
- Keep the implementation plan in sync with the actual implementation
