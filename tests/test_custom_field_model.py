import pytest
from moneysnake.custom_field_model import CustomFieldModel, CustomField


@pytest.fixture(name="custom_field_model")
def fixture_custom_field_model():
    """
    Fixture for CustomFieldModel
    """
    return CustomFieldModel()


def test_get_custom_field_existing(custom_field_model):
    """
    Test get_custom_field method with existing custom field
    """
    custom_field_model.custom_fields = [CustomField(id=1, value="test_value")]
    assert custom_field_model.get_custom_field(1) == "test_value"


def test_get_custom_field_non_existing(custom_field_model):
    """
    Test get_custom_field method with non-existing custom field
    """
    custom_field_model.custom_fields = [CustomField(id=1, value="test_value")]
    assert custom_field_model.get_custom_field(2) is None


def test_set_custom_field_existing(custom_field_model):
    """
    Test set_custom_field method with existing custom field
    """
    custom_field_model.custom_fields = [CustomField(id=1, value="test_value")]
    custom_field_model.set_custom_field(1, "new_value")
    assert custom_field_model.get_custom_field(1) == "new_value"


def test_set_custom_field_new(custom_field_model):
    """
    Test set_custom_field method with new custom field
    """
    custom_field_model.set_custom_field(1, "test_value")
    assert custom_field_model.get_custom_field(1) == "test_value"
