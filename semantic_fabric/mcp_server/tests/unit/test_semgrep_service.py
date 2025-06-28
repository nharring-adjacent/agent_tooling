import json
import subprocess

import pytest

from mcp_server.models.semgrep import (
    SemgrepExecuteRequest,
    SemgrepIdeateRequest,
    SemgrepScanRequest,
)
from mcp_server.services.semgrep import SemgrepService


@pytest.fixture
def semgrep_service():
    return SemgrepService()


def test_semgrep_scan_success(semgrep_service, monkeypatch):
    mock_stdout = json.dumps({"results": [{"path": "file.py", "start": {}, "end": {}, "extra": {}, "text": "match"}]})
    mock_result = subprocess.CompletedProcess(
        ["semgrep", "--json", "test-pattern"],
        0,
        stdout=mock_stdout,
        stderr="",
    )
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: mock_result)

    request = SemgrepScanRequest(pattern="test-pattern")
    response = semgrep_service.scan(request)

    assert len(response["matches"]) == 1
    assert response["matches"][0]["path"] == "file.py"


def test_semgrep_scan_no_matches(semgrep_service, monkeypatch):
    mock_stdout = json.dumps({"results": []})
    mock_result = subprocess.CompletedProcess(
        ["semgrep", "--json", "test-pattern"],
        0,
        stdout=mock_stdout,
        stderr="",
    )
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: mock_result)

    request = SemgrepScanRequest(pattern="test-pattern")
    response = semgrep_service.scan(request)

    assert response["matches"] == []


def test_semgrep_scan_error(semgrep_service, monkeypatch):
    def mock_run_error(*args, **kwargs):
        raise subprocess.CalledProcessError(1, "semgrep", stderr="Semgrep error")

    monkeypatch.setattr(subprocess, "run", mock_run_error)

    request = SemgrepScanRequest(pattern="test-pattern")
    response = semgrep_service.scan(request)

    assert response["matches"] == []


def test_semgrep_scan_with_file_filters(semgrep_service, monkeypatch):
    mock_stdout = json.dumps({"results": [{"path": "file.py", "start": {}, "end": {}, "extra": {}, "text": "match"}]})
    mock_result = subprocess.CompletedProcess(
        ["semgrep", "--json", "--include", "py,js", "test-pattern"],
        0,
        stdout=mock_stdout,
        stderr="",
    )
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: mock_result)

    request = SemgrepScanRequest(pattern="test-pattern", file_filters=["py", "js"])
    response = semgrep_service.scan(request)

    assert len(response["matches"]) == 1


def test_semgrep_ideate_success(semgrep_service, monkeypatch):
    mock_stdout = json.dumps({"results": [{"path": "<stdin>", "start": {}, "end": {}, "extra": {}, "text": "match"}]})
    mock_result = subprocess.CompletedProcess(
        ["semgrep", "--json", "--stdin", "test-pattern"],
        0,
        stdout=mock_stdout,
        stderr="",
    )
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: mock_result)

    request = SemgrepIdeateRequest(code_snippet='print("hello")', pattern="test-pattern")
    response = semgrep_service.ideate(request)

    assert len(response["matches"]) == 1
    assert response["matches"][0]["path"] == "<stdin>"


def test_semgrep_ideate_no_matches(semgrep_service, monkeypatch):
    mock_stdout = json.dumps({"results": []})
    mock_result = subprocess.CompletedProcess(
        ["semgrep", "--json", "--stdin", "test-pattern"],
        0,
        stdout=mock_stdout,
        stderr="",
    )
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: mock_result)

    request = SemgrepIdeateRequest(code_snippet='print("hello")', pattern="test-pattern")
    response = semgrep_service.ideate(request)

    assert response["matches"] == []


def test_semgrep_ideate_error(semgrep_service, monkeypatch):
    def mock_run_error(*args, **kwargs):
        raise subprocess.CalledProcessError(1, "semgrep", stderr="Semgrep error")

    monkeypatch.setattr(subprocess, "run", mock_run_error)

    request = SemgrepIdeateRequest(code_snippet='print("hello")', pattern="test-pattern")
    response = semgrep_service.ideate(request)

    assert response["matches"] == []


def test_semgrep_execute_success(semgrep_service, monkeypatch):
    mock_stdout = json.dumps({"results": []})
    mock_result = subprocess.CompletedProcess(
        ["semgrep", "--json", "--config", "rules.yaml"],
        0,
        stdout=mock_stdout,
        stderr="",
    )
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: mock_result)

    request = SemgrepExecuteRequest(rules="rules.yaml")
    response = semgrep_service.execute(request)

    assert response["matches"] == []


def test_semgrep_execute_error(semgrep_service, monkeypatch):
    def mock_run_error(*args, **kwargs):
        raise subprocess.CalledProcessError(1, "semgrep", stderr="Semgrep error")

    monkeypatch.setattr(subprocess, "run", mock_run_error)

    request = SemgrepExecuteRequest(rules="rules.yaml")
    response = semgrep_service.execute(request)

    assert response["matches"] == []


def test_semgrep_execute_with_file_filters(semgrep_service, monkeypatch):
    mock_stdout = json.dumps({"results": []})
    mock_result = subprocess.CompletedProcess(
        ["semgrep", "--json", "--config", "rules.yaml", "--include", "py,js"],
        0,
        stdout=mock_stdout,
        stderr="",
    )
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: mock_result)

    request = SemgrepExecuteRequest(rules="rules.yaml", file_filters=["py", "js"])
    response = semgrep_service.execute(request)

    assert response["matches"] == []
