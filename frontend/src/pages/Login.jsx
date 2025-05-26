import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Login = () => {
    const navigate = useNavigate();
    const { user } = useAuth();

    useEffect(() => {
        if (user) {
            navigate('/'); // Redirect to dashboard after login
        }
    }, [user]);

    const handleGoogleLogin = () => {
        window.location.href = 'http://localhost:5004/login/google';
    };

    return (
        <div className="h-screen flex items-center justify-center bg-gradient-to-r from-indigo-500 to-blue-500">
            <div className="bg-white p-10 rounded-xl shadow-lg text-center space-y-4 max-w-sm w-full">
                <h2 className="text-3xl font-bold text-gray-800">Login to AutoML</h2>
                <p className="text-gray-500">Start your ML experiments instantly.</p>
                <button
                    onClick={handleGoogleLogin}
                    className="bg-red-500 hover:bg-red-600 text-white py-2 px-4 rounded-lg text-lg font-semibold w-full"
                >
                    Continue with Google
                </button>
            </div>
        </div>
    );
};

export default Login;
