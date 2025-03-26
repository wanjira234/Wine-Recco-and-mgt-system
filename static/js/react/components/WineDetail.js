import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { wineService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Star, Award, Heart, ShoppingCart, Share2, ArrowLeft, AlertCircle } from 'lucide-react';

const WineDetail = () => {
    const { id } = useParams();
    const { user } = useAuth();
    const [wine, setWine] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [rating, setRating] = useState(0);
    const [userRating, setUserRating] = useState(0);
    const [isSaved, setIsSaved] = useState(false);
    const [similarWines, setSimilarWines] = useState([]);
    const [activeTab, setActiveTab] = useState('overview');

    useEffect(() => {
        fetchWineDetails();
        window.scrollTo(0, 0);
    }, [id]);

    const fetchWineDetails = async () => {
        try {
            setLoading(true);
            const response = await wineService.getWine(id);
            setWine(response.data);
            if (response.data.user_rating) {
                setUserRating(response.data.user_rating);
            }
            
            // Check if wine is saved
            if (user) {
                const savedResponse = await wineService.checkSavedWine(id);
                setIsSaved(savedResponse.data.is_saved);
            }
            
            // Fetch similar wines
            const similarResponse = await wineService.getSimilarWines(id);
            setSimilarWines(similarResponse.data.slice(0, 3));
        } catch (err) {
            setError('Failed to load wine details. Please try again later.');
            console.error('Error fetching wine details:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleRatingChange = async (newRating) => {
        if (!user) {
            window.location.href = '/login';
            return;
        }

        try {
            await wineService.rateWine(id, newRating);
            setUserRating(newRating);
            setRating(newRating);
        } catch (err) {
            setError('Failed to update rating. Please try again.');
        }
    };
    
    const handleSaveWine = async () => {
        if (!user) {
            window.location.href = '/login';
            return;
        }
        
        try {
            if (isSaved) {
                await wineService.unsaveWine(id);
                setIsSaved(false);
            } else {
                await wineService.saveWine(id);
                setIsSaved(true);
            }
        } catch (err) {
            setError('Failed to update saved wines. Please try again.');
        }
    };
    
    const handleShare = () => {
        navigator.clipboard.writeText(window.location.href);
        alert('Link copied to clipboard!');
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-wine-600"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gray-100 py-6">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded flex items-center">
                        <AlertCircle className="h-5 w-5 mr-2" />
                        {error}
                    </div>
                </div>
            </div>
        );
    }

    if (!wine) {
        return (
            <div className="min-h-screen bg-gray-100 py-6">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center text-gray-500">
                        Wine not found.
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-100 py-6">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="mb-6">
                    <Link to="/catalog" className="inline-flex items-center text-wine-600 hover:text-wine-800">
                        <ArrowLeft className="h-4 w-4 mr-1" />
                        Back to Catalog
                    </Link>
                </div>
                
                <div className="bg-white shadow rounded-lg overflow-hidden">
                    <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
                        <div className="flex justify-between items-start">
                            <div>
                                <h1 className="text-3xl font-bold text-gray-900">{wine.name}</h1>
                                <p className="mt-1 text-sm text-gray-500">
                                    {wine.variety} • {wine.region}, {wine.country} • {wine.vintage}
                                </p>
                            </div>
                            <div className="flex space-x-2">
                                <button 
                                    onClick={handleSaveWine}
                                    className={`p-2 rounded-full ${isSaved ? 'bg-red-100 text-red-600' : 'bg-gray-100 text-gray-600'} hover:bg-gray-200`}
                                >
                                    <Heart className={`h-5 w-5 ${isSaved ? 'fill-current' : ''}`} />
                                </button>
                                <button 
                                    onClick={handleShare}
                                    className="p-2 rounded-full bg-gray-100 text-gray-600 hover:bg-gray-200"
                                >
                                    <Share2 className="h-5 w-5" />
                                </button>
                            </div>
                        </div>
                    </div>
                    
                    <div className="px-4 py-5 sm:px-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                            {/* Wine Image */}
                            <div className="aspect-w-1 aspect-h-1 rounded-lg overflow-hidden bg-gray-200">
                                <img
                                    src={wine.image_url || '/images/wine-placeholder.jpg'}
                                    alt={wine.name}
                                    className="object-cover w-full h-full"
                                />
                            </div>

                            {/* Wine Details */}
                            <div className="space-y-6">
                                <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center">
                                    <div className="mb-4 sm:mb-0">
                                        <span className="text-3xl font-bold text-wine-600">${wine.price?.toFixed(2)}</span>
                                        {wine.original_price && wine.original_price > wine.price && (
                                            <span className="ml-2 text-lg text-gray-500 line-through">${wine.original_price.toFixed(2)}</span>
                                        )}
                                    </div>
                                    
                                    <button className="inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-wine-600 hover:bg-wine-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-wine-500">
                                        <ShoppingCart className="h-4 w-4 mr-2" />
                                        Add to Cart
                                    </button>
                                </div>
                                
                                <div className="border-t border-b border-gray-200 py-4">
                                    <div className="flex justify-between text-sm">
                                        <div className="flex items-center">
                                            <Award className="h-5 w-5 text-yellow-500 mr-1" />
                                            <span>Quality Score: <strong>{wine.quality_score || 'N/A'}</strong></span>
                                        </div>
                                        <div>
                                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${wine.in_stock ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                                {wine.in_stock ? 'In Stock' : 'Out of Stock'}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                                
                                <div>
                                    <div className="flex border-b border-gray-200">
                                        <button
                                            className={`px-4 py-2 text-sm font-medium ${activeTab === 'overview' ? 'text-wine-600 border-b-2 border-wine-600' : 'text-gray-500 hover:text-gray-700'}`}
                                            onClick={() => setActiveTab('overview')}
                                        >
                                            Overview
                                        </button>
                                        <button
                                            className={`px-4 py-2 text-sm font-medium ${activeTab === 'details' ? 'text-wine-600 border-b-2 border-wine-600' : 'text-gray-500 hover:text-gray-700'}`}
                                            onClick={() => setActiveTab('details')}
                                        >
                                            Details
                                        </button>
                                        <button
                                            className={`px-4 py-2 text-sm font-medium ${activeTab === 'pairings' ? 'text-wine-600 border-b-2 border-wine-600' : 'text-gray-500 hover:text-gray-700'}`}
                                            onClick={() => setActiveTab('pairings')}
                                        >
                                            Food Pairings
                                        </button>
                                    </div>
                                    
                                    <div className="py-4">
                                        {activeTab === 'overview' && (
                                            <p className="text-gray-600">{wine.description}</p>
                                        )}
                                        
                                        {activeTab === 'details' && (
                                            <div className="grid grid-cols-2 gap-4">
                                                <div>
                                                    <h3 className="text-sm font-medium text-gray-500">Body</h3>
                                                    <p className="mt-1 text-sm text-gray-900">{wine.body}</p>
                                                </div>
                                                <div>
                                                    <h3 className="text-sm font-medium text-gray-500">Sweetness</h3>
                                                    <p className="mt-1 text-sm text-gray-900">{wine.sweetness}</p>
                                                </div>
                                                <div>
                                                    <h3 className="text-sm font-medium text-gray-500">Acidity</h3>
                                                    <p className="mt-1 text-sm text-gray-900">{wine.acidity}</p>
                                                </div>
                                                <div>
                                                    <h3 className="text-sm font-medium text-gray-500">Tannins</h3>
                                                    <p className="mt-1 text-sm text-gray-900">{wine.tannins}</p>
                                                </div>
                                                <div>
                                                    <h3 className="text-sm font-medium text-gray-500">Alcohol</h3>
                                                    <p className="mt-1 text-sm text-gray-900">{wine.alcohol}%</p>
                                                </div>
                                                <div>
                                                    <h3 className="text-sm font-medium text-gray-500">Aging</h3>
                                                    <p className="mt-1 text-sm text-gray-900">{wine.aging || 'N/A'}</p>
                                                </div>
                                            </div>
                                        )}
                                        
                                        {activeTab === 'pairings' && (
                                            <div>
                                                <ul className="list-disc list-inside text-gray-600 space-y-1">
                                                    {wine.food_pairings?.map((pairing, index) => (
                                                        <li key={index}>{pairing}</li>
                                                    ))}
                                                </ul>
                                                
                                                {(!wine.food_pairings || wine.food_pairings.length === 0) && (
                                                    <p className="text-gray-500 italic">No food pairings available for this wine.</p>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                </div>

                                <div>
                                    <h3 className="text-lg font-medium text-gray-900">Your Rating</h3>
                                    <div className="mt-2 flex items-center space-x-1">
                                        {[1, 2, 3, 4, 5].map((star) => (
                                            <button
                                                key={star}
                                                onClick={() => handleRatingChange(star)}
                                                className={`focus:outline-none ${
                                                    star <= userRating ? 'text-yellow-400' : 'text-gray-300'
                                                } hover:text-yellow-400 transition-colors`}
                                            >
                                                <Star className="h-6 w-6 fill-current" />
                                            </button>
                                        ))}
                                        
                                        {userRating > 0 && (
                                            <span className="ml-2 text-sm text-gray-500">
                                                Your rating: {userRating}/5
                                            </span>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                {/* Similar Wines Section */}
                {similarWines.length > 0 && (
                    <div className="mt-12">
                        <h2 className="text-2xl font-bold text-gray-900 mb-6">You May Also Like</h2>
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                            {similarWines.map((similarWine) => (
                                <div key={similarWine.id} className="bg-white rounded-lg shadow overflow-hidden">
                                    <Link to={`/wines/${similarWine.id}`}>
                                        <img
                                            src={similarWine.image_url || '/images/wine-placeholder.jpg'}
                                            alt={similarWine.name}
                                            className="h-48 w-full object-cover"
                                        />
                                        <div className="p-4">
                                            <h3 className="text-lg font-medium text-gray-900">{similarWine.name}</h3>
                                            <p className="text-sm text-gray-500">{similarWine.variety} • {similarWine.region}</p>
                                            <p className="mt-2 text-wine-600 font-medium">${similarWine.price?.toFixed(2)}</p>
                                        </div>
                                    </Link>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default WineDetail;