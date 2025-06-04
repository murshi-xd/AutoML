import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Upload from './pages/upload';
import EDA from './pages/Eda';
import Visuals from './pages/visualise';
import ExperimentRunsComponent from './components/ExperimentRunsComponent';
import RunDetail from './pages/RunDetail';
import RunList from './pages/RunList';
import RunPipelinePage from './pages/RunPipelinePage';
import Login from './pages/Login';
import ProtectedRoute from './components/ProtectedRoute';
import { AuthProvider } from './context/AuthContext';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const AppLayout = () => {
    const location = useLocation();
    const [sidebarOpen, setSidebarOpen] = useState(true);

    const isLoginPage = location.pathname === '/login';

    return (
        <div className="flex" onClick={() => {
            if (window.innerWidth < 768 && sidebarOpen) setSidebarOpen(false);
        }}>
            {/* ✅ Top Navbar should always show */}
            <Navbar sidebarOpen={!isLoginPage && sidebarOpen} setSidebarOpen={setSidebarOpen} />

            {/* ✅ Only push content right when sidebar is open */}
            <div className={`${!isLoginPage && sidebarOpen ? 'md:pl-64' : ''} flex-1 min-h-screen bg-gray-100 pt-20 p-6 transition-all duration-300`}>
                <Routes>
                    <Route path="/login" element={<Login />} />
                    <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
                    <Route path="/upload" element={<ProtectedRoute><Upload /></ProtectedRoute>} />
                    <Route path="/eda" element={<ProtectedRoute><EDA /></ProtectedRoute>} />
                    <Route path="/visuals" element={<ProtectedRoute><Visuals /></ProtectedRoute>} />
                    <Route path="/experiments" element={<ProtectedRoute><ExperimentRunsComponent /></ProtectedRoute>} />
                    <Route path="/runs/:runId" element={<ProtectedRoute><RunDetail /></ProtectedRoute>} />
                    <Route path="/experiments/:experimentId" element={<ProtectedRoute><RunList /></ProtectedRoute>} />
                    <Route path="/run-pipeline" element={<ProtectedRoute><RunPipelinePage /></ProtectedRoute>} />
                </Routes>
                <ToastContainer position="top-right" autoClose={3000} hideProgressBar />
            </div>
        </div>
    );
};

export default function App() {
    return (
        <AuthProvider>
            <Router>
                <AppLayout />
            </Router>
        </AuthProvider>
    );
}
