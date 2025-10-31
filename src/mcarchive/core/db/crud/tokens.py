from sqlmodel import Session, select

from mcarchive.core.db.models import Tokens


def select_token(db: Session, token: str) -> Tokens | None:
    result = db.exec(select(Tokens).where(Tokens.token == token)).first()
    return result
