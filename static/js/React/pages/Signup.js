import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';

const Signup = () => {
    const { signup } = useAuth();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [wineTraits, setWineTraits] = useState([]);
    const [selectedTraits, setSelectedTraits] = useState([]);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchWineTraits = async () => {
            try {
                const response = await fetch('/api/wines/traits'); // Update the path as necessary
                const data = await response.json();
                setWineTraits(data);
            } catch (err) {
                setError('Failed to load wine traits.');
            }
        };

        fetchWineTraits();
    }, []);

    const handleTraitChange = (traitId) => {
        setSelectedTraits((prev) =>
            prev.includes(traitId) ? prev.filter((id) => id !== traitId) : [...prev, traitId]
        );
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await signup(email, password, selectedTraits);
            // Redirect or show success message
        } catch (err) {
            setError('Failed to create an account. Please try again.');
        }
    };

    return (
        <div className="container mx-auto px-4 py-16">
            <h1 className="text-4xl font-bold mb-4">Signup</h1>
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
                <div className="mb-4">
                    <label className="block text-lg">Select Your Wine Traits:</label>
                    {wineTraits.map((trait) => (
                        <div key={trait.id} className="flex items-center">
                            <input
                                type="checkbox"
                                id={`trait-${trait.id}`}
                                checked={selectedTraits.includes(trait.id)}
                                onChange={() => handleTraitChange(trait.id)}
                                className="mr-2"
                            />
                            <label htmlFor={`trait-${trait.id}`}>{trait.name}</label>
                        </div>
                    ))}
                </div>
                <button type="submit" className="bg-wine-primary text-white px-4 py-2 rounded">
                    Signup
                </button>
            </form>
        </div>
    );
};

export default Signup;