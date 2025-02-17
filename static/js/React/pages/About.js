import React from 'react';
import { FaWineBottle, FaGlobe, FaHeart } from 'react-icons/fa';

const About = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold text-wine-primary mb-8">About Our Wine Journey</h1>
      
      <div className="grid md:grid-cols-3 gap-8">
        <FeatureSection 
          icon={<FaWineBottle />}
          title="Our Passion"
          description="We are dedicated to bringing the finest wines from around the world to your table."
        />
        <FeatureSection 
          icon={<FaGlobe />}
          title="Global Selection"
          description="Carefully curated wines from the most renowned vineyards across different continents."
        />
        <FeatureSection 
          icon={<FaHeart />}
          title="Quality Commitment"
          description="We ensure every bottle meets our strict quality standards before reaching you."
        />
      </div>

      <div className="mt-12 text-center">
        <h2 className="text-3xl font-semibold mb-4">Our Mission</h2>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          To connect wine enthusiasts with exceptional wines, provide educational 
          resources, and create memorable tasting experiences that celebrate the 
          art and culture of winemaking.
        </p>
      </div>
    </div>
  );
};

const FeatureSection = ({ icon, title, description }) => (
  <div className="text-center p-6 bg-white shadow-lg rounded-lg">
    <div className="text-6xl text-wine-primary mb-4 flex justify-center">
      {icon}
    </div>
    <h3 className="text-2xl font-semibold mb-4">{title}</h3>
    <p className="text-gray-600">{description}</p>
  </div>
);

export default About;