from typing import Optional

from pydantic import BaseModel


class CustomField(BaseModel):
    id: Optional[int] = None
    value: Optional[str] = None
