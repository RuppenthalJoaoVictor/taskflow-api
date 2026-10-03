"""Autenticação: hash de senha e codificação/decodificação de JWT.

Usa a biblioteca ``bcrypt`` diretamente em vez do ``passlib``, que está sem
manutenção desde 2020 e é incompatível com as versões recentes do bcrypt.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from jose import JWTError, jwt

from taskflow.core.config import get_settings

settings = get_settings()

# O bcrypt considera no máximo 72 bytes; senhas maiores são recusadas na
# validação do schema para evitar truncamento silencioso.
MAX_PASSWORD_BYTES = 72


def hash_password(password: str) -> str:
    """Gera o hash bcrypt de uma senha em texto puro."""
    encoded = password.encode("utf-8")
    if len(encoded) > MAX_PASSWORD_BYTES:
        raise ValueError(f"A senha não pode exceder {MAX_PASSWORD_BYTES} bytes")
    return bcrypt.hashpw(encoded, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Confere se a senha em texto puro corresponde ao hash armazenado.

    Retorna ``False`` em vez de propagar exceção quando os hashes são
    incompatíveis, para não vazar informação por diferença de comportamento.
    """
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(subject: str | int, expires_delta: timedelta | None = None) -> str:
    """Cria um JWT assinado com o subject informado (normalmente o id do usuário)."""
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload: dict[str, Any] = {"sub": str(subject), "exp": expire}
    token: str = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    return token


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decodifica um JWT. Retorna None se o token for inválido ou expirado."""
    try:
        decoded: dict[str, Any] | None = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return decoded
    except JWTError:
        return None
