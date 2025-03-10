export const getRecommendations = async (userId) => {
    const response = await axios.get(`/api/recommendations/${userId}`); // Adjust the endpoint as necessary
    return response.data;
};