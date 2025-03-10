import React, { useState } from 'react';

const SearchBar = ({ onSearch }) => {
    const [query, setQuery] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        onSearch(query);
    };

    return (
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