from datetime import datetime
from pathlib import Path

from fastapi import HTTPException
from sqlmodel import Session

from mcarchive.app.utils.constant import CONSTANT
from mcarchive.core.config import settings
from mcarchive.core.db.crud.archives import (
    create_archive,
    select_all_archives,
    select_archive_by_id,
    update_archive,
)
from mcarchive.core.decorator import sql_session
from mcarchive.core.logging import logger
from mcarchive.core.model.archive import ArchiveRows, WorldSaveStatus
from mcarchive.core.util import dir_unique_id, find_subdir


@sql_session()
def get_all_archives(db: Session) -> list[ArchiveRows]:
    archives = select_all_archives(db=db)
    return [ArchiveRows.from_db(archive=archive) for archive in archives]


@sql_session()
def update_local_archives(db: Session) -> None:
    root = Path(settings.LOCAL_MC_VERSION_ROOT)
    if not root.is_dir() or not root.exists():
        logger.error(f"在尝试更新本地存档数据库时得到了无效路径 {root}")
        raise NotADirectoryError(f"{root} 不是有效的目录")

    for version in root.iterdir():
        if not version.is_dir():
            continue
        if find_subdir(parent=version, name=settings.LOCAL_MC_SAVE_NAME) is None:
            continue

        vid: str = dir_unique_id(version)
        version_name = version.name

        archive = select_archive_by_id(db=db, id=vid)
        if archive is None:
            create_archive(
                db=db,
                id=vid,
                server_file=version_name,
                server_name=version_name,
                port="",
                server_status=False,
            )
            logger.info(f"新增存档数据 -> {version_name}[{vid}]")
        else:
            archive.server_file = version_name
            update_archive(db=db, archive=archive)
            logger.info(f"更新存档数据 -> {version_name}[{vid}]")


def get_local_save_status(db: Session, vid: str) -> WorldSaveStatus:
    archive = select_archive_by_id(db=db, id=vid)
    if archive is None:
        raise HTTPException(**CONSTANT.ARCHIVE_NOT_EXISTED)

    version = Path(settings.LOCAL_MC_VERSION_ROOT) / archive.server_file
    world_dir: Path | None = find_subdir(parent=version, name=settings.LOCAL_MC_SAVE_NAME)

    if world_dir is None:
        logger.error(f"本地{version}下不存在世界存档")
        raise HTTPException(**CONSTANT.FILE_NOT_EXISTED)

    world_dat: Path = world_dir / "level.dat"
    if not world_dat.exists():
        logger.error(f"世界存档{world_dat}下不存在level.dat")
        raise HTTPException(**CONSTANT.FILE_NOT_EXISTED)

    return WorldSaveStatus(
        archive=archive,
        save_dir=world_dir,
        latest_sd=archive.snapshot_date,
        current_sd=datetime.fromtimestamp(world_dat.stat().st_mtime),
    )
