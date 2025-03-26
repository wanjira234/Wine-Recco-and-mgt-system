import React from 'react';
import { Link } from 'react-router-dom';
import { Facebook, Instagram, Twitter, Mail, Phone, MapPin } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-wine-primary text-white py-12">
      <div className="container mx-auto px-4">
        <div className="grid md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-xl font-bold mb-4">Vinera</h3>
            <p className="text-gray-300 mb-4">
              Discover your perfect wine match with personalized recommendations based on your taste preferences.
            </p>
            <div className="flex space-x-4">
              <a href="#" className="hover:text-gray-300 transition-colors">
                <Facebook size={20} />
              </a>
              <a href="#" className="hover:text-gray-300 transition-colors">
                <Instagram size={20} />
              </a>
              <a href="#" className="hover:text-gray-300 transition-colors">
                <Twitter size={20} />
              </a>
            </div>
          </div>
          
          <div>
            <h3 className="text-xl font-bold mb-4">Quick Links</h3>
            <ul className="space-y-2">
              <li><Link to="/" className="hover:underline transition-colors">Home</Link></li>
              <li><Link to="/catalog" className="hover:underline transition-colors">Catalog</Link></li>
              <li><Link to="/about" className="hover:underline transition-colors">About Us</Link></li>
              <li><Link to="/learn" className="hover:underline transition-colors">Wine Education</Link></li>
              <li><Link to="/preferences" className="hover:underline transition-colors">Set Preferences</Link></li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-xl font-bold mb-4">Customer Service</h3>
            <ul className="space-y-2">
              <li><Link to="/contact" className="hover:underline transition-colors">Contact</Link></li>
              <li><Link to="/shipping" className="hover:underline transition-colors">Shipping</Link></li>
              <li><Link to="/returns" className="hover:underline transition-colors">Returns</Link></li>
              <li><Link to="/faq" className="hover:underline transition-colors">FAQ</Link></li>
              <li><Link to="/privacy" className="hover:underline transition-colors">Privacy Policy</Link></li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-xl font-bold mb-4">Contact Us</h3>
            <ul className="space-y-3">
              <li className="flex items-center">
                <Mail size={18} className="mr-2" />
                <span>support@vinera.com</span>
              </li>
              <li className="flex items-center">
                <Phone size={18} className="mr-2" />
                <span>+1 (555) 123-4567</span>
              </li>
              <li className="flex items-start">
                <MapPin size={18} className="mr-2 mt-1" />
                <span>123 Wine Valley Road<br />Napa, CA 94558</span>
              </li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-gray-700 mt-10 pt-6 text-center">
          <p>&copy; {new Date().getFullYear()} Vinera Wine Recommender. All Rights Reserved.</p>
          <p className="text-sm text-gray-400 mt-2">Drink responsibly. Must be 21+ to purchase.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;