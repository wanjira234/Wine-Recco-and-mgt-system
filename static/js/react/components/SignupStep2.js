import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService, wineService } from '../services/api';

const SignupStep2 = () => {
    const navigate = useNavigate();
    const [categories, setCategories] = useState([]);
    const [formData, setFormData] = useState({
        wine_types: [],
        price_range: '',
        occasions: []
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const fetchCategories = async () => {
            try {
                const data = await wineService.getCategories();
                setCategories(data);
            } catch (err) {
                setError('Failed to load wine categories');
            }
        };
        fetchCategories();
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
            await authService.signupStep2(formData);
            navigate('/signup/step3');
        } catch (err) {
            setError(err.response?.data?.error || 'An error occurred while saving preferences');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-wine-900 to-wine-800 py-8 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md mx-auto bg-white rounded-lg shadow-lg p-8">
                <h2 className="text-3xl font-bold text-center text-wine-900 mb-8">Wine Preferences</h2>
                
                {error && (
                    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Preferred Wine Types
                        </label>
                        <div className="space-y-2">
                            {categories.map(category => (
                                <div key={category.id} className="flex items-center">
                                    <input
                                        type="checkbox"
                                        name="wine_types"
                                        value={category.id}
                                        checked={formData.wine_types.includes(category.id)}
                                        onChange={handleChange}
                                        className="h-4 w-4 text-wine-600 focus:ring-wine-500 border-gray-300 rounded"
                                    />
                                    <label className="ml-2 block text-sm text-gray-900">
                                        {category.name}
                                    </label>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div>
                        <label htmlFor="price_range" className="block text-sm font-medium text-gray-700">
                            Price Range
                        </label>
                        <select
                            id="price_range"
                            name="price_range"
                            value={formData.price_range}
                            onChange={handleChange}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-wine-500 focus:ring-wine-500"
                        >
                            <option value="">Select a price range</option>
                            <option value="budget">Budget ($10-20)</option>
                            <option value="mid">Mid-Range ($20-50)</option>
                            <option value="premium">Premium ($50+)</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Occasions
                        </label>
                        <div className="space-y-2">
                            {['Casual', 'Formal', 'Special Occasions', 'Gifts'].map(occasion => (
                                <div key={occasion} className="flex items-center">
                                    <input
                                        type="checkbox"
                                        name="occasions"
                                        value={occasion.toLowerCase()}
                                        checked={formData.occasions.includes(occasion.toLowerCase())}
                                        onChange={handleChange}
                                        className="h-4 w-4 text-wine-600 focus:ring-wine-500 border-gray-300 rounded"
                                    />
                                    <label className="ml-2 block text-sm text-gray-900">
                                        {occasion}
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
                        {loading ? 'Saving Preferences...' : 'Next: Taste Preferences'}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default SignupStep2; 