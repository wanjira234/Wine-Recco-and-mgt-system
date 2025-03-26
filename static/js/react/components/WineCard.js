import React from 'react';
import { Link } from 'react-router-dom';
import { Star, Award, Heart } from 'lucide-react';

export default function WineCard({ wine, onSave, isSaved }) {
  const {
    id,
    name,
    description,
    price,
    image_url,
    variety,
    region,
    vintage,
    rating,
    quality_score
  } = wine;

  const handleSaveClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (onSave) {
      onSave(id);
    }
  };

  return (
    <div className="overflow-hidden rounded-lg border bg-white shadow-sm transition-all hover:shadow-md">
      <div className="relative">
        <img
          src={image_url || '/static/images/wines/default.jpg'}
          alt={name}
          className="h-48 w-full object-cover"
        />
        
        {/* Quality badge */}
        {quality_score && quality_score >= 90 && (
          <div className="absolute top-2 left-2 bg-yellow-400 text-yellow-900 text-xs font-bold px-2 py-1 rounded-full flex items-center">
            <Award className="h-3 w-3 mr-1" />
            {quality_score}
          </div>
        )}
        
        {/* Save button */}
        {onSave && (
          <button 
            onClick={handleSaveClick}
            className={`absolute top-2 right-2 p-1.5 rounded-full ${isSaved ? 'bg-red-100 text-red-600' : 'bg-white/80 text-gray-600 hover:bg-white'}`}
          >
            <Heart className={`h-4 w-4 ${isSaved ? 'fill-current' : ''}`} />
          </button>
        )}
      </div>
      
      <div className="p-4">
        <div className="flex justify-between items-start">
          <h3 className="mb-1 text-lg font-semibold text-gray-900 line-clamp-1">
            {name}
          </h3>
          {rating && (
            <div className="flex items-center text-yellow-500">
              <Star className="h-4 w-4 fill-current" />
              <span className="ml-1 text-xs font-medium">{rating}</span>
            </div>
          )}
        </div>
        
        <p className="mb-2 text-sm text-gray-600">
          {variety} • {region} • {vintage}
        </p>
        
        <p className="mb-4 text-gray-600 text-sm line-clamp-2">
          {description}
        </p>
        
        <div className="flex items-center justify-between mt-auto pt-2 border-t border-gray-100">
          <span className="text-lg font-medium text-red-600">
            ${price?.toFixed(2)}
          </span>
          <Link
            to={`/wines/${id}`}
            className="rounded-md bg-red-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-red-700 transition-colors"
          >
            View Details
          </Link>
        </div>
      </div>
    </div>
  );
}