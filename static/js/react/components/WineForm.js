import React, { useState, useEffect } from 'react';

const WineForm = ({ wine, onSubmit }) => {
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [image, setImage] = useState('');

    useEffect(() => {
        if (wine) {
            setName(wine.name);
            setDescription(wine.description);
            setImage(wine.image);
        } else {
            setName('');
            setDescription('');
            setImage('');
        }
    }, [wine]);

    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit({ name, description, image });
    };

    return (
        <form onSubmit={handleSubmit} className="mb-8">
            <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Wine Name"
                className="border p-2 w-full mb-2"
                required
            />
            <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Description"
                className="border p-2 w-full mb-2"
                required
            />
            <input
                type="text"
                value={image}
                onChange={(e) => setImage(e.target.value)}
                placeholder="Image URL"
                className="border p-2 w-full mb-2"
            />
            <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded">
                {wine ? 'Update Wine' : 'Add Wine'}
            </button>
        </form>
    );
};

export default WineForm;