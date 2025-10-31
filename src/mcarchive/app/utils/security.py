from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from jose import ExpiredSignatureError, JWTError, jwt
from sqlmodel import Session

from mcarchive.app.utils.constant import CONSTANT
from mcarchive.core.config import settings
from mcarchive.core.db.crud.tokens import select_token
from mcarchive.core.db.models import Tokens
from mcarchive.core.decorator import sql_session
from mcarchive.core.logging import logger


@sql_session()
def verify_token(db: Session, token: str) -> Tokens:
    selected_token: Tokens | None = select_token(db=db, token=token)
    if selected_token is None:
        raise HTTPException(**CONSTANT.TOKEN_NOT_MATCH)
    if not selected_token.is_activated:
        raise HTTPException(**CONSTANT.TOKEN_NOT_ACTIVATED)

    return selected_token


def create_access_token(token: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "token": token,
        "timestamp": int(now.timestamp()),
        "exp": int(
            (now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MIN)).timestamp()
        ),
    }
    return jwt.encode(
        payload,
        settings.ACCESS_TOKEN_SECRET_KEY,
        algorithm=settings.ACCESS_TOKEN_ALGORITHM,
    )


def verify_access_token(token: str) -> Tokens:
    try:
        claims = jwt.decode(
            token,
            settings.ACCESS_TOKEN_SECRET_KEY,
            algorithms=settings.ACCESS_TOKEN_ALGORITHM,
        )
    except ExpiredSignatureError as es_err:
        raise HTTPException(**CONSTANT.ACCESS_TOKEN_EXPIRED) from es_err
    except JWTError as jwt_err:
        raise HTTPException(**CONSTANT.ACCESS_TOKEN_PARSE_ERR) from jwt_err

    result: Tokens = verify_token(token=claims.get("token"))
    return result
