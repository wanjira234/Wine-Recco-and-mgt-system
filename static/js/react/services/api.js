import axios from 'axios';

// Create axios instance with default config
const api = axios.create({
    baseURL: '/api',
    headers: {
        'Content-Type': 'application/json'
    }
});

// Add token to requests if it exists
api.interceptors.request.use(config => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Handle response errors
api.interceptors.response.use(
    response => response,
    error => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// Auth Service
export const authService = {
    login: (credentials) => api.post('/auth/login', credentials),
    signup: (userData) => api.post('/auth/signup', userData),
    signupStep2: (preferences) => api.post('/auth/signup/step2', preferences),
    signupStep3: (preferences) => api.post('/auth/signup/step3', preferences),
    logout: () => api.post('/auth/logout'),
    getCurrentUser: () => api.get('/auth/me'),
    verifyEmail: (token) => api.post('/auth/verify-email', { token }),
    resendVerification: () => api.post('/auth/resend-verification'),
    forgotPassword: (email) => api.post('/auth/forgot-password', { email }),
    resetPassword: (token, password) => api.post('/auth/reset-password', { token, password })
};

// Wine Service
export const wineService = {
    getWines: (params) => api.get('/wines', { params }),
    getWine: (id) => api.get(`/wines/${id}`),
    getRecommendations: () => api.get('/wines/recommendations'),
    getCategories: () => api.get('/wines/categories'),
    getTraits: () => api.get('/wines/traits'),
    rateWine: (id, rating) => api.post(`/wines/${id}/rate`, { rating }),
    searchWines: (query) => api.get('/wines/search', { params: { q: query } })
};

// Account Service
export const accountService = {
    updateProfile: (data) => api.put('/account/profile', data),
    updatePassword: (data) => api.put('/account/password', data),
    updatePreferences: (preferences) => api.put('/account/preferences', preferences),
    getNotifications: () => api.get('/account/notifications'),
    markNotificationRead: (id) => api.put(`/account/notifications/${id}/read`),
    deleteAccount: () => api.delete('/account')
};

export default api; 