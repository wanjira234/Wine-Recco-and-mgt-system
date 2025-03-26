import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldAlert, Home, ArrowLeft } from 'lucide-react';

const Unauthorized = () => {
    return (
        <div className="min-h-screen bg-gray-100 flex items-center justify-center px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full text-center">
                <div className="mb-8">
                    <div className="inline-flex items-center justify-center w-24 h-24 bg-red-100 rounded-full">
                        <ShieldAlert className="h-12 w-12 text-red-600" />
                    </div>
                </div>
                
                <h1 className="text-3xl font-extrabold text-gray-900 mb-2">Access Denied</h1>
                <p className="text-lg text-gray-600 mb-8">
                    You don't have permission to access this page.
                </p>
                
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                    <Link
                        to="/"
                        className="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-white bg-wine-600 hover:bg-wine-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-wine-500"
                    >
                        <Home className="h-5 w-5 mr-2" />
                        Go back home
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

export default Unauthorized;