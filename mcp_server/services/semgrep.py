"""Service layer for Semgrep operations."""

import json
import subprocess

from mcp_server.models.semgrep import (
    SemgrepExecuteRequest,
    SemgrepIdeateRequest,
    SemgrepScanRequest,
)


class SemgrepService:
    """Service for executing Semgrep commands."""

    def _run_semgrep_command(self, command: list[str], input_data: str | None = None):
        """Run a Semgrep command and return the output."""
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True, input=input_data)
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error executing Semgrep command: {e}")
            print(f"Stderr: {e.stderr}")
            return None

    def scan(self, request: SemgrepScanRequest):
        """Perform a Semgrep scan operation."""
        command = ["semgrep", "--json", request.pattern]
        if request.file_filters:
            command.extend(["--include", ",".join(request.file_filters)])

        output = self._run_semgrep_command(command)
        if not output:
            return {"matches": []}

        data = json.loads(output)
        return {"matches": data.get("results", [])}

    def ideate(self, request: SemgrepIdeateRequest):
        """Perform a Semgrep scan on a code snippet."""
        command = ["semgrep", "--json", "--stdin", request.pattern]
        output = self._run_semgrep_command(command, input_data=request.code_snippet)
        if not output:
            return {"matches": []}

        data = json.loads(output)
        return {"matches": data.get("results", [])}

    def execute(self, request: SemgrepExecuteRequest):
        """Execute a Semgrep rule against files."""
        # Semgrep's execute functionality is typically done via rules that modify files.
        # For simplicity in V1, we'll simulate this by just returning success.
        # A full implementation would involve parsing semgrep's diff output or
        # using a tool like `sg` for in-place rewrites.
        command = ["semgrep", "--json", "--config", request.rules]
        if request.file_filters:
            command.extend(["--include", ",".join(request.file_filters)])

        output = self._run_semgrep_command(command)
        if not output:
            return {"matches": []}

        data = json.loads(output)
        return {"matches": data.get("results", [])}
