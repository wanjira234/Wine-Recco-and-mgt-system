import React from 'react';

const SearchBar = () => {
    return (
        <input
            type="text"
            placeholder="Search for wines..."
            className="border rounded-md p-2 mb-4 w-full"
        />
    );
};

export default SearchBar;