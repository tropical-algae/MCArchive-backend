import os
import zipfile
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException

from mcarchive.app.utils.constant import CONSTANT
from mcarchive.core.db.models import Tokens


def summary_token(token: Tokens) -> str:
    return f"TOKEN[{token.id}]{'[Admin]' if token.is_admin else ''}{'[Activated]' if token.is_activated else ''}"


def zip_dir(source_dir: Path, output_zip: Path, level: int = 6) -> None:
    source_dir = source_dir.resolve()
    output_zip = output_zip.resolve()
    with zipfile.ZipFile(
        output_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=level
    ) as zf:
        for file_path in source_dir.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(source_dir)
                zf.write(file_path, relative_path)


def generate_filepath(filename: str, filepath: str) -> str:
    if not os.path.isdir(filepath):
        os.makedirs(filepath)
    return os.path.join(filepath, filename)


def dir_unique_id(p: Path) -> str:
    st = p.lstat()
    return f"{st.st_dev}-{st.st_ino}"


def find_subdir(parent: Path, name: str) -> Path | None:
    if not parent.is_dir() or not parent.exists():
        return None

    target = name.lower()
    for child in parent.iterdir():
        if not child.is_dir():
            continue
        if child.name.lower() == target:
            return child
    return None
