import axios from 'axios';

export const fetchCartItems = async () => {
    const response = await axios.get('/api/cart'); // Adjust the endpoint as necessary
    return response.data;
};

export const removeCartItem = async (id) => {
    await axios.delete(`/api/cart/${id}`); // Adjust the endpoint as necessary
};

export const updateCartItemQuantity = async (id, quantity) => {
    await axios.put(`/api/cart/${id}`, { quantity }); // Adjust the endpoint as necessary
};
export const saveCartToLocalStorage = (cartItems) => {
    localStorage.setItem('cart', JSON.stringify(cartItems));
};

export const loadCartFromLocalStorage = () => {
    const cart = localStorage.getItem('cart');
    return cart ? JSON.parse(cart) : [];
};