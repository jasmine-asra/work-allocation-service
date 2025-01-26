import pytest
import json
from unittest.mock import patch, mock_open
from services.user_manager import UserManager

@pytest.fixture
def mock_user_data():
    return [
        {
            "id": "1",
            "user_name": "jdoe",
            "first_name": "John",
            "last_name": "Doe",
            "preferred_doable_type": "task"
        },
        {
            "id": "2",
            "user_name": "asmith",
            "first_name": "Alice",
            "last_name": "Smith",
            "preferred_doable_type": "email"
        }
    ]

@pytest.fixture
def mock_user_manager(mock_user_data):
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_user_data))):
        user_manager = UserManager("mock_file_path.json")
    return user_manager


def test_load_users_from_file(mock_user_manager, mock_user_data):
    """Test that the users are correctly loaded from the JSON file"""
    assert len(mock_user_manager.users) == 2
    assert mock_user_manager.users["1"].user_name == "jdoe"
    assert mock_user_manager.users["2"].user_name == "asmith"


def test_get_user(mock_user_manager):
    """Test that a user can be retrieved by their ID"""
    user = mock_user_manager.get_user("1")
    assert user is not None
    assert user.user_name == "jdoe"


def test_get_user_not_found(mock_user_manager):
    """Test that None is returned if the user ID is not found"""
    user = mock_user_manager.get_user("nonexistent_id")
    assert user is None


def test_list_users(mock_user_manager):
    """Test that all users can be listed"""
    users = mock_user_manager.list_users()
    assert len(users) == 2
    assert users[0].user_name == "jdoe"
    assert users[1].user_name == "asmith"


def test_load_users_from_invalid_json():
    """Test handling of invalid JSON format in user data file"""
    with patch("builtins.open", mock_open(read_data="invalid json")):
        user_manager = UserManager("mock_invalid_file_path.json")
    
    assert len(user_manager.users) == 0


def test_load_users_from_nonexistent_file():
    """Test handling of missing user data file"""
    with patch("builtins.open", side_effect=FileNotFoundError):
        user_manager = UserManager("mock_missing_file_path.json")
    
    assert len(user_manager.users) == 0
