import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authService, wineService } from '../services/api';
import { Wine, Check, AlertCircle, ArrowLeft, ArrowRight } from 'lucide-react';

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
    const [loadingTraits, setLoadingTraits] = useState(true);

    useEffect(() => {
        const fetchTraits = async () => {
            try {
                setLoadingTraits(true);
                const data = await wineService.getTraits();
                setTraits(data);
            } catch (err) {
                setError('Failed to load wine traits');
                console.error('Error fetching traits:', err);
            } finally {
                setLoadingTraits(false);
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
        
        // Validate form
        if (!formData.sweetness || !formData.body || !formData.acidity) {
            setError('Please select your preferences for sweetness, body, and acidity');
            return;
        }
        
        setLoading(true);

        try {
            await authService.signupStep3(formData);
            navigate('/dashboard'); // Redirect to dashboard after successful signup
        } catch (err) {
            setError(err.response?.data?.error || 'An error occurred while saving preferences');
            console.error('Error saving preferences:', err);
        } finally {
            setLoading(false);
        }
    };

    // Group traits by category
    const traitsByCategory = traits.reduce((acc, trait) => {
        if (!acc[trait.category]) {
            acc[trait.category] = [];
        }
        acc[trait.category].push(trait);
        return acc;
    }, {});

    return (
        <div className="min-h-screen bg-gradient-to-br from-wine-900 to-wine-800 py-8 px-4 sm:px-6 lg:px-8">
            <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-lg overflow-hidden">
                {/* Progress Steps */}
                <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center">
                            <Wine className="h-5 w-5 text-wine-600 mr-2" />
                            <span className="text-sm font-medium text-gray-900">Step 3 of 3: Taste Preferences</span>
                        </div>
                        <div className="flex items-center space-x-1">
                            <div className="h-2 w-8 rounded-full bg-wine-600"></div>
                            <div className="h-2 w-8 rounded-full bg-wine-600"></div>
                            <div className="h-2 w-8 rounded-full bg-wine-600"></div>
                        </div>
                    </div>
                </div>
                
                <div className="p-6 sm:p-8">
                    <h2 className="text-2xl font-bold text-gray-900 mb-1">Your Taste Preferences</h2>
                    <p className="text-gray-600 mb-6">Tell us about your taste preferences to help us recommend wines you'll love.</p>
                    
                    {error && (
                        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6 flex items-center">
                            <AlertCircle className="h-5 w-5 mr-2" />
                            <span>{error}</span>
                        </div>
                    )}

                    {loadingTraits ? (
                        <div className="text-center py-8">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-wine-600 mx-auto"></div>
                            <p className="mt-4 text-gray-500">Loading taste preferences...</p>
                        </div>
                    ) : (
                        <form onSubmit={handleSubmit} className="space-y-8">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div>
                                    <label htmlFor="sweetness" className="block text-sm font-medium text-gray-700 mb-1">
                                        Preferred Sweetness Level
                                    </label>
                                    <select
                                        id="sweetness"
                                        name="sweetness"
                                        value={formData.sweetness}
                                        onChange={handleChange}
                                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-wine-500 focus:ring-wine-500"
                                        required
                                    >
                                        <option value="">Select sweetness level</option>
                                        <option value="dry">Dry</option>
                                        <option value="off_dry">Off-Dry</option>
                                        <option value="semi_sweet">Semi-Sweet</option>
                                        <option value="sweet">Sweet</option>
                                    </select>
                                    <p className="mt-1 text-xs text-gray-500">
                                        {formData.sweetness === 'dry' && 'Dry wines have minimal residual sugar, offering a crisp finish.'}
                                        {formData.sweetness === 'off_dry' && 'Off-dry wines have a hint of sweetness that balances acidity.'}
                                        {formData.sweetness === "semi_sweet' && 'Semi-sweet wines have noticeable sweetness but aren't overly sugary."}
                                        {formData.sweetness === 'sweet' && 'Sweet wines have high residual sugar content for a rich, sweet taste.'}
                                    </p>
                                </div>

                                <div>
                                    <label htmlFor="body" className="block text-sm font-medium text-gray-700 mb-1">
                                        Preferred Body
                                    </label>
                                    <select
                                        id="body"
                                        name="body"
                                        value={formData.body}
                                        onChange={handleChange}
                                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-wine-500 focus:ring-wine-500"
                                        required
                                    >
                                        <option value="">Select body type</option>
                                        <option value="light">Light</option>
                                        <option value="medium">Medium</option>
                                        <option value="full">Full</option>
                                    </select>
                                    <p className="mt-1 text-xs text-gray-500">
                                        {formData.body === 'light' && 'Light-bodied wines feel like water in your mouth, refreshing and easy to drink.'}
                                        {formData.body === 'medium' && 'Medium-bodied wines have more substance, similar to the weight of milk.'}
                                        {formData.body === 'full' && 'Full-bodied wines feel heavier and more substantial, like cream.'}
                                    </p>
                                </div>

                                <div>
                                    <label htmlFor="acidity" className="block text-sm font-medium text-gray-700 mb-1">
                                        Preferred Acidity Level
                                    </label>
                                    <select
                                        id="acidity"
                                        name="acidity"
                                        value={formData.acidity}
                                        onChange={handleChange}
                                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-wine-500 focus:ring-wine-500"
                                        required
                                    >
                                        <option value="">Select acidity level</option>
                                        <option value="low">Low</option>
                                        <option value="medium">Medium</option>
                                        <option value="high">High</option>
                                    </select>
                                    <p className="mt-1 text-xs text-gray-500">
                                        {formData.acidity === 'low' && 'Low acidity wines are smoother and less tart.'}
                                        {formData.acidity === 'medium' && 'Medium acidity provides balanced freshness without being too sharp.'}
                                        {formData.acidity === 'high' && 'High acidity wines are crisp, refreshing, and sometimes tart.'}
                                    </p>
                                </div>

                                <div>
                                    <label htmlFor="tannins" className="block text-sm font-medium text-gray-700 mb-1">
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
                                    <p className="mt-1 text-xs text-gray-500">
                                        {formData.tannins === 'low' && 'Low tannin wines are smoother and less astringent.'}
                                        {formData.tannins === 'medium' && 'Medium tannins provide structure without being too grippy.'}
                                        {formData.tannins === 'high' && 'High tannin wines create a drying, grippy sensation in your mouth.'}
                                    </p>
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-3">
                                    Preferred Flavor Profiles
                                </label>
                                <p className="text-xs text-gray-500 mb-4">Select all the flavors you typically enjoy in wines.</p>
                                
                                {Object.entries(traitsByCategory).map(([category, categoryTraits]) => (
                                    <div key={category} className="mb-6">
                                        <h3 className="text-sm font-medium text-gray-700 mb-2 capitalize">{category} Flavors</h3>
                                        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                                            {categoryTraits.map(trait => (
                                                <label key={trait.id} className="flex items-center p-2 border rounded-md hover:bg-gray-50">
                                                    <input
                                                        type="checkbox"
                                                        name="flavors"
                                                        value={trait.id}
                                                        checked={formData.flavors.includes(trait.id)}
                                                        onChange={handleChange}
                                                        className="h-4 w-4 text-wine-600 focus:ring-wine-500 border-gray-300 rounded"
                                                    />
                                                    <span className="ml-2 text-sm text-gray-900">
                                                        {trait.name}
                                                    </span>
                                                </label>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>

                            <div className="flex justify-between pt-6 border-t border-gray-200">
                                <Link
                                    to="/signup/step2"
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
                                            Completing Signup...
                                        </>
                                    ) : (
                                        <>
                                            Complete Signup
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

export default SignupStep3;