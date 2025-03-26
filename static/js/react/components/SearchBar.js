import React, { useState } from 'react';

const SearchBar = ({ onSearch }) => {
    const [query, setQuery] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        onSearch(query);
    };

    return (import React, { useState, useEffect } from 'react';
        import { Search, X, Filter } from 'lucide-react';
        
        const SearchBar = ({ onSearch, initialQuery = '', onFilter }) => {
            const [query, setQuery] = useState(initialQuery);
            const [isExpanded, setIsExpanded] = useState(false);
            const [showFilters, setShowFilters] = useState(false);
            const [filters, setFilters] = useState({
                priceRange: [0, 200],
                types: [],
                regions: []
            });
        
            useEffect(() => {
                setQuery(initialQuery);
            }, [initialQuery]);
        
            const handleSubmit = (e) => {
                e.preventDefault();
                onSearch(query);
            };
        
            const handleClear = () => {
                setQuery('');
                onSearch('');
            };
        
            const handleFilterChange = (filterType, value) => {
                setFilters(prev => {
                    const newFilters = { ...prev };
                    
                    if (filterType === 'priceRange') {
                        newFilters.priceRange = value;
                    } else if (filterType === 'types') {
                        if (newFilters.types.includes(value)) {
                            newFilters.types = newFilters.types.filter(type => type !== value);
                        } else {
                            newFilters.types = [...newFilters.types, value];
                        }
                    } else if (filterType === 'regions') {
                        if (newFilters.regions.includes(value)) {
                            newFilters.regions = newFilters.regions.filter(region => region !== value);
                        } else {
                            newFilters.regions = [...newFilters.regions, value];
                        }
                    }
                    
                    return newFilters;
                });
            };
        
            const applyFilters = () => {
                if (onFilter) {
                    onFilter(filters);
                }
                setShowFilters(false);
            };
        
            const wineTypes = ['Red', 'White', 'Rosé', 'Sparkling', 'Dessert'];
            const wineRegions = ['France', 'Italy', 'Spain', 'United States', 'Australia', 'Argentina', 'Chile'];
        
            return (
                <div className="relative mb-6">
                    <form onSubmit={handleSubmit} className="relative">
                        <div className={`flex items-center border ${isExpanded ? 'border-wine-500 ring-2 ring-wine-200' : 'border-gray-300'} rounded-lg overflow-hidden transition-all bg-white`}>
                            <div className="pl-3 text-gray-400">
                                <Search size={20} />
                            </div>
                            <input
                                type="text"
                                placeholder="Search for wines, regions, or varieties..."
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                onFocus={() => setIsExpanded(true)}
                                onBlur={() => setIsExpanded(false)}
                                className="w-full py-3 px-3 focus:outline-none"
                            />
                            {query && (
                                <button 
                                    type="button" 
                                    onClick={handleClear}
                                    className="px-3 text-gray-400 hover:text-gray-600"
                                >
                                    <X size={18} />
                                </button>
                            )}
                            <button 
                                type="button" 
                                onClick={() => setShowFilters(!showFilters)}
                                className={`px-4 py-3 border-l ${showFilters ? 'bg-wine-50 text-wine-600' : 'bg-gray-50 text-gray-600'} hover:bg-gray-100 flex items-center`}
                            >
                                <Filter size={18} className="mr-2" />
                                <span className="hidden sm:inline">Filters</span>
                            </button>
                            <button 
                                type="submit" 
                                className="bg-wine-primary hover:bg-wine-700 text-white px-5 py-3 font-medium transition-colors"
                            >
                                Search
                            </button>
                        </div>
                    </form>
                    
                    {/* Filters Panel */}
                    {showFilters && (
                        <div className="absolute z-10 mt-2 w-full bg-white rounded-lg shadow-lg border border-gray-200 p-4">
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                <div>
                                    <h3 className="font-medium text-gray-900 mb-2">Price Range</h3>
                                    <div className="flex items-center space-x-2">
                                        <input 
                                            type="number" 
                                            min="0" 
                                            value={filters.priceRange[0]} 
                                            onChange={(e) => handleFilterChange('priceRange', [parseInt(e.target.value), filters.priceRange[1]])}
                                            className="w-20 border border-gray-300 rounded p-1"
                                        />
                                        <span>to</span>
                                        <input 
                                            type="number" 
                                            min="0" 
                                            value={filters.priceRange[1]} 
                                            onChange={(e) => handleFilterChange('priceRange', [filters.priceRange[0], parseInt(e.target.value)])}
                                            className="w-20 border border-gray-300 rounded p-1"
                                        />
                                    </div>
                                </div>
                                
                                <div>
                                    <h3 className="font-medium text-gray-900 mb-2">Wine Type</h3>
                                    <div className="space-y-1">
                                        {wineTypes.map(type => (
                                            <label key={type} className="flex items-center">
                                                <input 
                                                    type="checkbox" 
                                                    checked={filters.types.includes(type)} 
                                                    onChange={() => handleFilterChange('types', type)}
                                                    className="mr-2"
                                                />
                                                {type}
                                            </label>
                                        ))}
                                    </div>
                                </div>
                                
                                <div>
                                    <h3 className="font-medium text-gray-900 mb-2">Region</h3>
                                    <div className="space-y-1">
                                        {wineRegions.map(region => (
                                            <label key={region} className="flex items-center">
                                                <input 
                                                    type="checkbox" 
                                                    checked={filters.regions.includes(region)} 
                                                    onChange={() => handleFilterChange('regions', region)}
                                                    className="mr-2"
                                                />
                                                {region}
                                            </label>
                                        ))}
                                    </div>
                                </div>
                            </div>
                            
                            <div className="flex justify-end mt-4 pt-3 border-t border-gray-200">
                                <button 
                                    type="button" 
                                    onClick={() => setShowFilters(false)}
                                    className="px-4 py-2 text-gray-600 hover:text-gray-800 mr-2"
                                >
                                    Cancel
                                </button>
                                <button 
                                    type="button" 
                                    onClick={applyFilters}
                                    className="px-4 py-2 bg-wine-primary text-white rounded-md hover:bg-wine-700"
                                >
                                    Apply Filters
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            );
        };
        
        export default SearchBar;
        <form onSubmit={handleSubmit} className="mb-4">
            <input
                type="text"
                placeholder="Search for wines..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="border rounded p-2 w-full"
            />
            <button type="submit" className="bg-wine-primary text-white px-4 py-2 rounded mt-2">
                Search
            </button>
        </form>
    );
};

export default SearchBar;