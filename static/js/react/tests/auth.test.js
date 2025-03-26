import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider, useAuth } from '../context/AuthContext';
import { authService } from '../services/api';

// Mock the API service
jest.mock('../services/api', () => ({
    authService: {
        login: jest.fn(),
        signup: jest.fn(),
        getCurrentUser: jest.fn(),
        logout: jest.fn()
    }
}));

// Test component to access auth context
const TestComponent = () => {
    const { user, login, logout, signup } = useAuth();
    return (
        <div>
            {user ? (
                <div>
                    <p>Logged in as: {user.email}</p>
                    <button onClick={logout}>Logout</button>
                </div>
            ) : (
                <div>
                    <button onClick={() => login({ email: 'test@example.com', password: 'password' })}>
                        Login
                    </button>
                    <button onClick={() => signup({ email: 'test@example.com', password: 'password' })}>
                        Signup
                    </button>
                </div>
            )}
        </div>
    );
};

describe('Authentication Flow', () => {
    beforeEach(() => {
        localStorage.clear();
        jest.clearAllMocks();
    });

    test('should handle successful login', async () => {
        const mockUser = { id: 1, email: 'test@example.com' };
        const mockResponse = { data: { user: mockUser, token: 'mock-token' } };
        authService.login.mockResolvedValueOnce(mockResponse);

        render(
            <BrowserRouter>
                <AuthProvider>
                    <TestComponent />
                </AuthProvider>
            </BrowserRouter>
        );

        const loginButton = screen.getByText('Login');
        fireEvent.click(loginButton);

        await waitFor(() => {
            expect(screen.getByText(`Logged in as: ${mockUser.email}`)).toBeInTheDocument();
        });

        expect(localStorage.getItem('token')).toBe('mock-token');
    });

    test('should handle successful signup', async () => {
        const mockUser = { id: 1, email: 'test@example.com' };
        const mockResponse = { data: { user: mockUser, token: 'mock-token' } };
        authService.signup.mockResolvedValueOnce(mockResponse);

        render(
            <BrowserRouter>
                <AuthProvider>
                    <TestComponent />
                </AuthProvider>
            </BrowserRouter>
        );

        const signupButton = screen.getByText('Signup');
        fireEvent.click(signupButton);

        await waitFor(() => {
            expect(screen.getByText(`Logged in as: ${mockUser.email}`)).toBeInTheDocument();
        });

        expect(localStorage.getItem('token')).toBe('mock-token');
    });

    test('should handle logout', async () => {
        // First login
        const mockUser = { id: 1, email: 'test@example.com' };
        const mockResponse = { data: { user: mockUser, token: 'mock-token' } };
        authService.login.mockResolvedValueOnce(mockResponse);
        authService.logout.mockResolvedValueOnce({});

        render(
            <BrowserRouter>
                <AuthProvider>
                    <TestComponent />
                </AuthProvider>
            </BrowserRouter>
        );

        // Login
        const loginButton = screen.getByText('Login');
        fireEvent.click(loginButton);

        await waitFor(() => {
            expect(screen.getByText(`Logged in as: ${mockUser.email}`)).toBeInTheDocument();
        });

        // Logout
        const logoutButton = screen.getByText('Logout');
        fireEvent.click(logoutButton);

        await waitFor(() => {
            expect(screen.getByText('Login')).toBeInTheDocument();
        });

        expect(localStorage.getItem('token')).toBeNull();
    });

    test('should handle authentication errors', async () => {
        const errorMessage = 'Invalid credentials';
        authService.login.mockRejectedValueOnce({ response: { data: { message: errorMessage } } });

        render(
            <BrowserRouter>
                <AuthProvider>
                    <TestComponent />
                </AuthProvider>
            </BrowserRouter>
        );

        const loginButton = screen.getByText('Login');
        fireEvent.click(loginButton);

        await waitFor(() => {
            expect(screen.getByText('Login')).toBeInTheDocument();
        });

        expect(localStorage.getItem('token')).toBeNull();
    });
}); 