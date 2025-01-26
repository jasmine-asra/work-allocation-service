import React, { useState } from 'react';
import api from '../utils/api';

const NewDoableModal = ({ isOpen, onClose }) => {
    const [doableTitle, setDoableTitle] = useState('');
    const [doableType, setDoableType] = useState('');
    const [caseId, setCaseId] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        try {
            const newDoable = {
                doableTitle,
                doableType,
                ...(caseId && { caseId }) // Only include caseId if it's not empty
            };

            await api.post('/doables', newDoable);
            
            setDoableTitle('');
            setDoableType('');
            setCaseId('');
            
            onClose();
        } catch (error) {
            console.error('Error creating doable:', error);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="modal-overlay">
            <div className="modal-content">
                <h2>Create New Doable</h2>
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>Doable Title</label>
                        <input
                            type="text"
                            value={doableTitle}
                            onChange={(e) => setDoableTitle(e.target.value)}
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label>Doable Type</label>
                        <select
                            value={doableType}
                            onChange={(e) => setDoableType(e.target.value)}
                            required
                        >
                            <option value="">Select Type</option>
                            <option value="email">Email</option>
                            <option value="task">Task</option>
                        </select>
                    </div>
                    <div className="form-group">
                        <label>Case ID (Optional)</label>
                        <input
                            type="text"
                            value={caseId}
                            onChange={(e) => setCaseId(e.target.value)}
                        />
                    </div>
                    <div className="modal-actions">
                        <button type="button" onClick={onClose}>Cancel</button>
                        <button type="submit">Create Doable</button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default NewDoableModal;