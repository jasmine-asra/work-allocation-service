import pytest
from unittest.mock import patch, mock_open
import json
from models.doable import Doable
from services.doable_manager import DoableManager

@pytest.fixture
def setup_manager():
    file_path = "mock_doables.json"
    manager = DoableManager(file_path)
    return manager

@pytest.fixture
def mock_doables_data():
    return [
        {
            "id": "message_1",
            "title": "Test email 1",
            "case_id": "case_1",
            "type": "email",
            "priority": "high",
            "status": "pending",
            "created_at": "2024-01-01T00:00:00",
        },
        {
            "id": "message_2",
            "title": "Test email 2",
            "case_id": "case_1",
            "type": "email",
            "priority": "medium",
            "status": "pending",
            "created_at": "2023-12-31T00:00:00",  # Older but medium priority
        },
        {
            "id": "task_1_case_1",
            "title": "Test Task 1",
            "case_id": "case_1",
            "type": "task",
            "priority": "low",
            "status": "pending",
            "created_at": "2024-01-02T00:00:00",
        },
        {
            "id": "task_2_case_1",
            "title": "Test Task 2",
            "case_id": "case_1",
            "type": "task",
            "priority": "medium",
            "status": "completed",
            "created_at": "2024-01-03T00:00:00",
        },
    ]


def test_load_from_file(setup_manager, mock_doables_data):
    """
    Test loading Doables from a file.
    """
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_doables_data))):
        setup_manager._load_from_file()
        
    assert len(setup_manager.doables) == 4
    assert setup_manager.doables["message_1"].title == "Test email 1"
    assert setup_manager.doables["task_1_case_1"].status == "pending"


def test_generate_id_for_task(setup_manager):
    """
    Test generating an ID for a task.
    """
    task_id = setup_manager.generate_id("Test Task", "task", case_id="case_32")
    assert task_id == "test_task_32"


def test_generate_id_for_email(setup_manager):
    """
    Test generating an ID for an email.
    """
    email_id = setup_manager.generate_id("Test Email", "email")
    assert email_id == "message_1"


def test_add_new_doable(setup_manager, mock_doables_data):
    """
    Test adding a new Doable instance.
    """
    new_doable = Doable.from_dict(mock_doables_data[0])

    setup_manager.add_doable_instance(new_doable)

    assert new_doable.id in setup_manager.doables
    assert setup_manager.doables[new_doable.id].title == "Test email 1"


def test_add_duplicate_doable(setup_manager, mock_doables_data):
    """
    Test adding a duplicate Doable raises an error.
    """
    new_doable = Doable.from_dict(mock_doables_data[0])
    
    setup_manager.add_doable_instance(new_doable)
    
    with pytest.raises(ValueError):
        setup_manager.add_doable_instance(new_doable)


def test_get_doable_existing_id(setup_manager, mock_doables_data):
    """
    Test retrieving a Doable by its ID.
    """
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_doables_data))):
        setup_manager._load_from_file()

    doable = setup_manager.get_doable("task_1_case_1")
    assert doable is not None
    assert doable.title == "Test Task 1"


def test_get_doable_non_existent_id(setup_manager, mock_doables_data):
    """
    Test retrieving a Doable that does not exist.
    """
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_doables_data))):
        setup_manager._load_from_file()
    
    doable = setup_manager.get_doable("non_existent_id")
    assert doable is None


def test_get_oldest_doable_by_type_without_specifying_type(setup_manager, mock_doables_data):
    """
    Test retrieving the oldest Doable without specifying a type.
    """
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_doables_data))):
        setup_manager._load_from_file()
    
    oldest_doable = setup_manager.get_oldest_doable_by_type()

    assert oldest_doable.id == "message_1"


def test_get_oldest_doable_by_type_email(setup_manager, mock_doables_data):
    """
    Test retrieving the oldest Doable with type 'email'.
    """
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_doables_data))):
        setup_manager._load_from_file()
    
    oldest_email = setup_manager.get_oldest_doable_by_type(type="email")
    assert oldest_email.id == "message_1"


def test_get_oldest_doable_by_type_task(setup_manager, mock_doables_data):
    """
    Test retrieving the oldest Doable with a non-existing type, expecting None.
    """
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_doables_data))):
        setup_manager._load_from_file()
    
    oldest_doable = setup_manager.get_oldest_doable_by_type(type="task")
    assert oldest_doable.id == "task_1_case_1"


