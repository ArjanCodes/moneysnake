from typing import Any

import requests

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
    response = requests.request(
        method, fullpath, json=data, headers=headers, timeout=timeout
    )
    if response.status_code >= 400:
        raise requests.exceptions.HTTPError(
            f"Error: {response.status_code} {response.text}"
        )
    if (
        "application/json" not in response.headers.get("Content-Type", "")
        or not response.text
    ):
        raise requests.exceptions.HTTPError(
            f"Error: {response.status_code} {response.text}"
        )
    return response.json()
