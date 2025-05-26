import { createContext, useContext, useEffect, useState } from 'react';
import { fetchCurrentUser } from "../useStore/useAuthController";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);

    useEffect(() => {
    const loadUser = async () => {
        // Wait 100ms to ensure cookie is set by browser
        await new Promise(resolve => setTimeout(resolve, 100));
        const user = await fetchCurrentUser();
        setUser(user);
    };

    loadUser();
    }, []);

    return (
        <AuthContext.Provider value={{ user, setUser }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
