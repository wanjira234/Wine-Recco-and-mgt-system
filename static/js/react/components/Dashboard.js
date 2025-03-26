import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { wineService, accountService } from '../services/api';
import WineCard from './WineCard';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Wine, Clock, Award, Heart, History } from 'lucide-react';

const Dashboard = () => {
    const { user } = useAuth();
    const navigate = useNavigate();
    const [recommendations, setRecommendations] = useState([]);
    const [savedWines, setSavedWines] = useState([]);
    const [recentlyViewed, setRecentlyViewed] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [activeTab, setActiveTab] = useState('recommendations');

    useEffect(() => {
        if (!user) {
            navigate('/login');
            return;
        }
        
        fetchUserData();
    }, [user, navigate]);

    const fetchUserData = async () => {
        try {
            setLoading(true);
            
            // Fetch recommendations
            const recommendationsData = await wineService.getRecommendations();
            setRecommendations(recommendationsData);
            
            // Fetch saved wines
            const savedWinesData = await wineService.getSavedWines();
            setSavedWines(savedWinesData);
            
            // Fetch recently viewed wines
            const recentlyViewedData = await wineService.getRecentlyViewed();
            setRecentlyViewed(recentlyViewedData);
        } catch (err) {
            console.error('Error fetching user data:', err);
            setError('Failed to load your data. Please try again later.');
        } finally {
            setLoading(false);
        }
    };
    
    const handleSaveWine = async (wineId) => {
        try {
            const isSaved = savedWines.some(wine => wine.id === wineId);
            
            if (isSaved) {
                await wineService.unsaveWine(wineId);
                setSavedWines(savedWines.filter(wine => wine.id !== wineId));
            } else {
                await wineService.saveWine(wineId);
                const wineToAdd = [...recommendations, ...recentlyViewed].find(wine => wine.id === wineId);
                if (wineToAdd) {
                    setSavedWines([...savedWines, wineToAdd]);
                }
            }
        } catch (err) {
            console.error('Error updating saved wines:', err);
        }
    };

    if (!user) {
        return null;
    }

    return (
        <div className="min-h-screen bg-gray-100">
            <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
                {/* Welcome Section */}
                <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
                    <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900">
                                Welcome back, {user.first_name}!
                            </h1>
                            <p className="mt-2 text-gray-600">
                                Here are your personalized wine recommendations and saved wines.
                            </p>
                        </div>
                        <div className="mt-4 md:mt-0">
                            <Link 
                                to="/preferences" 
                                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-wine-600 hover:bg-wine-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-wine-500"
                            >
                                Update Preferences
                            </Link>
                        </div>
                    </div>
                </div>

                {/* Stats Section */}
                <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
                    <div className="bg-white overflow-hidden shadow-sm rounded-lg">
                        <div className="p-5">
                            <div className="flex items-center">
                                <div className="flex-shrink-0 bg-red-100 rounded-md p-3">
                                    <Wine className="h-6 w-6 text-wine-600" />
                                </div>
                                <div className="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt className="text-sm font-medium text-gray-500 truncate">
                                            Wines Rated
                                        </dt>
                                        <dd className="text-lg font-medium text-gray-900">
                                            {user.wines_rated || 0}
                                        </dd>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white overflow-hidden shadow-sm rounded-lg">
                        <div className="p-5">
                            <div className="flex items-center">
                                <div className="flex-shrink-0 bg-red-100 rounded-md p-3">
                                    <Heart className="h-6 w-6 text-wine-600" />
                                </div>
                                <div className="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt className="text-sm font-medium text-gray-500 truncate">
                                            Saved Wines
                                        </dt>
                                        <dd className="text-lg font-medium text-gray-900">
                                            {savedWines.length}
                                        </dd>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white overflow-hidden shadow-sm rounded-lg">
                        <div className="p-5">
                            <div className="flex items-center">
                                <div className="flex-shrink-0 bg-red-100 rounded-md p-3">
                                    <Clock className="h-6 w-6 text-wine-600" />
                                </div>
                                <div className="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt className="text-sm font-medium text-gray-500 truncate">
                                            Last Visit
                                        </dt>
                                        <dd className="text-lg font-medium text-gray-900">
                                            {new Date(user.last_visit).toLocaleDateString()}
                                        </dd>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white overflow-hidden shadow-sm rounded-lg">
                        <div className="p-5">
                            <div className="flex items-center">
                                <div className="flex-shrink-0 bg-red-100 rounded-md p-3">
                                    <Award className="h-6 w-6 text-wine-600" />
                                </div>
                                <div className="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt className="text-sm font-medium text-gray-500 truncate">
                                            Account Status
                                        </dt>
                                        <dd className="text-lg font-medium text-gray-900">
                                            {user.is_active ? 'Active' : 'Inactive'}
                                        </dd>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Tabs Section */}
                <div className="bg-white rounded-lg shadow-sm overflow-hidden">
                    <div className="border-b border-gray-200">
                        <div className="px-6 py-4">
                            <nav className="-mb-px flex space-x-6">
                                <button
                                    onClick={() => setActiveTab('recommendations')}
                                    className={`${
                                        activeTab === 'recommendations'
                                            ? 'border-wine-500 text-wine-600'
                                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    } whitespace-nowrap pb-4 px-1 border-b-2 font-medium text-sm`}
                                >
                                    Recommendations
                                </button>
                                <button
                                    onClick={() => setActiveTab('saved')}
                                    className={`${
                                        activeTab === 'saved'
                                            ? 'border-wine-500 text-wine-600'
                                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    } whitespace-nowrap pb-4 px-1 border-b-2 font-medium text-sm`}
                                >
                                    Saved Wines
                                </button>
                                <button
                                    onClick={() => setActiveTab('history')}
                                    className={`${
                                        activeTab === 'history'
                                            ? 'border-wine-500 text-wine-600'
                                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    } whitespace-nowrap pb-4 px-1 border-b-2 font-medium text-sm`}
                                >
                                    Recently Viewed
                                </button>
                            </nav>
                        </div>
                    </div>

                    <div className="p-6">
                        {loading ? (
                            <div className="text-center py-12">
                                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-wine-600 mx-auto"></div>
                            </div>
                        ) : error ? (
                            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                                {error}
                            </div>
                        ) : (
                            <div>
                                {activeTab === 'recommendations' && (
                                    <div>
                                        <h2 className="text-xl font-semibold text-gray-900 mb-4">Your Wine Recommendations</h2>
                                        {recommendations.length > 0 ? (
                                            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                                                {recommendations.map(wine => (
                                                    <WineCard 
                                                        key={wine.id} 
                                                        wine={wine} 
                                                        onSave={handleSaveWine}
                                                        isSaved={savedWines.some(saved => saved.id === wine.id)}
                                                    />
                                                ))}
                                            </div>
                                        ) : (
                                            <p className="text-gray-500 text-center py-8">
                                                No recommendations available. Update your preferences to get personalized recommendations.
                                            </p>
                                        )}
                                    </div>
                                )}
                                
                                {activeTab === 'saved' && (
                                    <div>
                                        <h2 className="text-xl font-semibold text-gray-900 mb-4">Your Saved Wines</h2>
                                        {savedWines.length > 0 ? (
                                            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                                                {savedWines.map(wine => (
                                                    <WineCard 
                                                        key={wine.id} 
                                                        wine={wine} 
                                                        onSave={handleSaveWine}
                                                        isSaved={true}
                                                    />
                                                ))}
                                            </div>
                                        ) : (
                                            <p className="text-gray-500 text-center py-8">
                                                You haven't saved any wines yet. Browse our catalog and save wines you're interested in.
                                            </p>
                                        )}
                                    </div>
                                )}
                                
                                {activeTab === 'history' && (
                                    <div>
                                        <h2 className="text-xl font-semibold text-gray-900 mb-4">Recently Viewed Wines</h2>
                                        {recentlyViewed.length > 0 ? (
                                            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                                                {recentlyViewed.map(wine => (
                                                    <WineCard 
                                                        key={wine.id} 
                                                        wine={wine} 
                                                        onSave={handleSaveWine}
                                                        isSaved={savedWines.some(saved => saved.id === wine.id)}
                                                    />
                                                ))}
                                            </div>
                                        ) : (
                                            <p className="text-gray-500 text-center py-8">
                                                You haven't viewed any wines recently. Start exploring our catalog!
                                            </p>
                                        )}
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

export default Dashboard;