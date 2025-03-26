import React from 'react';
import { BrowserRouter as Router, Routes, Route, Switch, Redirect } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import PrivateRoute from './components/PrivateRoute';
import Navbar from './components/Navbar';
import Footer from './components/Footer';

// Import Pages
import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';
import SignupStep2 from './pages/SignupStep2';
import SignupStep3 from './pages/SignupStep3';
import Catalog from './pages/Catalog';
import WineDetails from './pages/WineDetails';
import Cart from './pages/Cart';
import MyAccount from './pages/MyAccount';

import './styles/index.css'; // Tailwind CSS

const App = () => {
    return (
        <AuthProvider>
            <Router basename="/react">
                <div className="flex flex-col min-h-screen">
                    <Navbar />
                    <main className="flex-grow">
                        <Routes>
                            <Route path="/" element={<Home />} />
                            <Route path="/login" element={<Login />} />
                            <Route path="/signup" element={<Signup />} />
                            <Route path="/signup/step2" element={<SignupStep2 />} />
                            <Route path="/signup/step3" element={<SignupStep3 />} />
                            <Route path="/catalog" element={
                                <PrivateRoute>
                                    <Catalog />
                                </PrivateRoute>
                            } />
                            <Route path="/wine/:id" element={
                                <PrivateRoute>
                                    <WineDetails />
                                </PrivateRoute>
                            } />
                            <Route path="/cart" element={
                                <PrivateRoute>
                                    <Cart />
                                </PrivateRoute>
                            } />
                            <Route path="/account" element={
                                <PrivateRoute>
                                    <MyAccount />
                                </PrivateRoute>
                            } />
                            <Route path="/">
                                <Redirect to="/signup" />
                            </Route>
                        </Routes>
                    </main>
                    <Footer />
                </div>
            </Router>
        </AuthProvider>
    );
};

export default App;