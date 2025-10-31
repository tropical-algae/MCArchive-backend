import uuid
from datetime import datetime, timezone

from sqlmodel import Session, select

from mcarchive.core.db.models import Archives
from mcarchive.core.logging import logger


def select_all_archives(db: Session) -> list[Archives]:
    result = db.exec(select(Archives)).all()
    return list(result)


def select_archive_by_id(db: Session, id: str) -> Archives | None:
    result = db.exec(select(Archives).where(Archives.id == id)).first()
    return result


def create_archive(
    db: Session,
    id: str,
    server_file: str,
    server_name: str,
    port: str,
    server_status: bool,
    modpack_name: str | None = None,
    snapshot_name: str | None = None,
    snapshot_date: datetime | None = None,
) -> Archives:
    archive = Archives(
        id=id,
        server_file=server_file,
        server_name=server_name,
        port=port,
        modpack_name=modpack_name,
        snapshot_name=snapshot_name,
        snapshot_date=snapshot_date,
        server_status=server_status,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(archive)
    db.commit()
    db.refresh(archive)
    return archive


def update_archive(db: Session, archive: Archives) -> Archives | None:
    result = db.get(Archives, ident=archive.id)
    if result:
        result.server_name = archive.server_name
        result.port = archive.port
        result.modpack_name = archive.modpack_name
        result.snapshot_name = archive.snapshot_name
        result.snapshot_date = archive.snapshot_date
        result.server_status = archive.server_status
        if db.is_modified(result, include_collections=False):
            result.updated_at = datetime.now(timezone.utc)
            logger.debug(f"Update archive {result.server_name}")

        db.add(result)
        db.commit()
        db.refresh(result)
        return result
    return None
