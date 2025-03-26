import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import WineCard from './WineCard';
import { wineService } from '../services/api';
import { ArrowRight, GlassWater, Award, BookOpen } from 'lucide-react';

export default function Home() {
  const { user } = useAuth();
  const [featuredWines, setFeaturedWines] = useState([]);
  const [topRatedWines, setTopRatedWines] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch featured wines
        const featuredResponse = await wineService.getFeaturedWines();
        setFeaturedWines(featuredResponse);
        
        // Fetch top rated wines
        const topRatedResponse = await wineService.getTopRatedWines();
        setTopRatedWines(topRatedResponse);
        
        // Fetch personalized recommendations if user is logged in
        if (user) {
          const recommendationsResponse = await wineService.getRecommendations();
          setRecommendations(recommendationsResponse);
        }
      } catch (err) {
        setError('Failed to load wine data');
        console.error('Error fetching wine data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [user]);

  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-r from-red-900 to-red-700 text-white">
        <div className="absolute inset-0 bg-black opacity-30"></div>
        <div className="container mx-auto px-4 py-32 relative">
          <div className="max-w-3xl">
            <h1 className="mb-6 text-5xl font-bold leading-tight">
              Discover Your Perfect Wine Match
            </h1>
            <p className="mb-8 text-xl text-gray-200">
              Get personalized wine recommendations based on your taste preferences and discover new favorites from our curated collection.
            </p>
            <div className="flex flex-wrap gap-4">
              {!user ? (
                <Link
                  to="/signup"
                  className="inline-block rounded-md bg-white px-8 py-3 text-lg font-medium text-red-600 hover:bg-gray-100 transition-colors"
                >
                  Get Started
                </Link>
              ) : (
                <Link
                  to="/preferences"
                  className="inline-block rounded-md bg-white px-8 py-3 text-lg font-medium text-red-600 hover:bg-gray-100 transition-colors"
                >
                  Update Preferences
                </Link>
              )}
              <Link
                to="/catalog"
                className="inline-block rounded-md bg-transparent border-2 border-white px-8 py-3 text-lg font-medium text-white hover:bg-white/10 transition-colors"
              >
                Browse Wines
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <h2 className="mb-12 text-center text-3xl font-bold text-gray-900">
            How Our Recommendation System Works
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white p-6 rounded-lg shadow-sm text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 mb-4 bg-red-100 rounded-full text-red-600">
                <GlassWater size={32} />
              </div>
              <h3 className="text-xl font-semibold mb-2">Set Your Preferences</h3>
              <p className="text-gray-600">Tell us about your taste preferences, favorite wine types, and price range.</p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-sm text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 mb-4 bg-red-100 rounded-full text-red-600">
                <Award size={32} />
              </div>
              <h3 className="text-xl font-semibold mb-2">Get Recommendations</h3>
              <p className="text-gray-600">Our AI analyzes your preferences to suggest wines you'll love.</p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-sm text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 mb-4 bg-red-100 rounded-full text-red-600">
                <BookOpen size={32} />
              </div>
              <h3 className="text-xl font-semibold mb-2">Learn & Discover</h3>
              <p className="text-gray-600">Explore detailed information about each wine and expand your knowledge.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Wines Section */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900">
              Featured Wines
            </h2>
            <Link to="/catalog" className="text-red-600 hover:text-red-800 flex items-center">
              View All <ArrowRight size={16} className="ml-1" />
            </Link>
          </div>
          
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto"></div>
            </div>
          ) : error ? (
            <div className="text-center text-red-600">{error}</div>
          ) : (
            <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {featuredWines.slice(0, 4).map((wine) => (
                <WineCard key={wine.id} wine={wine} />
              ))}
            </div>
          )}
        </div>
      </section>
      
      {/* Top Rated Wines Section */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900">
              Top Rated Wines
            </h2>
            <Link to="/catalog?sort=rating" className="text-red-600 hover:text-red-800 flex items-center">
              View All <ArrowRight size={16} className="ml-1" />
            </Link>
          </div>
          
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto"></div>
            </div>
          ) : error ? (
            <div className="text-center text-red-600">{error}</div>
          ) : (
            <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {topRatedWines.slice(0, 4).map((wine) => (
                <WineCard key={wine.id} wine={wine} />
              ))}
            </div>
          )}
        </div>
      </section>
      
      {/* Personalized Recommendations Section (only if user is logged in) */}
      {user && recommendations.length > 0 && (
        <section className="py-16">
          <div className="container mx-auto px-4">
            <div className="flex justify-between items-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900">
                Recommended For You
              </h2>
              <Link to="/recommendations" className="text-red-600 hover:text-red-800 flex items-center">
                View All <ArrowRight size={16} className="ml-1" />
              </Link>
            </div>
            
            <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {recommendations.slice(0, 4).map((wine) => (
                <WineCard key={wine.id} wine={wine} />
              ))}
            </div>
          </div>
        </section>
      )}
      
      {/* Call to Action Section */}
      <section className="py-16 bg-red-700 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to Find Your Perfect Wine?</h2>
          <p className="text-xl mb-8 max-w-2xl mx-auto">
            Join thousands of wine enthusiasts who have discovered new favorites with our personalized recommendation system.
          </p>
          <Link
            to={user ? "/preferences" : "/signup"}
            className="inline-block rounded-md bg-white px-8 py-3 text-lg font-medium text-red-600 hover:bg-gray-100 transition-colors"
          >
            {user ? "Update Your Preferences" : "Get Started Now"}
          </Link>
        </div>
      </section>
    </div>
  );
}