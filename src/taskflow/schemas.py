"""Schemas de entrada e saída (Pydantic v2)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    """Payload para criação de usuário."""

    email: EmailStr
    full_name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, v: str) -> str:
        """O bcrypt processa no máximo 72 bytes; acima disso ele não funciona."""
        if len(v.encode("utf-8")) > 72:
            raise ValueError("password deve ter no máximo 72 bytes")
        return v

    @field_validator("full_name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        """Remove espaços extras no início e fim do nome."""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("full_name não pode ser apenas espaços")
        return cleaned


class UserPublic(BaseModel):
    """Dados de usuário expostos na API (nunca inclui a senha)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    created_at: datetime


class Token(BaseModel):
    """Resposta do endpoint de login."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Conteúdo decodificado do JWT."""

    sub: int | None = None
    exp: int | None = None


class TaskBase(BaseModel):
    """Campos comuns de uma tarefa."""

    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)

    @field_validator("title")
    @classmethod
    def strip_title(cls, v: str) -> str:
        """Garante que o título não seja vazio após remover espaços."""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("title não pode ser vazio")
        return cleaned


class TaskCreate(TaskBase):
    """Payload para criação de tarefa."""


class TaskUpdate(BaseModel):
    """Payload para atualização parcial de tarefa."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    completed: bool | None = None

    @field_validator("title")
    @classmethod
    def strip_title(cls, v: str | None) -> str | None:
        """Aplica o mesmo saneamento do título quando ele é enviado."""
        if v is None:
            return None
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("title não pode ser vazio")
        return cleaned


class TaskPublic(TaskBase):
    """Representação pública de uma tarefa."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    completed: bool
    created_at: datetime
    completed_at: datetime | None


class TaskList(BaseModel):
    """Envelope de listagem paginada."""

    total: int
    skip: int
    limit: int
    items: list[TaskPublic]
