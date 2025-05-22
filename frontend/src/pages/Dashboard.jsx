import React from 'react';
import { useAuth } from '../context/AuthContext';

const Dashboard = () => {
    const { user } = useAuth();
    return (
        <div className="container mx-auto p-4 bg-white rounded-2xl shadow-md">
            <h2 className="text-2xl font-bold mb-4">
                Welcome{user ? `, ${user.name}` : ''} 👋
            </h2>
            <p className="text-gray-700">Start managing your AutoML projects.</p>
        </div>
    );
};

export default Dashboard;
