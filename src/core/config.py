"""Классы для настроек приложения."""

import os

from typing import List
from pathlib import Path
from zoneinfo import ZoneInfo

import secrets

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    PydanticBaseSettingsSource,
    YamlConfigSettingsSource,
)

from sqlalchemy.engine.url import URL


# Режим работы (задается значением переменной окружения)
APP_MODE = os.environ.get("MODE", "dev")


class ApplicationSettings(BaseSettings):
    """Класс настроек приложения."""

    PROJECT_NAME: str = Field(
        default="Управление заказами",
        title="Наименование проекта"
    )
    PROJECT_DESCRIPTION: str = Field(
        default="REST-API для управление закзами", title="Описание проекта"
    )
    VERSION: str = Field(default="0.1", title="Версия  API")
    API_VERSION: int = Field(default=1, title="Префикс версии")
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 10 * 60
    HOST: str = Field(default="orders.local")
    PORT: int = Field(default=8080)
    CACHE_TTL: int = Field(default=5, title="TTL для кэша в минутах")

    @property
    def BASE_API_PREFIX(self):
        """Возвращает базовый префикс для запроса."""
        return f"/api/v{self.API_VERSION}"


class PGSettings(BaseSettings):
    """Настройки PostgreSQL."""

    PG_DRIVER: str = "postgresql+asyncpg"
    PG_HOST: str = Field(default="localhost")
    PG_PORT: int = Field(default=5432)
    PG_USER: str = Field(default="manager")
    PG_PASSWORD: str = Field(default="")
    DATABASE: str = Field(default="orders_db")
    ECHO: bool = Field(default=False)

    @property
    def uri(self) -> URL:
        """Возвращает DSN соединения для SQLAlchemy."""

        return URL.create(
            self.PG_DRIVER,
            self.PG_USER,
            self.PG_PASSWORD,
            self.PG_HOST,
            self.PG_PORT,
            self.DATABASE,
        )


class RedisSettings(BaseSettings):
    """Настройки редиски"""
    REDIS_HOST: str = Field(default="localhost", title="Хост для `Redis`")
    REDIS_PORT: int = Field(default=6379, title="Порт для `Redis`")


class Settings(BaseSettings):
    """Настройки приложения."""

    model_config = SettingsConfigDict(
        secrets_dir=Path(__file__).parents[2] / "etc/secrets",
        yaml_file=Path(__file__).parents[2] / f"etc/config.{APP_MODE}.yaml",
    )

    APPLICATION: ApplicationSettings = Field(default=ApplicationSettings())
    SECRET_KEY: str = "61d4HpCGOq2JAYO5l_EeVJS7vA6IkGWIdVwj-ja3JfU" # Field(default=secrets.token_urlsafe(32))
    ALGORITHM: str = Field(default="HS256")

    DB: PGSettings = Field(default=PGSettings())
    REDIS: RedisSettings = Field(default=RedisSettings())
    DEBUG: bool = True
    BASE_DIR: Path = Path().absolute()
    TZ_NAME: str = "Europe/Moscow"
    TZ_OFFSET: int = 3
    ALLOW_ORIGINS: List[str] = ["http://orders.local:8000/",]

    @classmethod
    def settings_customise_sources(
        cls, settings_cls, *args, **kwargs
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (YamlConfigSettingsSource(settings_cls),)

    @property
    def TZ(self) -> ZoneInfo:
        """Возвращает таймзону."""

        return ZoneInfo(self.TZ_NAME)


def get_settings() -> Settings:
    """Возвращает настройки приложения."""

    return Settings()
