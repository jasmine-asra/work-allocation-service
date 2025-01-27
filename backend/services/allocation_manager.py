from typing import List, Dict
from models.allocation import Allocation
import json

class AllocationManager:
    def __init__(self, doable_manager, user_manager, file_path: str):
        self.doable_manager = doable_manager
        self.user_manager = user_manager
        self.file_path = file_path
        self.allocations: Dict[str, Allocation] = {}
        self._load_from_file()


    def _load_from_file(self):
        """
        Load Allocations from JSON file.
        """
        try:
            with open(self.file_path, "r") as f:
                allocations_data = json.load(f)
                for allocation_data in allocations_data:
                    allocation = Allocation.from_dict(allocation_data)
                    self.allocations[allocation.doable_id] = allocation
        except FileNotFoundError:
            print("File not found. Starting with an empty allocations list.")


    def _create_allocation(self, doable, user_id, is_case_allocation=False):
        """
        Create an allocation for a doable in a case.
        """
        allocation = Allocation(
            doable_id=doable.id,
            user_id=user_id,
            is_case_allocation=is_case_allocation
        )
        self.allocations[allocation.doable_id] = allocation 
        self.doable_manager.update_doable(doable.id, status="allocated")
        return allocation
    

    def _sort_allocations_by_priority_and_age(self, allocations: List[Dict]) -> List[Dict]:
        """
        Sort a list of Allocations by priority and age.
        """
        priority_order = {"high": 0, "medium": 1, "low": 2}

        return sorted(
            allocations,
            key=lambda a: (
                priority_order.get(a["priority"], float("inf")),
                a["created_at"],
            ),
        )


    def get_allocation_view(self) -> List[dict]:
        """
        Generate a list of all allocations.
        """
        allocation_list = []
        for allocation in self.allocations.values():
            doable = self.doable_manager.get_doable(allocation.doable_id)
            user = self.user_manager.get_user(allocation.user_id)
            if doable and user:
                allocation_list.append({
                    "doable_id": doable.id,
                    "doable_title": doable.title,
                    "doable_type": doable.type,
                    "case_id": doable.case_id,
                    "created_at": doable.created_at,
                    "user_name": user.user_name,
                    "user_first_name": user.first_name,
                    "user_last_name": user.last_name,
                    "user_preferred_type": user.preferred_doable_type,
                    "allocated_at": allocation.allocated_at,
                    "is_case_allocation": allocation.is_case_allocation,
                    "priority": doable.priority,
                    "status": doable.status
                })
        return self._sort_allocations_by_priority_and_age(allocation_list)
    

    def get_allocations_by_user(self, user_id: str) -> List[Allocation]:
        """
        Get all allocations assigned to a user.
        """
        return [allocation for allocation in self.allocations.values() if allocation.user_id == user_id]


    def allocate_by_doable(self, user_id: str, doable_type: str = None):
        """
        Assign the oldest unallocated Doable matching the user preferences to a user.
        If no type is specified, assign the oldest Doable regardless of type.
        Update the status of the doable to 'allocated'.
        """
        oldest_doable = self.doable_manager.get_oldest_doable_by_type(doable_type)

        if not oldest_doable:
            return None
        
        return self._create_allocation(oldest_doable, user_id)


    def allocate_by_case(self, user_id: str, doable_type: str = None) -> List[Allocation]:
        """
        Allocate the oldest case with no allocated doables.
        If no type is specified, allocate the oldest case regardless of type.
        """
        grouped_doables = self.doable_manager.get_doables_grouped_by_case()
        
        # Try to find case matching type preference
        for doables in grouped_doables.values():
            if not all(doable.status == "pending" for doable in doables):
                continue
            if doable_type and any(doable.type == doable_type for doable in doables):
                return [self._create_allocation(d, user_id, is_case_allocation=True) for d in doables]

        # If no matching case found, get case with oldest doable
        oldest_case = min(
            (doables for doables in grouped_doables.values() 
                if all(d.status == "pending" for d in doables)),
            key=lambda doables: min(d.created_at for d in doables),
            default=[]
        )
        
        return [self._create_case_allocation(d, user_id) for d in oldest_case]
        

    def allocate_related_doables(self, user_id: str, case_id: str) -> List[Allocation]:
        """
        Allocate all doables in a case to a user.
        """
        case_doables = self.doable_manager.get_doables_by_case(case_id)
        
        new_allocations = []
        for doable in case_doables:
            if doable.status == "pending":
                allocation = Allocation(   # is_case_allocation=False because full case might not be allocated
                    doable_id=doable.id,   # if some doables are already allocated
                    user_id=user_id
                )  
                self.allocations[allocation.doable_id] = allocation 
                new_allocations.append(allocation)
                self.doable_manager.update_doable(doable.id, status="allocated")

        return new_allocations
    

    def delete_allocation(self, doable_id: str):
        """
        Delete an allocation by its doable_id.
        """
        allocation = self.allocations.get(doable_id)
        if allocation:
            del self.allocations[doable_id]
            self.doable_manager.update_doable(doable_id, status="pending")
        else:
            raise ValueError(f"No allocation found for doable with ID {doable_id}.")


    def delete_case_allocations(self, case_id: str):
        """
        Delete all allocations for a case.
        """
        doables_to_delete = self.doable_manager.get_doables_by_case(case_id)
        deleted_count = 0
        for doable in doables_to_delete:
            if doable.id in self.allocations and doable.status == "allocated":
                del self.allocations[doable.id]
                self.doable_manager.update_doable(doable.id, status="pending")
                deleted_count += 1
            else:
                raise ValueError(f"No allocation found for doable with ID {doable.id}.")
        
        return deleted_count
    
    
    def save_allocations(self):
        """
        Save all allocations to the JSON file.
        """
        with open(self.file_path, "w") as file:
            json.dump([allocation.to_dict() for allocation in self.allocations.values()], file, indent=4)