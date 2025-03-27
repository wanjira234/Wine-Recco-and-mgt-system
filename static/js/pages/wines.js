// Wine list functionality
export function initializeWineList() {
    fetchWines();
    setupFilters();
    setupSorting();
}

async function fetchWines() {
    try {
        const response = await fetch('/api/wines');
        const wines = await response.json();
        displayWines(wines);
    } catch (error) {
        console.error('Error fetching wines:', error);
    }
}

function displayWines(wines) {
    const wineList = document.getElementById('wine-list');
    if (!wineList) return;

    wineList.innerHTML = wines.map(wine => `
        <div class="wine-card">
            <img src="${wine.image_url || '/static/images/placeholder-wine.jpg'}" alt="${wine.name}">
            <h3>${wine.name}</h3>
            <p>${wine.description}</p>
            <div class="wine-details">
                <span class="price">$${wine.price}</span>
                <span class="rating">${wine.rating}/5</span>
            </div>
            <button onclick="addToCart(${wine.id})">Add to Cart</button>
        </div>
    `).join('');
}

function setupFilters() {
    // Wine filtering functionality
    const filters = document.querySelectorAll('.wine-filter');
    filters.forEach(filter => {
        filter.addEventListener('change', () => {
            applyFilters();
        });
    });
}

function setupSorting() {
    // Wine sorting functionality
    const sortSelect = document.getElementById('sort-wines');
    if (sortSelect) {
        sortSelect.addEventListener('change', () => {
            const value = sortSelect.value;
            sortWines(value);
        });
    }
}

function applyFilters() {
    // Implementation of wine filtering
}

function sortWines(criteria) {
    // Implementation of wine sorting
} 