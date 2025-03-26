const SignupStep3 = () => {
    const [preferences, setPreferences] = React.useState({
        sweetness: '',
        body: '',
        acidity: '',
        tannins: '',
        flavors: []
    });
    const [error, setError] = React.useState('');
    const [loading, setLoading] = React.useState(false);
    const history = ReactRouterDOM.useHistory();

    const sweetnessLevels = [
        'Very Sweet',
        'Sweet',
        'Off-Dry',
        'Dry',
        'Very Dry'
    ];

    const bodyLevels = [
        'Light',
        'Medium-Light',
        'Medium',
        'Medium-Full',
        'Full'
    ];

    const acidityLevels = [
        'Low',
        'Medium-Low',
        'Medium',
        'Medium-High',
        'High'
    ];

    const tanninLevels = [
        'Low',
        'Medium-Low',
        'Medium',
        'Medium-High',
        'High'
    ];

    const flavorOptions = [
        'Fruit',
        'Floral',
        'Herbal',
        'Spicy',
        'Earthy',
        'Oak',
        'Vanilla',
        'Chocolate',
        'Coffee',
        'Tobacco'
    ];

    const handleFlavorChange = (flavor) => {
        setPreferences(prev => ({
            ...prev,
            flavors: prev.flavors.includes(flavor)
                ? prev.flavors.filter(f => f !== flavor)
                : [...prev.flavors, flavor]
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const response = await fetch('/api/signup/step3', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    taste_preferences: preferences
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to save preferences');
            }

            // Redirect to home page
            window.location.href = '/';
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
                        Taste Preferences
                    </h2>
                    <p className="mt-2 text-center text-sm text-gray-600">
                        Step 3 of 3: Tell us about your taste preferences
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
                                Preferred Sweetness Level
                            </label>
                            <select
                                value={preferences.sweetness}
                                onChange={(e) => setPreferences(prev => ({ ...prev, sweetness: e.target.value }))}
                                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-wine-500 focus:border-wine-500 sm:text-sm rounded-md"
                            >
                                <option value="">Select sweetness level</option>
                                {sweetnessLevels.map(level => (
                                    <option key={level} value={level}>{level}</option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700">
                                Preferred Body Style
                            </label>
                            <select
                                value={preferences.body}
                                onChange={(e) => setPreferences(prev => ({ ...prev, body: e.target.value }))}
                                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-wine-500 focus:border-wine-500 sm:text-sm rounded-md"
                            >
                                <option value="">Select body style</option>
                                {bodyLevels.map(level => (
                                    <option key={level} value={level}>{level}</option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700">
                                Preferred Acidity Level
                            </label>
                            <select
                                value={preferences.acidity}
                                onChange={(e) => setPreferences(prev => ({ ...prev, acidity: e.target.value }))}
                                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-wine-500 focus:border-wine-500 sm:text-sm rounded-md"
                            >
                                <option value="">Select acidity level</option>
                                {acidityLevels.map(level => (
                                    <option key={level} value={level}>{level}</option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700">
                                Preferred Tannin Level
                            </label>
                            <select
                                value={preferences.tannins}
                                onChange={(e) => setPreferences(prev => ({ ...prev, tannins: e.target.value }))}
                                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-wine-500 focus:border-wine-500 sm:text-sm rounded-md"
                            >
                                <option value="">Select tannin level</option>
                                {tanninLevels.map(level => (
                                    <option key={level} value={level}>{level}</option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700">
                                Preferred Flavors (Select all that apply)
                            </label>
                            <div className="mt-2 grid grid-cols-2 gap-2">
                                {flavorOptions.map(flavor => (
                                    <div key={flavor} className="flex items-center">
                                        <input
                                            id={flavor}
                                            type="checkbox"
                                            checked={preferences.flavors.includes(flavor)}
                                            onChange={() => handleFlavorChange(flavor)}
                                            className="h-4 w-4 text-wine-600 focus:ring-wine-500 border-gray-300 rounded"
                                        />
                                        <label htmlFor={flavor} className="ml-2 block text-sm text-gray-900">
                                            {flavor}
                                        </label>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    <div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-wine-600 hover:bg-wine-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-wine-500"
                        >
                            {loading ? 'Saving preferences...' : 'Complete Signup'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}; 