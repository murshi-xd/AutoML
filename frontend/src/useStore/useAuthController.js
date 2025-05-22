import api from '../lib/axios';

export const fetchCurrentUser = async () => {
    try {
        const res = await api.get('user', { withCredentials: true });
        return res.data;
    } catch (err) {
        return null;
    }
};

export const logout = async () => {
    try {
        await api.get('logout', { withCredentials: true });
    } catch (err) {
        console.error("Logout failed:", err);
    }
};
