import numpy as np
from typing import List, Dict

class RecommendationHelper:
    @staticmethod
    def calculate_similarity_score(wine1: Dict, wine2: Dict):
        """
        Calculate similarity between two wines
        """
        features = ['type', 'region', 'price', 'alcohol_percentage']
        
        # Normalize features
        def normalize(value):
            return (value - np.mean(value)) / np.std(value)
        
        similarity_score = 0
        for feature in features:
            if feature in wine1 and feature in wine2:
                similarity_score += 1 - abs(
                    normalize(wine1[feature]) - normalize(wine2[feature])
                )
        
        return similarity_score / len(features)

    @staticmethod
    def filter_recommendations(
        recommendations: List[Dict], 
        max_recommendations: int = 10,
        min_rating: float = 3.5
    ):
        """
        Filter and refine recommendations
        """
        filtered_recommendations = [
            wine for wine in recommendations 
            if wine.get('rating', 0) >= min_rating
        ]
        
        return filtered_recommendations[:max_recommendations]