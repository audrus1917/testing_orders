"""Подготовка и создание приложения."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import redis.asyncio

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from src.core.config import get_settings
from src.database.alchemy import engine
from src.core.auth.strategy import auth_router, register_router

from . import tags_metadata

settings = get_settings()


class BaseAPI(FastAPI):
    """Базовое ASGI-приложение."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.router.prefix = settings.APPLICATION.BASE_API_PREFIX


@asynccontextmanager
async def lifespan(_: BaseAPI) -> AsyncIterator[None]:
    """Цикл начала и завершения работы приложения."""

    redis_back = redis.asyncio.Redis.from_url(
        f'redis://{settings.REDIS.REDIS_HOST}:{settings.REDIS.REDIS_PORT}',
        encoding='utf-8',
        decode_responses=True,
    )
    FastAPICache.init(RedisBackend(redis_back), prefix='app-cache')

    yield

    await redis_back.close()
    engine.clear_compiled_cache()
    await engine.dispose()


app = BaseAPI(
    debug=settings.DEBUG,
    title=settings.APPLICATION.PROJECT_NAME,
    description=settings.APPLICATION.PROJECT_DESCRIPTION,
    version=str(settings.APPLICATION.API_VERSION) + '.0',
    lifespan=lifespan,
    contact={
        'name': 'Andrey Kozhevnikov',
        'url': 'https://t.me/audrus',
    },
    openapi_tags=tags_metadata,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(auth_router, tags=["auth"], prefix="/auth/jwt")
app.include_router(register_router, tags=["auth"], prefix="/auth")

for x in app.routes:
    print(x)