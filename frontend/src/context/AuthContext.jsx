import React, { createContext, useState, useEffect, useContext } from 'react';
import api from '../lib/api.js';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token') || null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (token) {
            api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
            localStorage.setItem('token', token);
            // Verify token and load profile
            api
                .get('/auth/profile')
                .then((res) => setUser(res.data))
                .catch(() => {
                    setToken(null);
                    setUser(null);
                })
                .finally(() => setLoading(false));
        } else {
            delete api.defaults.headers.common['Authorization'];
            localStorage.removeItem('token');
            setUser(null);
            setLoading(false);
        }
    }, [token]);

    const login = async (email, password) => {
        const { data } = await api.post('/auth/login', { email, password });
        setToken(data.access_token);
        const profile = await api.get('/auth/profile');
        setUser(profile.data);
        return true;
    };

    const register = async (email, password) => {
        await api.post('/auth/register', { email, password });
        return login(email, password); // auto-login
    };

    const logout = () => {
        setToken(null);
    };

    const value = {
        user,
        token,
        login,
        register,
        logout,
        loading
    };

    return <AuthContext.Provider value={value}>{!loading && children}</AuthContext.Provider>;
};
