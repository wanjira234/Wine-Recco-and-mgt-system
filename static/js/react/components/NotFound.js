import React from 'react';
import { Link } from 'react-router-dom';
import { Home, Search, ArrowLeft } from 'lucide-react';

const NotFound = () => {
    return (
        <div className="min-h-screen bg-gray-100 flex items-center justify-center px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full text-center">
                <div className="mb-8">
                    <div className="inline-flex items-center justify-center w-24 h-24 bg-wine-100 rounded-full">
                        <span className="text-5xl font-bold text-wine-600">404</span>
                    </div>
                </div>
                
                <h1 className="text-3xl font-extrabold text-gray-900 mb-2">Page Not Found</h1>
                <p className="text-lg text-gray-600 mb-8">
                    The page you're looking for doesn't exist or has been moved.
                </p>
                
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                    <Link
                        to="/"
                        className="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-white bg-wine-600 hover:bg-wine-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-wine-500"
                    >
                        <Home className="h-5 w-5 mr-2" />
                        Go back home
                    </Link>
                    
                    <Link
                        to="/wines"
                        className="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-wine-600 bg-white border-wine-600 hover:bg-wine-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-wine-500"
                    >
                        <Search className="h-5 w-5 mr-2" />
                        Browse wines
                    </Link>
                </div>
                
                <button 
                    onClick={() => window.history.back()}
                    className="mt-8 inline-flex items-center text-wine-600 hover:text-wine-800"
                >
                    <ArrowLeft className="h-4 w-4 mr-1" />
                    Go back to previous page
                </button>
                
                <div className="mt-12 border-t border-gray-200 pt-6">
                    <p className="text-sm text-gray-500">
                        If you believe this is an error, please <a href="/contact" className="text-wine-600 hover:text-wine-800">contact support</a>.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default NotFound;