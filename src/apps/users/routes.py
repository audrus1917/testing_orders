"""The routes for :cls:`User`."""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union

import logging

from pydantic import ValidationError
from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends, Form
from fastapi_cache.decorator import cache
from fastapi_users.exceptions import UserAlreadyExists

from src.core.http_response_schemas import UniqueConstraint, Unauthorized
from src.core.auth.strategy import get_current_user
from src.core.exceptions import UniqueConstraintError

from src.apps.users.models import UserModel
from src.apps.users.schemas import (
    UserInSchema, UserOutSchema, UserUpdateSchema, UserInTSchema, UserSchemaT
)
from src.apps.users.depends import get_controller

if TYPE_CHECKING:
    from src.apps.users.controller import UserController


logger = logging.getLogger(__name__)

users_router = APIRouter()


async def _register(
    user_schema: UserInSchema,
    controller: UserController = Depends(get_controller),
) -> UserOutSchema:
    """Add (register) the new :cls:`User`."""
           
    try:
        return await controller.create(user_schema)
    except UserAlreadyExists as exc:
        raise HTTPException(
            detail=f'Пользователь с почтой <{user_schema.email}> уже зарегистрирован в системе',
            status_code=status.HTTP_400_BAD_REQUEST,
        ) from exc

    except ValidationError as exc:
        raise HTTPException(
            detail=f'Ошибка валидации: {exc}',
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        ) from exc


@users_router.post(
    '',
    response_model=UserOutSchema,
    responses={
        status.HTTP_201_CREATED: {'model': UserOutSchema},
        status.HTTP_400_BAD_REQUEST: {'model': UniqueConstraint},
    },
    description='Регистрация нового пользователя',
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_data: UserInTSchema,
    controller: UserController = Depends(get_controller),
) -> UserOutSchema:
    """Add (register) the new :cls:`User`."""

    return await _register(user_data, controller=controller)


@users_router.post(
    '/tilda',
    response_model=Union[UserOutSchema, UserInTSchema],
    description='Регистрация нового пользователя',
    status_code=status.HTTP_201_CREATED,
)
async def tilda_register(
    user_data: UserSchemaT = Form(...),
    controller: UserController = Depends(get_controller),
) -> Optional[UserOutSchema]:
    """Add (register) the new :cls:`User` by Tilda data."""

    _test = user_data.model_dump()
    if "test" in _test:
        return _test
    return await _register(user_data, controller=controller)


@users_router.delete(
    '',
    description='Удалить пользователя',
    responses={
        status.HTTP_204_NO_CONTENT: {'description': 'Пользователь успешно удален.'},
        status.HTTP_401_UNAUTHORIZED: {'model': Unauthorized},
    },
    status_code=status.HTTP_204_NO_CONTENT,
)
async def user_delete(
    controller: UserController = Depends(get_controller),
    user: UserModel = Depends(get_current_user),
):
    """Deletes the :cls:`User`."""
    await controller.delete(user_pk=user.id)


@users_router.patch(
    '',
    description='Частично обновить учетные данные пользователя',
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {'model': UserUpdateSchema},
        status.HTTP_401_UNAUTHORIZED: {'model': Unauthorized},
        status.HTTP_400_BAD_REQUEST: {'model': UniqueConstraint},
    },
    response_model=UserOutSchema,
)
async def user_edit(
    user_to_update: UserUpdateSchema,
    controller: UserController = Depends(get_controller),
    user: UserModel = Depends(get_current_user),
) -> UserOutSchema:
    """Updates and returns the :cls:`User`."""
    try:
        return await controller.update(data=user_to_update, user_pk=user.id)
    except UserAlreadyExists as exc:
        raise UniqueConstraintError(
            detail=f'Пользователь с почтой <{user_to_update.email}> уже зарегистрирован в системе',
            status_code=status.HTTP_400_BAD_REQUEST,
        ) from exc


@users_router.get(
    '/me',
    description='Получение информации о текущем пользователе.',
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {'model': Unauthorized},
        status.HTTP_200_OK: {'model': UserOutSchema},
    },
    response_model=UserOutSchema,
)
@cache(expire=60 * 60)
async def get_user(
    controller: UserController = Depends(get_controller),
    user: UserModel = Depends(get_current_user),
) -> UserOutSchema:
    return await controller.get_by_pk(user_pk=user.id)
