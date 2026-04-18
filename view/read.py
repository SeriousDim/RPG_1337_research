"""Utilities for reading the prompt and generated quest files."""

from __future__ import annotations

import os
from pathlib import Path


PROMPT_PATH = Path(__file__).resolve().parent / "resources" / "prompts" / "automata_v2_delivery_v2.txt"


def read_prompt_and_generated_quest(quest_path: str | Path) -> tuple[str, str]:
    """Read the fixed prompt and a generated quest from disk.

    Args:
        quest_path: Path to the generated quest file.

    Returns:
        A tuple of (prompt_text, generated_quest_text).
    """
    prompt_text = PROMPT_PATH.read_text(encoding="utf-8")
    generated_quest_text = Path(quest_path).read_text(encoding="utf-8")
    return prompt_text, generated_quest_text


def zip_results_dir() -> bytes:
    """Create an in-memory ZIP archive with all files from the results directory.

    If the directory is empty or missing, an empty ZIP archive is returned.

    Returns:
        ZIP archive data as bytes.
    """
    import io
    import zipfile

    result_dir = Path(os.getenv("RESULTS_DIR", Path(__file__).resolve().parent / "results"))
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        if result_dir.exists():
            for path in list(result_dir.rglob("*")):
                if path.is_file():
                    archive.write(path, arcname=path.relative_to(result_dir))

    return buffer.getvalue()



