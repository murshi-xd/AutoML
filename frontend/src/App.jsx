import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import EDA from './pages/EDA';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Visuals from './pages/visualise';
import ExperimentRunsComponent from './components/ExperimentRunsComponent';
import RunDetail from './pages/RunDetail';
import RunList from './pages/RunList';
import RunPipelinePage from './pages/RunPipelinePage';

import {AuthProvider} from './context/AuthContext';
import Login from './pages/Login';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
    const [sidebarOpen, setSidebarOpen] = useState(true);

    const handleOutsideClick = (e) => {
        if (window.innerWidth < 768 && sidebarOpen) {
            setSidebarOpen(false);
        }
    };

    return (
        <AuthProvider>
            <Router>
                <div className="flex" onClick={handleOutsideClick}>
                    <Navbar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />
                    <div className={`${sidebarOpen ? 'md:pl-64' : 'pl-0'} flex-1 min-h-screen bg-gray-100 pt-20 p-6 overflow-auto transition-all duration-300`}>
                        <Routes>
                            <Route path="/login" element={<Login />} />
                            <Route
                                path="/"
                                element={
                                    <ProtectedRoute>
                                        <Dashboard />
                                    </ProtectedRoute>
                                }
                            />
                            <Route
                                path="/upload"
                                element={
                                    <ProtectedRoute>
                                        <Upload />
                                    </ProtectedRoute>
                                }
                            />
                            <Route
                                path="/eda"
                                element={
                                    <ProtectedRoute>
                                        <EDA />
                                    </ProtectedRoute>
                                }
                            />
                            <Route
                                path="/visuals"
                                element={
                                    <ProtectedRoute>
                                        <Visuals />
                                    </ProtectedRoute>
                                }
                            />
                            <Route
                                path="/experiments"
                                element={
                                    <ProtectedRoute>
                                        <ExperimentRunsComponent />
                                    </ProtectedRoute>
                                }
                            />
                            <Route
                                path="/runs/:runId"
                                element={
                                    <ProtectedRoute>
                                        <RunDetail />
                                    </ProtectedRoute>
                                }
                            />
                            <Route
                                path="/experiments/:experimentId"
                                element={
                                    <ProtectedRoute>
                                        <RunList />
                                    </ProtectedRoute>
                                }
                            />
                            <Route
                                path="/run-pipeline"
                                element={
                                    <ProtectedRoute>
                                        <RunPipelinePage />
                                    </ProtectedRoute>
                                }
                            />
                             <Route 
                                path="/login" 
                                element={
                                    <Login />
                                } 
                            />

                        </Routes>
                    </div>
                    <ToastContainer position="top-right" autoClose={3000} hideProgressBar />
                </div>
            </Router>
        </AuthProvider>
    );
}

export default App;
