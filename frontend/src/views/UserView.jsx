import {useState, useEffect} from "react";
import api from "../utils/api";
import SearchBar from "../components/SearchBar";
import UserCard from "../components/UserCard";
import './UserView.css';

const UserView = () => {
    const [users, setUsers] = useState([]);
    const [searchQuery, setSearchQuery] = useState("");

    // Fetch users from the API
    function getUsers() {
        api.get("/users").then((response) => {
            setUsers(response.data);
        });
    }

    useEffect(() => {
        getUsers();
    }, []);

    const filteredUsers = users.filter((user) =>
        user.firstName.toLowerCase().includes(searchQuery.toLowerCase()) ||
        user.lastName?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        user.userName.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className="user-view">
            <SearchBar 
                searchQuery={searchQuery} 
                setSearchQuery={setSearchQuery} 
                placeholder="Search users by name or preferred task type..."
            />
            <div className="user-grid">
                {filteredUsers.map((user) => (
                    <UserCard kay={user.id} user={user} />
                ))}
            </div>
        </div>
    );
};

export default UserView;