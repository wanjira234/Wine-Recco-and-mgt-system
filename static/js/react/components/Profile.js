import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { userService } from '../services/api';
import { User, Mail, Phone, MapPin, Calendar, Edit, Save, X, Camera, LogOut, Lock, AlertCircle, CheckCircle } from 'lucide-react';

const Profile = () => {
    const navigate = useNavigate();
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [editMode, setEditMode] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        phone: '',
        address: '',
        birthdate: '',
        bio: '',
        notification_preferences: {
            email_notifications: false,
            push_notifications: false,
            sms_notifications: false
        }
    });
    const [passwordData, setPasswordData] = useState({
        current_password: '',
        new_password: '',
        confirm_password: ''
    });
    const [passwordError, setPasswordError] = useState('');
    const [passwordSuccess, setPasswordSuccess] = useState('');
    const [showPasswordModal, setShowPasswordModal] = useState(false);

    useEffect(() => {
        fetchUserProfile();
    }, []);

    const fetchUserProfile = async () => {
        try {
            setLoading(true);
            const response = await userService.getProfile();
            setUser(response.data);
            setFormData({
                name: response.data.name || '',
                email: response.data.email || '',
                phone: response.data.phone || '',
                address: response.data.address || '',
                birthdate: response.data.birthdate || '',
                bio: response.data.bio || '',
                notification_preferences: response.data.notification_preferences || {
                    email_notifications: false,
                    push_notifications: false,
                    sms_notifications: false
                }
            });
        } catch (err) {
            console.error('Error fetching profile:', err);
            setError('Failed to load profile. Please try again later.');
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        
        if (name.startsWith('notification_')) {
            const prefName = name.replace('notification_', '');
            setFormData(prev => ({
                ...prev,
                notification_preferences: {
                    ...prev.notification_preferences,
                    [prefName]: checked
                }
            }));
        } else {
            setFormData(prev => ({
                ...prev,
                [name]: type === 'checkbox' ? checked : value
            }));
        }
    };

    const handlePasswordChange = (e) => {
        const { name, value } = e.target;
        setPasswordData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        
        try {
            await userService.updateProfile(formData);
            setSuccess('Profile updated successfully!');
            setEditMode(false);
            fetchUserProfile(); // Refresh user data
        } catch (err) {
            console.error('Error updating profile:', err);
            setError(err.response?.data?.message || 'Failed to update profile. Please try again.');
        }
    };

    const handlePasswordSubmit = async (e) => {
        e.preventDefault();
        setPasswordError('');
        setPasswordSuccess('');
        
        // Validate passwords
        if (passwordData.new_password !== passwordData.confirm_password) {
            setPasswordError('New passwords do not match');
            return;
        }
        
        if (passwordData.new_password.length < 8) {
            setPasswordError('Password must be at least 8 characters long');
            return;
        }
        
        try {
            await userService.changePassword(passwordData);
            setPasswordSuccess('Password changed successfully!');
            setPasswordData({
                current_password: '',
                new_password: '',
                confirm_password: ''
            });
            
            // Close modal after a delay
            setTimeout(() => {
                setShowPasswordModal(false);
                setPasswordSuccess('');
            }, 2000);
        } catch (err) {
            console.error('Error changing password:', err);
            setPasswordError(err.response?.data?.message || 'Failed to change password. Please check your current password.');
        }
    };

    const handleLogout = async () => {
        try {
            await userService.logout();
            // Clear local storage/session
            localStorage.removeItem('token');
            // Redirect to login
            navigate('/login');
        } catch (err) {
            console.error('Error logging out:', err);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-100 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-wine-600"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-100 py-8">
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
                {/* Profile Header */}
                <div className="bg-white shadow rounded-lg overflow-hidden mb-6">
                    <div className="relative h-40 bg-wine-700">
                        <button 
                            className="absolute top-4 right-4 bg-white p-2 rounded-full shadow-md hover:bg-gray-100"
                            title="Change cover photo"
                        >
                            <Camera className="h-5 w-5 text-gray-700" />
                        </button>
                    </div>
                    <div className="relative px-6 pb-6">
                        <div className="absolute -top-16 left-6">
                            <div className="relative">
                                <div className="h-32 w-32 rounded-full border-4 border-white bg-gray-200 flex items-center justify-center overflow-hidden">
                                    {user?.profile_image ? (
                                        <img 
                                            src={user.profile_image || "/placeholder.svg"} 
                                            alt={user.name} 
                                            className="h-full w-full object-cover"
                                        />
                                    ) : (
                                        <User className="h-16 w-16 text-gray-400" />
                                    )}
                                </div>
                                <button 
                                    className="absolute bottom-0 right-0 bg-white p-1.5 rounded-full shadow-md hover:bg-gray-100 border border-gray-200"
                                    title="Change profile photo"
                                >
                                    <Camera className="h-4 w-4 text-gray-700" />
                                </button>
                            </div>
                        </div>
                        
                        <div className="mt-16 sm:flex sm:items-center sm:justify-between">
                            <div>
                                <h1 className="text-2xl font-bold text-gray-900">{user?.name}</h1>
                                <p className="text-sm text-gray-500">Member since {new Date(user?.created_at).toLocaleDateString()}</p>
                            </div>
                            <div className="mt-4 sm:mt-0 flex space-x-3">
                                <button
                                    onClick={() => setShowPasswordModal(true)}
                                    className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                                >
                                    <Lock className="h-4 w-4 mr-2" />
                                    Change Password
                                </button>
                                <button
                                    onClick={handleLogout}
                                    className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700"
                                >
                                    <LogOut className="h-4 w-4 mr-2" />
                                    Logout
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                
                {/* Success Message */}
                {success && (
                    <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-6 flex items-center">
                        <CheckCircle className="h-5 w-5 mr-2" />
                        <span>{success}</span>
                    </div>
                )}
                
                {/* Error Message */}
                {error && (
                    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6 flex items-center">
                        <AlertCircle className="h-5 w-5 mr-2" />
                        <span>{error}</span>
                    </div>
                )}
                
                {/* Profile Information */}
                <div className="bg-white shadow rounded-lg overflow-hidden mb-6">
                    <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                        <h2 className="text-lg font-medium text-gray-900">Profile Information</h2>
                        <button
                            onClick={() => setEditMode(!editMode)}
                            className="inline-flex items-center px-3 py-1.5 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                        >
                            {editMode ? (
                                <>
                                    <X className="h-4 w-4 mr-1.5" />
                                    Cancel
                                </>
                            ) : (
                                <>
                                    <Edit className="h-4 w-4 mr-1.5" />
                                    Edit Profile
                                </>
                            )}
                        </button>
                    </div>
                    
                    <div className="px-6 py-4">
                        {editMode ? (
                            <form onSubmit={handleSubmit}>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div>
                                        <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                                            Full Name
                                        </label>
                                        <input
                                            type="text"
                                            id="name"
                                            name="name"
                                            value={formData.name}
                                            onChange={handleChange}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-wine-500 focus:border-wine-500"
                                            required
                                        />
                                    </div>
                                    
                                    <div>
                                        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                                            Email Address
                                        </label>
                                        <input
                                            type="email"
                                            id="email"
                                            name="email"
                                            value={formData.email}
                                            onChange={handleChange}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-wine-500 focus:border-wine-500"
                                            required
                                        />
                                    </div>
                                    
                                    <div>
                                        <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-1">
                                            Phone Number
                                        </label>
                                        <input
                                            type="tel"
                                            id="phone"
                                            name="phone"
                                            value={formData.phone}
                                            onChange={handleChange}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-wine-500 focus:border-wine-500"
                                        />
                                    </div>
                                    
                                    <div>
                                        <label htmlFor="birthdate" className="block text-sm font-medium text-gray-700 mb-1">
                                            Date of Birth
                                        </label>
                                        <input
                                            type="date"
                                            id="birthdate"
                                            name="birthdate"
                                            value={formData.birthdate}
                                            onChange={handleChange}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-wine-500 focus:border-wine-500"
                                        />
                                    </div>
                                    
                                    <div className="md:col-span-2">
                                        <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-1">
                                            Address
                                        </label>
                                        <input
                                            type="text"
                                            id="address"
                                            name="address"
                                            value={formData.address}
                                            onChange={handleChange}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-wine-500 focus:border-wine-500"
                                        />
                                    </div>
                                    
                                    <div className="md:col-span-2">
                                        <label htmlFor="bio" className="block text-sm font-medium text-gray-700 mb-1">
                                            Bio
                                        </label>
                                        <textarea
                                            id="bio"
                                            name="bio"
                                            rows="4"
                                            value={formData.bio}
                                            onChange={handleChange}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-wine-500 focus:border-wine-500"
                                            placeholder="Tell us about yourself and your wine preferences..."
                                        />
                                    </div>
                                </div>
                                
                                <div className="mt-6 border-t border-gray-200 pt-6">
                                    <h3 className="text-md font-medium text-gray-900 mb-4">Notification Preferences</h3>
                                    
                                    <div className="space-y-3">
                                        <div className="flex items-center">
                                            <input
                                                type="checkbox"
                                                id="notification_email_notifications"
                                                name="notification_email_notifications"
                                                checked={formData.notification_preferences.email_notifications}
                                                onChange={handleChange}
                                                className="h-4 w-4 text-wine-600 focus:ring-wine-500 border-gray-300 rounded"
                                            />
                                            <label htmlFor="notification_email_notifications" className="ml-2 block text-sm text-gray-700">
                                                Email Notifications
                                            </label>
                                        </div>
                                        
                                        <div className="flex items-center">
                                            <input
                                                type="checkbox"
                                                id="notification_push_notifications"
                                                name="notification_push_notifications"
                                                checked={formData.notification_preferences.push_notifications}
                                                onChange={handleChange}
                                                className="h-4 w-4 text-wine-600 focus:ring-wine-500 border-gray-300 rounded"
                                            />
                                            <label htmlFor="notification_push_notifications" className="ml-2 block text-sm text-gray-700">
                                                Push Notifications
                                            </label>
                                        </div>
                                        
                                        <div className="flex items-center">
                                            <input
                                                type="checkbox"
                                                id="notification_sms_notifications"
                                                name="notification_sms_notifications"
                                                checked={formData.notification_preferences.sms_notifications}
                                                onChange={handleChange}
                                                className="h-4 w-4 text-wine-600 focus:ring-wine-500 border-gray-300 rounded"
                                            />
                                            <label htmlFor="notification_sms_notifications" className="ml-2 block text-sm text-gray-700">
                                                SMS Notifications
                                            </label>
                                        </div>
                                    </div>
                                </div>
                                
                                <div className="mt-6 flex justify-end">
                                    <button
                                        type="button"
                                        onClick={() => setEditMode(false)}
                                        className="mr-3 px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        type="submit"
                                        className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-wine-600 hover:bg-wine-700"
                                    >
                                        <Save className="h-4 w-4 mr-2" />
                                        Save Changes
                                    </button>
                                </div>
                            </form>
                        ) : (
                            <div className="space-y-6">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div>
                                        <h3 className="text-sm font-medium text-gray-500">Full Name</h3>
                                        <p className="mt-1 flex items-center text-sm text-gray-900">
                                            <User className="h-4 w-4 mr-2 text-gray-400" />
                                            {user?.name || 'Not provided'}
                                        </p>
                                    </div>
                                    
                                    <div>
                                        <h3 className="text-sm font-medium text-gray-500">Email Address</h3>
                                        <p className="mt-1 flex items-center text-sm text-gray-900">
                                            <Mail className="h-4 w-4 mr-2 text-gray-400" />
                                            {user?.email || 'Not provided'}
                                        </p>
                                    </div>
                                    
                                    <div>
                                        <h3 className="text-sm font-medium text-gray-500">Phone Number</h3>
                                        <p className="mt-1 flex items-center text-sm text-gray-900">
                                            <Phone className="h-4 w-4 mr-2 text-gray-400" />
                                            {user?.phone || 'Not provided'}
                                        </p>
                                    </div>
                                    
                                    <div>
                                        <h3 className="text-sm font-medium text-gray-500">Date of Birth</h3>
                                        <p className="mt-1 flex items-center text-sm text-gray-900">
                                            <Calendar className="h-4 w-4 mr-2 text-gray-400" />
                                            {user?.birthdate ? new Date(user.birthdate).toLocaleDateString() : 'Not provided'}
                                        </p>
                                    </div>
                                    
                                    <div className="md:col-span-2">
                                        <h3 className="text-sm font-medium text-gray-500">Address</h3>
                                        <p className="mt-1 flex items-center text-sm text-gray-900">
                                            <MapPin className="h-4 w-4 mr-2 text-gray-400" />
                                            {user?.address || 'Not provided'}
                                        </p>
                                    </div>
                                    
                                    {user?.bio && (
                                        <div className="md:col-span-2">
                                            <h3 className="text-sm font-medium text-gray-500">Bio</h3>
                                            <p className="mt-1 text-sm text-gray-900">{user.bio}</p>
                                        </div>
                                    )}
                                </div>
                                
                                <div className="border-t border-gray-200 pt-6">
                                    <h3 className="text-sm font-medium text-gray-500 mb-3">Notification Preferences</h3>
                                    
                                    <div className="space-y-2">
                                        <p className="flex items-center text-sm">
                                            <span className={`inline-block h-2 w-2 rounded-full mr-2 ${user?.notification_preferences?.email_notifications ? 'bg-green-500' : 'bg-gray-300'}`}></span>
                                            Email Notifications: {user?.notification_preferences?.email_notifications ? 'Enabled' : 'Disabled'}
                                        </p>
                                        
                                        <p className="flex items-center text-sm">
                                            <span className={`inline-block h-2 w-2 rounded-full mr-2 ${user?.notification_preferences?.push_notifications ? 'bg-green-500' : 'bg-gray-300'}`}></span>
                                            Push Notifications: {user?.notification_preferences?.push_notifications ? 'Enabled' : 'Disabled'}
                                        </p>
                                        
                                        <p className="flex items-center text-sm">
                                            <span className={`inline-block h-2 w-2 rounded-full mr-2 ${user?.notification_preferences?.sms_notifications ? 'bg-green-500' : 'bg-gray-300'}`}></span>
                                            SMS Notifications: {user?.notification_preferences?.sms_notifications ? 'Enabled' : 'Disabled'}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
                
                {/* Wine Preferences Summary */}
                <div className="bg-white shadow rounded-lg overflow-hidden mb-6">
                    <div className="px-6 py-4 border-b border-gray-200">
                        <h2 className="text-lg font-medium text-gray-900">Wine Preferences</h2>
                    </div>
                    
                    <div className="px-6 py-4">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <div>
                                <h3 className="text-sm font-medium text-gray-500">Preferred Wine Types</h3>
                                <div className="mt-2 flex flex-wrap gap-2">
                                    {user?.preferences?.wine_types?.map(type => (
                                        <span key={type.id} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-wine-100 text-wine-800">
                                            {type.name}
                                        </span>
                                    ))}
                                    {(!user?.preferences?.wine_types || user.preferences.wine_types.length === 0) && (
                                        <span className="text-sm text-gray-500">No preferences set</span>
                                    )}
                                </div>
                            </div>
                            
                            <div>
                                <h3 className="text-sm font-medium text-gray-500">Flavor Preferences</h3>
                                <div className="mt-2 flex flex-wrap gap-2">
                                    {user?.preferences?.flavors?.map(flavor => (
                                        <span key={flavor.id} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800">
                                            {flavor.name}
                                        </span>
                                    ))}
                                    {(!user?.preferences?.flavors || user.preferences.flavors.length === 0) && (
                                        <span className="text-sm text-gray-500">No preferences set</span>
                                    )}
                                </div>
                            </div>
                            
                            <div>
                                <h3 className="text-sm font-medium text-gray-500">Price Range</h3>
                                <p className="mt-2 text-sm text-gray-900">
                                    {user?.preferences?.price_range === 'budget' && 'Budget ($10-20)'}
                                    {user?.preferences?.price_range === 'mid' && 'Mid-Range ($20-50)'}
                                    {user?.preferences?.price_range === 'premium' && 'Premium ($50-100)'}
                                    {user?.preferences?.price_range === 'luxury' && 'Luxury ($100+)'}
                                    {!user?.preferences?.price_range && 'No preference set'}
                                </p>
                            </div>
                        </div>
                        
                        <div className="mt-6 flex justify-end">
                            <button
                                onClick={() => navigate('/preferences')}
                                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-wine-600 hover:bg-wine-700"
                            >
                                <Edit className="h-4 w-4 mr-2" />
                                Update Wine Preferences
                            </button>
                        </div>
                    </div>
                </div>
                
                {/* Account Activity */}
                <div className="bg-white shadow rounded-lg overflow-hidden">
                    <div className="px-6 py-4 border-b border-gray-200">
                        <h2 className="text-lg font-medium text-gray-900">Account Activity</h2>
                    </div>
                    
                    <div className="px-6 py-4">
                        <div className="space-y-6">
                            <div>
                                <h3 className="text-sm font-medium text-gray-500">Recent Activity</h3>
                                <ul className="mt-2 divide-y divide-gray-200">
                                    {user?.activity?.slice(0, 5).map((item, index) => (
                                        <li key={index} className="py-3">
                                            <div className="flex space-x-3">
                                                <div className="flex-shrink-0">
                                                    <div className="h-8 w-8 rounded-full bg-wine-100 flex items-center justify-center">
                                                        <span className="text-wine-600 text-xs font-medium">{item.type.charAt(0)}</span>
                                                    </div>
                                                </div>
                                                <div className="min-w-0 flex-1">
                                                    <p className="text-sm text-gray-900">{item.description}</p>
                                                    <p className="text-xs text-gray-500">{new Date(item.timestamp).toLocaleString()}</p>
                                                </div>
                                            </div>
                                        </li>
                                    ))}
                                    {(!user?.activity || user.activity.length === 0) && (
                                        <li className="py-3 text-sm text-gray-500">No recent activity</li>
                                    )}
                                </ul>
                            </div>
                            
                            <div>
                                <h3 className="text-sm font-medium text-gray-500">Account Statistics</h3>
                                <dl className="mt-2 grid grid-cols-1 gap-5 sm:grid-cols-3">
                                    <div className="px-4 py-5 bg-gray-50 shadow rounded-lg overflow-hidden sm:p-6">
                                        <dt className="text-sm font-medium text-gray-500 truncate">Wines Rated</dt>
                                        <dd className="mt-1 text-3xl font-semibold text-gray-900">{user?.stats?.wines_rated || 0}</dd>
                                    </div>
                                    
                                    <div className="px-4 py-5 bg-gray-50 shadow rounded-lg overflow-hidden sm:p-6">
                                        <dt className="text-sm font-medium text-gray-500 truncate">Wines Saved</dt>
                                        <dd className="mt-1 text-3xl font-semibold text-gray-900">{user?.stats?.wines_saved || 0}</dd>
                                    </div>
                                    
                                    <div className="px-4 py-5 bg-gray-50 shadow rounded-lg overflow-hidden sm:p-6">
                                        <dt className="text-sm font-medium text-gray-500 truncate">Reviews Written</dt>
                                        <dd className="mt-1 text-3xl font-semibold text-gray-900">{user?.stats?.reviews_written || 0}</dd>
                                    </div>
                                </dl>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            {/* Password Change Modal */}
            {showPasswordModal && (
                <div className="fixed inset-0 z-10 overflow-y-auto">
                    <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
                        <div className="fixed inset-0 transition-opacity" aria-hidden="true">
                            <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
                        </div>
                        
                        <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
                        
                        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
                            <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                                <div className="sm:flex sm:items-start">
                                    <div className="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-wine-100 sm:mx-0 sm:h-10 sm:w-10">
                                        <Lock className="h-6 w-6 text-wine-600" />
                                    </div>
                                    <div className="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                                        <h3 className="text-lg leading-6 font-medium text-gray-900">
                                            Change Password
                                        </h3>
                                        <div className="mt-2">
                                            <p className="text-sm text-gray-500">
                                                Please enter your current password and a new password to update your account security.
                                            </p>
                                        </div>
                                    </div>
                                </div>
                                
                                {passwordSuccess && (
                                    <div className="mt-4 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded flex items-center">
                                        <CheckCircle className="h-5 w-5 mr-2" />
                                        <span>{passwordSuccess}</span>
                                    </div>
                                )}
                                
                                {passwordError && (
                                    <div className="mt-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded flex items-center">
                                        <AlertCircle className="h-5 w-5 mr-2" />
                                        <span>{passwordError}</span>
                                    </div>
                                )}
                                
                                <form onSubmit={handlePasswordSubmit} className="mt-4">
                                    <div className="space-y-4">
                                        <div>
                                            <label htmlFor="current_password" className="block text-sm font-medium text-gray-700 mb-1">
                                                Current Password
                                            </label>
                                            <input
                                                type="password"
                                                id="current_password"
                                                name="current_password"
                                                value={passwordData.current_password}
                                                onChange={handlePasswordChange}
                                                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-wine-500 focus:border-wine-500"
                                                required
                                            />
                                        </div>
                                        
                                        <div>
                                            <label htmlFor="new_password" className="block text-sm font-medium text-gray-700 mb-1">
                                                New Password
                                            </label>
                                            <input
                                                type="password"
                                                id="new_password"
                                                name="new_password"
                                                value={passwordData.new_password}
                                                onChange={handlePasswordChange}
                                                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-wine-500 focus:border-wine-500"
                                                required
                                                minLength={8}
                                            />
                                            <p className="mt-1 text-xs text-gray-500">
                                                Password must be at least 8 characters long
                                            </p>
                                        </div>
                                        
                                        <div>
                                            <label htmlFor="confirm_password" className="block text-sm font-medium text-gray-700 mb-1">
                                                Confirm New Password
                                            </label>
                                            <input
                                                type="password"
                                                id="confirm_password"
                                                name="confirm_password"
                                                value={passwordData.confirm_password}
                                                onChange={handlePasswordChange}
                                                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-wine-500 focus:border-wine-500"
                                                required
                                            />
                                        </div>
                                    </div>
                                </form>
                            </div>
                            <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                                <button
                                    type="button"
                                    onClick={handlePasswordSubmit}
                                    className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-wine-600 text-base font-medium text-white hover:bg-wine-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-wine-500 sm:ml-3 sm:w-auto sm:text-sm"
                                >
                                    Update Password
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setShowPasswordModal(false)}
                                    className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-wine-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
                                >
                                    Cancel
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Profile;