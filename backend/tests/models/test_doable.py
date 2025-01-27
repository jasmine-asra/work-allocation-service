import pytest
from datetime import datetime
from uuid import uuid4
from models.doable import Doable

def test_doable_from_dict_valid():
    """
    Test that the from_dict method correctly creates a Doable instance from a dictionary.
    """
    data = {
        "id": str(uuid4()),
        "title": "Test Task",
        "case_id": "12345",
        "type": "task",
        "priority": "high",
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }
    
    doable = Doable.from_dict(data)

    assert doable.id == data["id"]
    assert doable.title == data["title"]
    assert doable.case_id == data["case_id"]
    assert doable.type == data["type"]
    assert doable.priority == data["priority"]
    assert doable.status == data["status"]
    assert isinstance(doable.created_at, datetime)

def test_doable_invalid_type():
    """
    Test that providing an invalid 'type' (not 'task' or 'email') raises a ValueError.
    """
    data = {
        "id": str(uuid4()),
        "title": "Test Task",
        "type": "invalid_type",
        "priority": "high",
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }

    with pytest.raises(ValueError, match="Invalid type. Must be 'task' or 'email'."):
        Doable.from_dict(data)

def test_doable_invalid_priority():
    """
    Test that providing an invalid 'priority' (not 'low', 'medium', or 'high') raises a ValueError.
    """
    valid_priorities = {"low", "medium", "high"}
    data = {
        "id": str(uuid4()),
        "title": "Test Task",
        "type": "task",
        "priority": "invalid_priority",
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }

    with pytest.raises(ValueError, match=f"Invalid priority 'invalid_priority'. Must be one of {valid_priorities}."):
        Doable.from_dict(data)

def test_doable_invalid_status():
    """
    Test that providing an invalid 'status' (not 'pending', 'completed', or 'failed') raises a ValueError.
    """
    valid_statuses = {"pending", "allocated", "completed"}
    data = {
        "id": str(uuid4()),
        "title": "Test Task",
        "type": "task",
        "priority": "high",
        "status": "invalid_status",
        "created_at": datetime.now().isoformat(),
    }

    with pytest.raises(ValueError, match=f"Invalid status 'invalid_status'. Must be one of {valid_statuses}."):
        Doable.from_dict(data)

def test_doable_missing_priority():
    """
    Test that if the 'priority' field is missing, it defaults to 'medium'.
    """
    data = {
        "id": str(uuid4()),
        "title": "Test Task",
        "type": "task",
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }

    doable = Doable.from_dict(data)

    assert doable.priority == "medium"

def test_doable_missing_status():
    """
    Test that if the 'status' field is missing, it defaults to 'pending'.
    """
    data = {
        "id": str(uuid4()),
        "title": "Test Task",
        "type": "task",
        "priority": "high",
        "created_at": datetime.now().isoformat(),
    }

    doable = Doable.from_dict(data)

    assert doable.status == "pending"

def test_doable_missing_type():
    """
    Test that if the 'type' field is missing, it defaults to 'task'.
    """
    data = {
        "id": str(uuid4()),
        "title": "Test Task",
        "priority": "high",
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }

    doable = Doable.from_dict(data)

    assert doable.type == "task"

def test_doable_missing_case_id():
    """
    Test that if the 'case_id' field is missing, it defaults to None.
    """
    data = {
        "id": str(uuid4()),
        "title": "Test Task",
        "type": "task",
        "priority": "high",
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }

    doable = Doable.from_dict(data)

    assert doable.case_id is None

def test_doable_created_at_string_conversion():
    """
    Tests that the created_at field is converted to a datetime object when creating a Doable instance.
    """
    data = {
        "id": str(uuid4()),
        "title": "Test Task",
        "type": "task",
        "priority": "high",
        "status": "pending",
        "created_at": "2025-01-26T12:00:00",
    }

    doable = Doable.from_dict(data)

    assert isinstance(doable.created_at, datetime)
    assert doable.created_at == datetime.fromisoformat(data["created_at"])

def test_doable_to_dict():
    """
    Tests that the to_dict method returns a dictionary with the correct fields.
    """
    data = {
        "id": str(uuid4()),
        "title": "Test Task",
        "type": "task",
        "priority": "high",
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }

    doable = Doable.from_dict(data)
    doable_dict = doable.to_dict()

    assert doable_dict["id"] == data["id"]
    assert doable_dict["title"] == data["title"]
    assert doable_dict["type"] == data["type"]
    assert doable_dict["priority"] == data["priority"]
    assert doable_dict["status"] == data["status"]
    assert doable_dict["created_at"] == doable.created_at.isoformat()
    assert doable_dict["case_id"] is None

def test_doable_from_dict_missing_id():
    """
    Test that missing the 'id' field in the input data raises a KeyError.
    """
    data = {
        "title": "Test Task",
        "type": "task",
        "priority": "high",
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }

    with pytest.raises(KeyError):
        Doable.from_dict(data)