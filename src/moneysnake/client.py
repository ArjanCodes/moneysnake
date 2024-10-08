from typing import Any

import httpx

MB_URL = "https://moneybird.com/api/"
MB_VERSION_ID = "v2"

# Moneybird settings
admin_id = ""
token = ""
timeout = 20


def get_custom_field_value(obj: dict[str, Any], field_id: int) -> str | None:
    for field in obj["custom_fields"]:
        if field["id"] == str(field_id):
            return field["value"]
    return None


def post_request(
    path: str, data: dict[str, Any] | None = None, method: str = "post"
) -> dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    fullpath = f"{MB_URL}/{MB_VERSION_ID}/{admin_id}/{path}"
    response = httpx.request(
        method, fullpath, json=data, headers=headers, timeout=timeout
    )
    response.raise_for_status()

    return response.json()
