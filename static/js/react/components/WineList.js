import React, { useState, useEffect } from 'react';
import { wineService } from '../services/api';
import WineCard from './WineCard';

const WineList = () => {
    const [wines, setWines] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [filters, setFilters] = useState({
        category: '',
        priceRange: '',
        search: ''
    });

    useEffect(() => {
        fetchWines();
    }, [filters]);

    const fetchWines = async () => {
        try {
            setLoading(true);
            const response = await wineService.getWines(filters);
            setWines(response.data);
        } catch (err) {
            setError('Failed to load wines. Please try again later.');
        } finally {
            setLoading(false);
        }
    };

    const handleFilterChange = (e) => {
        const { name, value } = e.target;
        setFilters(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSearch = (e) => {
        e.preventDefault();
        fetchWines();
    };

    return (
        <div className="min-h-screen bg-gray-100 py-6">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                {/* Filters Section */}
                <div className="bg-white shadow rounded-lg p-6 mb-6">
                    <h2 className="text-xl font-semibold text-gray-900 mb-4">Filter Wines</h2>
                    <form onSubmit={handleSearch} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div>
                                <label htmlFor="category" className="block text-sm font-medium text-gray-700">
                                    Category
                                </label>
                                <select
                                    id="category"
                                    name="category"
                                    value={filters.category}
                                    onChange={handleFilterChange}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-wine-500 focus:ring-wine-500"
                                >
                                    <option value="">All Categories</option>
                                    <option value="red">Red Wine</option>
                                    <option value="white">White Wine</option>
                                    <option value="rose">Rosé Wine</option>
                                    <option value="sparkling">Sparkling Wine</option>
                                </select>
                            </div>
                            <div>
                                <label htmlFor="priceRange" className="block text-sm font-medium text-gray-700">
                                    Price Range
                                </label>
                                <select
                                    id="priceRange"
                                    name="priceRange"
                                    value={filters.priceRange}
                                    onChange={handleFilterChange}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-wine-500 focus:ring-wine-500"
                                >
                                    <option value="">All Prices</option>
                                    <option value="0-20">Under $20</option>
                                    <option value="20-50">$20 - $50</option>
                                    <option value="50-100">$50 - $100</option>
                                    <option value="100+">Over $100</option>
                                </select>
                            </div>
                            <div>
                                <label htmlFor="search" className="block text-sm font-medium text-gray-700">
                                    Search
                                </label>
                                <input
                                    type="text"
                                    id="search"
                                    name="search"
                                    value={filters.search}
                                    onChange={handleFilterChange}
                                    placeholder="Search wines..."
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-wine-500 focus:ring-wine-500"
                                />
                            </div>
                        </div>
                        <button
                            type="submit"
                            className="w-full md:w-auto px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-wine-600 hover:bg-wine-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-wine-500"
                        >
                            Apply Filters
                        </button>
                    </form>
                </div>

                {/* Wines Grid */}
                <div className="bg-white shadow rounded-lg p-6">
                    <h2 className="text-2xl font-bold text-gray-900 mb-6">Our Wine Collection</h2>
                    {loading ? (
                        <div className="text-center py-12">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-wine-600 mx-auto"></div>
                        </div>
                    ) : error ? (
                        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                            {error}
                        </div>
                    ) : wines.length === 0 ? (
                        <div className="text-center py-12 text-gray-500">
                            No wines found matching your criteria.
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                            {wines.map(wine => (
                                <WineCard key={wine.id} wine={wine} />
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default WineList; 