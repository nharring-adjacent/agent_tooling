import subprocess
import sys
from pathlib import Path
from typing import Any

import polars as pl
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from tools.doxygen_embedder.main import doxygen_embedding_tool


class DummyEncoding:
    def encode(self, text: str) -> list[str]:
        return text.split()

    def decode(self, tokens: list[str]) -> str:
        return " ".join(tokens)


class DummyResponse:
    def __init__(self, data: dict[str, Any]):
        self._data = data

    def raise_for_status(self) -> None:  # pragma: no cover
        pass

    def json(self) -> dict[str, Any]:
        return self._data


def test_embedding_tool(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    xml_dir = tmp_path / "xml"
    xml_dir.mkdir()
    sample_xml = xml_dir / "sample.xml"
    sample_xml.write_text(
        """
        <doxygen>
          <compounddef kind='class'>
            <compoundname>Example</compoundname>
            <briefdescription><para>Brief.</para></briefdescription>
            <detaileddescription><para>Detail text.</para></detaileddescription>
            <memberdef kind='function'>
              <name>foo</name>
              <briefdescription><para>Foo brief</para></briefdescription>
            </memberdef>
          </compounddef>
        </doxygen>
        """,
        encoding="utf-8",
    )

    def fake_run(cmd, input=None, cwd=None, check=None):
        # write xml to expected location
        dest = Path(input.decode().split("OUTPUT_DIRECTORY=")[1].split("\n")[0]) / "xml"
        dest.mkdir(parents=True, exist_ok=True)
        for file in xml_dir.iterdir():
            dest.joinpath(file.name).write_bytes(file.read_bytes())
        return subprocess.CompletedProcess(cmd, 0)

    def fake_post(url, headers=None, json=None, timeout=30):
        return DummyResponse({"embedding": [0.1, 0.2]})

    monkeypatch.setattr("subprocess.run", fake_run)
    monkeypatch.setattr("requests.post", fake_post)
    monkeypatch.setattr("tiktoken.get_encoding", lambda name: DummyEncoding())

    out_file = tmp_path / "out.parquet"
    result = doxygen_embedding_tool(str(repo), str(out_file), "http://base")
    assert Path(result).is_file()
    df = pl.read_parquet(out_file)
    assert {"class_name", "section", "member_name", "text", "embedding"} <= set(
        df.columns
    )
