import api from '../lib/axios';

export const fetchCurrentUser = async () => {
    try {
        console.log("Fetching user...");
        const res = await api.get('user');
        console.log("User fetched:", res.data);
        return res.data;
    } catch (err) {
        console.error("Fetch user failed", err);
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
