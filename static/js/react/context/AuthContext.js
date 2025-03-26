import React, { createContext, useState, useContext, useEffect } from 'react';
import { authService } from '../services/api';

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
            const token = localStorage.getItem('token');
            if (token) {
                const response = await authService.getCurrentUser();
                setUser(response.data);
            }
        } catch (err) {
            setUser(null);
            localStorage.removeItem('token');
            setError('Failed to check authentication status.');
        } finally {
            setLoading(false);
        }
    };

    const login = async (credentials) => {
        try {
            const response = await authService.login(credentials);
            localStorage.setItem('token', response.data.token);
            setUser(response.data.user);
            return response.data;
        } catch (error) {
            setError(error.response?.data?.message || 'Login failed. Please check your credentials.');
            throw error;
        }
    };

    const logout = async () => {
        try {
            await authService.logout();
            localStorage.removeItem('token');
            setUser(null);
        } catch (error) {
            console.error('Logout failed', error);
            setError('Logout failed. Please try again.');
        }
    };

    const signup = async (userData) => {
        try {
            const response = await authService.signup(userData);
            localStorage.setItem('token', response.data.token);
            setUser(response.data.user);
            return response.data;
        } catch (error) {
            setError(error.response?.data?.message || 'Signup failed. Please try again.');
            throw error;
        }
    };

    const signupStep2 = async (preferences) => {
        try {
            const response = await authService.signupStep2(preferences);
            return response.data;
        } catch (error) {
            setError(error.response?.data?.message || 'Failed to save preferences.');
            throw error;
        }
    };

    const signupStep3 = async (preferences) => {
        try {
            const response = await authService.signupStep3(preferences);
            return response.data;
        } catch (error) {
            setError(error.response?.data?.message || 'Failed to save preferences.');
            throw error;
        }
    };

    const value = {
        user,
        loading,
        error,
        login,
        logout,
        signup,
        signupStep2,
        signupStep3,
        checkAuthStatus
    };

    return (
        <AuthContext.Provider value={value}>
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

export const ProtectedRoute = ({ children }) => {
    const { user, loading } = useAuth();

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-wine-600"></div>
            </div>
        );
    }

    if (!user) {
        window.location.href = '/login';
        return null;
    }

    return children;
};