import React, { useEffect, useState } from 'react';
import { fetchWines } from '../services/wineService';
import WineCard from '../components/WineCard';
import SearchBar from '../components/SearchBar';

const Catalog = () => {
    const [wines, setWines] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

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

    if (loading) return <div>Loading...</div>;
    if (error) return <div>{error}</div>;

    return (
        <div className="catalog">
            <h1 className="text-3xl font-bold mb-4">Wine Catalog</h1>
            <SearchBar />
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {wines.map(wine => (
                    <WineCard key={wine.id} wine={wine} />
                ))}
            </div>
        </div>
    );
};

export default Catalog;