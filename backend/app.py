from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from http import HTTPStatus
from datetime import datetime
from services.user_manager import UserManager
from services.doable_manager import DoableManager
from services.allocation_manager import AllocationManager
from services.data_manager import DataManager
from models.doable import Doable
from utils import convert_dict_keys_to_camel_case

app = Flask(__name__)

CORS(app)

# Configuration
base_dir = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(base_dir, "data")
user_data_path = os.path.join(DATA_DIR, "users.json")
doable_data_path = os.path.join(DATA_DIR, "doables.json")
allocation_data_path = os.path.join(DATA_DIR, "allocations.json")

os.makedirs(DATA_DIR, exist_ok=True)

# Initialise managers
user_manager = UserManager(user_data_path)
doable_manager = DoableManager(doable_data_path)
allocation_manager = AllocationManager(doable_manager, user_manager, allocation_data_path)
data_manager = DataManager(doable_manager, allocation_manager)

def error_response(message, status_code):
    return jsonify({"error": message}), status_code

@app.errorhandler(404)
def not_found_error(error):
    return error_response("Resource not found", HTTPStatus.NOT_FOUND)

@app.errorhandler(500)
def internal_error(error):
    return error_response("Internal server error", HTTPStatus.INTERNAL_SERVER_ERROR)


@app.route('/api/users')
def get_users():
    """
    Get all users.
    """
    try:
        users = user_manager.list_users()
        sorted_users = sorted(
            [user.to_dict() for user in users],
            key=lambda user: user.get("first_name", "").lower()
        )
        return jsonify(convert_dict_keys_to_camel_case(sorted_users)), HTTPStatus.OK
    except Exception as e:
        return error_response(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)


@app.route('/api/users/<user_id>/doables')
def get_user_doables(user_id):
    """
    Get all doables assigned to a user.
    """
    try:
        user_allocations = allocation_manager.get_allocations_by_user(user_id)
        doable_ids = [allocation.doable_id for allocation in user_allocations]

        user_doables = [doable_manager.get_doable(doable_id) for doable_id in doable_ids]
        incomplete_doables = [doable for doable in user_doables if doable.status != "completed"]
        
        return jsonify(convert_dict_keys_to_camel_case([doable.to_dict() for doable in incomplete_doables])), HTTPStatus.OK
    except Exception as e:
        return error_response(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)


@app.route('/api/users/<user_id>/doables', methods=['POST'])
def allocate_doable_to_user(user_id):
    """
    Allocate a doable to a user.
    """
    try:
        doable_type = user_manager.get_user(user_id).preferred_doable_type
        
        allocation = allocation_manager.allocate_by_doable(user_id, doable_type)
        if allocation is None:
            return jsonify({
                "message": "No available doables to allocate."
            }), HTTPStatus.OK
        
        allocated_doable = doable_manager.get_doable(allocation.doable_id)
        data_manager.save_all()
        
        return jsonify(convert_dict_keys_to_camel_case(allocated_doable.to_dict())), HTTPStatus.OK
    except Exception as e:
        return error_response(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)


@app.route('/api/users/<user_id>/doables/case', methods=['POST'])
def allocate_case_to_user(user_id):
    """
    Allocate a case to a user.
    """
    try: 
        doable_type = user_manager.get_user(user_id).preferred_doable_type
        
        allocations = allocation_manager.allocate_by_case(user_id, doable_type)
        if not allocations:
            return jsonify({
                "message": "No available cases to allocate."
            }), HTTPStatus.OK
        
        allocated_doables = [doable_manager.get_doable(allocation.doable_id) for allocation in allocations]
        data_manager.save_all()
        
        return jsonify(convert_dict_keys_to_camel_case([doable.to_dict() for doable in allocated_doables])), HTTPStatus.OK
    except Exception as e:
        return error_response(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)


@app.route('/api/users/<user_id>/doables/case/<case_id>', methods=['POST'])
def allocate_case_to_user_by_id(user_id, case_id):
    """
    Allocate a case to a user by case ID.
    """
    try:
        allocations = allocation_manager.allocate_related_doables(user_id, case_id)
        if not allocations:
            return jsonify({
                "message": "No available doables to allocate."
            }), HTTPStatus.OK

        allocated_doables = [doable_manager.get_doable(allocation.doable_id) for allocation in allocations]
        data_manager.save_all()

        return jsonify(convert_dict_keys_to_camel_case([doable.to_dict() for doable in allocated_doables])), HTTPStatus.OK
    except Exception as e:
        return error_response(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)
    

@app.route('/api/allocations')
def get_allocations():
    """
    Get all allocations.
    """
    try:
        allocations = allocation_manager.get_allocation_view()
        return jsonify(convert_dict_keys_to_camel_case(allocations)), HTTPStatus.OK
    except Exception as e:
        return error_response(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)


@app.route('/api/allocations/<doable_id>', methods=['DELETE'])
def delete_allocation(doable_id):
    """
    Delete an allocation.
    """
    try:
        allocation_manager.delete_allocation(doable_id)
        data_manager.save_all()
        return jsonify({"message": "Allocation deleted."}), HTTPStatus.OK
    except ValueError as e:
        return error_response(str(e), HTTPStatus.NOT_FOUND)
    except Exception as e:
        return error_response(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)


@app.route('/api/allocations/case/<case_id>', methods=['DELETE'])
def delete_case_allocations(case_id):
    """
    Delete all allocations for a case.
    """
    try:
        allocation_manager.delete_case_allocations(case_id)
        data_manager.save_all()
        return jsonify({"message": "Case allocations deleted."}), HTTPStatus.OK
    except ValueError as e:
        return error_response(str(e), HTTPStatus.NOT_FOUND)
    except Exception as e:
        return error_response(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)


@app.route('/api/doables', methods=['POST'])
def add_doable():
    """
    Add a new doable.
    """
    try:
        data = request.get_json()

        data["id"] = doable_manager.generate_id(data.get("doableTitle"), data.get("doableType"), data.get("caseId"))
        data["created_at"] = datetime.now().isoformat()
    
        new_doable = Doable.from_dict({
            "id": data["id"],
            "title": data["doableTitle"],
            "case_id": data.get("caseId"),
            "type": data["doableType"],
            "priority": data.get("doablePriority"),
            "created_at": data["created_at"],
        })
        doable_manager.add_doable_instance(new_doable)
        doable_manager.save_doables()
        return jsonify({"message": "Doable added."}), HTTPStatus.CREATED
    except ValueError as e:
        return error_response(str(e), HTTPStatus.BAD_REQUEST)
    except Exception as e:
        return error_response(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)


@app.route('/api/doables/<doable_id>', methods=['PATCH'])
def update_doable(doable_id):
    """
    Update a doable.
    """
    try:
        data = request.get_json()
        
        status = data.get("status")
        doable_manager.update_doable(doable_id, status=status)
        doable_manager.save_doables()
        
        return jsonify({"message": "Doable updated."}), HTTPStatus.OK
    except ValueError as e:
        return error_response(str(e), HTTPStatus.BAD_REQUEST)
    except Exception as e:
        return error_response(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)


if __name__ == "__main__":
    app.run(debug=True)