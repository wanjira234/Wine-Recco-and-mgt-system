const SignupStep2 = () => {
    const [preferences, setPreferences] = React.useState({
        wine_types: [],
        price_range: '',
        occasion: ''
    });
    const [error, setError] = React.useState('');
    const [loading, setLoading] = React.useState(false);
    const history = ReactRouterDOM.useHistory();

    const wineTypes = [
        'Red Wine',
        'White Wine',
        'Rosé',
        'Sparkling Wine',
        'Dessert Wine'
    ];

    const priceRanges = [
        'Under $20',
        '$20 - $50',
        '$50 - $100',
        'Over $100'
    ];

    const occasions = [
        'Casual Drinking',
        'Special Occasions',
        'Food Pairing',
        'Gift Giving'
    ];

    const handleWineTypeChange = (type) => {
        setPreferences(prev => ({
            ...prev,
            wine_types: prev.wine_types.includes(type)
                ? prev.wine_types.filter(t => t !== type)
                : [...prev.wine_types, type]
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const response = await fetch('/api/signup/step2', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    wine_preferences: preferences
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to save preferences');
            }

            // Redirect to step 3
            history.push('/signup/step3');
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-lg shadow-lg">
                <div>
                    <h2 className="mt-6 text-center text-3xl font-extrabold text-wine-900">
                        Wine Preferences
                    </h2>
                    <p className="mt-2 text-center text-sm text-gray-600">
                        Step 2 of 3: Tell us about your wine preferences
                    </p>
                </div>
                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                    {error && (
                        <div className="rounded-md bg-red-50 p-4">
                            <div className="text-sm text-red-700">{error}</div>
                        </div>
                    )}
                    
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">
                                What types of wine do you enjoy?
                            </label>
                            <div className="mt-2 space-y-2">
                                {wineTypes.map(type => (
                                    <div key={type} className="flex items-center">
                                        <input
                                            id={type}
                                            type="checkbox"
                                            checked={preferences.wine_types.includes(type)}
                                            onChange={() => handleWineTypeChange(type)}
                                            className="h-4 w-4 text-wine-600 focus:ring-wine-500 border-gray-300 rounded"
                                        />
                                        <label htmlFor={type} className="ml-2 block text-sm text-gray-900">
                                            {type}
                                        </label>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700">
                                Preferred Price Range
                            </label>
                            <select
                                value={preferences.price_range}
                                onChange={(e) => setPreferences(prev => ({ ...prev, price_range: e.target.value }))}
                                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-wine-500 focus:border-wine-500 sm:text-sm rounded-md"
                            >
                                <option value="">Select a price range</option>
                                {priceRanges.map(range => (
                                    <option key={range} value={range}>{range}</option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700">
                                Primary Occasion for Wine
                            </label>
                            <select
                                value={preferences.occasion}
                                onChange={(e) => setPreferences(prev => ({ ...prev, occasion: e.target.value }))}
                                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-wine-500 focus:border-wine-500 sm:text-sm rounded-md"
                            >
                                <option value="">Select an occasion</option>
                                {occasions.map(occasion => (
                                    <option key={occasion} value={occasion}>{occasion}</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    <div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-wine-600 hover:bg-wine-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-wine-500"
                        >
                            {loading ? 'Saving preferences...' : 'Next: Taste Preferences'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}; 