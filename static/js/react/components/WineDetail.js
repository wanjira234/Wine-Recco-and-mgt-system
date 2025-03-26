import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { wineService } from '../services/api';
import { useAuth } from '../context/AuthContext';

const WineDetail = () => {
    const { id } = useParams();
    const { user } = useAuth();
    const [wine, setWine] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [rating, setRating] = useState(0);
    const [userRating, setUserRating] = useState(0);

    useEffect(() => {
        fetchWineDetails();
    }, [id]);

    const fetchWineDetails = async () => {
        try {
            setLoading(true);
            const response = await wineService.getWine(id);
            setWine(response.data);
            if (response.data.user_rating) {
                setUserRating(response.data.user_rating);
            }
        } catch (err) {
            setError('Failed to load wine details. Please try again later.');
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
                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
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
                <div className="bg-white shadow rounded-lg overflow-hidden">
                    <div className="px-4 py-5 sm:px-6">
                        <h1 className="text-3xl font-bold text-gray-900">{wine.name}</h1>
                        <p className="mt-1 text-sm text-gray-500">
                            {wine.variety} • {wine.region}, {wine.country} • {wine.vintage}
                        </p>
                    </div>
                    <div className="border-t border-gray-200 px-4 py-5 sm:px-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                            {/* Wine Image */}
                            <div className="aspect-w-1 aspect-h-1">
                                <img
                                    src={wine.image_url || '/images/wine-placeholder.jpg'}
                                    alt={wine.name}
                                    className="object-cover rounded-lg"
                                />
                            </div>

                            {/* Wine Details */}
                            <div className="space-y-6">
                                <div>
                                    <h2 className="text-xl font-semibold text-gray-900">Description</h2>
                                    <p className="mt-2 text-gray-600">{wine.description}</p>
                                </div>

                                <div>
                                    <h2 className="text-xl font-semibold text-gray-900">Characteristics</h2>
                                    <dl className="mt-2 grid grid-cols-2 gap-4">
                                        <div>
                                            <dt className="text-sm font-medium text-gray-500">Body</dt>
                                            <dd className="mt-1 text-sm text-gray-900">{wine.body}</dd>
                                        </div>
                                        <div>
                                            <dt className="text-sm font-medium text-gray-500">Sweetness</dt>
                                            <dd className="mt-1 text-sm text-gray-900">{wine.sweetness}</dd>
                                        </div>
                                        <div>
                                            <dt className="text-sm font-medium text-gray-500">Acidity</dt>
                                            <dd className="mt-1 text-sm text-gray-900">{wine.acidity}</dd>
                                        </div>
                                        <div>
                                            <dt className="text-sm font-medium text-gray-500">Tannins</dt>
                                            <dd className="mt-1 text-sm text-gray-900">{wine.tannins}</dd>
                                        </div>
                                    </dl>
                                </div>

                                <div>
                                    <h2 className="text-xl font-semibold text-gray-900">Your Rating</h2>
                                    <div className="mt-2 flex items-center space-x-2">
                                        {[1, 2, 3, 4, 5].map((star) => (
                                            <button
                                                key={star}
                                                onClick={() => handleRatingChange(star)}
                                                className={`focus:outline-none ${
                                                    star <= userRating ? 'text-yellow-400' : 'text-gray-300'
                                                }`}
                                            >
                                                <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 20 20">
                                                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                                                </svg>
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                <div>
                                    <h2 className="text-xl font-semibold text-gray-900">Food Pairings</h2>
                                    <ul className="mt-2 list-disc list-inside text-gray-600">
                                        {wine.food_pairings?.map((pairing, index) => (
                                            <li key={index}>{pairing}</li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default WineDetail; 