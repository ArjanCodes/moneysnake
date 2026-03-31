import logging
from typing import Any

import httpx

from .exceptions import (
    MoneybirdAPIError,
    MoneybirdNotFoundError,
    MoneybirdRateLimitError,
    MoneybirdValidationError,
)

logger = logging.getLogger("moneysnake")

MB_URL = "https://moneybird.com/api"
MB_VERSION_ID = "v2"

# Moneybird settings
admin_id_ = 0
token_ = ""
timeout_ = 20


def set_admin_id(admin_id: int) -> None:
    global admin_id_
    admin_id_ = admin_id


def set_token(token: str) -> None:
    global token_
    token_ = token


def set_timeout(timeout: int) -> None:
    global timeout_
    timeout_ = timeout


def make_request(
    path: str,
    data: dict[str, Any] | None = None,
    method: str = "post",
    params: dict[str, Any] | None = None,
) -> Any:
    headers = {
        "Authorization": f"Bearer {token_}",
        "Content-Type": "application/json",
    }
    fullpath = f"{MB_URL}/{MB_VERSION_ID}/{admin_id_}/{path}"
    logger.debug("%s %s", method.upper(), fullpath)
    response = httpx.request(
        method,
        fullpath,
        json=data,
        headers=headers,
        timeout=timeout_,
        params=params,
    )

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        body = response.text
        logger.warning(
            "%s %s returned %d: %s",
            method.upper(),
            fullpath,
            response.status_code,
            body,
        )
        error_cls: type[MoneybirdAPIError] = {
            404: MoneybirdNotFoundError,
            422: MoneybirdValidationError,
            429: MoneybirdRateLimitError,
        }.get(response.status_code, MoneybirdAPIError)
        raise error_cls(
            status_code=response.status_code,
            response_body=body,
            method=method,
            path=path,
        ) from exc

    logger.debug("%s %s returned %d", method.upper(), fullpath, response.status_code)

    # return json if there is content
    return response.json() if response.content else {}


def http_get(path: str, params: dict[str, Any] | None = None) -> Any:
    return make_request(path, method="get", params=params)


def http_post(path: str, data: dict[str, Any] | None = None) -> Any:
    return make_request(path, method="post", data=data)


def http_patch(path: str, data: dict[str, Any] | None = None) -> Any:
    return make_request(path, method="patch", data=data)


def http_delete(path: str, data: dict[str, Any] | None = None) -> Any:
    return make_request(path, method="delete", data=data)


def paginate(path: str, params: dict[str, Any] | None = None, per_page: int = 100) -> list[Any]:
    """Fetch all pages from a paginated list endpoint."""
    all_results: list[Any] = []
    page = 1
    params = dict(params) if params else {}
    params["per_page"] = per_page

    while True:
        params["page"] = page
        results = http_get(path, params=params)
        if not isinstance(results, list):
            return [results] if results else []
        all_results.extend(results)
        if len(results) < per_page:
            break
        page += 1

    return all_results
