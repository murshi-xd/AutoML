import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import EDA from './pages/EDA';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

function App() {
    const [sidebarOpen, setSidebarOpen] = useState(true);

    const handleOutsideClick = (e) => {
        if (window.innerWidth < 768 && sidebarOpen) {
            setSidebarOpen(false);
        }
    };

    return (
        <Router>
            <div className="flex" onClick={handleOutsideClick}>
                <Navbar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />
                <div className={`${sidebarOpen ? 'md:pl-64' : 'pl-0'} flex-1 min-h-screen bg-gray-100 pt-20 p-6 overflow-auto transition-all duration-300`}>
                    <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/upload" element={<Upload />} />
                        <Route path="/eda" element={<EDA />} />
                    </Routes>
                </div>
                <ToastContainer position="top-right" autoClose={3000} hideProgressBar />
            </div>
        </Router>
    );
}

export default App;
