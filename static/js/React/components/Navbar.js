import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { user, logout } = useAuth();

  return (
    <nav className="bg-wine-primary text-white">
      <div className="container mx-auto px-4 py-3 flex justify-between items-center">
        <Link to="/" className="text-2xl font-bold">
          Wine Recommender
        </Link>
        <ul className="flex space-x-4">
          <li><Link to="/catalog">Catalog</Link></li>
          <li><Link to="/cart">Cart</Link></li>
          {user ? (
            <>
              <li><Link to="/my-account">My Account</Link></li>
              <li><button onClick={logout}>Logout</button></li>
            </>
          ) : (
            <>
              <li><Link to="/login">Login</Link></li>
              <li><Link to="/signup">Sign Up</Link></li>
            </>
          )}
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;