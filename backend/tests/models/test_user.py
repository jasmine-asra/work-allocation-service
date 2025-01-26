import pytest
from models.user import User
from uuid import uuid4

def test_user_auto_generate_id():
    """
    Test that a UUID is automatically generated if no ID is provided.
    """
    user = User(user_name="autouser", first_name="Auto")
    assert user.id is not None
    assert isinstance(user.id, str)
    
    from uuid import UUID
    try:
        UUID(user.id, version=4)
    except ValueError:
        pytest.fail("Generated ID is not a valid UUID.")

def test_user_creation():
    """
    Test creating a User instance with valid data.
    """
    user = User(
        id="123",
        user_name="johndoe",
        first_name="John",
        last_name="Doe",
        preferred_doable_type="task"
    )
    assert user.id == "123"
    assert user.user_name == "johndoe"
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.preferred_doable_type == "task"

def test_user_creation_without_optional_fields():
    """
    Test creating a User instance without optional fields.
    """
    user = User(
        id="456",
        user_name="janedoe",
        first_name="Jane"
    )
    assert user.id == "456"
    assert user.user_name == "janedoe"
    assert user.first_name == "Jane"
    assert user.last_name is None
    assert user.preferred_doable_type is None

def test_user_invalid_preferred_doable_type():
    """
    Test creating a User instance with an invalid preferred doable type.
    """
    with pytest.raises(ValueError, match="Invalid preferred doable type. Must be 'task', 'email' or None."):
        User(
            id="789",
            user_name="invaliduser",
            first_name="Invalid",
            preferred_doable_type="invalid_type"
        )

def test_user_from_dict_valid():
    """
    Test creating a User instance from a valid dictionary.
    """
    user_dict = {
        "user_name": "johndoe",
        "first_name": "John",
        "last_name": "Doe",
        "preferred_doable_type": "task",
        "id": str(uuid4())
    }

    user = User.from_dict(user_dict)
    
    assert user.user_name == "johndoe"
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.preferred_doable_type == "task"
    assert isinstance(user.id, str)
    assert len(user.id) > 0

def test_user_from_dict_missing_last_name():
    """
    Test creating a User instance from a dictionary without the 'last_name' field.
    """
    user_dict = {
        "user_name": "janedoe",
        "first_name": "Jane",
        "preferred_doable_type": "email",
        "id": str(uuid4())
    }

    user = User.from_dict(user_dict)

    assert user.user_name == "janedoe"
    assert user.first_name == "Jane"
    assert user.last_name is None
    assert user.preferred_doable_type == "email"
    assert isinstance(user.id, str)

def test_user_from_dict_missing_id():
    """
    Test creating a User instance from a dictionary without the 'id' field.
    """
    user_dict = {
        "user_name": "alexdoe",
        "first_name": "Alex",
        "preferred_doable_type": "task",
        "last_name": "Doe"
    }

    user = User.from_dict(user_dict)

    assert user.user_name == "alexdoe"
    assert user.first_name == "Alex"
    assert user.last_name == "Doe"
    assert user.preferred_doable_type == "task"
    assert isinstance(user.id, str)
    assert len(user.id) > 0

def test_user_from_dict_invalid_missing_fields():
    """
    Test creating a User instance from a dictionary with missing required fields.
    """
    user_dict = {
        "first_name": "MissingUser"
    }

    with pytest.raises(KeyError):
        User.from_dict(user_dict)

def test_user_from_dict_invalid_preferred_doable_type():
    """
    Test creating a User instance from a dictionary with an invalid preferred doable type.
    """
    user_dict = {
        "user_name": "invaliduser",
        "first_name": "Invalid",
        "last_name": "User",
        "preferred_doable_type": "notavalidtype",
        "id": str(uuid4())
    }

    with pytest.raises(ValueError, match="Invalid preferred doable type. Must be 'task', 'email' or None."):
        User.from_dict(user_dict)

def test_to_dict_method():
    """
    Test the `to_dict` method of the User class.
    """
    user = User(
        id="123",
        user_name="johndoe",
        first_name="John",
        last_name="Doe",
        preferred_doable_type="email"
    )
    user_dict = user.to_dict()
    expected_dict = {
        "id": "123",
        "user_name": "johndoe",
        "first_name": "John",
        "last_name": "Doe",
        "preferred_doable_type": "email",
    }
    assert user_dict == expected_dict

def test_to_dict_method_with_missing_optional_fields():
    """
    Test the `to_dict` method when optional fields are missing.
    """
    user = User(
        id="456",
        user_name="janedoe",
        first_name="Jane"
    )
    user_dict = user.to_dict()
    expected_dict = {
        "id": "456",
        "user_name": "janedoe",
        "first_name": "Jane",
        "last_name": None,
        "preferred_doable_type": None,
    }
    assert user_dict == expected_dict