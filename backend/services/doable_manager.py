from typing import Dict, List, Optional
import json
from models.doable import Doable

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
                    
                    # Update counter based on existing IDs
                    if doable.id.startswith("message_"):
                        number = int(doable.id.split("_")[1])
                        self.message_counter = max(self.message_counter, number)

        except FileNotFoundError:
            print("File not found. Starting with an empty doables list.")  


    def _sort_doables_by_priority_and_age(self, doables: List[Doable]) -> List[Doable]:
        """
        Sort a list of Doables by:
        1. Status ("pending" first, "completed" last),
        2. Priority (high -> medium -> low),
        3. Age (oldest first).
        """
        priority_order = {"high": 0, "medium": 1, "low": 2}

        return sorted(
            doables,
            key=lambda x: (
                0 if x.status == "pending" else 1,
                priority_order.get(x.priority, float("inf")),
                x.created_at,
            ),
        )


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
        Retrieve the oldest Doable by type and priority.
        Prioritises high priority items first, then medium, then low.
        If no type is specified, returns the oldest highest-priority Doable regardless of type.
        """
        filtered_doables = [
            doable for doable in self.doables.values()
            if (type is None or doable.type == type) and doable.status == "pending"
        ]
        
        if not filtered_doables:
            return None
        
        sorted_doables = self._sort_doables_by_priority_and_age(filtered_doables)

        return sorted_doables[0] if sorted_doables else None


    def get_doables_by_case(self, case_id: str) -> List[Doable]:
        """
        Retrieve all Doables for a case, sorted by priority and then by age.
        """
        case_doables = [doable for doable in self.doables.values() if doable.case_id == case_id]
        return self._sort_doables_by_priority_and_age(case_doables)


    def get_doables_grouped_by_case(self) -> Dict[str, List[Doable]]:
        """
        Group Doables by case ID, and sort each group by priority and then by age.
        """
        doables_by_case = {}

        for doable in self.doables.values():
            if doable.case_id is None: # Skip doables with None as case_id
                continue

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