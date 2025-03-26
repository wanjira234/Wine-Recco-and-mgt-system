import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authService } from '../services/api';
import { Eye, EyeOff, CheckCircle, AlertCircle } from 'lucide-react';

const Signup = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        first_name: '',
        last_name: '',
        email: '',
        password: '',
        confirm_password: ''
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [passwordStrength, setPasswordStrength] = useState(0);
    const [passwordFeedback, setPasswordFeedback] = useState('');

    const handleChange = (e) => {
        const { name, value } = e.target;
        
        setFormData({
            ...formData,
            [name]: value
        });
        
        // Check password strength when password field changes
        if (name === 'password') {
            checkPasswordStrength(value);
        }
    };
    
    const checkPasswordStrength = (password) => {
        // Simple password strength checker
        let strength = 0;
        let feedback = '';
        
        if (password.length >= 8) {
            strength += 1;
        } else {
            feedback = 'Password should be at least 8 characters long';
        }
        
        if (/[A-Z]/.test(password)) {
            strength += 1;
        }
        
        if (/[0-9]/.test(password)) {
            strength += 1;
        }
        
        if (/[^A-Za-z0-9]/.test(password)) {
            strength += 1;
        }
        
        setPasswordStrength(strength);
        
        if (strength === 4) {
            setPasswordFeedback('Strong password');
        } else if (strength >= 2) {
            setPasswordFeedback('Moderate password');
        } else if (password) {
            setPasswordFeedback(feedback || 'Weak password');
        } else {
            setPasswordFeedback('');
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        
        // Validate form
        if (!formData.first_name || !formData.last_name || !formData.email || !formData.password || !formData.confirm_password) {
            setError('All fields are required');
            return;
        }
        
        if (formData.password !== formData.confirm_password) {
            setError('Passwords do not match');
            return;
        }
        
        if (passwordStrength < 2) {
            setError('Please use a stronger password');
            return;
        }
        
        setLoading(true);

        try {
            const { confirm_password, ...signupData } = formData;
            await authService.signup(signupData);
            navigate('/signup/preferences');
        } catch (err) {
            setError(err.response?.data?.error || 'An error occurred during signup');
            console.error('Signup error:', err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-wine-900 to-wine-800 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md mx-auto bg-white rounded-lg shadow-lg p-8">
                <div className="text-center mb-8">
                    <h2 className="text-3xl font-bold text-wine-900">Create Your Account</h2>
                    <p className="mt-2 text-gray-600">Join our community of wine enthusiasts</p>
                </div>
                
                {error && (
                    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6 flex items-start">
                        <AlertCircle className="h-5 w-5 mr-2 mt-0.5 flex-shrink-0" />
                        <span>{error}</span>
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label htmlFor="first_name" className="block text-sm font-medium text-gray-700 mb-1">
                                First Name
                            </label>
                            <input
                                type="text"
                                name="first_name"
                                id="first_name"
                                required
                                value={formData.first_name}
                                onChange={handleChange}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-wine-500 focus:border-wine-500"
                            />
                        </div>

                        <div>
                            <label htmlFor="last_name" className="block text-sm font-medium text-gray-700 mb-1">
                                Last Name
                            </label>
                            <input
                                type="text"
                                name="last_name"
                                id="last_name"
                                required
                                value={formData.last_name}
                                onChange={handleChange}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-wine-500 focus:border-wine-500"
                            />
                        </div>
                    </div>

                    <div>
                        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                            Email
                        </label>
                        <input
                            type="email"
                            name="email"
                            id="email"
                            required
                            value={formData.email}
                            onChange={handleChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-wine-500 focus:border-wine-500"
                        />
                    </div>

                    <div>
                        <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                            Password
                        </label>
                        <div className="relative">
                            <input
                                type={showPassword ? "text" : "password"}
                                name="password"
                                id="password"
                                required
                                value={formData.password}
                                onChange={handleChange}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-wine-500 focus:border-wine-500"
                            />
                            <button
                                type="button"
                                className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
                                onClick={() => setShowPassword(!showPassword)}
                            >
                                {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                            </button>
                        </div>
                        {formData.password && (
                            <div className="mt-2">
                                <div className="flex items-center mb-1">
                                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                                        <div 
                                            className={`h-2.5 rounded-full ${
                                                passwordStrength === 0 ? 'bg-red-500 w-1/4' :
                                                passwordStrength === 1 ? 'bg-orange-500 w-2/4' :
                                                passwordStrength === 2 ? 'bg-yellow-500 w-3/4' :
                                                'bg-green-500 w-full'
                                            }`}
                                        ></div>
                                    </div>
                                    <span className="ml-2 text-xs text-gray-500">
                                        {passwordStrength === 4 ? (
                                            <CheckCircle className="h-4 w-4 text-green-500" />
                                        ) : (
                                            passwordStrength
                                        )}
                                    </span>
                                </div>
                                <p className={`text-xs ${
                                    passwordStrength >= 3 ? 'text-green-600' :
                                    passwordStrength >= 2 ? 'text-yellow-600' :
                                    'text-red-600'
                                }`}>
                                    {passwordFeedback}
                                </p>
                            </div>
                        )}
                    </div>

                    <div>
                        <label htmlFor="confirm_password" className="block text-sm font-medium text-gray-700 mb-1">
                            Confirm Password
                        </label>
                        <div className="relative">
                            <input
                                type={showConfirmPassword ? "text" : "password"}
                                name="confirm_password"
                                id="confirm_password"
                                required
                                value={formData.confirm_password}
                                onChange={handleChange}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-wine-500 focus:border-wine-500"
                            />
                            <button
                                type="button"
                                className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
                                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                            >
                                {showConfirmPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                            </button>
                        </div>
                        {formData.password && formData.confirm_password && (
                            <p className={`mt-1 text-xs ${
                                formData.password === formData.confirm_password ? 'text-green-600' : 'text-red-600'
                            }`}>
                                {formData.password === formData.confirm_password ? (
                                    <span className="flex items-center">
                                        <CheckCircle className="h-3 w-3 mr-1" />
                                        Passwords match
                                    </span>
                                ) : 'Passwords do not match'}
                            </p>
                        )}
                    </div>

                    <div className="pt-2">
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-wine-600 hover:bg-wine-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-wine-500 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? 'Creating Account...' : 'Create Account'}
                        </button>
                    </div>
                </form>
                
                <div className="mt-6 text-center">
                    <p className="text-sm text-gray-600">
                        Already have an account?{' '}
                        <Link to="/login" className="font-medium text-wine-600 hover:text-wine-500">
                            Sign in
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Signup;