import axios from 'axios';

export const getUserDetails = async () => {
    const response = await axios.get('/api/user'); // Adjust the endpoint as necessary
    return response.data;
};

export const updateUserDetails = async (userData) => {
    const response = await axios.put('/api/user', userData); // Adjust the endpoint as necessary
    return response.data;
};