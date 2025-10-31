import secrets
from pathlib import Path

from pydantic_settings import BaseSettings


class SysSetting(BaseSettings):
    VERSION: str = "0.1.0"
    PROJECT_NAME: str = "MCArchive"
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    WORKERS: int = 2
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    ALLOW_ORIGIN: list[str] = ["http://localhost:5173", "http://0.0.0.0:5173"]


class ServiceSetting(BaseSettings):
    SQL_DATABASE_URI: str = ""

    ACCESS_TOKEN_EXPIRE_MIN: int = 60 * 3  # 3小时
    ACCESS_TOKEN_SECRET_KEY: str = secrets.token_hex(32)
    ACCESS_TOKEN_ALGORITHM: str = "HS256"

    LOCAL_MC_VERSION_ROOT: str = ""
    LOCAL_MC_SAVE_NAME: str = "world"

    SAVE_CACHE_ROOT: str = "./cache"
    DAILY_MAX_UPLOAD_NUM: int = 3


class OssConfig(BaseSettings):
    # service
    OSS_ACCESS_KEY_ID: str = ""
    OSS_ACCESS_KEY_SECRET: str = ""
    OSS_BUCKET: str = ""
    OSS_REGION: str = ""


class LogSetting(BaseSettings):
    # logger
    LOG_NAME: str = "log.test.record"
    LOG_PATH: str = "./log"
    LOG_FILE_LEVEL: str = "INFO"
    LOG_STREAM_LEVEL: str = "DEBUG"
    LOG_FILE_ENCODING: str = "utf-8"
    LOG_CONSOLE_OUTPUT: bool = True


class Setting(SysSetting, ServiceSetting, LogSetting, OssConfig):
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Setting()

Path(settings.SAVE_CACHE_ROOT).mkdir(parents=True, exist_ok=True)
