import pytest
from datetime import datetime
from models.allocation import Allocation

def test_allocation_creation():
    """
    Test creating an Allocation instance with valid parameters.
    """
    allocation = Allocation(
        doable_id="123",
        user_id="456",
        allocated_at=datetime(2025, 1, 26, 10, 0, 0),
        is_case_allocation=True
    )
    
    assert allocation.doable_id == "123"
    assert allocation.user_id == "456"
    assert allocation.allocated_at == datetime(2025, 1, 26, 10, 0, 0)
    assert allocation.is_case_allocation is True


def test_allocation_creation_default_values():
    """
    Test creating an Allocation with default values.
    """
    allocation = Allocation(
        doable_id="123",
        user_id="456"
    )

    assert allocation.doable_id == "123"
    assert allocation.user_id == "456"
    assert isinstance(allocation.allocated_at, datetime)
    assert allocation.is_case_allocation is False


def test_allocation_missing_doable_id():
    """
    Test if ValueError is raised when no doable_id is provided.
    """
    with pytest.raises(ValueError, match="Doable ID must be provided."):
        Allocation(
            doable_id=None,
            user_id="456"
        )


def test_allocation_missing_user_id():
    """
    Test if ValueError is raised when no user_id is provided.
    """
    with pytest.raises(ValueError, match="User ID must be provided."):
        Allocation(
            doable_id="123",
            user_id=None
        )


def test_allocation_from_dict():
    """
    Test creating an Allocation instance from a dictionary.
    """
    data = {
        "doable_id": "123",
        "user_id": "456",
        "allocated_at": "2025-01-26T10:00:00",
        "is_case_allocation": True
    }

    allocation = Allocation.from_dict(data)
    
    assert allocation.doable_id == "123"
    assert allocation.user_id == "456"
    assert allocation.allocated_at == datetime(2025, 1, 26, 10, 0, 0)
    assert allocation.is_case_allocation is True


def test_allocation_to_dict():
    """
    Test converting an Allocation instance to a dictionary.
    """
    allocation = Allocation(
        doable_id="123",
        user_id="456",
        allocated_at=datetime(2025, 1, 26, 10, 0, 0),
        is_case_allocation=True
    )

    data = allocation.to_dict()

    assert data["doable_id"] == "123"
    assert data["user_id"] == "456"
    assert data["allocated_at"] == "2025-01-26T10:00:00"
    assert data["is_case_allocation"] is True


def test_allocation_from_dict_missing_field():
    """
    Test if missing fields in dictionary raise an error.
    """
    data = {
        "doable_id": "123",
        "user_id": "456",
        "allocated_at": "2025-01-26T10:00:00"
    }

    allocation = Allocation.from_dict(data)
    
    assert allocation.is_case_allocation is False


def test_allocation_invalid_status_in_dict():
    """
    Test if invalid status in the dictionary raises a ValueError.
    """
    data = {
        "doable_id": "123",
        "user_id": "456",
        "allocated_at": "2025-01-26T10:00:00",
        "is_case_allocation": "not_valid"
    }
    
    with pytest.raises(ValueError, match="is_case_allocation must be a boolean value."):
        Allocation.from_dict(data)
