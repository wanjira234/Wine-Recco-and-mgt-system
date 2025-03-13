import React from 'react';
import { Link } from 'react-router-dom';

const Footer = () => {
  return (
    <footer className="bg-wine-primary text-white py-8">
      <div className="container mx-auto px-4 grid md:grid-cols-3 gap-8">
        <div>
          <h3 className="text-xl font-bold mb-4">Quick Links</h3>
          <ul>
            <li><Link to="/" className="hover:underline">Home</Link></li>
            <li><Link to="/catalog" className="hover:underline">Catalog</Link></li>
            <li><Link to="/about" className="hover:underline">About Us</Link></li>
          </ul>
        </div>
        <div>
          <h3 className="text-xl font-bold mb-4">Customer Service</h3>
          <ul>
            <li><Link to="/contact" className="hover:underline">Contact</Link></li>
            <li><Link to="/shipping" className="hover:underline">Shipping</Link></li>
            <li><Link to="/returns" className="hover:underline">Returns</Link></li>
          </ul>
        </div>
        <div>
          <h3 className="text-xl font-bold mb-4">Connect With Us</h3>
          <div className="flex space-x-4">
            <a href="#" className="hover:text-gray-300">Facebook</a>
            <a href="#" className="hover:text-gray-300">Instagram</a>
            <a href="#" className="hover:text-gray-300">Twitter</a>
          </div>
        </div>
      </div>
      <div className="text-center mt-8">
        <p>&copy; {new Date().getFullYear()} Wine Recommender. All Rights Reserved.</p>
      </div>
    </footer>
  );
};

export default Footer;