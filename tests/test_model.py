from pytest_mock import MockType
from moneysnake.model import MoneybirdModel


def test_load(mocker: MockType):
    """
    Test that the load method fetches the data from the API and updates the model.
    """
    mocker.patch("moneysnake.model.post_request", return_value={"id": 1})
    model = MoneybirdModel()
    model.load(1)
    assert model.id == 1


def test_save_create(mocker: MockType):
    """
    Test that the save method creates a new model if the model has no id.
    """
    mocker.patch("moneysnake.model.post_request", return_value={"id": 1})
    model = MoneybirdModel()
    model.save()
    assert model.id == 1


def test_save_update(mocker: MockType):
    """
    Test that the save method updates the model if the model has an id.
    """
    mocker.patch("moneysnake.model.post_request", return_value={"id": 1})
    model = MoneybirdModel(id=1)
    model.save()
    assert model.id == 1


def test_delete(mocker: MockType):
    """
    Test that the delete method removes the id from the model.
    """
    mocker.patch("moneysnake.model.post_request")
    model = MoneybirdModel(id=1)
    model.delete()
    assert model.id is None


def test_to_dict(mocker: MockType):
    """
    Test that the to_dict method returns a dictionary representation of the model.
    """
    mocker.patch("moneysnake.model.post_request")
    model = MoneybirdModel(id=1)
    assert model.to_dict() == {"id": 1}


def test_from_dict(mocker: MockType):
    """
    Test that the from_dict method creates a model from a dictionary.
    """
    mocker.patch("moneysnake.model.post_request")
    data = {"id": 1}
    model = MoneybirdModel.from_dict(data)
    assert model.id == 1


def test_find_by_id(mocker: MockType):
    """
    Test that the find_by_id method fetches the data from the API and returns a model.
    """
    mocker.patch("moneysnake.model.post_request", return_value={"id": 1})
    model = MoneybirdModel.find_by_id(1)
    assert model.id == 1


def test_update_by_id(mocker: MockType):
    """
    Test that the update_by_id method fetches the data from the API and updates the model.
    """
    mocker.patch("moneysnake.model.post_request", return_value={"id": 1})
    model = MoneybirdModel.update_by_id(1, {"id": 1})
    assert model.id == 1


def test_delete_by_id(mocker: MockType):
    """
    Test that the delete_by_id method returns a model with no id.
    """
    mocker.patch("moneysnake.model.post_request")
    model = MoneybirdModel.delete_by_id(1)
    assert model.id is None
