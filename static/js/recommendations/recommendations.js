// Recommendations functionality
export function setupRecommendations() {
    initializeRecommendations();
    setupPreferenceForm();
}

async function initializeRecommendations() {
    try {
        const response = await fetch('/api/recommendations');
        if (!response.ok) throw new Error('Failed to fetch recommendations');
        
        const recommendations = await response.json();
        displayRecommendations(recommendations);
    } catch (error) {
        console.error('Error fetching recommendations:', error);
        showError('Failed to load recommendations');
    }
}

function displayRecommendations(recommendations) {
    const container = document.getElementById('recommendations-container');
    if (!container) return;

    container.innerHTML = recommendations.map(wine => `
        <div class="wine-card recommendation">
            <img src="${wine.image}" alt="${wine.name}" class="wine-image">
            <div class="wine-details">
                <h3>${wine.name}</h3>
                <p class="wine-description">${wine.description}</p>
                <div class="wine-meta">
                    <span class="wine-price">$${wine.price.toFixed(2)}</span>
                    <span class="wine-rating">${'★'.repeat(Math.round(wine.rating))}</span>
                </div>
                <div class="recommendation-reason">
                    <p>Recommended because: ${wine.recommendationReason}</p>
                </div>
                <button class="add-to-cart" data-wine-id="${wine.id}">
                    Add to Cart
                </button>
            </div>
        </div>
    `).join('');
}

function setupPreferenceForm() {
    const form = document.getElementById('preference-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        
        try {
            const response = await fetch('/api/preferences', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({
                    priceRange: formData.get('price-range'),
                    wineTypes: Array.from(formData.getAll('wine-types')),
                    tastePreferences: Array.from(formData.getAll('taste-preferences')),
                    occasions: Array.from(formData.getAll('occasions'))
                })
            });

            if (!response.ok) throw new Error('Failed to update preferences');
            
            // Refresh recommendations based on new preferences
            const recommendations = await response.json();
            displayRecommendations(recommendations);
            showSuccess('Preferences updated successfully');
        } catch (error) {
            console.error('Error updating preferences:', error);
            showError('Failed to update preferences');
        }
    });
}

function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    document.body.appendChild(errorDiv);
    setTimeout(() => errorDiv.remove(), 3000);
}

function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.textContent = message;
    document.body.appendChild(successDiv);
    setTimeout(() => successDiv.remove(), 3000);
} 