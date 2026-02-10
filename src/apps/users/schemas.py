"""The `User` and `Role` schemas."""

import re

from datetime import datetime
from typing import Optional, Union

from fastapi_users import schemas
from pydantic import EmailStr, ConfigDict, field_validator, BaseModel
from pydantic_core import PydanticCustomError

from src.core.schemas import OwnFieldsOnlyMixin
from src.apps.roles.schemas import RoleOut

PASSWORD_VALID_RE = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*]).{6,}$')
PASSWORD_INVALID_MSG = """Значение должно содержать:
* хотя бы одну строчную латинскую букву;
* хотя бы одну заглавную латинскую букву;
* хотя бы одну цифру;
* хотя бы один спецсимвол (!@#$%^&*).
"""


class PasswordMixin:
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str):
        if not PASSWORD_VALID_RE.match(v):
            raise PydanticCustomError(
                'invalid_password_value',
                f"Неверное значение для поля 'Пароль'. {PASSWORD_INVALID_MSG}",
            )

        return v


class UserInSchema(PasswordMixin, OwnFieldsOnlyMixin, schemas.BaseUserCreate):
    """The incoming data schema."""

    # Для дополнительных полей, которые присылает Тильда (test, UTM).
    model_config = ConfigDict(extra='allow')

    email: EmailStr
    password: str
    is_active: Optional[bool] = True
    is_verified: Optional[bool] = False
    person_id: Optional[int] = None


class UserOutSchema(schemas.BaseUser[int]):
    id: int
    email: EmailStr
    is_active: bool = True
    is_verified: bool = False
    first_name: Optional[str] = None
    roles: Optional[list[RoleOut]] = None


class UserUpdateSchema(PasswordMixin, schemas.BaseUserUpdate):
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    last_login: Optional[datetime] = None


class UserRegisterSchema(PasswordMixin, schemas.BaseUserCreate):
    """The incoming data schema."""

    # Для дополнительных полей, которые присылает Тильда (test, UTM).
    model_config = ConfigDict(extra='allow')

    email: EmailStr
    password: str


class UserInTSchema(BaseModel):
    model_config = ConfigDict(extra='allow')

    test: str 


UserSchemaT = Union[UserInTSchema, UserInSchema]