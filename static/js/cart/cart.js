// Cart functionality
export function initializeCart() {
    setupCartListeners();
    updateCartDisplay();
}

let cart = JSON.parse(localStorage.getItem('cart')) || [];

function setupCartListeners() {
    // Listen for add to cart button clicks
    document.addEventListener('click', (e) => {
        if (e.target.matches('.add-to-cart')) {
            const wineId = e.target.dataset.wineId;
            addToCart(wineId);
        }
    });

    // Setup cart icon click for showing cart modal
    const cartIcon = document.getElementById('cart-icon');
    if (cartIcon) {
        cartIcon.addEventListener('click', showCartModal);
    }
}

async function addToCart(wineId) {
    try {
        const response = await fetch(`/api/wines/${wineId}`);
        if (!response.ok) throw new Error('Wine not found');
        
        const wine = await response.json();
        const existingItem = cart.find(item => item.id === wine.id);
        
        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            cart.push({
                id: wine.id,
                name: wine.name,
                price: wine.price,
                quantity: 1,
                image: wine.image
            });
        }
        
        saveCart();
        updateCartDisplay();
        showNotification('Added to cart');
    } catch (error) {
        console.error('Error adding to cart:', error);
        showNotification('Failed to add to cart', 'error');
    }
}

function removeFromCart(wineId) {
    cart = cart.filter(item => item.id !== wineId);
    saveCart();
    updateCartDisplay();
    showNotification('Removed from cart');
}

function updateQuantity(wineId, change) {
    const item = cart.find(item => item.id === wineId);
    if (item) {
        item.quantity += change;
        if (item.quantity <= 0) {
            removeFromCart(wineId);
        } else {
            saveCart();
            updateCartDisplay();
        }
    }
}

function saveCart() {
    localStorage.setItem('cart', JSON.stringify(cart));
}

function updateCartDisplay() {
    // Update cart count
    const cartCount = document.getElementById('cart-count');
    if (cartCount) {
        const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
        cartCount.textContent = totalItems;
    }

    // Update cart modal if it's open
    const cartItems = document.getElementById('cart-items');
    if (cartItems) {
        cartItems.innerHTML = cart.map(item => `
            <div class="cart-item">
                <img src="${item.image}" alt="${item.name}" class="cart-item-image">
                <div class="cart-item-details">
                    <h3>${item.name}</h3>
                    <p>$${item.price.toFixed(2)}</p>
                    <div class="quantity-controls">
                        <button onclick="updateQuantity('${item.id}', -1)">-</button>
                        <span>${item.quantity}</span>
                        <button onclick="updateQuantity('${item.id}', 1)">+</button>
                    </div>
                </div>
                <button onclick="removeFromCart('${item.id}')" class="remove-item">×</button>
            </div>
        `).join('');

        // Update total
        const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        const cartTotal = document.getElementById('cart-total');
        if (cartTotal) {
            cartTotal.textContent = `Total: $${total.toFixed(2)}`;
        }
    }
}

function showCartModal() {
    const modal = document.getElementById('cart-modal');
    if (modal) {
        modal.style.display = 'block';
        updateCartDisplay();
    }
}

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}

// Expose necessary functions to window for onclick handlers
window.removeFromCart = removeFromCart;
window.updateQuantity = updateQuantity; 