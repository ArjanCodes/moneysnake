from dataclasses import dataclass
from typing import Any, Optional, Self, Union, get_origin, get_args
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
            raise ValueError(f"Cannot delete {self.__class__.__name__} without an id")
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
    def _get_param_type(cls, param_type: Any) -> Any:
        """
        Resolve the actual type of a parameter, handling Optionals and Unions.
        """
        if param_type is not inspect.Parameter.empty:
            origin = get_origin(param_type)
            args = get_args(param_type)
            if origin is Union and type(None) in args:
                return next(arg for arg in args if arg is not type(None))
        return param_type

    @classmethod
    def _convert_value(cls, value: Any, param_type: Any) -> Any:
        """
        Attempt to convert a value to the given parameter type.
        """
        if value is not None:
            try:
                return param_type(value)
            except (ValueError, TypeError):
                pass
        return value

    @classmethod
    def _filter_params(
        cls, data: dict[str, Any], params: inspect.Signature
    ) -> dict[str, Any]:
        """
        Filter and convert input data based on class parameters.
        """
        filtered_data = {}
        for key, value in data.items():
            if key in params:
                param_type = cls._get_param_type(params[key].annotation)
                filtered_data[key] = cls._convert_value(value, param_type)
        return filtered_data

    @classmethod
    def from_dict(cls: type[Self], data: dict[str, Any]) -> Self:
        """
        Create an instance of the class from a dictionary, performing type conversion.
        """
        params = inspect.signature(cls).parameters
        filtered_data = cls._filter_params(data, params)
        return cls(**{k: v for k, v in filtered_data.items() if k in params})
