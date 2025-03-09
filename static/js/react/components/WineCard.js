import React from 'react';
import { Link } from 'react-router-dom';

const WineCard = ({ wine }) => {
    return (
        <div className="border rounded-lg overflow-hidden shadow-lg">
            <img src={wine.image} alt={wine.name} className="w-full h-48 object-cover" />
            <div className="p-4">
                <h2 className="text-xl font-semibold">{wine.name}</h2>
                <p className="text-gray-600">{wine.description}</p>
                <Link to={`/wine/${wine.id}`} className="text-blue-500 hover:underline">View Details</Link>
            </div>
        </div>
    );
};

export default WineCard;