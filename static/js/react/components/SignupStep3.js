import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService, wineService } from '../services/api';

const SignupStep3 = () => {
    const navigate = useNavigate();
    const [traits, setTraits] = useState([]);
    const [formData, setFormData] = useState({
        sweetness: '',
        body: '',
        acidity: '',
        tannins: '',
        flavors: []
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const fetchTraits = async () => {
            try {
                const data = await wineService.getTraits();
                setTraits(data);
            } catch (err) {
                setError('Failed to load wine traits');
            }
        };
        fetchTraits();
    }, []);

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' 
                ? checked 
                    ? [...prev[name], value]
                    : prev[name].filter(item => item !== value)
                : value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            await authService.signupStep3(formData);
            navigate('/dashboard'); // Redirect to dashboard after successful signup
        } catch (err) {
            setError(err.response?.data?.error || 'An error occurred while saving preferences');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-wine-900 to-wine-800 py-8 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md mx-auto bg-white rounded-lg shadow-lg p-8">
                <h2 className="text-3xl font-bold text-center text-wine-900 mb-8">Taste Preferences</h2>
                
                {error && (
                    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label htmlFor="sweetness" className="block text-sm font-medium text-gray-700">
                            Preferred Sweetness Level
                        </label>
                        <select
                            id="sweetness"
                            name="sweetness"
                            value={formData.sweetness}
                            onChange={handleChange}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-wine-500 focus:ring-wine-500"
                        >
                            <option value="">Select sweetness level</option>
                            <option value="dry">Dry</option>
                            <option value="off_dry">Off-Dry</option>
                            <option value="semi_sweet">Semi-Sweet</option>
                            <option value="sweet">Sweet</option>
                        </select>
                    </div>

                    <div>
                        <label htmlFor="body" className="block text-sm font-medium text-gray-700">
                            Preferred Body
                        </label>
                        <select
                            id="body"
                            name="body"
                            value={formData.body}
                            onChange={handleChange}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-wine-500 focus:ring-wine-500"
                        >
                            <option value="">Select body type</option>
                            <option value="light">Light</option>
                            <option value="medium">Medium</option>
                            <option value="full">Full</option>
                        </select>
                    </div>

                    <div>
                        <label htmlFor="acidity" className="block text-sm font-medium text-gray-700">
                            Preferred Acidity Level
                        </label>
                        <select
                            id="acidity"
                            name="acidity"
                            value={formData.acidity}
                            onChange={handleChange}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-wine-500 focus:ring-wine-500"
                        >
                            <option value="">Select acidity level</option>
                            <option value="low">Low</option>
                            <option value="medium">Medium</option>
                            <option value="high">High</option>
                        </select>
                    </div>

                    <div>
                        <label htmlFor="tannins" className="block text-sm font-medium text-gray-700">
                            Preferred Tannin Level
                        </label>
                        <select
                            id="tannins"
                            name="tannins"
                            value={formData.tannins}
                            onChange={handleChange}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-wine-500 focus:ring-wine-500"
                        >
                            <option value="">Select tannin level</option>
                            <option value="low">Low</option>
                            <option value="medium">Medium</option>
                            <option value="high">High</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Preferred Flavors
                        </label>
                        <div className="space-y-2">
                            {traits.map(trait => (
                                <div key={trait.id} className="flex items-center">
                                    <input
                                        type="checkbox"
                                        name="flavors"
                                        value={trait.id}
                                        checked={formData.flavors.includes(trait.id)}
                                        onChange={handleChange}
                                        className="h-4 w-4 text-wine-600 focus:ring-wine-500 border-gray-300 rounded"
                                    />
                                    <label className="ml-2 block text-sm text-gray-900">
                                        {trait.name}
                                    </label>
                                </div>
                            ))}
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-wine-600 hover:bg-wine-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-wine-500 disabled:opacity-50"
                    >
                        {loading ? 'Completing Signup...' : 'Complete Signup'}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default SignupStep3; 