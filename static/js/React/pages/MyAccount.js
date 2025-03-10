import React, { useEffect, useState } from 'react';
import { getUserDetails, updateUserDetails } from '../services/userService'; // Create this service

const MyAccount = () => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');

    useEffect(() => {
        const loadUser = async () => {
            try {
                const userData = await getUserDetails();
                setUser(userData);
                setName(userData.name);
                setEmail(userData.email);
            } catch (err) {
                setError('Failed to load user details.');
            } finally {
                setLoading(false);
            }
        };

        loadUser();
    }, []);

    const handleUpdate = async (e) => {
        e.preventDefault();
        try {
            const updatedUser = await updateUserDetails({ name, email });
            setUser(updatedUser);
            setError('User details updated successfully.');
        } catch (err) {
            setError('Failed to update user details.');
        }
    };

    if (loading) return <div>Loading...</div>;
    if (error) return <div>{error}</div>;

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-4xl font-bold mb-4">My Account</h1>
            <form onSubmit={handleUpdate}>
                <div className="mb-4">
                    <label className="block text-lg">Name</label>
                    <input
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        className="border rounded p-2 w-full"
                    />
                </div>
                <div className="mb-4">
                    <label className="block text-lg">Email</label>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="border rounded p-2 w-full"
                    />
                </div>
                <button type="submit" className="bg-wine-primary text-white px-4 py-2 rounded">
                    Update
                </button>
            </form>
        </div>
    );
};

export default MyAccount;