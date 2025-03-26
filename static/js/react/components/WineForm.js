import React, { useState, useEffect } from 'react';
import { Wine, Image, X, Upload, Save } from 'lucide-react';

const WineForm = ({ wine, onSubmit, onCancel }) => {
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        image: '',
        variety: '',
        region: '',
        country: '',
        vintage: '',
        price: '',
        body: '',
        sweetness: '',
        acidity: '',
        tannins: '',
        food_pairings: []
    });
    const [errors, setErrors] = useState({});
    const [imagePreview, setImagePreview] = useState('');
    const [pairingInput, setPairingInput] = useState('');

    useEffect(() => {
        if (wine) {
            setFormData({
                name: wine.name || '',
                description: wine.description || '',
                image: wine.image_url || '',
                variety: wine.variety || '',
                region: wine.region || '',
                country: wine.country || '',
                vintage: wine.vintage || '',
                price: wine.price || '',
                body: wine.body || '',
                sweetness: wine.sweetness || '',
                acidity: wine.acidity || '',
                tannins: wine.tannins || '',
                food_pairings: wine.food_pairings || []
            });
            
            if (wine.image_url) {
                setImagePreview(wine.image_url);
            }
        }
    }, [wine]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({
            ...formData,
            [name]: value
        });
        
        // Clear error when field is edited
        if (errors[name]) {
            setErrors({
                ...errors,
                [name]: ''
            });
        }
    };

    const handleImageChange = (e) => {
        const value = e.target.value;
        setFormData({
            ...formData,
            image: value
        });
        
        // Update image preview
        setImagePreview(value);
    };

    const handleAddPairing = () => {
        if (pairingInput.trim()) {
            setFormData({
                ...formData,
                food_pairings: [...formData.food_pairings, pairingInput.trim()]
            });
            setPairingInput('');
        }
    };

    const handleRemovePairing = (index) => {
        const updatedPairings = [...formData.food_pairings];
        updatedPairings.splice(index, 1);
        setFormData({
            ...formData,
            food_pairings: updatedPairings
        });
    };

    const validateForm = () => {
        const newErrors = {};
        
        if (!formData.name) newErrors.name = 'Name is required';
        if (!formData.description) newErrors.description = 'Description is required';
        if (!formData.variety) newErrors.variety = 'Variety is required';
        if (!formData.region) newErrors.region = 'Region is required';
        if (!formData.country) newErrors.country = 'Country is required';
        
        if (formData.price && isNaN(parseFloat(formData.price))) {
            newErrors.price = 'Price must be a number';
        }
        
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        
        if (validateForm()) {
            // Convert price to number if it exists
            const submissionData = {
                ...formData,
                price: formData.price ? parseFloat(formData.price) : null
            };
            
            onSubmit(submissionData);
        }
    };

    return (
        <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900 flex items-center">
                    <Wine className="h-6 w-6 mr-2 text-wine-600" />
                    {wine ? 'Edit Wine' : 'Add New Wine'}
                </h2>
                {onCancel && (
                    <button 
                        type="button" 
                        onClick={onCancel}
                        className="text-gray-500 hover:text-gray-700"
                    >
                        <X className="h-5 w-5" />
                    </button>
                )}
            </div>
            
            <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Left Column */}
                    <div className="space-y-6">
                        <div>
                            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                                Wine Name*
                            </label>
                            <input
                                type="text"
                                id="name"
                                name="name"
                                value={formData.name}
                                onChange={handleChange}
                                className={`w-full px-3 py-2 border ${errors.name ? 'border-red-500' : 'border-gray-300'} rounded-md shadow-sm focus:outline-none focus:ring-wine-500 focus:border-wine-500`}
                            />
                            {errors.name && <p className="mt-1 text-sm text-red-600">{errors.name}</p>}
                        </div>
                        
                        <div>
                            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
                                Description*
                            </label>
                            <textarea
                                id="description"
                                name="description"
                                rows="4"
                                value={formData.description}
                                onChange={handleChange}
                                className={`w-full px-3 py-2 border ${errors.description ? 'border-red-500' : 'border-gray-300'} rounded-md shadow-sm focus:outline-none focus:ring-wine-500 focus:border-wine-500`}
                            />
                            {errors.description && <p className="mt-1 text-sm text-red-600">{errors.description}</p>}
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label htmlFor="variety" className="block text-sm font-medium text-gray-700 mb-1">
                                    Variety*
                                </label>
                                <input
                                    type="text"
                                    id="variety"
                                    name="variety"
                                    value={formData.variety}
                                    onChange={handleChange}
                                    className={`w-full px-3 py-2 border ${errors.variety ? 'border-red-500' : 'border-gray-300'} rounded-md shadow-sm focus:outline-none focus:ring-wine-500 focus:border-wine-500`}
                                />
                                {errors.variety && <p className="mt-1 text-sm text-red-600">{errors.variety}</p>}
                            </div>
                            
                            <div>
                                <label htmlFor="vintage" className="block text-sm font-medium text-gray-700 mb-1">
                                    Vintage
                                </label>
                                <input
                                    type="text"
                                    id="vintage"
                                    name="vintage"
                                    value={formData.vintage}
                                    onChange={handleChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-wine-500 focus:border-wine-500"
                                />
                            </div>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label htmlFor="region" className="block text-sm font-medium text-gray-700 mb-1">
                                    Region*
                                </label>
                                <input
                                    type="text"
                                    id="region"
                                    name="region"
                                    value={formData.region}
                                    onChange={handleChange}
                                    className={`w-full px-3 py-2 border ${errors.region ? 'border-red-500' : 'border-gray-300'} rounded-md shadow-sm focus:outline-none focus:ring-wine-500 focus:border-wine-500`}
                                />
                                {errors.region && <p className="mt-1 text-sm text-red-600">{errors.region}</p>}
                            </div>
                            
                            <div>
                                <label htmlFor="country" className="block text-sm font-medium text-gray-700 mb-1">
                                    Country*
                                </label>
                                <input
                                    type="text"
                                    id="country"
                                    name="country"
                                    value={formData.country}
                                    onChange={handleChange}
                                    className={`w-full px-3 py-2 border ${errors.country ? 'border-red-500' : 'border-gray-300'} rounded-md shadow-sm focus:outline-none focus:ring-wine-500 focus:border-wine-500`}
                                />
                                {errors.country && <p className="mt-1 text-sm text-red-600">{errors.country}</p>}
                            </div>
                        </div>
                        
                        <div>
                            <label htmlFor="price" className="block text-sm font-medium text-gray-700 mb-1">
                                Price ($)
                            </label>
                            <input
                                type="text"
                                id="price"
                                name="price"
                                value={formData.price}
                                onChange={handleChange}
                                className={`w-full px-3 py-2 border ${errors.price ? 'border-red-500' : 'border-gray-300'} rounded-md shadow-sm focus:outline-none focus:ring-wine-500 focus:border-wine-500`}
                            />
                            {errors.price && <p className="mt-1 text-sm text-red-600">{errors.price}</p>}
                        </div>
                    </div>
                    
                    {/* Right Column */}
                    <div className="space-y-6">
                        <div>
                            <label htmlFor="image" className="block text-sm font-medium text-gray-700 mb-1">
                                Image URL
                            </label>
                            <div className="flex">
                                <input
                                    type="text"
                                    id="image"
                                    name="image"
                                    value={formData.image}
                                    onChange={handleImageChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-l-md shadow-sm focus:outline-none focus:ring-wine-500 focus:border-wine-500"
                                />
                                <button
                                    type="button"
                                    className="px-3 py-2 bg-gray-100 border border-l-0 border-gray-300 rounded-r-md text-gray-600 hover:bg-gray-200"
                                >
                                    <Upload className="h-5 w-5" />
                                </button>
                            </div>
                            
                            {imagePreview && (
                                <div className="mt-2 relative">
                                    <div className="aspect-w-1 aspect-h-1 rounded-md overflow-hidden bg-gray-200 w-full max-h-48">
                                        <img 
                                            src={imagePreview || "/placeholder.svg"} 
                                            alt="Wine preview" 
                                            className="object-cover"
                                            onError={(e) => {
                                                e.target.onerror = null;
                                                e.target.src = '/images/wine-placeholder.jpg';
                                            }}
                                        />
                                    </div>
                                    <button
                                        type="button"
                                        onClick={() => {
                                            setFormData({...formData, image: ''});
                                            setImagePreview('');
                                        }}
                                        className="absolute top-2 right-2 bg-white rounded-full p-1 shadow-sm"
                                    >
                                        <X className="h-4 w-4 text-gray-600" />
                                    </button>
                                </div>
                            )}
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label htmlFor="body" className="block text-sm font-medium text-gray-700 mb-1">
                                    Body
                                </label>
                                <select
                                    id="body"
                                    name="body"
                                    value={formData.body}
                                    onChange={handleChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-wine-500 focus:border-wine-500"
                                >
                                    <option value="">Select body</option>
                                    <option value="Light">Light</option>
                                    <option value="Medium">Medium</option>
                                    <option value="Full">Full</option>
                                </select>
                            </div>
                            
                            <div>
                                <label htmlFor="sweetness" className="block text-sm font-medium text-gray-700 mb-1">
                                    Sweetness
                                </label>
                                <select
                                    id="sweetness"
                                    name="sweetness"
                                    value={formData.sweetness}
                                    onChange={handleChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-wine-500 focus:border-wine-500"
                                >
                                    <option value="">Select sweetness</option>
                                    <option value="Dry">Dry</option>
                                    <option value="Off-Dry">Off-Dry</option>
                                    <option value="Medium">Medium</option>
                                    <option value="Sweet">Sweet</option>
                                </select>
                            </div>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label htmlFor="acidity" className="block text-sm font-medium text-gray-700 mb-1">
                                    Acidity
                                </label>
                                <select
                                    id="acidity"
                                    name="acidity"
                                    value={formData.acidity}
                                    onChange={handleChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-wine-500 focus:border-wine-500"
                                >
                                    <option value="">Select acidity</option>
                                    <option value="Low">Low</option>
                                    <option value="Medium">Medium</option>
                                    <option value="High">High</option>
                                </select>
                            </div>
                            
                            <div>
                                <label htmlFor="tannins" className="block text-sm font-medium text-gray-700 mb-1">
                                    Tannins
                                </label>
                                <select
                                    id="tannins"
                                    name="tannins"
                                    value={formData.tannins}
                                    onChange={handleChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-wine-500 focus:border-wine-500"
                                >
                                    <option value="">Select tannins</option>
                                    <option value="Low">Low</option>
                                    <option value="Medium">Medium</option>
                                    <option value="High">High</option>
                                </select>
                            </div>
                        </div>
                        
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Food Pairings
                            </label>
                            <div className="flex">
                                <input
                                    type="text"
                                    value={pairingInput}
                                    onChange={(e) => setPairingInput(e.target.value)}
                                    placeholder="Add a food pairing"
                                    className="w-full px-3 py-2 border border-gray-300 rounded-l-md shadow-sm focus:outline-none focus:ring-wine-500 focus:border-wine-500"
                                    onKeyPress={(e) => {
                                        if (e.key === 'Enter') {
                                            e.preventDefault();
                                            handleAddPairing();
                                        }
                                    }}
                                />
                                <button
                                    type="button"
                                    onClick={handleAddPairing}
                                    className="px-3 py-2 bg-wine-600 border border-wine-600 rounded-r-md text-white hover:bg-wine-700"
                                >
                                    Add
                                </button>
                            </div>
                            
                            {formData.food_pairings.length > 0 && (
                                <div className="mt-2 flex flex-wrap gap-2">
                                    {formData.food_pairings.map((pairing, index) => (
                                        <div 
                                            key={index} 
                                            className="bg-gray-100 px-3 py-1 rounded-full flex items-center text-sm"
                                        >
                                            <span>{pairing}</span>
                                            <button
                                                type="button"
                                                onClick={() => handleRemovePairing(index)}
                                                className="ml-1 text-gray-500 hover:text-gray-700"
                                            >
                                                <X className="h-3 w-3" />
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
                
                <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
                    {onCancel && (
                        <button
                            type="button"
                            onClick={onCancel}
                            className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-wine-500"
                        >
                            Cancel
                        </button>
                    )}
                    <button
                        type="submit"
                        className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-wine-600 hover:bg-wine-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-wine-500"
                    >
                        <Save className="h-4 w-4 mr-2" />
                        {wine ? 'Update Wine' : 'Add Wine'}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default WineForm;