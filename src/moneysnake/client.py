from typing import Any

import httpx

MB_URL = "https://moneybird.com/api"
MB_VERSION_ID = "v2"

# Moneybird settings
admin_id_ = 0
token_ = ""
timeout_ = 20


def init_mb_client(admin_id: int, token: str, timeout: int = 20) -> None:
    global admin_id_, token_, timeout_
    admin_id_ = admin_id
    token_ = token
    timeout_ = timeout


def post_request(
    path: str, data: dict[str, Any] | None = None, method: str = "post"
) -> dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {token_}",
        "Content-Type": "application/json",
    }
    fullpath = f"{MB_URL}/{MB_VERSION_ID}/{admin_id_}/{path}"
    response = httpx.request(
        method, fullpath, json=data, headers=headers, timeout=timeout_
    )
    response.raise_for_status()

    return response.json()
