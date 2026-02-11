from typing import Optional

import hashlib

from fastapi import Request, Response
from fastapi_cache import FastAPICache

def custom_key_builder(
    func,
    namespace: Optional[str] = "",
    request: Optional[Request] = None,
    response: Optional[Response] = None,
    args: Optional[tuple] = None,
    kwargs: Optional[dict] = None,
):
    """
    Кастомная функция построения ключей, для попытки принудительной 
    инвалидации.
    """
    prefix_data = [
        f"{FastAPICache.get_prefix()}",
        f"{namespace}"
    ]
    if request and request.method and request.url:
        prefix_data += [request.method.lower(), request.url.path]

    prefix = ":" . join(prefix_data) + ":"
    cache_key = (
        prefix
        + hashlib.md5(  # nosec:B303
            f"{func.__module__}:{func.__name__}:{args}:{kwargs}".encode()
        ).hexdigest()
    )
    return cache_key
