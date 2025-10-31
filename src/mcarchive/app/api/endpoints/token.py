from fastapi import APIRouter, Depends, HTTPException

from mcarchive.app.utils.constant import CONSTANT
from mcarchive.app.utils.security import create_access_token, verify_token
from mcarchive.core.config import settings
from mcarchive.core.db.models import Tokens
from mcarchive.core.logging import logger
from mcarchive.core.model.token import AccessTokenRequest, AccessTokenResponse
from mcarchive.core.util import summary_token

router = APIRouter()


@router.post("/access-token", response_model=AccessTokenResponse)
async def login_access_token(form_data: AccessTokenRequest):
    token: Tokens = verify_token(token=form_data.token)
    access_token = create_access_token(token=form_data.token)
    logger.info(f"{summary_token(token)} 成功校验")

    return AccessTokenResponse(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MIN * 60,
        is_admin=token.is_admin,
    )
