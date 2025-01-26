from typing import Dict, List, Optional
import json
from models.doable import Doable
from utils import sort_object_list_by_key

class DoableManager:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.doables: Dict[str, Doable] = {}
        self.message_counter = 0
        self._load_from_file()


    def _load_from_file(self):
        """
        Load Doables from JSON file and populate the manager.
        """
        try:
            with open(self.file_path, "r") as f:
                doables_data = json.load(f)
                for doable_data in doables_data:
                    doable = Doable.from_dict(doable_data)
                    self.doables[doable.id] = doable
                    
                    # Update counters based on existing IDs
                    if doable.id.startswith("message_"):
                        number = int(doable.id.split("_")[1])
                        self.message_counter = max(self.message_counter, number)

        except FileNotFoundError:
            print("File not found. Starting with an empty doables list.")  


    def generate_id(self, title: str, type: str, case_id: Optional[str]=None) -> str:
        """
        Generate a unique ID.
        """
        if type == "email":
            self.message_counter += 1 # increment number of messages in the system
            return f"message_{self.message_counter}"
        
        elif type == "task": 
            # Append case number to title
            if case_id:
                case_num = case_id.split("_")[-1]
                if title.lower() == "set up the case":
                    return f"case_setup_{case_num}"
                else:
                    base_id = title.replace(" ", "_").lower()
                    return f"{base_id}_{case_num}"
            else:
                raise ValueError("Case ID is required for task type.")
        
        else:
            raise ValueError("Invalid type. Must be 'task' or 'email'.")


    def add_doable_instance(self, doable: Doable):
        """
        Add a new Doable to the manager.
        """
        if doable.id in self.doables:
            raise ValueError(f"Doable with ID {doable.id} already exists.")
        self.doables[doable.id] = doable


    def get_doable(self, doable_id: str) -> Optional[Doable]:
        """
        Retrieve a Doable by its ID.
        """
        return self.doables.get(doable_id)


    def get_oldest_doable_by_type(self, type: Optional[str] = None) -> Optional[Doable]:
        """
        Retrieve the oldest Doable by type.
        If no type is specified, returns the oldest Doable regardless of type.
        """
        sorted_doables = sort_object_list_by_key(self.doables.values(), "created_at")
        for doable in sorted_doables: # get first matching doable as it is the oldest
            if type is None or doable.type == type:
                return doable
        
        return None  


    def get_doables_by_case(self, case_id: str) -> List[Doable]:
        """
        Retrieve all Doables for a case.
        """
        case_doables = [doable for doable in self.doables.values() if doable.case_id == case_id]
        return sort_object_list_by_key(case_doables, "created_at")


    def get_doables_grouped_by_case(self) -> Dict[str, List[Doable]]:
        """
        Group Doables by case ID.
        """
        doables_by_case = {}
        for doable in self.doables.values():
            if doable.case_id not in doables_by_case:
                doables_by_case[doable.case_id] = []
            doables_by_case[doable.case_id].append(doable)
        
        return doables_by_case
    

    def update_doable(self, doable_id: str, **kwargs):
        """
        Update an existing Doable's attributes.
        """
        doable = self.get_doable(doable_id)
        if not doable:
            raise ValueError(f"No Doable found with ID {doable_id}.")
        for key, value in kwargs.items():
            if hasattr(doable, key):
                setattr(doable, key, value)
            else:
                raise KeyError(f"Invalid attribute '{key}' for Doable.")
        
        doable.__post_init__()


    def save_doables(self):
        """
        Save all Doables to a JSON file.
        """
        with open(self.file_path, "w") as file:
            json.dump([doable.to_dict() for doable in self.doables.values()], file, indent=4)