import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import SignupStep2 from './SignupStep2';

const Signup = () => {
    const { signup } = useAuth();
    const [currentStep, setCurrentStep] = useState(1);
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        winePreferences: []
    });
    const [error, setError] = useState('');

    const handleStep1Submit = (e) => {
        e.preventDefault();
        if (!formData.email || !formData.password) {
            setError('Please fill in all fields');
            return;
        }
        setCurrentStep(2);
    };

    const handleStep2Back = () => {
        setCurrentStep(1);
    };

    const handleStep2Next = (selectedWines) => {
        setFormData(prev => ({
            ...prev,
            winePreferences: selectedWines
        }));
        handleFinalSubmit();
    };

    const handleFinalSubmit = async () => {
        try {
            await signup(formData.email, formData.password, formData.winePreferences);
            // Redirect or show success message
        } catch (err) {
            setError('Failed to create an account. Please try again.');
            setCurrentStep(1);
        }
    };

    if (currentStep === 2) {
        return <SignupStep2 onNext={handleStep2Next} onBack={handleStep2Back} />;
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-teal-500 to-teal-600 py-8 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md mx-auto bg-white rounded-xl shadow-xl p-6">
                <div className="text-center mb-8">
                    <h2 className="text-2xl font-bold text-gray-800">
                        Create Account
                    </h2>
                    <p className="mt-2 text-sm text-gray-600">
                        Enter your details to get started
                    </p>
                    {/* Progress indicator */}
                    <div className="flex justify-center items-center space-x-2 mt-4">
                        <div className="w-3 h-3 rounded-full bg-teal-500"></div>
                        <div className="w-3 h-3 rounded-full bg-gray-300"></div>
                        <div className="w-3 h-3 rounded-full bg-gray-300"></div>
                    </div>
                </div>

                {error && <div className="text-red-600 text-center mb-4">{error}</div>}
                
                <form onSubmit={handleStep1Submit} className="space-y-6">
                    <div>
                        <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                            Email
                        </label>
                        <input
                            type="email"
                            id="email"
                            value={formData.email}
                            onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-teal-500 focus:ring-teal-500"
                            required
                        />
                    </div>
                    <div>
                        <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                            Password
                        </label>
                        <input
                            type="password"
                            id="password"
                            value={formData.password}
                            onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-teal-500 focus:ring-teal-500"
                            required
                        />
                    </div>
                    <div>
                        <button
                            type="submit"
                            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-full shadow-sm text-sm font-medium text-white bg-teal-500 hover:bg-teal-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-teal-500"
                        >
                            Continue
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default Signup;