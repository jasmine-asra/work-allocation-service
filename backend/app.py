from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
from services.user_manager import UserManager
from services.doable_manager import DoableManager
from services.allocation_manager import AllocationManager
from services.data_manager import DataManager
from models.doable import Doable
from utils import convert_dict_keys_to_camel_case

app = Flask(__name__)

CORS(app)

base_dir = os.path.dirname(os.path.abspath(__file__))
user_data_path = os.path.join(base_dir, "data", "users.json")
doable_data_path = os.path.join(base_dir, "data", "doables.json")
allocation_data_path = os.path.join(base_dir, "data", "allocations.json")

user_manager = UserManager(user_data_path)
doable_manager = DoableManager(doable_data_path)
allocation_manager = AllocationManager(doable_manager, user_manager, allocation_data_path)
data_manager = DataManager(doable_manager, allocation_manager)


@app.route('/api/users')
def get_users():
    """
    Get all users.
    """
    users = user_manager.list_users()

    # Sort users by first name
    sorted_users = sorted(
        [user.to_dict() for user in users],
        key=lambda user: user.get("first_name", "").lower()
    )

    return jsonify(convert_dict_keys_to_camel_case(sorted_users))


@app.route('/api/users/<user_id>/doables')
def get_user_doables(user_id):
    """
    Get all doables assigned to a user.
    """
    user_allocations = allocation_manager.get_allocations_by_user(user_id)
    doable_ids = [allocation.doable_id for allocation in user_allocations]

    user_doables = [doable_manager.get_doable(doable_id) for doable_id in doable_ids]
    incomplete_doables = [doable for doable in user_doables if doable.status != "completed"]
    
    return jsonify(convert_dict_keys_to_camel_case([doable.to_dict() for doable in incomplete_doables]))


@app.route('/api/users/<user_id>/doables', methods=['POST'])
def allocate_doable_to_user(user_id):
    """
    Allocate a doable to a user.
    """
    doable_type = user_manager.get_user(user_id).preferred_doable_type
    
    allocation = allocation_manager.allocate_by_doable(user_id, doable_type)
    allocated_doable = doable_manager.get_doable(allocation.doable_id)
    data_manager.save_all()
    
    return jsonify(convert_dict_keys_to_camel_case(allocated_doable.to_dict()))


@app.route('/api/users/<user_id>/doables/case', methods=['POST'])
def allocate_case_to_user(user_id):
    """
    Allocate a case to a user.
    """
    doable_type = user_manager.get_user(user_id).preferred_doable_type
    
    allocations = allocation_manager.allocate_by_case(user_id, doable_type)
    allocated_doables = [doable_manager.get_doable(allocation.doable_id) for allocation in allocations]
    data_manager.save_all()
    
    return jsonify(convert_dict_keys_to_camel_case([doable.to_dict() for doable in allocated_doables]))


@app.route('/api/users/<user_id>/doables/case/<case_id>', methods=['POST'])
def allocate_case_to_user_by_id(user_id, case_id):
    """
    Allocate a case to a user by case ID.
    """
    allocations = allocation_manager.allocate_related_doables(user_id, case_id)
    allocated_doables = [doable_manager.get_doable(allocation.doable_id) for allocation in allocations]
    data_manager.save_all()

    return jsonify(convert_dict_keys_to_camel_case([doable.to_dict() for doable in allocated_doables]))


@app.route('/api/allocations')
def get_allocations():
    """
    Get all allocations.
    """
    allocations = allocation_manager.get_allocation_view()

    return jsonify(convert_dict_keys_to_camel_case(allocations))


@app.route('/api/allocations/<doable_id>', methods=['DELETE'])
def delete_allocation(doable_id):
    """
    Delete an allocation.
    """
    allocation_manager.delete_allocation(doable_id)
    data_manager.save_all()

    return jsonify({"message": "Allocation deleted."})


@app.route('/api/allocations/case/<case_id>', methods=['DELETE'])
def delete_case_allocations(case_id):
    """
    Delete all allocations for a case.
    """
    allocation_manager.delete_case_allocations(case_id)
    data_manager.save_all()

    return jsonify({"message": "Case allocations deleted."})


if __name__ == "__main__":
    app.run(debug=True)