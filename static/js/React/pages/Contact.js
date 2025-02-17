import React, { useState } from 'react';
import { FaEnvelope, FaMapMarkerAlt, FaPhoneAlt } from 'react-icons/fa';

const Contact = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Implement form submission logic
    console.log('Form submitted:', formData);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold text-wine-primary mb-8">Contact Us</h1>
      
      <div className="grid md:grid-cols-2 gap-8">
        <div>
          <h2 className="text-2xl font-semibold mb-4">Get in Touch</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <input 
              type="text"
              name="name"
              placeholder="Your Name"
              value={formData.name}
              onChange={handleChange}
              className="w-full border rounded px-4 py-2"
              required
            />
            <input 
              type="email"
              name="email"
              placeholder="Your Email"
              value={formData.email}
              onChange={handleChange}
              className="w-full border rounded px-4 py-2"
              required
            />
            <textarea 
              name="message"
              placeholder="Your Message"
              value={formData.message}
              onChange={handleChange}
              className="w-full border rounded px-4 py-2 h-32"
              required
            />
            <button 
              type="submit"
              className="bg-wine-primary text-white px-6 py-2 rounded hover:bg-wine-secondary"
            >
              Send Message
            </button>
          </form>
        </div>
        
        <div>
          <h2 className="text-2xl font-semibold mb-4">Contact Information</h2>
          <div className="space-y-4">
            <ContactInfo 
              icon={<FaMapMarkerAlt />}
              title="Address"
              description="123 Wine Street, Vineyard District, CA 90210"
            />
            <ContactInfo 
              icon={<FaPhoneAlt />}
              title="Phone"
              description="+1 (555) 123-4567"
            />
            <ContactInfo 
              icon={<FaEnvelope />}
              title="Email"
              description="support@winerecommender.com"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

const ContactInfo = ({ icon, title, description }) => (
  <div className="flex items-center">
    <div className="text-2xl text-wine-primary mr-4">{icon}</div>
    <div>
      <h3 className="font-semibold">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  </div>
);

export default Contact;