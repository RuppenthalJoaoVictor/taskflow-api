"""Dependências de autenticação reutilizadas pelas rotas."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from taskflow.core.database import get_db
from taskflow.core.security import decode_access_token
from taskflow.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

CREDENTIALS_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Credenciais inválidas ou token expirado",
    headers={"WWW-Authenticate": "Bearer"},
)

DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: DbSession) -> User:
    """Extrai o usuário autenticado a partir do token Bearer."""
    payload = decode_access_token(token)
    if payload is None:
        raise CREDENTIALS_ERROR

    subject = payload.get("sub")
    try:
        user_id = int(subject)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        raise CREDENTIALS_ERROR from None

    user = db.get(User, user_id)
    if user is None:
        raise CREDENTIALS_ERROR
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
