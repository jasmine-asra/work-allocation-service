import json
from models.user import User
from typing import List

class UserManager:
    def __init__(self, file_path: str):
        """
        Manages user creation, retrieval, and storage.

        :param file_path: Path to the JSON file containing user data.
        """
        self.file_path = file_path
        self.users = {}
        self._load_users_from_file()

    def _load_users_from_file(self):
        """
        Load users from JSON file into memory.
        """
        try:
            with open(self.file_path, "r") as file:
                data = json.load(file)
                for user_data in data:
                    user = User.from_dict(user_data)
                    self.users[user.id] = user
        except FileNotFoundError:
            print("User data file not found. Created empty user list.")
        except json.JSONDecodeError:
            print("Invalid JSON format in user data file.")

    def get_user(self, user_id: str) -> User:
        """
        Retrieve a user by their ID.
        """
        return self.users.get(user_id)        

    def list_users(self) -> List[User]:
        """
        List all users in the system.
        """
        return list(self.users.values())