from typing import Any, Self, TypeVar

from pydantic import BaseModel, ConfigDict

from .client import http_delete, http_get, http_patch, http_post, paginate

T = TypeVar("T", bound=BaseModel)


def ensure_list_of(model_cls: type[T], value: list) -> list[T]:
    return [
        item if isinstance(item, model_cls) else model_cls(**item) for item in value
    ]


class MoneybirdModel(BaseModel):
    id: int | None = None
    model_config = ConfigDict(extra="ignore")

    _endpoint: str | None = None

    @property
    def endpoint(self) -> str:
        if self._endpoint is not None:
            return self._endpoint
        return "".join(
            [
                "_" + letter.lower() if letter.isupper() else letter
                for letter in self.__class__.__name__
            ]
        ).lstrip("_")

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True)

    def update(self, data: dict[str, Any]) -> None:
        # Use model_validate to ensure field validators run
        validated = self.model_validate({**self.model_dump(), **data})
        # Copy validated field values directly (not via model_dump which converts to dicts)
        for key in self.__class__.model_fields:
            object.__setattr__(self, key, getattr(validated, key))


class Loadable(MoneybirdModel):
    """Mixin that adds read capabilities (load, find_by_id)."""

    def load(self, id: int) -> None:
        data = http_get(f"{self.endpoint}s/{id}")
        self.update(data)

    @classmethod
    def find_by_id(cls: type[Self], id: int) -> Self:
        entity = cls(id=id)
        entity.load(id)
        return entity


class Saveable(MoneybirdModel):
    """Mixin that adds create/update capabilities (save, update_by_id)."""

    def save(self) -> None:
        if self.id is None:
            data = http_post(
                f"{self.endpoint}s",
                data={self.endpoint: self.to_dict()},
            )
            self.update(data)
        else:
            data = http_patch(
                f"{self.endpoint}s/{self.id}",
                data={self.endpoint: self.to_dict()},
            )
            self.update(data)

    @classmethod
    def update_by_id(cls: type[Self], id: int, data: dict[str, Any]) -> Self:
        entity = cls(id=id)
        entity.update(data)
        entity.save()
        return entity


class Deletable(MoneybirdModel):
    """Mixin that adds delete capabilities (delete, delete_by_id)."""

    def delete(self) -> None:
        if not self.id:
            raise ValueError(f"Cannot delete {self.__class__.__name__} without an id")
        http_delete(f"{self.endpoint}s/{self.id}")
        self.id = None

    @classmethod
    def delete_by_id(cls: type[Self], id: int) -> Self:
        entity = cls(id=id)
        entity.delete()
        return entity


class Synchronizable(MoneybirdModel):
    """Mixin that adds synchronization endpoints for efficient bulk data access."""

    @classmethod
    def sync_list(cls: type[Self], filter: str | None = None) -> list[dict[str, Any]]:
        """Get all IDs and versions for this resource.

        Returns a list of dicts with 'id' and 'version' keys, useful for
        checking which records have changed since last sync.
        """
        params: dict[str, str] = {}
        if filter:
            params["filter"] = filter
        return paginate(f"{cls._sync_endpoint()}s/synchronization", params=params or None)

    @classmethod
    def sync_fetch(cls: type[Self], ids: list[int]) -> list[Self]:
        """Fetch full records by IDs (max 100 per request).

        Use sync_list() first to get IDs, then fetch changed records in bulk.
        """
        if len(ids) > 100:
            raise ValueError("sync_fetch supports a maximum of 100 IDs per request")
        data = http_post(
            f"{cls._sync_endpoint()}s/synchronization",
            data={"ids": ids},
        )
        if not isinstance(data, list):
            return []
        return [cls(**item) for item in data]

    @classmethod
    def _sync_endpoint(cls) -> str:
        """Derive the endpoint name for synchronization."""
        instance = cls()
        return instance.endpoint


class CrudModel(Loadable, Saveable, Deletable, MoneybirdModel):
    """Full CRUD model with load, save, and delete capabilities."""
