from pydantic_settings import BaseSettings


class Constant(BaseSettings):
    # 返回值
    RESP_200: dict = {"status_code": 200, "detail": "success"}
    RESP_VALIDATION_ERROR: dict = {"status_code": 401, "detail": "参数校验错误"}
    RESP_SERVER_ERROR: dict = {"status_code": 501, "detail": "服务器错误"}
    TOKEN_NOT_MATCH: dict = {"status_code": 401, "detail": "Token校验失败"}
    TOKEN_NOT_ACTIVATED: dict = {"status_code": 401, "detail": "Token未激活"}
    TOKEN_PERMISSION_DENIED: dict = {"status_code": 403, "detail": "权限不足"}

    ACCESS_TOKEN_NOT_EXISTED: dict = {"status_code": 401, "detail": "未校验身份"}
    ACCESS_TOKEN_PARSE_ERR: dict = {"status_code": 401, "detail": "AccessToken解析失败"}
    ACCESS_TOKEN_EXPIRED: dict = {
        "status_code": 401,
        "detail": "AccessToken超时，需重新校验",
    }

    FILE_NOT_EXISTED: dict = {"status_code": 404, "detail": "目标文件不存在或已损坏"}
    ARCHIVE_NOT_EXISTED: dict = {"status_code": 404, "detail": "不存在的档案信息"}

    # task 任务
    INFERENCE_RESULT_NOT_EXISTS: str = "推理结果不存在"
    DELETE_INFERENCE_RESULT_FILE_FAIL: str = "删除推理结果文件失败"


CONSTANT = Constant()
