import pytest
from unittest.mock import patch, MagicMock, mock_open
import json
from models.allocation import Allocation
from models.doable import Doable
from models.user import User
from services.allocation_manager import AllocationManager

@pytest.fixture
def mock_doables_data():
    return [
        {"id": "task_1_case_1", "title": "Test Task 1", "status": "pending", "type": "task", "case_id": "case_1", "created_at": "2025-01-01T00:00:00"},
        {"id": "task_2_case_1", "title": "Test Task 2", "status": "pending", "type": "task", "case_id": "case_1", "created_at": "2025-01-02T00:00:00"}
    ]

@pytest.fixture
def mock_users_data():
    return [
        {"id": "user_1", "user_name": "test_user", "first_name": "Test", "last_name": "User", "preferred_doable_type": "task"}
    ]

@pytest.fixture
def mock_allocations_data():
    return [
        {"doable_id": "task_1_case_1", "user_id": "user_1", "allocated_at": "2025-01-01T01:00:00", "is_case_allocation": False}
    ]

@pytest.fixture
def setup_manager(mock_doables_data, mock_users_data, mock_allocations_data):
    doable_manager = MagicMock()
    user_manager = MagicMock()
    allocation_manager = AllocationManager(doable_manager, user_manager, "mock_file.json")

    doable_manager.get_doable.side_effect = lambda doable_id: Doable.from_dict(next(doable for doable in mock_doables_data if doable["id"] == doable_id))
    user_manager.get_user.side_effect = lambda user_id: User.from_dict(next(user for user in mock_users_data if user["id"] == user_id))

    allocation_manager._load_from_file = MagicMock()
    allocation_manager.allocations = {allocation['doable_id']: Allocation.from_dict(allocation) for allocation in mock_allocations_data}

    return allocation_manager


def test_initialization_and_load_from_file(setup_manager, mock_allocations_data):
    """
    Test if allocations are loaded correctly during initialization.
    """
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_allocations_data))):
        allocation_manager = setup_manager
        allocation_manager._load_from_file()

    assert allocation_manager.allocations
    assert "task_1_case_1" in allocation_manager.allocations
    assert allocation_manager.allocations["task_1_case_1"].user_id == "user_1"


def test_allocate_by_doable(setup_manager):
   """
   Test allocating single oldest doable to user
   """
   user_id = "user_1"
   doable_type = "task"
   mock_doable = Doable.from_dict({
       "id": "task_3",
       "title": "Test Task 3",
       "status": "pending",
       "type": "task",
       "created_at": "2025-01-01T00:00:00"
   })
   
   setup_manager.doable_manager.get_oldest_doable_by_type.return_value = mock_doable
   
   allocation = setup_manager.allocate_by_doable(user_id, doable_type)
   
   assert allocation.doable_id == mock_doable.id
   assert allocation.user_id == user_id
   setup_manager.doable_manager.update_doable.assert_called_with(mock_doable.id, status="allocated")


def test_allocate_by_case(setup_manager):
   """
   Test allocating oldest case to user
   """
   user_id = "user_1"
   doable_type = "task"
   
   mock_case_doables = [
       Doable.from_dict({
           "id": f"task_{i}", 
            "title": f"Test Task {i}",
           "type": "task",
           "status": "pending",
           "case_id": "case_1",
           "created_at": f"2025-01-0{i}T00:00:00"
       }) for i in range(1,4)
   ]
   
   setup_manager.doable_manager.get_doables_grouped_by_case.return_value = {
       "case_1": mock_case_doables
   }
   
   allocations = setup_manager.allocate_by_case(user_id, doable_type)
   
   assert len(allocations) == 3
   for i, allocation in enumerate(allocations):
       assert allocation.doable_id == f"task_{i+1}"
       assert allocation.user_id == user_id
       assert allocation.is_case_allocation


def test_delete_allocation(setup_manager):
    """
    Test deleting a single allocation.
    """
    allocation_id = "task_1_case_1"
    
    setup_manager.delete_allocation(allocation_id)

    assert allocation_id not in setup_manager.allocations
    assert setup_manager.doable_manager.update_doable.called


def test_delete_case_allocations(setup_manager):
    """
    Test deleting all allocations for a case.
    """
    case_id = "case_1"

    allocations_before = len(setup_manager.allocations)
    
    setup_manager.delete_case_allocations(case_id)

    allocations_after = len(setup_manager.allocations)
    assert allocations_after < allocations_before


def test_save_allocations(setup_manager, mock_allocations_data):
    """
    Test saving allocations to a file.
    """
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_allocations_data))):
        setup_manager._load_from_file()

    with patch("builtins.open", mock_open()) as mock_file:
        setup_manager.save_allocations()

        written_data = ''.join(call.args[0] for call in mock_file().write.call_args_list)
        expected_data = json.dumps([allocation.to_dict() for allocation in setup_manager.allocations.values()], indent=4)
        assert written_data == expected_data


def test_get_allocations_by_user(setup_manager):
    """
    Test getting all allocations assigned to a user.
    """
    user_id = "user_1"
    allocations = setup_manager.get_allocations_by_user(user_id)

    assert len(allocations) == 1
    assert allocations[0].user_id == user_id
    assert allocations[0].doable_id == "task_1_case_1"


def test_get_allocation_view(setup_manager):
    """
    Test generating allocation view.
    """
    allocation_view = setup_manager.get_allocation_view()

    assert len(allocation_view) == 1
    assert allocation_view[0]["doable_id"] == "task_1_case_1"
    assert allocation_view[0]["user_name"] == "test_user"