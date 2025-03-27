import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Dashboard from './components/Dashboard';

export default function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            {/* Add more routes as needed */}
          </Routes>
        </main>
      </div>
    </Router>
  );
} 