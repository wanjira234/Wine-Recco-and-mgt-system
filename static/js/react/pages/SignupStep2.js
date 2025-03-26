import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const SignupStep2 = ({ onNext, onBack }) => {
    const [selectedWines, setSelectedWines] = useState([]);
    const navigate = useNavigate();

    const wineTypes = [
        { id: 1, name: 'Red Wine', image: '/static/images/backgrounds/red_wine.jpg' },
        { id: 2, name: 'White Wine', image: '/static/images/backgrounds/white_wine.jpg' },
        { id: 3, name: 'Rosé', image: '/static/images/backgrounds/rose_wine.jpg' },
        { id: 4, name: 'Sparkling', image: '/static/images/backgrounds/sparkling_wine.jpg' }
    ];

    const handleWineSelection = (wineId) => {
        setSelectedWines(prev => 
            prev.includes(wineId) 
                ? prev.filter(id => id !== wineId)
                : [...prev, wineId]
        );
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onNext(selectedWines);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-teal-500 to-teal-600 py-8 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md mx-auto bg-white rounded-xl shadow-xl p-6">
                <div className="text-center mb-8">
                    <h2 className="text-2xl font-bold text-gray-800">
                        Create Account
                    </h2>
                    <p className="mt-2 text-sm text-gray-600">
                        Select your wine preferences
                    </p>
                    {/* Progress indicator */}
                    <div className="flex justify-center items-center space-x-2 mt-4">
                        <div className="w-3 h-3 rounded-full bg-teal-500"></div>
                        <div className="w-3 h-3 rounded-full bg-teal-500"></div>
                        <div className="w-3 h-3 rounded-full bg-gray-300"></div>
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="grid grid-cols-2 gap-4">
                        {wineTypes.map((wine) => (
                            <div key={wine.id} className="relative group">
                                <input
                                    type="checkbox"
                                    id={`wine-${wine.id}`}
                                    checked={selectedWines.includes(wine.id)}
                                    onChange={() => handleWineSelection(wine.id)}
                                    className="peer absolute opacity-0 w-full h-full top-0 left-0 cursor-pointer z-10"
                                />
                                <label
                                    htmlFor={`wine-${wine.id}`}
                                    className="block relative overflow-hidden rounded-lg border-2 border-gray-200 transition-all duration-300 peer-checked:border-teal-500 hover:border-teal-200"
                                >
                                    <div className="relative p-4 transition-all duration-300">
                                        <img
                                            src={wine.image}
                                            alt={wine.name}
                                            className="w-full h-24 object-cover rounded-md mb-2"
                                        />
                                        <h3 className="text-gray-800 font-medium text-sm">{wine.name}</h3>
                                        <div className="absolute top-2 right-2 w-5 h-5 rounded-full bg-teal-500 text-white flex items-center justify-center transform scale-0 transition-transform duration-300 peer-checked:scale-100">
                                            ✓
                                        </div>
                                    </div>
                                </label>
                            </div>
                        ))}
                    </div>

                    <div className="flex justify-between pt-6">
                        <button
                            type="button"
                            onClick={onBack}
                            className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-full text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-teal-500"
                        >
                            Back
                        </button>
                        <button
                            type="submit"
                            className="inline-flex items-center px-6 py-2 border border-transparent text-sm font-medium rounded-full text-white bg-teal-500 hover:bg-teal-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-teal-500"
                        >
                            Continue
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default SignupStep2; 