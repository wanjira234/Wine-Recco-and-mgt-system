import React, { useState, useEffect } from 'react';
import { wineService } from '../services/api';
import WineCard from './WineCard';
import { Filter, Search, ChevronDown, Wine, SlidersHorizontal, X } from 'lucide-react';

const WineList = () => {
    const [wines, setWines] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [filters, setFilters] = useState({
        category: '',
        priceRange: '',
        region: '',
        rating: '',
        search: ''
    });
    const [showMobileFilters, setShowMobileFilters] = useState(false);
    const [sortBy, setSortBy] = useState('recommended');
    const [totalWines, setTotalWines] = useState(0);
    const [page, setPage] = useState(1);
    const [hasMore, setHasMore] = useState(true);

    useEffect(() => {
        fetchWines(1, true);
    }, [filters, sortBy]);

    const fetchWines = async (pageNum = 1, reset = false) => {
        try {
            setLoading(true);
            const response = await wineService.getWines({
                ...filters,
                page: pageNum,
                sort: sortBy
            });
            
            if (reset) {
                setWines(response.data.wines);
            } else {
                setWines(prev => [...prev, ...response.data.wines]);
            }
            
            setTotalWines(response.data.total);
            setHasMore(response.data.wines.length > 0 && response.data.wines.length === response.data.per_page);
            setPage(pageNum);
        } catch (err) {
            console.error('Error fetching wines:', err);
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
        fetchWines(1, true);
    };
    
    const handleSortChange = (e) => {
        setSortBy(e.target.value);
    };
    
    const handleLoadMore = () => {
        if (!loading && hasMore) {
            fetchWines(page + 1);
        }
    };
    
    const clearFilters = () => {
        setFilters({
            category: '',
            priceRange: '',
            region: '',
            rating: '',
            search: ''
        });
    };
    
    const hasActiveFilters = Object.values(filters).some(value => value !== '');

    return (
        <div className="min-h-screen bg-gray-100 py-8">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                {/* Page Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">Wine Collection</h1>
                    <p className="mt-2 text-gray-600">Discover our curated selection of exceptional wines from around the world</p>
                </div>
                
                {/* Search and Sort Bar - Desktop */}
                <div className="bg-white shadow rounded-lg p-4 mb-6 hidden md:block">
                    <div className="flex items-center justify-between">
                        <form onSubmit={handleSearch} className="flex-1 mr-4">
                            <div className="relative">
                                <input
                                    type="text"
                                    name="search"
                                    value={filters.search}
                                    onChange={handleFilterChange}
                                    placeholder="Search wines, regions, or varieties..."
                                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-wine-500 focus:border-wine-500"
                                />
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <Search className="h-5 w-5 text-gray-400" />
                                </div>
                                {filters.search && (
                                    <button
                                        type="button"
                                        onClick={() => setFilters({...filters, search: ''})}
                                        className="absolute inset-y-0 right-0 pr-3 flex items-center"
                                    >
                                        <X className="h-4 w-4 text-gray-400 hover:text-gray-600" />
                                    </button>
                                )}
                            </div>
                        </form>
                        
                        <div className="flex items-center">
                            <label htmlFor="sort" className="mr-2 text-sm font-medium text-gray-700">Sort by:</label>
                            <div className="relative">
                                <select
                                    id="sort"
                                    value={sortBy}
                                    onChange={handleSortChange}
                                    className="appearance-none pl-3 pr-8 py-2 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-wine-500 focus:border-wine-500 text-sm"
                                >
                                    <option value="recommended">Recommended</option>
                                    <option value="price_asc">Price: Low to High</option>
                                    <option value="price_desc">Price: High to Low</option>
                                    <option value="rating_desc">Highest Rated</option>
                                    <option value="newest">Newest</option>
                                </select>
                                <div className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
                                    <ChevronDown className="h-4 w-4 text-gray-400" />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                {/* Mobile Search and Filter Toggle */}
                <div className="bg-white shadow rounded-lg p-4 mb-6 md:hidden">
                    <form onSubmit={handleSearch} className="mb-4">
                        <div className="relative">
                            <input
                                type="text"
                                name="search"
                                value={filters.search}
                                onChange={handleFilterChange}
                                placeholder="Search wines..."
                                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-wine-500 focus:border-wine-500"
                            />
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <Search className="h-5 w-5 text-gray-400" />
                            </div>
                        </div>
                    </form>
                    
                    <div className="flex justify-between">
                        <button
                            type="button"
                            onClick={() => setShowMobileFilters(!showMobileFilters)}
                            className="flex items-center px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                        >
                            <Filter className="h-4 w-4 mr-2" />
                            Filters {hasActiveFilters && <span className="ml-1 bg-wine-600 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs">!</span>}
                        </button>
                        
                        <div className="relative">
                            <select
                                value={sortBy}
                                onChange={handleSortChange}
                                className="appearance-none pl-3 pr-8 py-2 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-wine-500 focus:border-wine-500 text-sm"
                            >
                                <option value="recommended">Recommended</option>
                                <option value="price_asc">Price: Low to High</option>
                                <option value="price_desc">Price: High to Low</option>
                                <option value="rating_desc">Highest Rated</option>
                                <option value="newest">Newest</option>
                            </select>
                            <div className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
                                <ChevronDown className="h-4 w-4 text-gray-400" />
                            </div>
                        </div>
                    </div>
                </div>

                <div className="flex flex-col md:flex-row gap-6">
                    {/* Filters Section - Desktop */}
                    <div className="w-full md:w-64 hidden md:block">
                        <div className="bg-white shadow rounded-lg p-4 sticky top-4">
                            <div className="flex items-center justify-between mb-4">
                                <h2 className="text-lg font-medium text-gray-900 flex items-center">
                                    <SlidersHorizontal className="h-5 w-5 mr-2 text-wine-600" />
                                    Filters
                                </h2>
                                {hasActiveFilters && (
                                    <button
                                        type="button"
                                        onClick={clearFilters}
                                        className="text-sm text-wine-600 hover:text-wine-800"
                                    >
                                        Clear all
                                    </button>
                                )}
                            </div>
                            
                            <div className="space-y-6">
                                <div>
                                    <h3 className="text-sm font-medium text-gray-900 mb-2">Wine Type</h3>
                                    <div className="space-y-2">
                                        <label className="flex items-center">
                                            <input
                                                type="radio"
                                                name="category"
                                                value=""
                                                checked={filters.category === ''}
                                                onChange={handleFilterChange}
                                                className="h-4 w-4 text-wine-600 focus:ring-wine-500 border-gray-300"
                                            />
                                            <span className="ml-2 text-sm text-gray-700">All Types</span>
                                        </label>
                                        <label className="flex items-center">
                                            <input
                                                type="radio"
                                                name="category"
                                                value="red"
                                                checked={filters.category === 'red'}
                                                onChange={handleFilterChange}
                                                className="h-4 w-4 text-wine-600 focus:ring-wine-500 border-gray-300"
                                            />
                                            <span className="ml-2 text-sm text-gray-700">Red Wine</span>
                                        </label>
                                        <label className="flex items-center">
                                            <input
                                                type="radio"
                                                name="category"
                                                value="white"
                                                checked={filters.category === 'white'}
                                                onChange={handleFilterChange}
                                                className="h-4 w-4 text-wine-600 focus:ring-wine-500 border-gray-300"
                                            />
                                            <span className="ml-2 text-sm text-gray-700">White Wine</span>
                                        </label>
                                        <label className="flex items-center">
                                            <input
                                                type="radio"
                                                name="category"
                                                value="rose"
                                                checked={filters.category === 'rose'}
                                                onChange={handleFilterChange}
                                                className="h-4 w-4 text-wine-600 focus:ring-wine-500 border-gray-300"
                                            />
                                            <span className="ml-2 text-sm text-gray-700">Rosé Wine</span>
                                        </label>
                                        <label className="flex items-center">
                                            <input
                                                type="radio"
                                                name="category"
                                                value="sparkling"
                                                checked={filters.category === 'sparkling'}
                                                onChange={handleFilterChange}
                                                className="h-4 w-4 text-wine-600 focus:ring-wine-500 border-gray-300"
                                            />
                                            <span className="ml-2 text-sm text-gray-700">Sparkling Wine</span>
                                        </label>
                                    </div>
                                </div>
                                
                                <div>
                                    <h3 className="text-sm font-medium text-gray-900 mb-2">Price Range</h3>
                                    <div className="space-y-2">
                                        <label className="flex items-center">
                                            <input
                                                type="radio"
                                                name="priceRange"
                                                value=""
                                                checked={filters.priceRange === ''}
                                                onChange={handleFilterChange}
                                                className="h-4 w-4 text-wine-600 focus:ring-wine-500 border-gray-300"
                                            />
                                            <span className="ml-2 text-sm text-gray-700">All Prices</span>
                                        </label>
                                        <label className="flex items-center">
                                            <input
                                                type="radio"
                                                name="priceRange"
                                                value="0-20"
                                                checked={filters.priceRange === '0-20'}
                                                onChange={handleFilterChange}
                                                className="h-4 w-4 text-wine-600 focus:ring-wine-500 border-gray-300"
                                            />
                                            <span className="ml-2 text-sm text-gray-700">Under $20</span>
                                        </label>
                                        <label className="flex items-center">
                                            <input
                                                type="radio"
                                                name="priceRange"
                                                value="20-50"
                                                checked={filters.priceRange === '20-50'}
                                                onChange={handleFilterChange}
                                                className="h-4 w-4 text-wine-600 focus:ring-wine-500 border-gray-300"
                                            />
                                            <span className="ml-2 text-sm text-gray-700">$20 - $50</span>
                                        </label>
                                        <label className="flex items-center">
                                            <input
                                                type="radio"
                                                name="priceRange"
                                                value="50-100"
                                                checked={filters.priceRange === '50-100'}
                                                onChange={handleFilterChange}
                                                className="h-4 w-4 text-wine-600 focus:ring-wine-500 border-gray-300"
                                            />
                                            <span className="ml-2 text-sm text-gray-700">$50 - $100</span>
                                        </label>
                                        <label className="flex items-center">
                                            <input
                                                type="radio"
                                                name="priceRange"
                                                value="100+"
                                                checked={filters.priceRange === '100+'}
                                                onChange={handleFilterChange}
                                                className="h-4 w-4 text-wine-600 focus:ring-wine-500 border-gray-300"
                                            />
                                            <span className="ml-2 text-sm text-gray-700">Over $100</span>
                                        </label>
                                    </div>
                                </div>
                                
                                <div>
                                    <h3 className="text-sm font-medium text-gray-900 mb-2">Rating</h3>
                                    <div className="space-y-2">
                                        <label className="flex items-center">
                                            <input
                                                type="radio"
                                                name="rating"
                                                value=""
                                                checked={filters.rating === ''}
                                                onChange={handleFilterChange}
                                                className="h-4 w-4 text-wine-600 focus:ring-wine-500 border-gray-300"
                                            />
                                            <span className="ml-2 text-sm text-gray-700">Any Rating</span>
                                        </label>
                                        <label className="flex items-center">
                                            <input
                                                type="radio"
                                                name="rating"
                                                value="4+"
                                                checked={filters.rating === '4+'}
                                                onChange={handleFilterChange}
                                                className="h-4 w-4 text-wine-600 focus:ring-wine-500 border-gray-300"
                                            />
                                            <span className="ml-2 text-sm text-gray-700">4+ Stars</span>
                                        </label>
                                        <label className="flex items-center">
                                            <input
                                                type="radio"
                                                name="rating"
                                                value="4.5+"
                                                checked={filters.rating === '4.5+'}
                                                onChange={handleFilterChange}
                                                className="h-4 w-4 text-wine-600 focus:ring-wine-500 border-gray-300"
                                            />
                                            <span className="ml-2 text-sm text-gray-700">4.5+ Stars</span>
                                        </label>
                                    </div>
                                </div>
                                
                                <div>
                                    <h3 className="text-sm font-medium text-gray-900 mb-2">Region</h3>
                                    <select
                                        name="region"
                                        value={filters.region}
                                        onChange={handleFilterChange}
                                        className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-wine-500 focus:border-wine-500 sm:text-sm rounded-md"
                                    >
                                        <option value="">All Regions</option>
                                        <option value="france">France</option>
                                        <option value="italy">Italy</option>
                                        <option value="spain">Spain</option>
                                        <option value="usa">United States</option>
                                        <option value="australia">Australia</option>
                                        <option value="argentina">Argentina</option>
                                        <option value="chile">Chile</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    {/* Mobile Filters (Slide-in panel) */}
                    {showMobileFilters && (
                        <div className="fixed inset-0 z-40 md:hidden">
                            <div className="fixed inset-0 bg-black bg-opacity-25" onClick={() => setShowMobileFilters(false)}></div>
                            <div className="fixed inset-y-0 right-0 max-w-xs w-full bg-white shadow-xl flex flex-col">
                                <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
                                    <h2 className="text-lg font-medium text-gray-900">Filters</h2>
                                    <button
                                        type="button"
                                        onClick={() => setShowMobileFilters(false)}
                                        className="text-gray-400 hover:text-gray-500"
                                    >
                                        <X className="h-6 w-6" />
                                    </button>
                                </div>
                                
                                <div className="overflow-y-auto flex-1 p-4">
                                    <div className="space-y-6">
                                        {/* Same filter options as desktop */}
                                        <div>
                                            <h3 className="text-sm font-medium text-gray-900 mb-2">Wine Type</h3>
                                            <div className="space-y-2">
                                                <label className="flex items-center">
                                                    <input
                                                        type="radio"
                                                        name="category"
                                                        value=""
                                                        checked={filters.category === ''}
                                                        onChange={handleFilterChange}
                                                        className="h-4 w-4 text-wine-600 focus:ring-wine-500 border-gray-300"
                                                    />
                                                    <span className="ml-2 text-sm text-gray-700">All Types</span>
                                                </label>
                                                <label className="flex items-center">
                                                    <input
                                                        type="radio"
                                                        name="category"
                                                        value="red"
                                                        checked={filters.category === 'red'}
                                                        onChange={handleFilterChange}
                                                        className="h-4 w-4 text-wine-600 focus:ring-wine-500 border-gray-300"
                                                    />
                                                    <span className="ml-2 text-sm text-gray-700">Red Wine</span>
                                                </label>
                                                <label className="flex items-center">
                                                    <input
                                                        type="radio"
                                                        name="category"
                                                        value="white"
                                                        checked={filters.category === 'white'}
                                                        onChange={handleFilterChange}
                                                        className="h-4 w-4 text-wine-600 focus:ring-wine-500 border-gray-300"
                                                    />
                                                    <span className="ml-2 text-sm text-gray-700">White Wine</span>
                                                </label>
                                                <label className="flex items-center">
                                                    <input
                                                        type="radio"
                                                        name="category"
                                                        value="rose"
                                                        checked={filters.category === 'rose'}
                                                        onChange={handleFilterChange}
                                                        className="h-4 w-4 text-wine-600 focus:ring-wine-500 border-gray-300"
                                                    />
                                                    <span className="ml-2 text-sm text-gray-700">Rosé Wine</span>
                                                </label>
                                                <label className="flex items-center">
                                                    <input
                                                        type="radio"
                                                        name="category"
                                                        value="sparkling"
                                                        checked={filters.category === 'sparkling'}
                                                        onChange={handleFilterChange}
                                                        className="h-4 w-4 text-wine-600 focus:ring-wine-500 border-gray-300"
                                                    />
                                                    <span className="ml-2 text-sm text-gray-700">Sparkling Wine</span>
                                                </label>
                                            </div>
                                        </div>
                                        
                                        <div>
                                            <h3 className="text-sm font-medium text-gray-900 mb-2">Price Range</h3>
                                            <div className="space-y-2">
                                                <label className="flex items-center">
                                                    <input
                                                        type="radio"
                                                        name="priceRange"
                                                        value=""
                                                        checked={filters.priceRange === ''}
                                                        onChange={handleFilterChange}
                                                        className="h-4 w-4 text-wine-600 focus:ring-wine-500 border-gray-300"
                                                    />
                                                    <span className="ml-2 text-sm text-gray-700">All Prices</span>
                                                </label>
                                                <label className="flex items-center">
                                                    <input
                                                        type="radio"
                                                        name="priceRange"
                                                        value="0-20"
                                                        checked={filters.priceRange === '0-20'}
                                                        onChange={handleFilterChange}
                                                        className="h-4 w-4 text-wine-600 focus:ring-wine-500 border-gray-300"
                                                    />
                                                    <span className="ml-2 text-sm text-gray-700">Under $20</span>
                                                </label>
                                                <label className="flex items-center">
                                                    <input
                                                        type="radio"
                                                        name="priceRange"
                                                        value="20-50"
                                                        checked={filters.priceRange === '20-50'}
                                                        onChange={handleFilterChange}
                                                        className="h-4 w-4 text-wine-600 focus:ring-wine-500 border-gray-300"
                                                    />
                                                    <span className="ml-2 text-sm text-gray-700">$20 - $50</span>
                                                </label>
                                                <label className="flex items-center">
                                                    <input
                                                        type="radio"
                                                        name="priceRange"
                                                        value="50-100"
                                                        checked={filters.priceRange === '50-100'}
                                                        onChange={handleFilterChange}
                                                        className="h-4 w-4 text-wine-600 focus:ring-wine-500 border-gray-300"
                                                    />
                                                    <span className="ml-2 text-sm text-gray-700">$50 - $100</span>
                                                </label>
                                                <label className="flex items-center">
                                                    <input
                                                        type="radio"
                                                        name="priceRange"
                                                        value="100+"
                                                        checked={filters.priceRange === '100+'}
                                                        onChange={handleFilterChange}
                                                        className="h-4 w-4 text-wine-600 focus:ring-wine-500 border-gray-300"
                                                    />
                                                    <span className="ml-2 text-sm text-gray-700">Over $100</span>
                                                </label>
                                            </div>
                                        </div>
                                        
                                        <div>
                                            <h3 className="text-sm font-medium text-gray-900 mb-2">Region</h3>
                                            <select
                                                name="region"
                                                value={filters.region}
                                                onChange={handleFilterChange}
                                                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-wine-500 focus:border-wine-500 sm:text-sm rounded-md"
                                            >
                                                <option value="">All Regions</option>
                                                <option value="france">France</option>
                                                <option value="italy">Italy</option>
                                                <option value="spain">Spain</option>
                                                <option value="usa">United States</option>
                                                <option value="australia">Australia</option>
                                                <option value="argentina">Argentina</option>
                                                <option value="chile">Chile</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                                
                                <div className="border-t border-gray-200 p-4">
                                    <div className="flex space-x-3">
                                        <button
                                            type="button"
                                            onClick={clearFilters}
                                            className="flex-1 py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                                        >
                                            Clear All
                                        </button>
                                        <button
                                            type="button"
                                            onClick={() => {
                                                setShowMobileFilters(false);
                                                fetchWines(1, true);
                                            }}
                                            className="flex-1 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-wine-600 hover:bg-wine-700"
                                        >
                                            Apply Filters
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Wines Grid */}
                    <div className="flex-1">
                        {/* Active Filters */}
                        {hasActiveFilters && (
                            <div className="bg-white shadow rounded-lg p-4 mb-6">
                                <div className="flex items-center justify-between">
                                    <h3 className="text-sm font-medium text-gray-700">Active Filters:</h3>
                                    <button
                                        type="button"
                                        onClick={clearFilters}
                                        className="text-sm text-wine-600 hover:text-wine-800"
                                    >
                                        Clear all
                                    </button>
                                </div>
                                
                                <div className="mt-2 flex flex-wrap gap-2">
                                    {filters.category && (
                                        <div className="bg-gray-100 px-3 py-1 rounded-full flex items-center text-sm">
                                            <span>Type: {filters.category.charAt(0).toUpperCase() + filters.category.slice(1)}</span>
                                            <button
                                                type="button"
                                                onClick={() => setFilters({...filters, category: ''})}
                                                className="ml-1 text-gray-500 hover:text-gray-700"
                                            >
                                                <X className="h-3 w-3" />
                                            </button>
                                        </div>
                                    )}
                                    
                                    {filters.priceRange && (
                                        <div className="bg-gray-100 px-3 py-1 rounded-full flex items-center text-sm">
                                            <span>Price: {
                                                filters.priceRange === '0-20' ? 'Under $20' :
                                                filters.priceRange === '20-50' ? '$20 - $50' :
                                                filters.priceRange === '50-100' ? '$50 - $100' :
                                                'Over $100'
                                            }</span>
                                            <button
                                                type="button"
                                                onClick={() => setFilters({...filters, priceRange: ''})}
                                                className="ml-1 text-gray-500 hover:text-gray-700"
                                            >
                                                <X className="h-3 w-3" />
                                            </button>
                                        </div>
                                    )}
                                    
                                    {filters.region && (
                                        <div className="bg-gray-100 px-3 py-1 rounded-full flex items-center text-sm">
                                            <span>Region: {filters.region.charAt(0).toUpperCase() + filters.region.slice(1)}</span>
                                            <button
                                                type="button"
                                                onClick={() => setFilters({...filters, region: ''})}
                                                className="ml-1 text-gray-500 hover:text-gray-700"
                                            >
                                                <X className="h-3 w-3" />
                                            </button>
                                        </div>
                                    )}
                                    
                                    {filters.rating && (
                                        <div className="bg-gray-100 px-3 py-1 rounded-full flex items-center text-sm">
                                            <span>Rating: {filters.rating} Stars</span>
                                            <button
                                                type="button"
                                                onClick={() => setFilters({...filters, rating: ''})}
                                                className="ml-1 text-gray-500 hover:text-gray-700"
                                            >
                                                <X className="h-3 w-3" />
                                            </button>
                                        </div>
                                    )}
                                    
                                    {filters.search && (
                                        <div className="bg-gray-100 px-3 py-1 rounded-full flex items-center text-sm">
                                            <span>Search: "{filters.search}"</span>
                                            <button
                                                type="button"
                                                onClick={() => setFilters({...filters, search: ''})}
                                                className="ml-1 text-gray-500 hover:text-gray-700"
                                            >
                                                <X className="h-3 w-3" />
                                            </button>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}
                        
                        {/* Results Count */}
                        <div className="bg-white shadow rounded-lg p-4 mb-6">
                            <div className="flex items-center justify-between">
                                <p className="text-sm text-gray-700">
                                    Showing <span className="font-medium">{wines.length}</span> of <span className="font-medium">{totalWines}</span> wines
                                </p>
                            </div>
                        </div>
                        
                        {/* Wine Grid */}
                        {loading && wines.length === 0 ? (
                            <div className="bg-white shadow rounded-lg p-12 text-center">
                                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-wine-600 mx-auto"></div>
                                <p className="mt-4 text-gray-500">Loading wines...</p>
                            </div>
                        ) : error ? (
                            <div className="bg-white shadow rounded-lg p-6">
                                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded flex items-center">
                                    <svg className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                    {error}
                                </div>
                            </div>
                        ) : wines.length === 0 ? (
                            <div className="bg-white shadow rounded-lg p-12 text-center">
                                <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-gray-100">
                                    <Wine className="h-6 w-6 text-gray-400" />
                                </div>
                                <h3 className="mt-3 text-lg font-medium text-gray-900">No wines found</h3>
                                <p className="mt-2 text-gray-500">Try adjusting your filters or search criteria.</p>
                                <div className="mt-6">
                                    <button
                                        type="button"
                                        onClick={clearFilters}
                                        className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-wine-600 hover:bg-wine-700"
                                    >
                                        Clear all filters
                                    </button>
                                </div>
                            </div>
                        ) : (
                            <div>
                                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                                    {wines.map(wine => (
                                        <WineCard key={wine.id} wine={wine} />
                                    ))}
                                </div>
                                
                                {/* Load More Button */}
                                {hasMore && (
                                    <div className="mt-8 text-center">
                                        <button
                                            type="button"
                                            onClick={handleLoadMore}
                                            disabled={loading}
                                            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-wine-600 hover:bg-wine-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-wine-500 disabled:opacity-50"
                                        >
                                            {loading ? (
                                                <>
                                                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                                    </svg>
                                                    Loading...
                                                </>
                                            ) : (
                                                'Load More Wines'
                                            )}
                                        </button>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default WineList;