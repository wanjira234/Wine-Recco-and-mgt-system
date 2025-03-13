import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    try {
      await logout();
      // Optionally, redirect to home or show a message
    } catch (error) {
      console.error("Logout failed", error);
    }
  };

  return (
    <nav className="bg-wine-primary text-white">
      <div className="container mx-auto px-4 py-3 flex justify-between items-center">
        <Link to="/" className="text-2xl font-bold hover:underline">
          Wine Recommender
        </Link>
        <ul className="flex space-x-4">
          <li><Link to="/catalog" className="hover:underline">Catalog</Link></li>
          <li><Link to="/cart" className="hover:underline">Cart</Link></li>
          {user ? (
            <>
              <li><Link to="/my-account" className="hover:underline">My Account</Link></li>
              <li>
                <button 
                  onClick={handleLogout} 
                  className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded"
                >
                  Logout
                </button>
              </li>
            </>
          ) : (
            <>
              <li><Link to="/login" className="hover:underline">Login</Link></li>
              <li><Link to="/signup" className="hover:underline">Sign Up</Link></li>
            </>
          )}
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;