import { useState, useEffect } from 'react';
import axios from 'axios';

export const useWineRecommendation = (userTraits) => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchRecommendations = async () => {
      if (!userTraits || userTraits.length === 0) return;

      setLoading(true);
      try {
        const response = await axios.post('/api/recommendations', { traits: userTraits });
        setRecommendations(response.data.wines);
        setError(null);
      } catch (err) {
        setError('Failed to fetch wine recommendations');
        setRecommendations([]);
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, [userTraits]);

  return { recommendations, loading, error };
};