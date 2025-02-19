import pytest
from services.recommendation_service import RecommendationEngine

def test_recommendation_engine(test_wines):
    """Test recommendation engine functionality"""
    recommendation_engine = RecommendationEngine()
    
    # Test basic recommendation generation
    recommendations = recommendation_engine.get_recommendations(test_wines[0].id)
    
    assert len(recommendations) > 0
    assert all(wine.id != test_wines[0].id for wine in recommendations)

def test_collaborative_filtering(test_wines, test_user):
    """Test collaborative filtering recommendations"""
    recommendation_engine = RecommendationEngine()
    
    # Simulate user interactions
    user_interactions = {
        'user_id': test_user.id,
        'liked_wines': [wine.id for wine in test_wines[:3]]
    }
    
    recommendations = recommendation_engine.collaborative_filter(user_interactions)
    
    assert len(recommendations) > 0