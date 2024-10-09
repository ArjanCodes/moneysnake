from typing import Any, Optional, Self

from client import post_request
from pydantic import BaseModel


def to_endpoint(class_name: str) -> str:
    return "".join(
        ["_" + letter.lower() if letter.isupper() else letter for letter in class_name]
    ).lstrip("_")


class MoneybirdModel(BaseModel):
    id: Optional[int] = None

    def save(self) -> None:
        endpoint = to_endpoint(self.__class__.__name__)
        if self.id is None:
            data = post_request(
                f"{endpoint}s",
                data={endpoint: self.model_dump()},
                method="post",
            )
            # update the current object with the data
            self.update(data)
        else:
            data = post_request(
                f"{endpoint}s/{self.id}",
                data={endpoint: self.model_dump()},
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
    def find_by_id(cls, id: int) -> Self:
        endpoint = to_endpoint(cls.__class__.__name__)
        data = post_request(f"{endpoint}s/{id}", method="get")
        return cls.from_dict(data)

    @classmethod
    def update_by_id(cls, id: int, data: dict[str, Any]) -> Self:
        contact = cls.find_by_id(id)
        contact.update(data)
        contact.save()
        return contact

    @classmethod
    def delete_by_id(cls, contact_id: int) -> Self:
        contact = cls.find_by_id(contact_id)
        contact.delete()
        return contact

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(**data)
