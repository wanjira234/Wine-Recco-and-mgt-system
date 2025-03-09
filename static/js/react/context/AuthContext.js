import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        checkAuthStatus();
    }, []);

    const checkAuthStatus = async () => {
        try {
            const response = await axios.get('/api/auth/status');
            setUser(response.data.user);
        } catch (err) {
            setUser(null);
            setError('Failed to check authentication status.');
        } finally {
            setLoading(false);
        }
    };

    const login = async (username, password) => {
        try {
            const response = await axios.post('/api/auth/login', { username, password });
            setUser(response.data.user);
            return response.data.user;
        } catch (error) {
            setError('Login failed. Please check your credentials.');
            throw error;
        }
    };

    const logout = async () => {
        try {
            await axios.post('/api/auth/logout');
            setUser(null);
        } catch (error) {
            console.error('Logout failed', error);
            setError('Logout failed. Please try again.');
        }
    };

    const signup = async (username, password) => {
        try {
            const response = await axios.post('/api/auth/signup', { username, password });
            setUser(response.data.user);
            return response.data.user;
        } catch (error) {
            setError('Signup failed. Please try again.');
            throw error;
        }
    };

    const isAdmin = () => user && user.role === 'admin'; // Assuming user object has a role property

    return (
        <AuthContext.Provider value={{ user, loading, error, login, logout, signup, isAdmin }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};