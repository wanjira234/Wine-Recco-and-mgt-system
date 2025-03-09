import axios from 'axios';

export const fetchWines = async () => {
    const response = await axios.get('/api/wines');
    return response.data;
};
export const fetchWineDetails = async (id) => {
    const response = await axios.get(`/api/wines/${id}`);
    return response.data;
};
export const deleteWine = async (id) => {
    await axios.delete(`/api/wines/${id}`); // Adjust the endpoint as necessary
};