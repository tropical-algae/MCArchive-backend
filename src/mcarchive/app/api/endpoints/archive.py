from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Security
from sqlmodel import Session

from mcarchive.app.api.deps import get_current_token, get_db
from mcarchive.core.config import settings
from mcarchive.core.logging import logger
from mcarchive.core.model.archive import (
    ArchiveColumns,
    ArchivesResponse,
    DownloadRequest,
    DownloadResponse,
    OssUpdateRequest,
    OssUpdateResponse,
)
from mcarchive.core.services.aliyun_oss import (
    check_daily_update_num,
    get_oss_url,
    upload_file,
    upload_local_backup_task,
)
from mcarchive.core.services.archive_manage import get_all_archives, get_local_save_status
from mcarchive.core.util import summary_token, zip_dir

router = APIRouter()

ARCHIVE_COLUMNS = [
    ArchiveColumns(key="server", title="Server", value_type="text", is_necessary=True),
    ArchiveColumns(key="port", title="Port", value_type="num", is_necessary=False),
    ArchiveColumns(
        key="modpack", title="Modpack", value_type="download", is_necessary=True
    ),
    ArchiveColumns(
        key="snapshot", title="Snapshot", value_type="download", is_necessary=True
    ),
    ArchiveColumns(key="date", title="Date", value_type="num", is_necessary=False),
    ArchiveColumns(key="status", title="Status", value_type="bool", is_necessary=False),
]


@router.post("/get_download_url", response_model=DownloadResponse)
async def get_oss_download_url(
    data: DownloadRequest, token=Depends(get_current_token(False))
) -> DownloadResponse:
    logger.info(f"{summary_token(token)} 请求获取文件 {data.filename} 下载链接")
    url = get_oss_url(data.filename)
    return DownloadResponse(url=url)


@router.get("/items", response_model=ArchivesResponse)
async def get_items() -> ArchivesResponse:
    return ArchivesResponse(columns=ARCHIVE_COLUMNS, rows=get_all_archives())


@router.post("/update_oss", response_model=OssUpdateResponse)
async def update_oss_file(
    data: OssUpdateRequest,
    bt: BackgroundTasks,
    db: Session = Depends(get_db),
    token=Depends(get_current_token(True)),
) -> OssUpdateResponse:
    logger.info(f"{summary_token(token)} 请求更新存档快照 {data.archive_id}")
    save_status = get_local_save_status(db=db, vid=data.archive_id)
    if not save_status.need_update_backup():
        logger.warning(f"{summary_token(token)} 存档快照 {data.archive_id} 已是最新")
        return OssUpdateResponse(message="存档已是最新")

    daily_update_num = check_daily_update_num(save_status.get_save_name())
    if daily_update_num > settings.DAILY_MAX_UPLOAD_NUM:
        logger.warning(
            f"{summary_token(token)} 存档快照 {data.archive_id} 今日已更新 {daily_update_num} 次，超过阈值"
        )
        return OssUpdateResponse(message="该存档更新次数超过今日最大配额")

    bt.add_task(upload_local_backup_task, db=db, save_status=save_status)
    return OssUpdateResponse(message="开始更新存档，这大概会花2~5分钟时间")
