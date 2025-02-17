import React from 'react';
import { Link } from 'react-router-dom';
import { FaWineBottle, FaSearch, FaGlassWhiskey } from 'react-icons/fa';

const Home = () => {
  return (
    <div className="min-h-screen bg-white">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-wine-primary mb-6">
            Discover Your Perfect Wine
          </h1>
          <p className="text-xl text-gray-600 mb-12">
            Explore, Taste, and Enjoy the World of Wines
          </p>

          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard 
              icon={<FaWineBottle className="text-5xl text-wine-primary" />}
              title="Extensive Catalog"
              description="Browse through our curated collection of wines from around the world"
              link="/catalog"
            />
            <FeatureCard 
              icon={<FaSearch className="text-5xl text-wine-primary" />}
              title="Wine Recommender"
              description="Get personalized wine recommendations based on your taste"
              link="/recommend"
            />
            <FeatureCard 
              icon={<FaGlassWhiskey className="text-5xl text-wine-primary" />}
              title="Learn About Wines"
              description="Expand your wine knowledge with our educational resources"
              link="/learn"
            />
          </div>

          <div className="mt-16">
            <Link 
              to="/catalog" 
              className="bg-wine-primary text-white px-8 py-3 rounded-full hover:bg-wine-secondary transition duration-300"
            >
              Explore Wines
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