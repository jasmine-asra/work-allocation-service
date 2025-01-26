class DataManager:
    def __init__(self, doable_manager, allocation_manager):
        self.doable_manager = doable_manager
        self.allocation_manager = allocation_manager

    def save_all(self):
        self.doable_manager.save_doables()
        self.allocation_manager.save_allocations()