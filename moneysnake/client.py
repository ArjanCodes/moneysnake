import logging
import math
import time
from typing import Any

import httpx
from httpx import Response

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
max_retries_ = 3


def set_admin_id(admin_id: int) -> None:
    global admin_id_
    admin_id_ = admin_id


def set_token(token: str) -> None:
    global token_
    token_ = token


def set_timeout(timeout: int) -> None:
    global timeout_
    timeout_ = timeout


def set_max_retries(max_retries: int) -> None:
    global max_retries_
    max_retries_ = max_retries


_IDEMPOTENT_METHODS = frozenset({"get", "put", "delete", "head", "options"})


def _is_retryable(status_code: int, method: str) -> bool:
    if status_code == 429:
        return True
    if status_code >= 500 and method.lower() in _IDEMPOTENT_METHODS:
        return True
    return False


# Moneybird sends Retry-After as an absolute Unix epoch timestamp (seconds since
# the epoch), not the RFC 7231 "delay in seconds". We still accept a plain delay
# for robustness: values below this threshold are read as a relative number of
# seconds, values at or above it as an absolute epoch time to wait until.
_EPOCH_THRESHOLD = 1_000_000_000  # 2001-09-09; far beyond any sane retry delay


def _retry_delay(retry_after: str | None, attempt: int) -> int:
    """Whole seconds to wait before the next retry.

    Falls back to exponential backoff when there is no usable Retry-After
    header. A Retry-After given as an absolute epoch timestamp is converted to a
    relative delay (rounded up so we never retry before the reset time); a plain
    delay-in-seconds is used as-is.
    """
    backoff = 2 ** attempt
    if not retry_after:
        return backoff
    try:
        value = int(retry_after)
    except ValueError:
        # e.g. an HTTP-date string; fall back to exponential backoff.
        return backoff
    if value >= _EPOCH_THRESHOLD:
        value = math.ceil(value - time.time())
    return max(value, 1)


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

    last_exc: httpx.HTTPStatusError | None = None
    for attempt in range(max_retries_ + 1):
        logger.debug("%s %s (attempt %d)", method.upper(), fullpath, attempt + 1)
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
            last_exc = exc
            if _is_retryable(response.status_code, method) and attempt < max_retries_:
                delay = _retry_delay(response.headers.get("Retry-After"), attempt)
                logger.warning(
                    "%s %s returned %d, retrying in %ds (attempt %d/%d)",
                    method.upper(),
                    fullpath,
                    response.status_code,
                    delay,
                    attempt + 1,
                    max_retries_ + 1,
                )
                time.sleep(delay)
                continue

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
        return response.json() if response.content else {}

    # All retries exhausted — raise from last exception
    assert last_exc is not None
    body = last_exc.response.text
    status_code = last_exc.response.status_code
    error_cls = {
        404: MoneybirdNotFoundError,
        422: MoneybirdValidationError,
        429: MoneybirdRateLimitError,
    }.get(status_code, MoneybirdAPIError)
    raise error_cls(
        status_code=status_code,
        response_body=body,
        method=method,
        path=path,
    ) from last_exc


def http_get(path: str, params: dict[str, Any] | None = None) -> Any:
    return make_request(path, method="get", params=params)


def http_get_raw(path: str) -> Response:
    """Perform a GET and return the raw httpx Response (for binary downloads)."""
    headers = {
        "Authorization": f"Bearer {token_}",
    }
    fullpath = f"{MB_URL}/{MB_VERSION_ID}/{admin_id_}/{path}"
    logger.debug("GET %s (raw)", fullpath)
    response = httpx.get(fullpath, headers=headers, timeout=timeout_)
    response.raise_for_status()
    return response


def http_post(path: str, data: dict[str, Any] | None = None) -> Any:
    return make_request(path, method="post", data=data)


def http_patch(path: str, data: dict[str, Any] | None = None) -> Any:
    return make_request(path, method="patch", data=data)


def http_delete(path: str, data: dict[str, Any] | None = None) -> Any:
    return make_request(path, method="delete", data=data)


def http_post_file(
    path: str,
    *,
    field: str,
    filename: str,
    content: bytes,
    content_type: str = "application/octet-stream",
) -> Any:
    """POST a multipart/form-data file upload (e.g. document attachments).

    httpx sets the multipart Content-Type (with boundary) itself, so we only
    pass the Authorization header. Uploads aren't retried.
    """
    headers = {"Authorization": f"Bearer {token_}"}
    fullpath = f"{MB_URL}/{MB_VERSION_ID}/{admin_id_}/{path}"
    logger.debug("POST %s (multipart upload)", fullpath)
    response = httpx.post(
        fullpath,
        headers=headers,
        files={field: (filename, content, content_type)},
        timeout=timeout_,
    )
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        body = response.text
        logger.warning("POST %s returned %d: %s", fullpath, response.status_code, body)
        error_cls: type[MoneybirdAPIError] = {
            404: MoneybirdNotFoundError,
            422: MoneybirdValidationError,
            429: MoneybirdRateLimitError,
        }.get(response.status_code, MoneybirdAPIError)
        raise error_cls(
            status_code=response.status_code,
            response_body=body,
            method="post",
            path=path,
        ) from exc
    return response.json() if response.content else {}


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
