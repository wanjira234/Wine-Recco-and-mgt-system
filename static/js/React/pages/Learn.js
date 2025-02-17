import React, { useState } from 'react';
import { FaBook, FaGlassWineGlass, FaGlobeEurope } from 'react-icons/fa';

const learnTopics = [
  {
    id: 1,
    title: 'Wine Tasting 101',
    description: 'Learn the basics of wine tasting, including how to observe, smell, and taste wine like a pro.',
    icon: <FaGlassWineGlass />,
    content: '...'
  },
  {
    id: 2,
    title: 'Wine Regions of the World',
    description: 'Explore the most famous wine-producing regions and their unique characteristics.',
    icon: <FaGlobeEurope />,
    content: '...'
  },
  {
    id: 3,
    title: 'Wine and Food Pairing',
    description: 'Discover the art of matching wines with different cuisines and dishes.',
    icon: <FaBook />,
    content: '...'
  }
];

const Learn = () => {
  const [selectedTopic, setSelectedTopic] = useState(null);

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold text-wine-primary mb-8">Wine Education</h1>
      
      <div className="grid md:grid-cols-3 gap-6">
        {learnTopics.map(topic => (
          <div 
            key={topic.id} 
            className="border rounded-lg p-6 hover:shadow-lg transition cursor-pointer"
            onClick={() => setSelectedTopic(topic)}
          >
            <div className="text-5xl text-wine-primary mb-4">
              {topic.icon}
            </div>
            <h3 className="text-2xl font-semibold mb-2">{topic.title}</h3>
            <p className="text-gray-600">{topic.description}</p>
          </div>
        ))}
      </div>

      {selectedTopic && (
        <TopicModal 
          topic={selectedTopic} 
          onClose={() => setSelectedTopic(null)} 
        />
      )}
    </div>
  );
};

const TopicModal = ({ topic, onClose }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg max-w-2xl">
        <h2 className="text-3xl font-bold mb-4">{topic.title}</h2>
        <p>{topic.content}</p>
        <button 
          onClick={onClose}
          className="mt-4 bg-wine-primary text-white px-4 py-2 rounded"
        >
          Close
        </button>
      </div>
    </div>
  );
};

export default Learn;