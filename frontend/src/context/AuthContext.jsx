import React, { createContext, useState, useEffect, useContext } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token') || null);
    const [loading, setLoading] = useState(true);

    // Set default axios header if token exists
    useEffect(() => {
        if (token) {
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
            localStorage.setItem('token', token);
            // We would ideally verify the token here with a /me endpoint, 
            // but for MVP we assume presence of token means logged in
            setUser({ token });
        } else {
            delete axios.defaults.headers.common['Authorization'];
            localStorage.removeItem('token');
            setUser(null);
        }
        setLoading(false);
    }, [token]);

    const login = async (email, password) => {
        const formData = new FormData();
        formData.append('username', email); // OAuth2 requires 'username'
        formData.append('password', password);

        // In production we would use process.env.VITE_API_BASE_URL
        const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

        try {
            const response = await axios.post(`${API_BASE}/auth/login`, formData);
            setToken(response.data.access_token);
            return true;
        } catch (error) {
            console.error("Login failed", error);
            throw error;
        }
    };

    const register = async (email, password) => {
        const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
        try {
            await axios.post(`${API_BASE}/auth/register`, { email, password });
            return await login(email, password); // Auto login after register
        } catch (error) {
            console.error("Register failed", error);
            throw error;
        }
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
