import React, { useState } from 'react';
import { FaTrash, FaShoppingCart } from 'react-icons/fa';

const Cart = () => {
  const [cartItems, setCartItems] = useState([
    {
      id: 1,
      name: 'Château Margaux',
      price: 599.99,
      quantity: 1
    },
    // More cart items
  ]);

  const removeFromCart = (id) => {
    setCartItems(cartItems.filter(item => item.id !== id));
  };

  const updateQuantity = (id, newQuantity) => {
    setCartItems(cartItems.map(item => 
      item.id === id ? { ...item, quantity: newQuantity } : item
    ));
  };

  const total = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold text-wine-primary mb-8 flex items-center">
        <FaShoppingCart className="mr-4" /> Your Cart
      </h1>

      {cartItems.length === 0 ? (
        <p className="text-center text-gray-600">Your cart is empty</p>
      ) : (
        <>
          {cartItems.map(item => (
            <CartItem 
              key={item.id} 
              item={item} 
              onRemove={removeFromCart}
              onUpdateQuantity={updateQuantity}
            />
          ))}

          <div className="mt-8 text-right">
            <h3 className="text-2xl font-bold">
              Total: ${total.toFixed(2)}
            </h3>
            <button className="mt-4 bg-wine-primary text-white px-8 py-3 rounded">
              Proceed to Checkout
            </button>
          </div>
        </>
      )}
    </div>
  );
};

const CartItem = ({ item, onRemove, onUpdateQuantity }) => {
  return (
    <div className="flex items-center border-b py-4">
      <div className="flex-grow">
        <h3 className="text-xl font-semibold">{item.name}</h3>
        <p className="text-gray-600">${item.price}</p>
      </div>
      
      <div className="flex items-center mr-4">
        <button 
          onClick={() => onUpdateQuantity(item.id, Math.max(1, item.quantity - 1))}
          className="px-2 bg-gray-200"
        >
          -
        </button>
        <span className="mx-2">{item.quantity}</span>
        <button 
          onClick={() => onUpdateQuantity(item.id, item.quantity + 1)}
          className="px-2 bg-gray-200"
        >
          +
        </button>
      </div>

      <button 
        onClick={() => onRemove(item.id)}
        className="text-red-500"
      >
        <FaTrash />
      </button>
    </div>
  );
};

export default Cart;