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


_ERROR_CLASSES: dict[int, type[MoneybirdAPIError]] = {
    404: MoneybirdNotFoundError,
    422: MoneybirdValidationError,
    429: MoneybirdRateLimitError,
}


def _send(
    method: str,
    path: str,
    *,
    json: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    files: dict[str, tuple[str, bytes, str]] | None = None,
    headers: dict[str, str] | None = None,
    follow_redirects: bool = False,
) -> Response:
    """Send one request to Moneybird and raise the matching error on failure."""
    fullpath = f"{MB_URL}/{MB_VERSION_ID}/{admin_id_}/{path}"
    logger.debug("%s %s", method.upper(), fullpath)
    response = httpx.request(
        method,
        fullpath,
        json=json,
        params=params,
        files=files,
        headers={"Authorization": f"Bearer {token_}", **(headers or {})},
        timeout=timeout_,
        follow_redirects=follow_redirects,
    )
    if not response.is_error:
        logger.debug("%s %s returned %d", method.upper(), fullpath, response.status_code)
        return response
    logger.warning(
        "%s %s returned %d: %s",
        method.upper(),
        fullpath,
        response.status_code,
        response.text,
    )
    error_cls = _ERROR_CLASSES.get(response.status_code, MoneybirdAPIError)
    raise error_cls(
        status_code=response.status_code,
        response_body=response.text,
        method=method,
        path=path,
        retry_after=response.headers.get("Retry-After"),
    )


def make_request(
    path: str,
    data: dict[str, Any] | None = None,
    method: str = "post",
    params: dict[str, Any] | None = None,
) -> Any:
    attempt = 0
    while True:
        try:
            response = _send(
                method,
                path,
                json=data,
                params=params,
                headers={"Content-Type": "application/json"},
            )
        except MoneybirdAPIError as error:
            if attempt >= max_retries_ or not _is_retryable(error.status_code, method):
                raise
            delay = _retry_delay(error.retry_after, attempt)
            logger.warning(
                "%s %s returned %d, retrying in %ds (attempt %d/%d)",
                method.upper(),
                path,
                error.status_code,
                delay,
                attempt + 1,
                max_retries_ + 1,
            )
            time.sleep(delay)
            attempt += 1
        else:
            return response.json() if response.content else {}


def http_get(path: str, params: dict[str, Any] | None = None) -> Any:
    return make_request(path, method="get", params=params)


def http_get_raw(path: str) -> Response:
    """Perform a GET and return the raw httpx Response (for binary downloads).

    Follows redirects, because download endpoints redirect to a short-lived URL.
    Downloads aren't retried.
    """
    return _send("get", path, follow_redirects=True)


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
    response = _send("post", path, files={field: (filename, content, content_type)})
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
