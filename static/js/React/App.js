// static/js/react/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import PrivateRoute from './components/PrivateRoute';
import Navbar from './components/Navbar';
import Footer from './components/Footer';

// Import Pages
import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Catalog from './pages/Catalog';
import WineDetails from './pages/WineDetails';
import Cart from './pages/Cart';
import MyAccount from './pages/MyAccount';

import './styles/index.css'; // Tailwind CSS

function App() {
    return (
        <AuthProvider>
            <Router>
                <div className="flex flex-col min-h-screen">
                    <Navbar />
                    <main className="flex-grow">
                        <Routes>
                            <Route path="/" element={<Home />} />
                            <Route path="/login" element={<Login />} />
                            <Route path="/signup" element={<Signup />} />
                            <Route path="/catalog" element={<Catalog />} />
                            <Route path="/wine/:id" element={<WineDetails />} />
                            {/* Protected Routes */}
                            <Route 
                                path="/catalog" 
                                element={
                                    <PrivateRoute>
                                        <Catalog />
                                    </PrivateRoute>
                                } 
                            />
                            <Route 
                                path="/wine/:id" 
                                element={
                                    <PrivateRoute>
                                        <WineDetails />
                                    </PrivateRoute>
                                } 
                            />
                            <Route 
                                path="/cart" 
                                element={
                                    <PrivateRoute>
                                        <Cart />
                                    </PrivateRoute>
                                } 
                            />
                            <Route 
                                path="/account" 
                                element={
                                    <PrivateRoute>
                                        <MyAccount />
                                    </PrivateRoute>
                                } 
                            />
                        </Routes>
                    </main>
                    <Footer />
                </div>
            </Router>
        </AuthProvider>
    );
}

export default App;