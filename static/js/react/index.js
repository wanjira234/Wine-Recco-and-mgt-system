import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './styles/index.css';

// Wait for the DOM to be ready
document.addEventListener('DOMContentLoaded', () => {
  // Get the root element
  const container = document.getElementById('root');
  
  if (container) {
    // Create a root
    const root = createRoot(container);
    
    // Initial render
    root.render(
      <React.StrictMode>
        <App />
      </React.StrictMode>
    );
  } else {
    console.error('Root element not found');
  }
}); 