import React, { useEffect, useState } from 'react';
import { fetchWines, deleteWine } from '../services/wineService';
import WineForm from '../components/WineForm';

const Admin = () => {
    const [wines, setWines] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [editingWine, setEditingWine] = useState(null);

    useEffect(() => {
        const loadWines = async () => {
            try {
                const wineData = await fetchWines();
                setWines(wineData);
            } catch (err) {
                setError('Failed to load wines.');
            } finally {
                setLoading(false);
            }
        };

        loadWines();
    }, []);

    const handleDelete = async (id) => {
        await deleteWine(id);
        setWines(wines.filter(wine => wine.id !== id));
    };

    const handleEdit = (wine) => {
        setEditingWine(wine);
    };

    const handleFormSubmit = async (wineData) => {
        if (editingWine) {
            // Handle update logic
        } else {
            // Handle add logic
        }
        setEditingWine(null);
        const updatedWines = await fetchWines();
        setWines(updatedWines);
    };

    if (loading) return <div>Loading...</div>;
    if (error) return <div>{error}</div>;

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-4xl font-bold mb-4">Admin Panel</h1>
            <WineForm wine={editingWine} onSubmit={handleFormSubmit} />
            <h2 className="text-2xl font-semibold mt-8">Current Wines</h2>
            <ul>
                {wines.map(wine => (
                    <li key={wine.id} className="flex justify-between items-center mt-4">
                        <span>{wine.name}</span>
                        <div>
                            <button onClick={() => handleEdit(wine)} className="mr-2">Edit</button>
                            <button onClick={() => handleDelete(wine.id)} className="text-red-500">Delete</button>
                        </div>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default Admin;