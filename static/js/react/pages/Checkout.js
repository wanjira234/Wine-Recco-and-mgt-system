import React, { useState } from 'react';

const Checkout = () => {
    const [name, setName] = useState('');
    const [address, setAddress] = useState('');
    const [city, setCity] = useState('');
    const [zip, setZip] = useState('');
    const [error, setError] = useState('');
    const [cart, setCart] = useState([
        { id: 1, name: 'Chardonnay', price: 20, quantity: 1 },
        { id: 2, name: 'Merlot', price: 25, quantity: 2 },
        // Add more items as needed
    ]);

    const handleSubmit = (e) => {
        e.preventDefault();
        setError('');

        // Validate inputs
        if (!name || !address || !city || !zip) {
            setError('Please fill in all fields.');
            return;
        }

        // Process checkout (You should implement the actual checkout logic here)
        console.log('Checkout successful:', { name, address, city, zip, cart });
        // Redirect to a thank you page or order confirmation page
    };

    return (
        <div className="container mx-auto px-4 py-16">
            <h1 className="text-4xl font-bold mb-4">Checkout</h1>
            {error && <div className="text-red-600 mb-4">{error}</div>}
            <form onSubmit={handleSubmit}>
                <div className="mb-4">
                    <label className="block text-lg">Name</label>
                    <input
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        className="border rounded p-2 w-full"
                        required
                    />
                </div>
                <div className="mb-4">
                    <label className="block text-lg">Address</label>
                    <input
                        type="text"
                        value={address}
                        onChange={(e) => setAddress(e.target.value)}
                        className="border rounded p-2 w-full"
                        required
                    />
                </div>
                <div className="mb-4">
                    <label className="block text-lg">City</label>
                    <input
                        type="text"
                        value={city}
                        onChange={(e) => setCity(e.target.value)}
                        className="border rounded p-2 w-full"
                        required
                    />
                </div>
                <div className="mb-4">
                    <label className="block text-lg">ZIP Code</label>
                    <input
                        type="text"
                        value={zip}
                        onChange={(e) => setZip(e.target.value)}
                        className="border rounded p-2 w-full"
                        required
                    />
                </div>
                <h2 className="text-2xl font-bold mt-8 mb-4">Your Cart</h2>
                <div className="mb-4">
                    {cart.map(item => (
                        <div key={item.id} className="flex justify-between mb-2">
                            <span>{item.name} (x{item.quantity})</span>
                            <span>${item.price * item.quantity}</span>
                        </div>
                    ))}
                </div>
                <button type="submit" className="bg-wine-primary text-white px-4 py-2 rounded">
                    Complete Purchase
                </button>
            </form>
        </div>
    );
};

export default Checkout;