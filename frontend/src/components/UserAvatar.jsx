import React from 'react';
import { useAuth } from '../context/AuthContext';
import { logout } from '../useStore/useAuthController';
import { useNavigate } from 'react-router-dom';

const UserAvatar = () => {
    const { user, setUser } = useAuth();
    const navigate = useNavigate();

    const handleLogout = async () => {
        await logout();
        setUser(null);
        navigate('/login');
    };

    if (!user) return null;

    return (
        <div className="flex items-center space-x-2">
            <img
                src={user.picture}
                alt={user.name}
                className="w-8 h-8 rounded-full border"
                title={user.name}
            />
            <button onClick={handleLogout} className="text-sm text-white hover:underline">Logout</button>
        </div>
    );
};

export default UserAvatar;
