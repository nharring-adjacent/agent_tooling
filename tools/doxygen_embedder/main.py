from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional
import xml.etree.ElementTree as ET

import polars as pl
import requests
from crewai_tools import tool


def _get_text(element: Optional[ET.Element]) -> str:
    if element is None:
        return ""
    return " ".join(part.strip() for part in element.itertext()).strip()


def _chunk_text(text: str, max_tokens: int) -> List[str]:
    """Split *text* into overlapping chunks using token counts.

    This function uses ``tiktoken`` to ensure that each chunk contains at most
    ``max_tokens`` tokens. Adjacent chunks overlap by roughly 20% of the token
    length to preserve context.
    """

    import tiktoken

    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)
    if len(tokens) <= max_tokens:
        return [text]

    step = max(int(max_tokens * 0.8), 1)
    chunks = []
    for i in range(0, len(tokens), step):
        chunk_tokens = tokens[i : i + max_tokens]
        chunks.append(enc.decode(chunk_tokens))
        if i + max_tokens >= len(tokens):
            break
    return chunks


def _embed(text: str, base_url: str, api_key: Optional[str]) -> List[float]:
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    resp = requests.post(base_url, headers=headers, json={"text": text}, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    embedding = data.get("embedding")
    if not isinstance(embedding, list):
        raise ValueError("Invalid embedding response")
    return embedding


def _parse_member(
    member: ET.Element, class_name: str, max_tokens: int
) -> List[Dict[str, Any]]:
    rows = []
    member_name = _get_text(member.find("name")) or None
    kind = member.get("kind", "member")
    brief = _get_text(member.find("briefdescription"))
    detailed = _get_text(member.find("detaileddescription"))

    for section, text in [(f"{kind} brief", brief), (f"{kind} detailed", detailed)]:
        if not text:
            continue
        for chunk in _chunk_text(text, max_tokens):
            rows.append(
                {
                    "class_name": class_name,
                    "section": section,
                    "member_name": member_name,
                    "text": chunk,
                }
            )
    return rows


def _parse_compound(compound: ET.Element, max_tokens: int) -> List[Dict[str, Any]]:
    rows = []
    class_name = _get_text(compound.find("compoundname"))
    brief = _get_text(compound.find("briefdescription"))
    detailed = _get_text(compound.find("detaileddescription"))

    for section, text in [
        ("brief description", brief),
        ("detailed description", detailed),
    ]:
        if not text:
            continue
        for chunk in _chunk_text(text, max_tokens):
            rows.append(
                {
                    "class_name": class_name,
                    "section": section,
                    "member_name": None,
                    "text": chunk,
                }
            )

    for member in compound.findall("memberdef"):
        rows.extend(_parse_member(member, class_name, max_tokens))
    return rows


def _parse_xml(xml_dir: Path, max_tokens: int) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for path in xml_dir.glob("*.xml"):
        tree = ET.parse(path)
        root = tree.getroot()
        for compound in root.findall("compounddef"):
            kind = compound.get("kind")
            if kind in {"class", "struct"}:
                rows.extend(_parse_compound(compound, max_tokens))
    return rows


@tool
def doxygen_embedding_tool(
    repo_path: str,
    output_file: str,
    base_url: str,
    api_key: str | None = None,
    max_chunk_tokens: int = 8191,
) -> str:
    """Generate embeddings for Doxygen class documentation and save to Parquet.

    Parameters
    ----------
    repo_path: Path to the repository to process.
    output_file: Destination Parquet file path.
    base_url: URL of the embedding service accepting POST {"text": str}.
    api_key: Optional authorization token.
    max_chunk_tokens: Maximum tokens per text chunk before splitting.

    Returns
    -------
    Path to the generated Parquet file containing columns:
    - class_name: class or struct name.
    - section: documentation section.
    - member_name: related member if applicable.
    - text: documentation text chunk.
    - embedding: embedding vector for the text.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        doxyfile = f"OUTPUT_DIRECTORY={tmpdir}\nGENERATE_XML=YES\nRECURSIVE=YES\nINPUT={repo_path}"
        subprocess.run(
            ["doxygen", "-"], input=doxyfile.encode(), cwd=repo_path, check=True
        )
        xml_dir = Path(tmpdir) / "xml"
        rows = _parse_xml(xml_dir, max_chunk_tokens)
    for row in rows:
        row["embedding"] = _embed(row["text"], base_url, api_key)
    df = pl.DataFrame(rows)
    df.write_parquet(output_file)
    return output_file
