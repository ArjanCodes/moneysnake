from typing import Any, Protocol

type JSONDict = dict[str, Any]
type JSONList = list[Any]
type JSON = JSONDict | JSONList

MB_URL: str

class MBClient(Protocol):
    admin_id: str
    token: str
    timeout: int = 20

    def get_custom_field_value(self, obj: JSONDict, field_id: int) -> str | None: ...
    def post_request(
        self, path: str, data: dict[str, Any] | None = None, method: str = "post"
    ) -> JSON: ...

def get_custom_field_value(obj: JSONDict, field_id: int) -> str | None: ...
