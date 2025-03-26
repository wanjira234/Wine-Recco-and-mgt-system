import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authService, wineService } from '../services/api';
import { Wine, AlertCircle, ArrowLeft, ArrowRight } from 'lucide-react';

const SignupStep2 = () => {
    const navigate = useNavigate();
    const [categories, setCategories] = useState([]);
    const [formData, setFormData] = useState({
        wine_types: [],
        price_range: '',
        occasions: [],
        frequency: ''
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [loadingCategories, setLoadingCategories] = useState(true);

    useEffect(() => {
        const fetchCategories = async () => {
            try {
                setLoadingCategories(true);
                const data = await wineService.getCategories();
                setCategories(data);
            } catch (err) {
                setError('Failed to load wine categories');
                console.error('Error fetching categories:', err);
            } finally {
                setLoadingCategories(false);
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
        
        // Validate form
        if (formData.wine_types.length === 0) {
            setError('Please select at least one wine type');
            return;
        }
        
        if (!formData.price_range) {
            setError('Please select a price range');
            return;
        }
        
        setLoading(true);

        try {
            await authService.signupStep2(formData);
            navigate('/signup/step3');
        } catch (err) {
            setError(err.response?.data?.error || 'An error occurred while saving preferences');
            console.error('Error saving preferences:', err);
        } finally {
            setLoading(false);
        }
    };

    const occasions = [
        { id: 'casual', name: 'Casual Drinking' },
        { id: 'dinner', name: 'Dinner Parties' },
        { id: 'special', name: 'Special Occasions' },
        { id: 'gifts', name: 'Gifts' },
        { id: 'collection', name: 'Collection' }
    ];

    return (
        <div className="min-h-screen bg-gradient-to-br from-wine-900 to-wine-800 py-8 px-4 sm:px-6 lg:px-8">
            <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-lg overflow-hidden">
                {/* Progress Steps */}
                <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center">
                            <Wine className="h-5 w-5 text-wine-600 mr-2" />
                            <span className="text-sm font-medium text-gray-900">Step 2 of 3: Wine Preferences</span>
                        </div>
                        <div className="flex items-center space-x-1">
                            <div className="h-2 w-8 rounded-full bg-wine-600"></div>
                            <div className="h-2 w-8 rounded-full bg-wine-600"></div>
                            <div className="h-2 w-8 rounded-full bg-gray-300"></div>
                        </div>
                    </div>
                </div>
                
                <div className="p-6 sm:p-8">
                    <h2 className="text-2xl font-bold text-gray-900 mb-1">Your Wine Preferences</h2>
                    <p className="text-gray-600 mb-6">Tell us about your wine preferences to help us recommend wines you'll love.</p>
                    
                    {error && (
                        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6 flex items-center">
                            <AlertCircle className="h-5 w-5 mr-2" />
                            <span>{error}</span>
                        </div>
                    )}

                    {loadingCategories ? (
                        <div className="text-center py-8">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-wine-600 mx-auto"></div>
                            <p className="mt-4 text-gray-500">Loading wine categories...</p>
                        </div>
                    ) : (
                        <form onSubmit={handleSubmit} className="space-y-8">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-3">
                                    What types of wine do you enjoy?
                                </label>
                                <p className="text-xs text-gray-500 mb-4">Select all that apply</p>
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                    {categories.map(category => (
                                        <label 
                                            key={category.id} 
                                            className={`
                                                relative flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-50
                                                ${formData.wine_types.includes(category.id) ? 'border-wine-500 bg-wine-50' : 'border-gray-300'}
                                            `}
                                        >
                                            <input
                                                type="checkbox"
                                                name="wine_types"
                                                value={category.id}
                                                checked={formData.wine_types.includes(category.id)}
                                                onChange={handleChange}
                                                className="h-4 w-4 text-wine-600 focus:ring-wine-500 border-gray-300 rounded"
                                            />
                                            <div className="ml-3">
                                                <span className="block text-sm font-medium text-gray-900">{category.name}</span>
                                                {category.description && (
                                                    <span className="block text-xs text-gray-500">{category.description}</span>
                                                )}
                                            </div>
                                        </label>
                                    ))}
                                </div>
                            </div>

                            <div>
                                <label htmlFor="price_range" className="block text-sm font-medium text-gray-700 mb-1">
                                    What's your typical price range for a bottle of wine?
                                </label>
                                <select
                                    id="price_range"
                                    name="price_range"
                                    value={formData.price_range}
                                    onChange={handleChange}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-wine-500 focus:ring-wine-500"
                                    required
                                >
                                    <option value="">Select a price range</option>
                                    <option value="budget">Budget ($10-20)</option>
                                    <option value="mid">Mid-Range ($20-50)</option>
                                    <option value="premium">Premium ($50-100)</option>
                                    <option value="luxury">Luxury ($100+)</option>
                                </select>
                            </div>
                            
                            <div>
                                <label htmlFor="frequency" className="block text-sm font-medium text-gray-700 mb-1">
                                    How often do you drink wine?
                                </label>
                                <select
                                    id="frequency"
                                    name="frequency"
                                    value={formData.frequency}
                                    onChange={handleChange}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-wine-500 focus:ring-wine-500"
                                >
                                    <option value="">Select frequency</option>
                                    <option value="rarely">Rarely (Special occasions only)</option>
                                    <option value="monthly">Monthly</option>
                                    <option value="weekly">Weekly</option>
                                    <option value="frequently">Frequently (Several times a week)</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-3">
                                    For what occasions do you typically buy wine?
                                </label>
                                <p className="text-xs text-gray-500 mb-4">Select all that apply</p>
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                    {occasions.map(occasion => (
                                        <label 
                                            key={occasion.id} 
                                            className={`
                                                relative flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-50
                                                ${formData.occasions.includes(occasion.id) ? 'border-wine-500 bg-wine-50' : 'border-gray-300'}
                                            `}
                                        >
                                            <input
                                                type="checkbox"
                                                name="occasions"
                                                value={occasion.id}
                                                checked={formData.occasions.includes(occasion.id)}
                                                onChange={handleChange}
                                                className="h-4 w-4 text-wine-600 focus:ring-wine-500 border-gray-300 rounded"
                                            />
                                            <span className="ml-3 block text-sm font-medium text-gray-900">{occasion.name}</span>
                                        </label>
                                    ))}
                                </div>
                            </div>

                            <div className="flex justify-between pt-6 border-t border-gray-200">
                                <Link
                                    to="/signup"
                                    className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                                >
                                    <ArrowLeft className="h-4 w-4 mr-2" />
                                    Back
                                </Link>
                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="inline-flex items-center px-6 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-wine-600 hover:bg-wine-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-wine-500 disabled:opacity-50"
                                >
                                    {loading ? (
                                        <>
                                            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                            </svg>
                                            Saving Preferences...
                                        </>
                                    ) : (
                                        <>
                                            Next: Taste Preferences
                                            <ArrowRight className="h-4 w-4 ml-2" />
                                        </>
                                    )}
                                </button>
                            </div>
                        </form>
                    )}
                </div>
            </div>
        </div>
    );
};

export default SignupStep2;