import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';

const Search = () => {
    const navigate = useNavigate();
    const [searchQuery, setSearchQuery] = useState('');
    const [filters, setFilters] = useState({
        category: '',
        price_range: '',
        region: '',
        variety: '',
        vintage: ''
    });
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [categories, setCategories] = useState([]);
    const [regions, setRegions] = useState([]);
    const [varieties, setVarieties] = useState([]);

    useEffect(() => {
        const fetchFilterOptions = async () => {
            try {
                const [categoriesRes, regionsRes, varietiesRes] = await Promise.all([
                    fetch('/api/categories'),
                    fetch('/api/regions'),
                    fetch('/api/varieties')
                ]);

                if (!categoriesRes.ok || !regionsRes.ok || !varietiesRes.ok) {
                    throw new Error('Failed to fetch filter options');
                }

                const [categoriesData, regionsData, varietiesData] = await Promise.all([
                    categoriesRes.json(),
                    regionsRes.json(),
                    varietiesRes.json()
                ]);

                setCategories(categoriesData.categories);
                setRegions(regionsData.regions);
                setVarieties(varietiesData.varieties);
            } catch (error) {
                toast.error('Failed to load filter options');
            }
        };

        fetchFilterOptions();
    }, []);

    const handleSearch = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            const queryParams = new URLSearchParams({
                q: searchQuery,
                ...filters
            });

            const response = await fetch(`/api/search?${queryParams}`);
            if (!response.ok) {
                throw new Error('Search failed');
            }

            const data = await response.json();
            setResults(data.wines);
        } catch (error) {
            toast.error('Search failed');
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

    const handleWineClick = (wineId) => {
        navigate(`/wines/${wineId}`);
    };

    return (
        <div className="min-h-screen bg-gray-100 py-8">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <h1 className="text-3xl font-bold text-gray-900 mb-8">Search Wines</h1>

                {/* Search Form */}
                <div className="bg-white rounded-lg shadow-md p-6 mb-8">
                    <form onSubmit={handleSearch} className="space-y-4">
                        <div className="flex gap-4">
                            <div className="flex-1">
                                <input
                                    type="text"
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    placeholder="Search wines..."
                                    className="w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
                                />
                            </div>
                            <button
                                type="submit"
                                disabled={loading}
                                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:opacity-50"
                            >
                                {loading ? 'Searching...' : 'Search'}
                            </button>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Category</label>
                                <select
                                    name="category"
                                    value={filters.category}
                                    onChange={handleFilterChange}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
                                >
                                    <option value="">All Categories</option>
                                    {categories.map(category => (
                                        <option key={category.id} value={category.id}>
                                            {category.name}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700">Region</label>
                                <select
                                    name="region"
                                    value={filters.region}
                                    onChange={handleFilterChange}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
                                >
                                    <option value="">All Regions</option>
                                    {regions.map(region => (
                                        <option key={region.id} value={region.id}>
                                            {region.name}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700">Variety</label>
                                <select
                                    name="variety"
                                    value={filters.variety}
                                    onChange={handleFilterChange}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
                                >
                                    <option value="">All Varieties</option>
                                    {varieties.map(variety => (
                                        <option key={variety.id} value={variety.id}>
                                            {variety.name}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700">Price Range</label>
                                <select
                                    name="price_range"
                                    value={filters.price_range}
                                    onChange={handleFilterChange}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
                                >
                                    <option value="">Any Price</option>
                                    <option value="0-20">Under $20</option>
                                    <option value="20-50">$20 - $50</option>
                                    <option value="50-100">$50 - $100</option>
                                    <option value="100+">Over $100</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700">Vintage</label>
                                <input
                                    type="number"
                                    name="vintage"
                                    value={filters.vintage}
                                    onChange={handleFilterChange}
                                    placeholder="Year"
                                    min="1900"
                                    max={new Date().getFullYear()}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
                                />
                            </div>
                        </div>
                    </form>
                </div>

                {/* Search Results */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {results.map(wine => (
                        <div
                            key={wine.id}
                            onClick={() => handleWineClick(wine.id)}
                            className="bg-white rounded-lg shadow-md overflow-hidden cursor-pointer hover:shadow-lg transition-shadow"
                        >
                            <img
                                src={wine.image_url}
                                alt={wine.name}
                                className="w-full h-48 object-cover"
                            />
                            <div className="p-4">
                                <h3 className="text-lg font-semibold text-gray-900">{wine.name}</h3>
                                <p className="text-sm text-gray-500">{wine.variety}</p>
                                <p className="text-sm text-gray-500">{wine.region}</p>
                                <p className="text-sm text-gray-500">{wine.vintage}</p>
                                <p className="mt-2 text-lg font-semibold text-purple-600">
                                    ${wine.price}
                                </p>
                            </div>
                        </div>
                    ))}
                </div>

                {results.length === 0 && !loading && (
                    <div className="text-center py-12">
                        <p className="text-gray-500">No wines found matching your criteria.</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Search; 