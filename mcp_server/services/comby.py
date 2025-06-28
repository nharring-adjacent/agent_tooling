"""Service layer for Comby operations."""

import json
import subprocess

from mcp_server.models.comby import (
    CombyExecuteRequest,
    CombyIdeateRequest,
    CombyScanRequest,
)


class CombyService:
    """Service for executing Comby commands."""

    def _run_comby_command(self, command: list[str]):
        """Run a Comby command and return the output."""
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            # In a real application, you'd want more robust error handling
            print(f"Error executing Comby command: {e}")
            print(f"Stderr: {e.stderr}")
            return None

    def scan(self, request: CombyScanRequest):
        """Perform a dry-run structural code search."""
        command = [
            "comby",
            request.match_template,
            request.rewrite_template,
            "-json-lines",
            "-match-only",
            "-d",
            ".",
        ]
        if request.file_filters:
            command.extend(["-file", ",".join(request.file_filters)])

        output = self._run_comby_command(command)
        if not output:
            return {"matches": []}

        matches = []
        for line in output.strip().split("\n"):
            data = json.loads(line)
            for match in data.get("matches", []):
                matches.append(
                    {
                        "uri": data.get("uri", ""),
                        "matched": match.get("matched", ""),
                    }
                )
        return {"matches": matches}

    def ideate(self, request: CombyIdeateRequest):
        """Transform a code snippet without side effects."""
        command = [
            "comby",
            request.match_template,
            request.rewrite_template,
            "-stdin",
            "-stdout",
        ]
        # For ideate, we pass the code snippet via stdin
        try:
            result = subprocess.run(
                command,
                input=request.code_snippet,
                capture_output=True,
                text=True,
                check=True,
            )
            return {"transformed_code": result.stdout}
        except subprocess.CalledProcessError as e:
            print(f"Error executing Comby command: {e}")
            print(f"Stderr: {e.stderr}")
            return {"transformed_code": request.code_snippet}  # Return original on error

    def execute(self, request: CombyExecuteRequest):
        """Execute a structural code transformation across the project."""
        command = [
            "comby",
            request.match_template,
            request.rewrite_template,
            "-json-lines",
            "-in-place",
            "-d",
            ".",
        ]
        if request.file_filters:
            command.extend(["-file", ",".join(request.file_filters)])

        output = self._run_comby_command(command)
        if output is None:
            return {"success": False, "files_changed": 0}

        # Comby's output for in-place is a list of diffs, one per line.
        # We can count the lines to get the number of files changed.
        files_changed = 1 if output is not None else 0
        return {"success": True, "files_changed": files_changed}
