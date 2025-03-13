import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext'; // Assuming you have an AuthContext

const Login = () => {
    const { login } = useAuth(); // Assuming you have a login function in your Auth Context
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            await login(email, password);
            // Redirect to home or another page after successful login
        } catch (err) {
            setError('Failed to log in. Please check your credentials.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container mx-auto px-4 py-16">
            <h1 className="text-4xl font-bold mb-4">Login</h1>
            {error && <div className="text-red-600 mb-4">{error}</div>}
            <form onSubmit={handleSubmit}>
                <div className="mb-4">
                    <label className="block text-lg">Email</label>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="border rounded p-2 w-full"
                        required
                    />
                </div>
                <div className="mb-4">
                    <label className="block text-lg">Password</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="border rounded p-2 w-full"
                        required
                    />
                </div>
                <button 
                    type="submit" 
                    className="bg-wine-primary text-white px-4 py-2 rounded"
                    disabled={loading}
                >
                    {loading ? 'Logging in...' : 'Login'}
                </button>
            </form>
        </div>
    );
};

export default Login;