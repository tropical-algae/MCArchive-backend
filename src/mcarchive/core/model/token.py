from pydantic import BaseModel


class AccessTokenRequest(BaseModel):
    token: str


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    is_admin: bool
