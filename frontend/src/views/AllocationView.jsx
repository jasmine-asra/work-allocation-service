import { useState, useEffect } from "react";
import api from "../utils/api";
import SearchBar from "../components/SearchBar";
import DoableCard from "../components/DoableCard";
import "./AllocationView.css";

const AllocationView = () => {
    const [allocations, setAllocations] = useState([]);
    const [searchQuery, setSearchQuery] = useState("");
    const [viewMode, setViewMode] = useState('single');

    // Fetch allocations from the API
    const getAllocations = async () => {
        api.get("/allocations").then((response) => {
            setAllocations(response.data);
        });
    };

    useEffect(() => {
        getAllocations();
    }, []);

    // Update a doable's status to 'completed'
    const markDoableComplete = (doableId) => {
        api.patch(`/doables/${doableId}`, { status: 'completed' }).then(() => {
            setAllocations(prevAllocations => prevAllocations.map(allocation => {
                if (allocation.doableId === doableId) {
                    return { ...allocation, status: 'completed' };
                }
                return allocation;
            }));
        }).catch((error) => {
            console.error("Error marking doable as complete:", error);
        });
    };

    const unallocateSingle = (doableId) => {
        api.delete(`/allocations/${doableId}`).then(() => {
            setAllocations(prevAllocations => prevAllocations.filter(allocation => allocation.doableId !== doableId));
        }).catch((error) => {
            console.error("Error deleting allocation:", error);
        });
    };

    const unallocateCase = (caseId) => {
        api.delete(`/allocations/case/${caseId}`).then(() => {
            setAllocations(prevAllocations => prevAllocations.filter(allocation => allocation.caseId !== caseId));
        }).catch((error) => {
            console.error("Error deleting case allocation:", error);
        });
    };

    const filteredAllocations = allocations.filter(allocation => 
        allocation.doableTitle.toLowerCase().includes(searchQuery.toLowerCase()) ||
        allocation.doableType.toLowerCase().includes(searchQuery.toLowerCase()) ||
        allocation.status.toLowerCase().includes(searchQuery.toLowerCase())
    );

    // Separate completed and incomplete allocations
    const completedAllocations = filteredAllocations.filter(allocation => allocation.status === 'completed');
    const incompleteAllocations = filteredAllocations.filter(allocation => allocation.status !== 'completed');

    // Group incomplete and completed allocations by case
    const groupByCase = (allocationsList) =>
        allocationsList.reduce((acc, allocation) => {
            const caseId = allocation.caseId || 'Uncategorized';
            if (!acc[caseId]) {
                acc[caseId] = [];
            }
            acc[caseId].push(allocation);
            return acc;
        }, {});

    const incompleteGroupedAllocations = groupByCase(incompleteAllocations);
    const completedGroupedAllocations = groupByCase(completedAllocations);

    const renderAllocations = () => {
        if (viewMode === 'single') {
            return (
                <>
                    <div className="allocation-grid">
                        {incompleteAllocations.map(allocation => (
                            <DoableCard
                                key={allocation.doableId}
                                allocation={allocation}
                                onMarkComplete={() => markDoableComplete(allocation.doableId)}
                                onToggleAllocateSingle={() => unallocateSingle(allocation.doableId)}
                                onToggleAllocateCase={() => unallocateCase(allocation.caseId)}
                            />
                        ))}
                    </div>
                    {completedAllocations.length > 0 && (
                        <div className="completed-section">
                            <h2>Completed Allocations</h2>
                            <div className="allocation-grid">
                                {completedAllocations.map(allocation => (
                                    <DoableCard
                                        key={allocation.doableId}
                                        allocation={allocation}
                                    />
                                ))}
                            </div>
                        </div>
                    )}
                </>
            );
        }

        return (
            <>
                <div className="case-view">
                    {Object.entries(incompleteGroupedAllocations).map(([caseId, caseAllocations]) => (
                        <div key={caseId} className="case-section">
                            <h2 className="case-heading">{caseId}</h2>
                            <div className="allocation-grid">
                                {caseAllocations.map(allocation => (
                                    <DoableCard
                                        key={allocation.doableId}
                                        allocation={allocation}
                                        onMarkComplete={() => markDoableComplete(allocation.doableId)}
                                        onToggleAllocateSingle={() => unallocateSingle(allocation.doableId)}
                                        onToggleAllocateCase={() => unallocateCase(allocation.caseId)}
                                    />
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
                {Object.keys(completedGroupedAllocations).length > 0 && (
                    <div className="completed-section">
                        <h2>Completed Cases</h2>
                        {Object.entries(completedGroupedAllocations).map(([caseId, caseAllocations]) => (
                            <div key={caseId} className="case-section">
                                <h2 className="case-heading">{caseId}</h2>
                                <div className="allocation-grid">
                                    {caseAllocations.map(allocation => (
                                        <DoableCard
                                            key={allocation.doableId}
                                            allocation={allocation}
                                        />
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </>
        );
    };

    return (
        <div className="allocation-view">
            <select
                value={viewMode}
                onChange={(e) => setViewMode(e.target.value)}
            >
                <option value="single">Single Allocations</option>
                <option value="case">By Case</option>
            </select>
            <SearchBar
                searchQuery={searchQuery}
                setSearchQuery={setSearchQuery}
                placeholder="Search doables by title or type..."
            />
            {renderAllocations()}
        </div>
    );
};

export default AllocationView;