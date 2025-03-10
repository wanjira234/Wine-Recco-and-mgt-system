import React from 'react';
import { Link } from 'react-router-dom';
import { FaWineBottle, FaSearch, FaGlassWhiskey } from 'react-icons/fa';
import { useAuth } from '../context/AuthContext';

const DEFAULT_WINE_IMAGE = "/images/default-wine.jpg"; // Default wine image

const featuredWines = [
    { id: 1, name: "Chardonnay", image: "/images/wines/chardonnay.jpg", price: 20 },
    { id: 2, name: "Merlot", image: "/images/wines/merlot.jpg", price: 25 },
    { id: 3, name: "Cabernet Sauvignon", image: "/images/wines/cabernet.jpg", price: 30 },
    { id: 4, name: "Pinot Noir", image: DEFAULT_WINE_IMAGE, price: 22 },
    { id: 5, name: "Sauvignon Blanc", image: DEFAULT_WINE_IMAGE, price: 18 },
];

const Home = () => {
    const { user } = useAuth();

    return (
        <div className="min-h-screen bg-gradient-to-b from-wine-dark to-wine-primary text-white">
            <div className="container mx-auto px-4 py-16">
                <div className="text-center">
                    <h1 className="text-5xl font-extrabold mb-6">
                        Welcome to the Wine Recommendation System
                    </h1>
                    <p className="text-xl mb-12">Your one-stop shop for the best wines!</p>
                    {user && <p className="text-lg text-gray-200 mb-8">Hello, {user.username}!</p>}

                    <div className="grid md:grid-cols-3 gap-8 mb-12">
                        <FeatureCard 
                            icon={<FaWineBottle className="text-5xl text-white" />}
                            title="Extensive Catalog"
                            description="Browse through our curated collection of wines from around the world"
                            link="/catalog"
                        />
                        <FeatureCard 
                            icon={<FaSearch className="text-5xl text-white" />}
                            title="Wine Recommender"
                            description="Get personalized wine recommendations based on your taste"
                            link="/recommend"
                        />
                        <FeatureCard 
                            icon={<FaGlassWhiskey className="text-5xl text-white" />}
                            title="Learn About Wines"
                            description="Expand your wine knowledge with our educational resources"
                            link="/learn"
                        />
                    </div>

                    <h2 className="text-3xl font-bold mb-6">Featured Wines</h2>
                    <div className="grid md:grid-cols-3 gap-8">
                        {featuredWines.map(wine => (
                            <div key={wine.id} className="bg-white shadow-lg rounded-lg p-6 text-center hover:shadow-xl transition duration-300">
                                <img src={wine.image} alt={wine.name} className="w-full h-48 object-cover rounded" />
                                <h3 className="text-2xl font-semibold mt-4">{wine.name}</h3>
                                <p className="text-lg text-gray-600">${wine.price}</p>
                                <Link 
                                    to={`/wine/${wine.id}`} 
                                    className="text-wine-primary hover:underline mt-2 inline-block"
                                >
                                    View Details
                                </Link>
                            </div>
                        ))}
                    </div>

                    <div className="mt-16">
                        <Link 
                            to="/catalog" 
                            className="bg-wine-secondary text-white px-8 py-3 rounded-full hover:bg-wine-primary transition duration-300"
                        >
                            Explore All Wines
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
};

const FeatureCard = ({ icon, title, description, link }) => (
    <div className="bg-white shadow-lg rounded-lg p-6 text-center hover:shadow-xl transition duration-300">
        <div className="flex justify-center mb-4">{icon}</div>
        <h3 className="text-2xl font-semibold mb-4">{title}</h3>
        <p className="text-gray-600 mb-4">{description}</p>
        <Link 
            to={link} 
            className="text-wine-primary hover:underline"
        >
            Learn More
        </Link>
    </div>
);

export default Home;