import React from 'react';
import { Link } from 'react-router-dom';
import { Bell, Search, User } from 'lucide-react';

export default function Header() {
  return (
    <header className="border-b">
      <div className="flex h-16 items-center px-4">
        <div className="flex items-center space-x-4">
          <Link to="/" className="text-xl font-bold">WineRecco</Link>
          <nav className="hidden md:flex space-x-4">
            <Link to="/wines" className="text-sm font-medium hover:text-primary">Wines</Link>
            <Link to="/recommendations" className="text-sm font-medium hover:text-primary">Recommendations</Link>
            <Link to="/inventory" className="text-sm font-medium hover:text-primary">Inventory</Link>
            <Link to="/analytics" className="text-sm font-medium hover:text-primary">Analytics</Link>
          </nav>
        </div>
        <div className="ml-auto flex items-center space-x-4">
          <button className="p-2 hover:bg-gray-100 rounded-full">
            <Search className="h-5 w-5" />
          </button>
          <button className="p-2 hover:bg-gray-100 rounded-full">
            <Bell className="h-5 w-5" />
          </button>
          <button className="p-2 hover:bg-gray-100 rounded-full">
            <User className="h-5 w-5" />
          </button>
        </div>
      </div>
    </header>
  );
} 