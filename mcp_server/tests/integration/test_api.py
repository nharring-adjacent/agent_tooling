import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_comby_scan():
    async with AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/v1/comby/scan",
            json={
                "match_template": "func :[name]()",
                "rewrite_template": "function :[name]()",
                "file_filters": ["py"],
            },
        )
    assert response.status_code == 200
    assert response.json() == {"matches": []}


@pytest.mark.asyncio
async def test_comby_ideate():
    async with AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/v1/comby/ideate",
            json={
                "code_snippet": "def hello():\n    pass",
                "match_template": "def :[name]():",
                "rewrite_template": "async def :[name]():",
            },
        )
    assert response.status_code == 200
    assert response.json() == {"transformed_code": "async def hello():\n    pass"}


@pytest.mark.asyncio
async def test_semgrep_scan():
    async with AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/v1/semgrep/scan",
            json={
                "pattern": "pattern-test",
                "file_filters": ["py"],
            },
        )
    assert response.status_code == 200
    assert response.json() == {"matches": []}


@pytest.mark.asyncio
async def test_semgrep_ideate():
    async with AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/v1/semgrep/ideate",
            json={
                "code_snippet": 'print("hello")',
                "pattern": "pattern-test",
            },
        )
    assert response.status_code == 200
    assert response.json() == {"matches": []}


@pytest.mark.asyncio
async def test_semgrep_execute():
    async with AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/v1/semgrep/execute",
            json={
                "rules": "rules-test",
                "file_filters": ["py"],
            },
        )
    assert response.status_code == 200
    assert response.json() == {"matches": []}


@pytest.mark.asyncio
async def test_comby_execute():
    # Create a dummy file for testing in-place modification
    with open("test_execute_file.py", "w") as f:
        f.write("def old_function():\n    pass\n")

    async with AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/v1/comby/execute",
            json={
                "match_template": "old_function",
                "rewrite_template": "new_function",
                "file_filters": ["py"],
            },
        )
    assert response.status_code == 200
    assert response.json() == {"success": True, "files_changed": 1}

    # Clean up the dummy file
    import os

    os.remove("test_execute_file.py")
