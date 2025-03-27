// Main application JavaScript file
import { initializeWineList } from './pages/wines.js';
import { setupAuthentication } from './auth/auth.js';
import { initializeCart } from './cart/cart.js';
import { setupRecommendations } from './recommendations/recommendations.js';

document.addEventListener('DOMContentLoaded', () => {
    // Initialize components
    setupAuthentication();
    initializeWineList();
    initializeCart();
    setupRecommendations();

    // Setup navigation
    const navLinks = document.querySelectorAll('nav a');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = e.target.getAttribute('href').substring(1);
            navigateToPage(page);
        });
    });
});

// Handle page navigation
function navigateToPage(page) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(p => p.style.display = 'none');
    
    // Show requested page
    const pageElement = document.getElementById(`${page}-page`);
    if (pageElement) {
        pageElement.style.display = 'block';
    }
} 