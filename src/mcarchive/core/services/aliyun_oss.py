from datetime import datetime, timedelta, timezone
from pathlib import Path

import alibabacloud_oss_v2 as oss
from cachetools import TTLCache
from sqlmodel import Session

from mcarchive.app.utils.constant import CONSTANT
from mcarchive.core.config import settings
from mcarchive.core.db.crud.archives import update_archive
from mcarchive.core.logging import logger
from mcarchive.core.model.archive import WorldSaveStatus
from mcarchive.core.services.thread_manage import thread_pool
from mcarchive.core.util import zip_dir

_URL_CACHE: TTLCache = TTLCache(maxsize=1024, ttl=30 * 60)
OSS_CONFIG = oss.config.load_default()
OSS_CONFIG.credentials_provider = oss.credentials.StaticCredentialsProvider(
    access_key_id=settings.OSS_ACCESS_KEY_ID,
    access_key_secret=settings.OSS_ACCESS_KEY_SECRET,
)
OSS_CONFIG.region = settings.OSS_REGION


def get_oss_url(key: str) -> str:
    if key in _URL_CACHE:
        return _URL_CACHE[key]
    client = oss.Client(OSS_CONFIG)
    response = client.presign(
        request=oss.GetObjectRequest(bucket=settings.OSS_BUCKET, key=key),
        expires=timedelta(minutes=30),
    )
    _URL_CACHE[key] = response.url
    return response.url


def check_daily_update_num(file_prefix: str) -> int:
    num = 0
    localtime = datetime.now(timezone.utc)
    client = oss.Client(OSS_CONFIG)
    paginator = client.list_objects_v2_paginator()
    for page in paginator.iter_page(
        oss.ListObjectsV2Request(
            bucket=settings.OSS_BUCKET,
            prefix=file_prefix,
        )
    ):
        for o in page.contents:
            if localtime.date() == o.last_modified.date():
                num += 1
    logger.debug(f"检索到{localtime.date()}共上传{num}份{file_prefix}文件")
    return num


def upload_file(filename: str, filepath: str | Path) -> bool:
    filepath = str(filepath)
    try:
        client = oss.Client(OSS_CONFIG)
        result = client.put_object_from_file(
            oss.PutObjectRequest(bucket=settings.OSS_BUCKET, key=filename), filepath
        )
        return result.status_code == 200
    except Exception:
        return False


async def upload_local_backup_task(db: Session, save_status: WorldSaveStatus) -> None:
    def _upload_local_backup():
        filepath = save_status.gen_backup_filepath("zip")
        filename = filepath.name
        try:
            logger.info(f"[后台任务] 开始压缩存档 {save_status.archive.server_name}")
            zip_dir(source_dir=save_status.save_dir, output_zip=filepath, level=6)

            logger.info(f"[后台任务] 准备上传文件到云 {save_status.archive.server_name}")
            upload_done = upload_file(filename=filename, filepath=filepath)
            if upload_done:
                save_status.archive.snapshot_date = save_status.current_sd
                save_status.archive.snapshot_name = filename
                logger.info(f"[后台任务] 更新数据库 {save_status.archive.server_name}")
                update_archive(db=db, archive=save_status.archive)
            else:
                logger.error(f"[后台任务] 文件上传失败 {save_status.archive.server_name}")

        except Exception as err:
            logger.error(f"[后台任务] 更新存档时出错：{err}")
        finally:
            if filepath.exists():
                filepath.unlink()

    await thread_pool.submit_sync(_upload_local_backup)
