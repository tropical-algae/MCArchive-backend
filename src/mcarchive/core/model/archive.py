from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from mcarchive.core.config import settings
from mcarchive.core.db.models import Archives


class ArchiveColumns(BaseModel):
    key: str
    title: str
    value_type: Literal["text", "num", "download", "bool"]
    is_necessary: bool


class ArchiveRows(BaseModel):
    id: str
    server: str
    port: str
    modpack: str
    snapshot: str
    date: str
    status: bool

    @classmethod
    def from_db(cls, archive: Archives) -> "ArchiveRows":
        date = (
            archive.snapshot_date.strftime("%Y-%m-%d %H:%M")
            if archive.snapshot_date
            else ""
        )
        return ArchiveRows(
            id=archive.id,
            server=archive.server_name,
            port=archive.port,
            modpack=archive.modpack_name or "",
            snapshot=archive.snapshot_name or "",
            date=date,
            status=archive.server_status,
        )


class ArchivesResponse(BaseModel):
    columns: list[ArchiveColumns] = Field(default_factory=list)
    rows: list[ArchiveRows] = Field(default_factory=list)


class DownloadRequest(BaseModel):
    filename: str


class DownloadResponse(BaseModel):
    url: str


class OssUpdateRequest(BaseModel):
    archive_id: str


class OssUpdateResponse(BaseModel):
    message: str


class WorldSaveStatus(BaseModel):
    archive: Archives
    save_dir: Path
    latest_sd: datetime | None
    current_sd: datetime

    def get_save_name(self) -> str:
        return f"save-{self.archive.server_file}"

    def gen_backup_filepath(self, file_extension: str) -> Path:
        save_name = f"{self.get_save_name()}-{self.current_sd.strftime('%Y-%m-%d_%H-%M-%S')}.{file_extension}"
        return Path(settings.SAVE_CACHE_ROOT) / save_name

    def need_update_backup(self) -> bool:
        return self.latest_sd is None or self.current_sd > self.latest_sd
