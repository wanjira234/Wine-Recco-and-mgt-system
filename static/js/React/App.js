import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider, ProtectedRoute } from './context/AuthContext';
import Navbar from './components/Navbar';
import Home from './components/Home';
import Login from './components/Login';
import Signup from './components/Signup';
import SignupStep2 from './components/SignupStep2';
import SignupStep3 from './components/SignupStep3';
import Dashboard from './components/Dashboard';
import Profile from './components/Profile';
import WineList from './components/WineList';
import WineDetail from './components/WineDetail';
import NotFound from './components/NotFound';

import './styles/index.css'; // Tailwind CSS

const App = () => {
    return (
        <AuthProvider>
            <Router>
                <div className="min-h-screen bg-gray-100">
                    <Navbar />
                    <main>
                        <Routes>
                            <Route path="/" element={<Home />} />
                            <Route path="/login" element={<Login />} />
                            <Route path="/signup" element={<Signup />} />
                            <Route path="/signup/step2" element={<SignupStep2 />} />
                            <Route path="/signup/step3" element={<SignupStep3 />} />
                            <Route
                                path="/dashboard"
                                element={
                                    <ProtectedRoute>
                                        <Dashboard />
                                    </ProtectedRoute>
                                }
                            />
                            <Route
                                path="/profile"
                                element={
                                    <ProtectedRoute>
                                        <Profile />
                                    </ProtectedRoute>
                                }
                            />
                            <Route path="/wines" element={<WineList />} />
                            <Route path="/wines/:id" element={<WineDetail />} />
                            <Route path="*" element={<NotFound />} />
                        </Routes>
                    </main>
                </div>
            </Router>
        </AuthProvider>
    );
};

export default App;