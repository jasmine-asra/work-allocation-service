import React from "react";
import "./DoableCard.css";
import { format } from "date-fns";
import { MdDone } from "react-icons/md";

const DoableCard = ({
  allocation,
  onMarkComplete,
  onToggleAllocateSingle,
  onToggleAllocateCase,
}) => {
  const {
    allocatedAt,
    caseId,
    createdAt,
    doableTitle,
    doableType,
    status,
    priority,
    userFirstName,
    userLastName,
    isCaseAllocation
    } = allocation;

    const formatDate = (date) => {
        return format(new Date(date), "dd MMM yyyy HH:mm");
    };

    return (
        <div className="doable-card">
            <div className="doable-card-header">
                <h2 className="doable-card-title">
                    {doableTitle}
                    {isCaseAllocation && (
                        <span 
                            className="case-allocation-badge" 
                            title="Allocated as part of a case"
                        >
                            Case
                        </span>
                    )}
                </h2>
                {status === "allocated" && (
                    <MdDone 
                        onClick={onMarkComplete} 
                        className="doable-card-complete"
                        title="Mark as Complete"
                    />
                )}
            </div>
            <div className="doable-card-content">
                {caseId && (
                    <div className="doable-card-row">
                        <span className="doable-card-label">Case ID:</span>
                        <span>{caseId}</span>
                    </div>
                )}

                <div className="doable-card-row">
                    <span className="doable-card-label">Type:</span>
                    <span>{doableType}</span>
                </div>

                <div className="doable-card-row">
                    <span className="doable-card-label">Created At:</span>
                    <span>{formatDate(createdAt)}</span>
                </div>

                <div className="doable-card-row">
                    <span className="doable-card-label">Priority:</span>
                    <span>{priority}</span>
                </div>
                
                <div className="doable-card-row">
                    <span className="doable-card-label">Status:</span>
                    <span>{status}</span>
                </div>

                {status === "allocated" && (
                <>
                    <div className="doable-card-row">
                        <span className="doable-card-label">Allocated To:</span>
                        <span>{userFirstName} {userLastName}</span>
                    </div>
                    <div className="doable-card-row">
                        <span className="doable-card-label">Allocated At:</span>
                        <span>{formatDate(allocatedAt)}</span>
                    </div>
                </>
                )}

                <div className="doable-card-actions">
                    {status !== "completed" && (
                        <button 
                            onClick={onToggleAllocateSingle} 
                            className="doable-card-button single-button"
                        >
                            {status === "allocated" ? "Unallocate" : "Allocate"} This Doable
                        </button>
                    )}
     
                    {isCaseAllocation && (
                        <button 
                            onClick={onToggleAllocateCase} 
                            className="doable-card-button case-button"
                        >
                        Unallocate Case
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};

export default DoableCard;