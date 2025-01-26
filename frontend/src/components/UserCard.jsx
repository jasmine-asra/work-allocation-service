import { useState } from "react";
import { FaChevronDown, FaChevronUp } from "react-icons/fa";
import api from "../utils/api";
import "./UserCard.css";

const UserCard = ({ user }) => {
    const [isExpanded, setIsExpanded] = useState(false);
    const [doables, setDoables] = useState([]);

    const toggleExpand = () => {
        if (!isExpanded) {
            api.get(`/users/${user.id}/doables`).then((response) => {
                setDoables(response.data); // Update doables list when expanded
            });
        }
        setIsExpanded(!isExpanded);
    };

    const handleAllocateDoable = () => {
        api.post(`/users/${user.id}/doables`).then((response) => {
            // Update the doables with the new allocated doable
            setDoables((prevDoables) => [...prevDoables, response.data]);
        });
    };

    const handleAllocateCase = () => {
        api.post(`/users/${user.id}/doables/case`).then((response) => {
            setDoables((prevDoables) => [...prevDoables, response.data]);
        });
    }

    const handleRelatedDoables = (caseId) => {
        api.post(`/users/${user.id}/doables/case/${caseId}`).then((response) => {
            setDoables((prevDoables) => [...prevDoables, ...response.data]);
        });
    }

    return (
        <div className="user-card">
            <div className="user-card-header">
                <h3 className="user-card-name">
                    {user.firstName} {user.lastName || ""}
                </h3>
                {user.preferredDoableType && (
                    <p className="user-card-preferred">
                        Prefers: {user.preferredDoableType}s
                    </p>
                )}
            </div>
            <div className="user-card-toggle" onClick={toggleExpand}>
                {isExpanded ? <FaChevronUp /> : <FaChevronDown />}
            </div>

            <div className="user-card-buttons">
                <button 
                    className="doable-button"
                    onClick={handleAllocateDoable}
                >Allocate Doable</button>
                <button 
                    className="case-button"
                    onClick={handleAllocateCase}
                >Allocate Case</button>
            </div>

            <div className={`user-card-content ${isExpanded ? "expanded" : ""}`}>
                {isExpanded && (
                    <ul className="doable-list">
                        {doables.map((doable) => (
                            <div className="doable-item-container">
                                <li key={doable.id} className="doable-item">
                                    <div className="doable-title">{doable.title}</div>
                                    <div className="doable-case-id">{doable.caseId}</div>
                                </li>
                                <button 
                                    className="related-doables-button"
                                    onClick={() => handleRelatedDoables(doable.caseId)}
                                >+ related doables</button>
                            </div>
                        ))}
                    </ul>
                )}
            </div>

        </div>
    );
};

export default UserCard;


