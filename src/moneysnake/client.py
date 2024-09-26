from dataclasses import dataclass
from typing import Any

import requests

JSONDict = dict[str, Any]
JSONList = list[Any]
JSON = JSONDict | JSONList

MB_URL = "https://moneybird.com/api/"


@dataclass
class MBClient:
    admin_id: str
    token: str
    timeout: int = 20
    version: str = "v2"

    def get_custom_field_value(self, obj: JSONDict, field_id: int) -> str | None:
        for field in obj["custom_fields"]:
            if field["id"] == str(field_id):
                return field["value"]
        return None

    def post_request(
        self, path: str, data: dict[str, Any] | None = None, method: str = "post"
    ) -> JSON:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        fullpath = f"{MB_URL}/{self.version}/{self.admin_id}/{path}"
        response = requests.request(
            method, fullpath, json=data, headers=headers, timeout=self.timeout
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


def get_custom_field_value(obj: JSONDict, field_id: int) -> str | None:
    for field in obj["custom_fields"]:
        if field["id"] == str(field_id):
            return field["value"]
    return None
