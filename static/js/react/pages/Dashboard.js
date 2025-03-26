import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { toast } from 'react-toastify';

const Dashboard = () => {
    const { user } = useAuth();
    const [recommendations, setRecommendations] = useState([]);
    const [recentOrders, setRecentOrders] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                const [recommendationsRes, ordersRes] = await Promise.all([
                    fetch('/api/recommendations', {
                        headers: {
                            'Authorization': `Bearer ${localStorage.getItem('token')}`
                        }
                    }),
                    fetch('/api/orders/recent', {
                        headers: {
                            'Authorization': `Bearer ${localStorage.getItem('token')}`
                        }
                    })
                ]);

                if (!recommendationsRes.ok || !ordersRes.ok) {
                    throw new Error('Failed to fetch dashboard data');
                }

                const [recommendationsData, ordersData] = await Promise.all([
                    recommendationsRes.json(),
                    ordersRes.json()
                ]);

                setRecommendations(recommendationsData.recommendations);
                setRecentOrders(ordersData.orders);
            } catch (error) {
                toast.error('Failed to load dashboard data');
            } finally {
                setLoading(false);
            }
        };

        fetchDashboardData();
    }, []);

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-100 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-100 py-8">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <h1 className="text-3xl font-bold text-gray-900 mb-8">
                    Welcome back, {user?.username}!
                </h1>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {/* Personalized Recommendations */}
                    <div className="bg-white rounded-lg shadow-md p-6">
                        <h2 className="text-xl font-semibold text-gray-900 mb-4">
                            Recommended for You
                        </h2>
                        <div className="space-y-4">
                            {recommendations.map(wine => (
                                <div key={wine.id} className="flex items-center space-x-4">
                                    <img
                                        src={wine.image_url}
                                        alt={wine.name}
                                        className="w-16 h-16 object-cover rounded"
                                    />
                                    <div>
                                        <h3 className="text-sm font-medium text-gray-900">
                                            {wine.name}
                                        </h3>
                                        <p className="text-sm text-gray-500">
                                            {wine.variety} • {wine.region}
                                        </p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Recent Orders */}
                    <div className="bg-white rounded-lg shadow-md p-6">
                        <h2 className="text-xl font-semibold text-gray-900 mb-4">
                            Recent Orders
                        </h2>
                        <div className="space-y-4">
                            {recentOrders.map(order => (
                                <div key={order.id} className="border-b pb-4">
                                    <div className="flex justify-between items-start">
                                        <div>
                                            <p className="text-sm font-medium text-gray-900">
                                                Order #{order.id}
                                            </p>
                                            <p className="text-sm text-gray-500">
                                                {new Date(order.created_at).toLocaleDateString()}
                                            </p>
                                        </div>
                                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                                            order.status === 'completed' ? 'bg-green-100 text-green-800' :
                                            order.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                                            'bg-yellow-100 text-yellow-800'
                                        }`}>
                                            {order.status}
                                        </span>
                                    </div>
                                    <p className="text-sm text-gray-500 mt-1">
                                        {order.items.length} items • ${order.total_amount}
                                    </p>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Quick Actions */}
                <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4">
                    <a
                        href="/wines"
                        className="bg-white p-4 rounded-lg shadow-md text-center hover:shadow-lg transition-shadow"
                    >
                        <i className="fas fa-wine-bottle text-2xl text-purple-600 mb-2"></i>
                        <p className="text-sm font-medium text-gray-900">Browse Wines</p>
                    </a>
                    <a
                        href="/cart"
                        className="bg-white p-4 rounded-lg shadow-md text-center hover:shadow-lg transition-shadow"
                    >
                        <i className="fas fa-shopping-cart text-2xl text-purple-600 mb-2"></i>
                        <p className="text-sm font-medium text-gray-900">View Cart</p>
                    </a>
                    <a
                        href="/orders"
                        className="bg-white p-4 rounded-lg shadow-md text-center hover:shadow-lg transition-shadow"
                    >
                        <i className="fas fa-list text-2xl text-purple-600 mb-2"></i>
                        <p className="text-sm font-medium text-gray-900">All Orders</p>
                    </a>
                    <a
                        href="/profile"
                        className="bg-white p-4 rounded-lg shadow-md text-center hover:shadow-lg transition-shadow"
                    >
                        <i className="fas fa-user text-2xl text-purple-600 mb-2"></i>
                        <p className="text-sm font-medium text-gray-900">Profile</p>
                    </a>
                </div>
            </div>
        </div>
    );
};

export default Dashboard; 