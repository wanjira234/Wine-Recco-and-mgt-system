import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Menu, X } from 'lucide-react';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="bg-wine-primary text-white">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="text-xl font-bold">Wine Recommender</Link>
          
          {/* Mobile menu button */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden"
            aria-label="Toggle menu"
          >
            {isOpen ? <X size={24} /> : <Menu size={24} />}
          </button>

          {/* Desktop menu */}
          <div className="hidden md:flex space-x-8">
            <Link to="/" className="hover:text-gray-300 transition-colors">Home</Link>
            <Link to="/search" className="hover:text-gray-300 transition-colors">Search</Link>
            <Link to="/recommendations" className="hover:text-gray-300 transition-colors">Recommendations</Link>
            <Link to="/profile" className="hover:text-gray-300 transition-colors">Profile</Link>
            <Link to="/about" className="hover:text-gray-300 transition-colors">About</Link>
          </div>
        </div>

        {/* Mobile menu */}
        {isOpen && (
          <div className="md:hidden py-4">
            <div className="flex flex-col space-y-4">
              <Link to="/" className="hover:text-gray-300 transition-colors">Home</Link>
              <Link to="/search" className="hover:text-gray-300 transition-colors">Search</Link>
              <Link to="/recommendations" className="hover:text-gray-300 transition-colors">Recommendations</Link>
              <Link to="/profile" className="hover:text-gray-300 transition-colors">Profile</Link>
              <Link to="/about" className="hover:text-gray-300 transition-colors">About</Link>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;