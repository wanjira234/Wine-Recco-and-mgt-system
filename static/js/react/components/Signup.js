const Signup = () => {
    const [formData, setFormData] = React.useState({
        first_name: '',
        last_name: '',
        email: '',
        password: '',
        confirm_password: ''
    });
    const [error, setError] = React.useState('');
    const [loading, setLoading] = React.useState(false);
    const history = ReactRouterDOM.useHistory();

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        if (formData.password !== formData.confirm_password) {
            setError('Passwords do not match');
            setLoading(false);
            return;
        }

        try {
            const response = await fetch('/api/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    first_name: formData.first_name,
                    last_name: formData.last_name,
                    email: formData.email,
                    password: formData.password
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Signup failed');
            }

            // Redirect to step 2
            history.push('/signup/step2');
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
                        Create your account
                    </h2>
                    <p className="mt-2 text-center text-sm text-gray-600">
                        Step 1 of 3: Basic Information
                    </p>
                </div>
                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                    {error && (
                        <div className="rounded-md bg-red-50 p-4">
                            <div className="text-sm text-red-700">{error}</div>
                        </div>
                    )}
                    <div className="rounded-md shadow-sm -space-y-px">
                        <div>
                            <label htmlFor="first_name" className="sr-only">First Name</label>
                            <input
                                id="first_name"
                                name="first_name"
                                type="text"
                                required
                                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-wine-500 focus:border-wine-500 focus:z-10 sm:text-sm"
                                placeholder="First Name"
                                value={formData.first_name}
                                onChange={handleChange}
                            />
                        </div>
                        <div>
                            <label htmlFor="last_name" className="sr-only">Last Name</label>
                            <input
                                id="last_name"
                                name="last_name"
                                type="text"
                                required
                                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-wine-500 focus:border-wine-500 focus:z-10 sm:text-sm"
                                placeholder="Last Name"
                                value={formData.last_name}
                                onChange={handleChange}
                            />
                        </div>
                        <div>
                            <label htmlFor="email" className="sr-only">Email address</label>
                            <input
                                id="email"
                                name="email"
                                type="email"
                                required
                                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-wine-500 focus:border-wine-500 focus:z-10 sm:text-sm"
                                placeholder="Email address"
                                value={formData.email}
                                onChange={handleChange}
                            />
                        </div>
                        <div>
                            <label htmlFor="password" className="sr-only">Password</label>
                            <input
                                id="password"
                                name="password"
                                type="password"
                                required
                                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-wine-500 focus:border-wine-500 focus:z-10 sm:text-sm"
                                placeholder="Password"
                                value={formData.password}
                                onChange={handleChange}
                            />
                        </div>
                        <div>
                            <label htmlFor="confirm_password" className="sr-only">Confirm Password</label>
                            <input
                                id="confirm_password"
                                name="confirm_password"
                                type="password"
                                required
                                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-wine-500 focus:border-wine-500 focus:z-10 sm:text-sm"
                                placeholder="Confirm Password"
                                value={formData.confirm_password}
                                onChange={handleChange}
                            />
                        </div>
                    </div>

                    <div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-wine-600 hover:bg-wine-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-wine-500"
                        >
                            {loading ? 'Creating account...' : 'Next: Wine Preferences'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}; 