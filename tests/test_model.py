from pytest_mock import MockType
from pydantic import field_validator
from typing import Any
from moneysnake.model import MoneybirdModel


class NestedModel(MoneybirdModel):
    """A simple nested model for testing."""

    name: str | None = None


class ModelWithValidator(MoneybirdModel):
    """A model with a field validator for testing update validation."""

    items: list[NestedModel] | None = None

    @field_validator("items")
    def ensure_items(
        cls, value: list[dict[str, Any]] | None
    ) -> list[NestedModel] | None:
        if value is None:
            return None
        return [
            item if isinstance(item, NestedModel) else NestedModel(**item)
            for item in value
        ]


def test_update_runs_field_validators():
    """
    Test that the update method runs field validators, converting dicts to model instances.
    """
    model = ModelWithValidator()
    # Simulate API response with raw dicts
    model.update({"items": [{"id": 1, "name": "test"}, {"id": 2, "name": "test2"}]})

    assert model.items is not None
    assert len(model.items) == 2
    assert all(isinstance(item, NestedModel) for item in model.items)
    assert model.items[0].id == 1
    assert model.items[0].name == "test"


def test_update_preserves_existing_model_instances():
    """
    Test that the update method preserves existing model instances when updating.
    """
    model = ModelWithValidator(items=[NestedModel(id=1, name="existing")])
    # Update with new items as dicts
    model.update({"items": [{"id": 2, "name": "new"}]})

    assert model.items is not None
    assert len(model.items) == 1
    assert isinstance(model.items[0], NestedModel)
    assert model.items[0].id == 2
    assert model.items[0].name == "new"


def test_update_with_none_value():
    """
    Test that the update method handles None values correctly.
    """
    model = ModelWithValidator(items=[NestedModel(id=1, name="test")])
    model.update({"items": None})

    assert model.items is None


def test_load(mocker: MockType):
    """
    Test that the load method fetches the data from the API and updates the model.
    """
    mocker.patch("moneysnake.model.http_get", return_value={"id": 1})
    model = MoneybirdModel()
    model.load(1)
    assert model.id == 1


def test_save_create(mocker: MockType):
    """
    Test that the save method creates a new model if the model has no id.
    """
    mocker.patch("moneysnake.model.http_post", return_value={"id": 1})
    model = MoneybirdModel()
    model.save()
    assert model.id == 1


def test_save_update(mocker: MockType):
    """
    Test that the save method updates the model if the model has an id.
    """
    mocker.patch("moneysnake.model.http_post", return_value={"id": 1})
    mocker.patch("moneysnake.model.http_patch", return_value={"id": 1})
    model = MoneybirdModel(id=1)
    model.save()
    assert model.id == 1


def test_delete(mocker: MockType):
    """
    Test that the delete method removes the id from the model.
    """
    mocker.patch("moneysnake.model.http_delete")
    model = MoneybirdModel(id=1)
    model.delete()
    assert model.id is None


def test_to_dict(mocker: MockType):
    """
    Test that the to_dict method returns a dictionary representation of the model.
    """
    mocker.patch("moneysnake.model.http_post")
    model = MoneybirdModel(id=1)
    assert model.to_dict() == {"id": 1}


def test_from_dict(mocker: MockType):
    """
    Test that the from_dict method creates a model from a dictionary.
    """
    mocker.patch("moneysnake.model.http_post")
    data = {"id": 1}
    model = MoneybirdModel(**data)
    assert model.id == 1


def test_find_by_id(mocker: MockType):
    """
    Test that the find_by_id method fetches the data from the API and returns a model.
    """
    mocker.patch("moneysnake.model.http_get", return_value={"id": 1})
    model = MoneybirdModel.find_by_id(1)
    assert model.id == 1


def test_update_by_id(mocker: MockType):
    """
    Test that the update_by_id method fetches the data from the API and updates the model.
    """
    mocker.patch("moneysnake.model.http_patch", return_value={"id": 1})
    model = MoneybirdModel.update_by_id(1, {"id": 1})
    assert model.id == 1


def test_delete_by_id(mocker: MockType):
    """
    Test that the delete_by_id method returns a model with no id.
    """
    mocker.patch("moneysnake.model.http_delete")
    model = MoneybirdModel.delete_by_id(1)
    assert model.id is None
