import numpy as np
from typing import List, Dict, Any
import scipy.spatial.distance as distance

class RecommendationHelper:
    """
    Recommendation and Similarity Calculation Utilities
    """
    
    @staticmethod
    def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors
        
        :param vec1: First vector
        :param vec2: Second vector
        :return: Cosine similarity score
        """
        return 1 - distance.cosine(vec1, vec2)

    @staticmethod
    def pearson_correlation(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate Pearson correlation between two vectors
        
        :param vec1: First vector
        :param vec2: Second vector
        :return: Pearson correlation coefficient
        """
        return np.corrcoef(vec1, vec2)[0, 1]

    @staticmethod
    def jaccard_similarity(set1: set, set2: set) -> float:
        """
        Calculate Jaccard similarity between two sets
        
        :param set1: First set
        :param set2: Second set
        :return: Jaccard similarity score
        """
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union != 0 else 0

    @staticmethod
    def normalize_vector(vector: np.ndarray) -> np.ndarray:
        """
        Normalize a vector to unit length
        
        :param vector: Input vector
        :return: Normalized vector
        """
        return vector / np.linalg.norm(vector)

    @staticmethod
    def calculate_weighted_score(
        items: List[Dict[str, Any]], 
        weights: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """
        Calculate weighted recommendation scores
        
        :param items: List of recommendation items
        :param weights: Scoring weights
        :return: Scored and sorted recommendations
        """
        for item in items:
            score = sum(
                item.get(key, 0) * weight 
                for key, weight in weights.items()
            )
            item['recommendation_score'] = score
        
        return sorted(items, key=lambda x: x['recommendation_score'], reverse=True)