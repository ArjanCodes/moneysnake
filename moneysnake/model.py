from dataclasses import dataclass
from typing import Any, Optional, Self
import inspect

from .client import post_request


@dataclass
class MoneybirdModel:
    id: Optional[int] = None

    @property
    def endpoint(self) -> str:
        return "".join(
            [
                "_" + letter.lower() if letter.isupper() else letter
                for letter in self.__class__.__name__
            ]
        ).lstrip("_")

    def to_dict(self, exclude_none: bool = False) -> dict[str, Any]:
        def convert_value(value: Any) -> Any:
            if isinstance(value, MoneybirdModel):
                return value.to_dict()
            return value

        return {
            key: convert_value(value)
            for key, value in self.__dict__.items()
            if not (exclude_none and value is None)
        }

    def load(self, id: int) -> None:
        data = post_request(f"{self.endpoint}s/{id}", method="get")
        self.update(data)

    def save(self) -> None:
        if self.id is None:
            data = post_request(
                f"{self.endpoint}s",
                data={self.endpoint: self.to_dict()},
                method="post",
            )
            # update the current object with the data
            self.update(data)
        else:
            data = post_request(
                f"{self.endpoint}s/{self.id}",
                data={self.endpoint: self.to_dict()},
                method="patch",
            )
            self.update(data)

    def update(self, data: dict[str, Any]) -> None:
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def delete(self) -> None:
        if not self.id:
            raise ValueError("Contact has no id.")
        post_request(f"{self.endpoint}s/{self.id}", method="delete")
        # remove the id from the object
        self.id = None

    @classmethod
    def find_by_id(cls: type[Self], id: int) -> Self:
        entity = cls()
        entity.load(id)
        return entity

    @classmethod
    def update_by_id(cls: type[Self], id: int, data: dict[str, Any]) -> Self:
        entity = cls(id)
        entity.update(data)
        entity.save()
        return entity

    @classmethod
    def delete_by_id(cls: type[Self], id: int) -> Self:
        entity = cls(id)
        entity.delete()
        return entity

    @classmethod
    def from_dict(cls: type[Self], data: dict[str, Any]) -> Self:
        return cls(
            **{k: v for k, v in data.items() if k in inspect.signature(cls).parameters}
        )
