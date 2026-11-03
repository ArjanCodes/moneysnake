from typing import Any

from pydantic import BaseModel, Field

from .model import CrudModel


class CustomField(BaseModel):
    id: int | None = None
    value: str | None = None


class CustomFieldModel(CrudModel):
    custom_fields: list[CustomField] = Field(default_factory=list)

    def _write_data(self) -> dict[str, Any]:
        data = super()._write_data()
        if "custom_fields" in data:
            data["custom_fields_attributes"] = data.pop("custom_fields")
        return data

    def get_custom_field(self, field_id: int) -> str | None:
        for field in self.custom_fields:
            if field.id == field_id:
                return field.value
        return None

    def set_custom_field(self, field_id: int, value: str) -> None:
        for field in self.custom_fields:
            if field.id == field_id:
                field.value = value
                return
        self.custom_fields = [*self.custom_fields, CustomField(id=field_id, value=value)]
