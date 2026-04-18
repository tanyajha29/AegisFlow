import React, { createContext, useState, useEffect, useContext } from 'react';
import api from '../lib/api.js';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token') || null);
    const [loading, setLoading] = useState(true);

    const applyToken = (value) => {
        setToken(value);
        if (value) {
            api.defaults.headers.common['Authorization'] = `Bearer ${value}`;
            localStorage.setItem('token', value);
        }
    };

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
        if (data.mfa_required) {
            return { mfa_required: true, challenge_token: data.challenge_token };
        }
        applyToken(data.access_token);
        const profile = await api.get('/auth/profile');
        setUser(profile.data);
        return { mfa_required: false };
    };

    const register = async (email, password) => {
        // Step 1: initiate registration — returns challenge_token + QR
        const { data } = await api.post('/auth/register', { email, password });
        // Return the challenge data so the UI can show the QR setup screen
        return {
            registration_pending: true,
            challenge_token: data.challenge_token,
            qr_code_base64: data.qr_code_base64,
            otpauth_url: data.otpauth_url,
            backup_codes: data.backup_codes,
        };
    };

    const verifyRegistration = async (challengeToken, otp) => {
        // Step 2: verify OTP, activate account, get full token
        const { data } = await api.post('/auth/register/verify', {
            challenge_token: challengeToken,
            otp,
        });
        applyToken(data.access_token);
        const profile = await api.get('/auth/profile');
        setUser(profile.data);
        return true;
    };

    const verifyLoginMfa = async (challengeToken, otp) => {
        const { data } = await api.post('/auth/verify-login-mfa', {
            challenge_token: challengeToken,
            otp
        });
        applyToken(data.access_token);
        const profile = await api.get('/auth/profile');
        setUser(profile.data);
        return true;
    };

    const fetchProfile = async () => {
        const profile = await api.get('/auth/profile');
        setUser(profile.data);
        return profile.data;
    };

    const startMfaSetup = async () => {
        const { data } = await api.post('/auth/setup-mfa');
        return data;
    };

    const verifyMfa = async (otp) => {
        const { data } = await api.post('/auth/verify-mfa', { otp });
        await fetchProfile();
        return data;
    };

    const disableMfa = async (otp) => {
        const { data } = await api.post('/auth/disable-mfa', { otp });
        await fetchProfile();
        return data;
    };

    const logout = () => {
        setToken(null);
    };

    const value = {
        user,
        token,
        login,
        register,
        verifyRegistration,
        logout,
        loading,
        verifyLoginMfa,
        startMfaSetup,
        verifyMfa,
        disableMfa,
        fetchProfile
    };

    return <AuthContext.Provider value={value}>{!loading && children}</AuthContext.Provider>;
};
