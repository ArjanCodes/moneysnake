from typing import Any

MB_URL: str
MB_VERSION_ID: str

admin_id: str
token: str
timeout: int

def get_custom_field_value(obj: dict[str, Any], field_id: int) -> str | None: ...
def post_request(
    path: str, data: dict[str, Any] | None = None, method: str = "post"
) -> dict[str, Any]: ...
