import { useState, useEffect, useContext, createContext } from 'react';
import { authService } from '../services/api';

// Create an auth context
const AuthContext = createContext(null);

// Provider component that wraps your app and makes auth object available to any child component that calls useAuth().
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check if user is authenticated on mount
  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        setIsLoading(true);
        const token = localStorage.getItem('token');
        
        if (!token) {
          setIsAuthenticated(false);
          setUser(null);
          return;
        }
        
        // Verify token and get user data
        const userData = await authService.getCurrentUser();
        setUser(userData);
        setIsAuthenticated(true);
      } catch (err) {
        console.error('Auth error:', err);
        setError(err);
        setIsAuthenticated(false);
        setUser(null);
        // Clear invalid token
        localStorage.removeItem('token');
      } finally {
        setIsLoading(false);
      }
    };
    
    checkAuthStatus();
  }, []);

  // Login function
  const login = async (credentials) => {
    try {
      setIsLoading(true);
      const response = await authService.login(credentials);
      localStorage.setItem('token', response.data.token);
      
      // Get user data
      const userData = await authService.getCurrentUser();
      setUser(userData);
      setIsAuthenticated(true);
      setError(null);
      
      return userData;
    } catch (err) {
      console.error('Login error:', err);
      setError(err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Signup function
  const signup = async (userData) => {
    try {
      setIsLoading(true);
      const response = await authService.signup(userData);
      localStorage.setItem('token', response.data.token);
      
      // Get user data
      const user = await authService.getCurrentUser();
      setUser(user);
      setIsAuthenticated(true);
      setError(null);
      
      return user;
    } catch (err) {
      console.error('Signup error:', err);
      setError(err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Logout function
  const logout = async () => {
    try {
      setIsLoading(true);
      await authService.logout();
      localStorage.removeItem('token');
      setUser(null);
      setIsAuthenticated(false);
    } catch (err) {
      console.error('Logout error:', err);
      setError(err);
    } finally {
      setIsLoading(false);
    }
  };

  // Update user data
  const updateUser = (userData) => {
    setUser(userData);
  };

  // Return the auth context value
  const value = {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    signup,
    logout,
    updateUser
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// Hook for components to get the auth object and re-render when it changes
export const useAuth = () => {
  return useContext(AuthContext);
};