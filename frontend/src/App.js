import {useState} from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import './App.css';
import { FaTasks } from "react-icons/fa";
import NewDoableModal from './components/NewDoableModal';
import UserView from './views/UserView';
import AllocationView from './views/AllocationView';


function App() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleOpenModal = () => {
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  return (
    <Router>
      <div>
        <div className="header">
          <h1 className="header-title">
            <FaTasks className="header-icon" /> Work Allocation Service
          </h1>
          <div className="header-right">
            <button 
              className="add-doable-button"
              onClick={handleOpenModal}
            >+ Add Doable</button>
            <a href='/'>Users</a>
            <a href='/allocations'>Allocations</a>
          </div>
        </div>

        <NewDoableModal 
          isOpen={isModalOpen} 
          onClose={handleCloseModal}
        />

        <Routes>
          <Route path="/" element={<UserView />} />
          <Route path="/allocations" element={<AllocationView />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
