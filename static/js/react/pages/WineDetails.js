import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { fetchWineDetails } from '../services/wineService';

const WineDetails = () => {
    const { id } = useParams();
    const [wine, setWine] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const loadWineDetails = async () => {
            try {
                const wineData = await fetchWineDetails(id);
                setWine(wineData);
            } catch (err) {
                setError('Failed to load wine details.');
            } finally {
                setLoading(false);
            }
        };

        loadWineDetails();
    }, [id]);

    if (loading) return <div>Loading...</div>;
    if (error) return <div>{error}</div>;

    return (
        <div className="wine-details">
            <h1 className="text-3xl font-bold">{wine.name}</h1>
            <img src={wine.image} alt={wine.name} className="w-full h-64 object-cover" />
            <p className="mt-4">{wine.description}</p>
            <button className="mt-4 bg-blue-500 text-white p-2 rounded">
                Add to Cart
            </button>
        </div>
    );
};

export default WineDetails;