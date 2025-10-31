from collections.abc import Generator

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from mcarchive.app.utils.constant import CONSTANT
from mcarchive.app.utils.security import verify_access_token
from mcarchive.core.db.models import Tokens
from mcarchive.core.db.session import LocalSession

BEARER_SCHEME = HTTPBearer(auto_error=False)


def get_db() -> Generator:
    db = None
    try:
        db = LocalSession()
        yield db
    finally:
        if db:
            db.close()


def get_current_token(need_admin: bool = False):
    async def _verify_token(
        credentials: HTTPAuthorizationCredentials = Depends(BEARER_SCHEME),
    ) -> Tokens:
        if not credentials or credentials.scheme.lower() != "bearer":
            raise HTTPException(**CONSTANT.ACCESS_TOKEN_NOT_EXISTED)
        token = verify_access_token(credentials.credentials)
        if need_admin and not token.is_admin:
            raise HTTPException(**CONSTANT.TOKEN_PERMISSION_DENIED)
        return token

    return _verify_token
