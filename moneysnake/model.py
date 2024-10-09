from dataclasses import dataclass
from typing import Any, Optional, Self

from .client import post_request


def to_endpoint(class_name: str) -> str:
    return "".join(
        ["_" + letter.lower() if letter.isupper() else letter for letter in class_name]
    ).lstrip("_")


@dataclass
class MoneybirdModel:
    id: Optional[int] = None

    def to_dict(self) -> dict[str, Any]:
        return {key: value for key, value in self.__dict__.items() if value is not None}

    def load(self, id: int) -> None:
        endpoint = to_endpoint(self.__class__.__name__)
        data = post_request(f"{endpoint}s/{id}", method="get")
        self.update(data)

    def save(self) -> None:
        endpoint = to_endpoint(self.__class__.__name__)
        if self.id is None:
            data = post_request(
                f"{endpoint}s",
                data={endpoint: self.to_dict()},
                method="post",
            )
            # update the current object with the data
            self.update(data)
        else:
            data = post_request(
                f"{endpoint}s/{self.id}",
                data={endpoint: self.to_dict()},
                method="patch",
            )
            self.update(data)

    def update(self, data: dict[str, Any]) -> None:
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def delete(self) -> None:
        endpoint = to_endpoint(self.__class__.__name__)
        if not self.id:
            raise ValueError("Contact has no id.")
        post_request(f"{endpoint}s/{self.id}", method="delete")
        # remove the id from the object
        self.id = None

    @classmethod
    def find_by_id(cls: type[Self], id: int) -> Self:
        entity = cls()
        entity.load(id)
        return entity

    @classmethod
    def update_by_id(cls: type[Self], id: int, data: dict[str, Any]) -> Self:
        contact = cls.find_by_id(id)
        contact.update(data)
        contact.save()
        return contact

    @classmethod
    def delete_by_id(cls: type[Self], contact_id: int) -> Self:
        contact = cls.find_by_id(contact_id)
        contact.delete()
        return contact

    @classmethod
    def from_dict(cls: type[Self], data: dict[str, Any]) -> Self:
        return cls(**data)
