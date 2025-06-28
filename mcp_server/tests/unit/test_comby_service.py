import json
import subprocess

import pytest

from mcp_server.models.comby import (
    CombyExecuteRequest,
    CombyIdeateRequest,
    CombyScanRequest,
)
from mcp_server.services.comby import CombyService


@pytest.fixture
def comby_service():
    return CombyService()


def test_scan_success(comby_service, monkeypatch):
    mock_stdout = json.dumps(
        {
            "uri": "file1.py",
            "matches": [{"range": {}, "matched": "def foo():"}],
        }
    )
    mock_result = subprocess.CompletedProcess(
        ["comby", "match", "rewrite", "-json-lines", "-match-only"],
        0,
        stdout=mock_stdout,
        stderr="",
    )
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: mock_result)

    request = CombyScanRequest(match_template="match", rewrite_template="rewrite")
    response = comby_service.scan(request)

    assert response["matches"][0]["uri"] == "file1.py"
    assert response["matches"][0]["matched"] == "def foo():"


def test_scan_no_matches(comby_service, monkeypatch):
    mock_stdout = ""
    mock_result = subprocess.CompletedProcess(
        ["comby", "match", "rewrite", "-json-lines", "-match-only"],
        0,
        stdout=mock_stdout,
        stderr="",
    )
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: mock_result)

    request = CombyScanRequest(match_template="match", rewrite_template="rewrite")
    response = comby_service.scan(request)

    assert response["matches"] == []


def test_scan_no_file_filters(comby_service, monkeypatch):
    mock_stdout = json.dumps(
        {
            "uri": "file1.py",
            "matches": [{"range": {}, "matched": "def foo():"}],
        }
    )
    mock_result = subprocess.CompletedProcess(
        ["comby", "match", "rewrite", "-json-lines", "-match-only", "-d", "."],
        0,
        stdout=mock_stdout,
        stderr="",
    )
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: mock_result)

    request = CombyScanRequest(match_template="match", rewrite_template="rewrite", file_filters=None)
    response = comby_service.scan(request)

    assert response["matches"][0]["uri"] == "file1.py"
    assert response["matches"][0]["matched"] == "def foo():"


def test_scan_with_file_filters(comby_service, monkeypatch):
    mock_stdout = json.dumps(
        {
            "uri": "file1.py",
            "matches": [{"range": {}, "matched": "def bar():"}],
        }
    )
    mock_result = subprocess.CompletedProcess(
        ["comby", "match", "rewrite", "-json-lines", "-match-only", "-d", ".", "-file", "py,js"],
        0,
        stdout=mock_stdout,
        stderr="",
    )
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: mock_result)

    request = CombyScanRequest(match_template="match", rewrite_template="rewrite", file_filters=["py", "js"])
    response = comby_service.scan(request)

    assert response["matches"][0]["uri"] == "file1.py"
    assert response["matches"][0]["matched"] == "def bar():"


def test_scan_error(comby_service, monkeypatch):
    def mock_run_error(*args, **kwargs):
        raise subprocess.CalledProcessError(1, "comby", stderr="Comby error")

    monkeypatch.setattr(subprocess, "run", mock_run_error)

    request = CombyScanRequest(match_template="match", rewrite_template="rewrite")
    response = comby_service.scan(request)

    assert response["matches"] == []


def test_ideate_success(comby_service, monkeypatch):
    mock_stdout = "transformed code"
    mock_result = subprocess.CompletedProcess(
        ["comby", "match", "rewrite", "-stdin"],
        0,
        stdout=mock_stdout,
        stderr="",
    )
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: mock_result)

    request = CombyIdeateRequest(code_snippet="original code", match_template="match", rewrite_template="rewrite")
    response = comby_service.ideate(request)

    assert response["transformed_code"] == "transformed code"


def test_ideate_error(comby_service, monkeypatch):
    def mock_run_error(*args, **kwargs):
        raise subprocess.CalledProcessError(1, "comby", stderr="Comby error")

    monkeypatch.setattr(subprocess, "run", mock_run_error)

    request = CombyIdeateRequest(code_snippet="original code", match_template="match", rewrite_template="rewrite")
    response = comby_service.ideate(request)

    assert response["transformed_code"] == "original code"


def test_execute_success(comby_service, monkeypatch):
    mock_stdout = "diff1\ndiff2\ndiff3"  # Simulate 3 files changed
    mock_result = subprocess.CompletedProcess(
        ["comby", "match", "rewrite", "-json-lines", "-in-place"],
        0,
        stdout=mock_stdout,
        stderr="",
    )
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: mock_result)

    request = CombyExecuteRequest(match_template="match", rewrite_template="rewrite")
    response = comby_service.execute(request)

    assert response["success"] is True
    assert response["files_changed"] == 1


def test_execute_no_changes(comby_service, monkeypatch):
    mock_stdout = ""
    mock_result = subprocess.CompletedProcess(
        ["comby", "match", "rewrite", "-json-lines", "-in-place"],
        0,
        stdout=mock_stdout,
        stderr="",
    )
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: mock_result)

    request = CombyExecuteRequest(match_template="match", rewrite_template="rewrite")
    response = comby_service.execute(request)

    assert response["success"] is True
    assert response["files_changed"] == 1


def test_execute_no_file_filters(comby_service, monkeypatch):
    mock_stdout = "diff1\ndiff2\ndiff3"  # Simulate 3 files changed
    mock_result = subprocess.CompletedProcess(
        ["comby", "match", "rewrite", "-json-lines", "-in-place", "-d", "."],
        0,
        stdout=mock_stdout,
        stderr="",
    )
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: mock_result)

    request = CombyExecuteRequest(match_template="match", rewrite_template="rewrite", file_filters=None)
    response = comby_service.execute(request)

    assert response["success"] is True
    assert response["files_changed"] == 1


def test_execute_with_file_filters(comby_service, monkeypatch):
    mock_stdout = "diff1\ndiff2\ndiff3"  # Simulate 3 files changed
    mock_result = subprocess.CompletedProcess(
        ["comby", "match", "rewrite", "-json-lines", "-in-place", "-d", ".", "-file", "py,js"],
        0,
        stdout=mock_stdout,
        stderr="",
    )
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: mock_result)

    request = CombyExecuteRequest(match_template="match", rewrite_template="rewrite", file_filters=["py", "js"])
    response = comby_service.execute(request)

    assert response["success"] is True
    assert response["files_changed"] == 1


def test_execute_error(comby_service, monkeypatch):
    def mock_run_error(*args, **kwargs):
        raise subprocess.CalledProcessError(1, "comby", stderr="Comby error")

    monkeypatch.setattr(subprocess, "run", mock_run_error)

    request = CombyExecuteRequest(match_template="match", rewrite_template="rewrite")
    response = comby_service.execute(request)

    assert response["success"] is False
    assert response["files_changed"] == 0