def test_get_oldest_doable_by_type_respects_priority(setup_manager, mock_doables_data):
    """
    Test retrieving the highest priority doable first, regardless of age.
    """
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_doables_data))):
        setup_manager._load_from_file()
    
    oldest_doable = setup_manager.get_oldest_doable_by_type()
    
    assert oldest_doable.id == "message_1"
    assert oldest_doable.priority == "high"


def test_get_oldest_doable_by_type_same_priority(setup_manager):
    """
    Test that when multiple doables have same priority, the oldest is returned.
    """
    test_data = [
        {
            "id": "task_1",
            "title": "Newer Task",
            "type": "task",
            "priority": "high",
            "status": "pending",
            "created_at": "2024-01-02T00:00:00",
        },
        {
            "id": "task_2",
            "title": "Older Task",
            "type": "task",
            "priority": "high",
            "status": "pending",
            "created_at": "2024-01-01T00:00:00",
        }
    ]
    
    with patch("builtins.open", mock_open(read_data=json.dumps(test_data))):
        setup_manager._load_from_file()
    
    oldest_doable = setup_manager.get_oldest_doable_by_type()
    assert oldest_doable.id == "task_2"


def test_get_oldest_doable_by_type_priority_fallback(setup_manager):
    """
    Test that when no high priority doables exist, falls back to medium, then low.
    """
    test_data = [
        {
            "id": "task_1",
            "title": "Low Priority Old",
            "type": "task",
            "priority": "low",
            "status": "pending",
            "created_at": "2024-01-01T00:00:00",
        },
        {
            "id": "task_2",
            "title": "Medium Priority Newer",
            "type": "task",
            "priority": "medium",
            "status": "pending",
            "created_at": "2024-01-02T00:00:00",
        }
    ]
    
    with patch("builtins.open", mock_open(read_data=json.dumps(test_data))):
        setup_manager._load_from_file()
    
    oldest_doable = setup_manager.get_oldest_doable_by_type()
    assert oldest_doable.id == "task_2" 


def test_get_doables_by_case(setup_manager, mock_doables_data):
    """
    Test getting doables by case ID.
    """
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_doables_data))):
        setup_manager._load_from_file()
    
    case_doables = setup_manager.get_doables_by_case("case_1")

    assert len(case_doables) == 4
    assert [doable.id for doable in case_doables] == [
        "message_1",  # Pending, high priority, oldest
        "message_2",  # Pending, medium priority, oldest
        "task_1_case_1",  # Pending, low priority
        "task_2_case_1",  # Completed, medium priority
    ]


def test_get_doables_grouped_by_case(setup_manager, mock_doables_data):
    """
    Test getting doables grouped by case.
    """
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_doables_data))):
        setup_manager._load_from_file()
    
    doables_by_case = setup_manager.get_doables_grouped_by_case()
    
    assert len(doables_by_case) == 1
    assert "case_1" in doables_by_case
    assert [doable.id for doable in doables_by_case["case_1"]] == [
        "message_1",  # Pending, high priority, oldest
        "message_2",  # Pending, medium priority, oldest
        "task_1_case_1",  # Pending, low priority
        "task_2_case_1",  # Completed, medium priority
    ]


def test_update_doable(setup_manager, mock_doables_data):
    """
    Test updating a doable.
    """
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_doables_data))):
        setup_manager._load_from_file()

    setup_manager.update_doable("task_1_case_1", title="Updated Task Title")
    updated_doable = setup_manager.get_doable("task_1_case_1")
    
    assert updated_doable.title == "Updated Task Title"


def test_update_doable_non_existent(setup_manager, mock_doables_data):
    """
    Test updating a doable that does not exist raises an error.
    """
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_doables_data))):
        setup_manager._load_from_file()

    with pytest.raises(ValueError):
        setup_manager.update_doable("non_existent_id", title="New Title")


def test_save_doables(setup_manager, mock_doables_data):
    """
    Test saving doables to a file.
    """
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_doables_data))):
        setup_manager._load_from_file()

    with patch("builtins.open", mock_open()) as mock_file:
        setup_manager.save_doables()
 
        written_data = ''.join(call.args[0] for call in mock_file().write.call_args_list)
        expected_data = json.dumps([doable.to_dict() for doable in setup_manager.doables.values()], indent=4)
        assert written_data == expected_data