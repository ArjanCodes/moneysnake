from dataclasses import dataclass
from typing import Any

JSONDict = dict[str, Any]
JSONList = list[Any]
JSON = JSONDict | JSONList

MB_URL: str

@dataclass
class MBClient:
    admin_id: str
    token: str
    timeout: int = 20

    def get_custom_field_value(self, obj: JSONDict, field_id: int) -> str | None: ...
    def post_request(
        self, path: str, data: dict[str, Any] | None = None, method: str = "post"
    ) -> JSON: ...

def get_custom_field_value(obj: JSONDict, field_id: int) -> str | None: ...
