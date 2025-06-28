# API Specification

This document defines the API endpoints and request/response formats for the Semantic Fabric server.

## Base URL

All API endpoints are relative to the base URL:

```
http://localhost:8000/api/v1
```

## Authentication

The API does not currently implement authentication as it is designed to be run locally.

## Common Models

### Error Response

All API errors use the following response format:

```json
{
  "success": false,
  "error_type": "string",
  "details": "string or object"
}
```

Where:
- `error_type`: Identifies the category of error (e.g., "Validation Error", "Comby Execution Error")
- `details`: Contains a human-readable error message or an object with additional details

## Endpoints

### Ideate Endpoint

Used for testing transformations on isolated code snippets without side effects.

#### Request

```
POST /ideate
```

```json
{
  "language": "string",
  "match_template": "string",
  "rewrite_template": "string",
  "source_code": "string",
  "rule_options": {
    "match_only": "boolean (optional)",
    "case_sensitive": "boolean (optional)"
  }
}
```

Where:
- `language`: The language extension (e.g., ".py", ".js") for the code
- `match_template`: The Comby pattern to match
- `rewrite_template`: The Comby pattern for rewriting
- `source_code`: The code to transform
- `rule_options`: Optional settings for the transformation

#### Success Response

```json
{
  "success": true,
  "rewritten_code": "string",
  "matches": [
    {
      "range": {
        "start": { "line": "integer", "column": "integer" },
        "end": { "line": "integer", "column": "integer" }
      },
      "matched_text": "string",
      "environment": [
        { "variable": "string", "value": "string" }
      ]
    }
  ]
}
```

Where:
- `rewritten_code`: The transformed code
- `matches`: Array of match objects with position and capture information
  - `range`: The position of the match in the source
  - `matched_text`: The text that was matched
  - `environment`: The captured variables and their values

### Scan Endpoint

Used for finding matches in the workspace without modification.

#### Request

```
POST /scan
```

```json
{
  "language": "string",
  "match_template": "string",
  "file_filters": ["string"],
  "rule_options": {
    "case_sensitive": "boolean (optional)"
  }
}
```

Where:
- `language`: The language extension (e.g., ".py", ".js") for the code
- `match_template`: The Comby pattern to match
- `file_filters`: Array of glob patterns to filter files (e.g., "*.py", "src/**/*.js")
- `rule_options`: Optional settings for the scan operation

#### Success Response

```json
{
  "success": true,
  "matches_by_file": [
    {
      "file_path": "string",
      "matches": [
        {
          "range": {
            "start": { "line": "integer", "column": "integer" },
            "end": { "line": "integer", "column": "integer" }
          },
          "matched_text": "string",
          "environment": [
            { "variable": "string", "value": "string" }
          ]
        }
      ]
    }
  ]
}
```

Where:
- `matches_by_file`: Array of objects grouping matches by file
  - `file_path`: Path to the file (relative to workspace)
  - `matches`: Array of match objects as described in the ideate endpoint

### Execute Endpoint

Used for applying transformations with in-place file modifications.

#### Request

```
POST /execute
```

```json
{
  "language": "string",
  "match_template": "string",
  "rewrite_template": "string",
  "file_filters": ["string"],
  "rule_options": {
    "case_sensitive": "boolean (optional)"
  }
}
```

Where:
- `language`: The language extension (e.g., ".py", ".js") for the code
- `match_template`: The Comby pattern to match
- `rewrite_template`: The Comby pattern for rewriting
- `file_filters`: Array of glob patterns to filter files (e.g., "*.py", "src/**/*.js")
- `rule_options`: Optional settings for the transformation

#### Success Response

```json
{
  "success": true,
  "message": "string",
  "modified_files": ["string"],
  "stats": {
    "match_count": "integer",
    "files_with_match": "integer"
  }
}
```

Where:
- `message`: Human-readable summary of the operation
- `modified_files`: Array of paths to modified files (relative to workspace)
- `stats`: Statistics about the operation
  - `match_count`: Total number of matches found
  - `files_with_match`: Number of files with at least one match

## Error Codes

| HTTP Status | Error Type | Description |
|-------------|------------|-------------|
| 400 | Validation Error | Invalid request format or parameters |
| 422 | Comby Execution Error | Error executing Comby command |
| 500 | Internal Server Error | Unexpected server error |

## Usage Examples

### Example 1: Rename a function

```json
{
  "language": ".py",
  "match_template": "old_function(:[args])",
  "rewrite_template": "new_function(:[args])",
  "source_code": "print(old_function(42))"
}
```

Response:
```json
{
  "success": true,
  "rewritten_code": "print(new_function(42))",
  "matches": [
    {
      "range": {
        "start": { "line": 1, "column": 6 },
        "end": { "line": 1, "column": 22 }
      },
      "matched_text": "old_function(42)",
      "environment": [
        { "variable": "args", "value": "42" }
      ]
    }
  ]
}
```

### Example 2: Find all occurrences of a pattern

```json
{
  "language": ".js",
  "match_template": "console.log(:[message])",
  "file_filters": ["src/**/*.js"]
}
```

### Example 3: Replace pattern across multiple files

```json
{
  "language": ".py",
  "match_template": "import :[module] as :[alias]",
  "rewrite_template": "from :[module] import *",
  "file_filters": ["**/*.py"]
}
```

## Implementation Notes

- The server operates on a `/workspace` directory mount
- All file paths are relative to this workspace
- The execution model is synchronous; requests block until completion
- Large operations may timeout after a configurable duration (default: 30s)
