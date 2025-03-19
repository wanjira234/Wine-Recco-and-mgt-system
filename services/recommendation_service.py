import logging
import numpy as np
import pandas as pd
from typing import List, Optional, Dict, Any

from flask import current_app
from sqlalchemy import func

from extensions import db
from models import (
    Wine, 
    WineReview, 
    User, 
    UserWineInteraction, 
    WineVarietal, 
    WineRegion
)

class RecommendationEngine:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(RecommendationEngine, cls).__new__(cls)
            cls._instance.logger = logging.getLogger(__name__)
            cls._instance.wine_df = None
            cls._instance.interaction_matrix = None
            cls._instance.initialized = False
        return cls._instance

    def initialize(self):
        """
        Initialize recommendation engine
        """
        try:
            with current_app.app_context():
                self._load_wine_data()
                self._create_interaction_matrix()
                self.initialized = True
                self.logger.info("Recommendation engine initialized successfully")
        except Exception as e:
            self.logger.error(f"Recommendation engine initialization failed: {e}")
            self.initialized = False
        return self

    def _load_wine_data(self):
        """
        Load comprehensive wine data
        """
        wines = Wine.query.all()
        
        self.wine_df = pd.DataFrame([
            {
                'id': wine.id,
                'name': wine.name,
                'type': wine.type,
                'varietal': wine.varietal.name if wine.varietal else 'Unknown',
                'region': wine.region.name if wine.region else 'Unknown',
                'description': wine.description or '',
                'price': wine.price,
                'alcohol_percentage': wine.alcohol_percentage,
                'avg_rating': self._calculate_average_rating(wine),
                'total_reviews': WineReview.query.filter_by(wine_id=wine.id).count()
            } for wine in wines
        ])

    def _calculate_average_rating(self, wine):
        """
        Calculate average rating for a wine
        """
        avg_rating = db.session.query(func.avg(WineReview.rating))\
            .filter(WineReview.wine_id == wine.id)\
            .scalar() or 0
        return round(avg_rating, 2)

    def _create_interaction_matrix(self):
        """
        Create user-wine interaction matrix
        """
        interactions = UserWineInteraction.query.all()
        
        # Create interaction matrix
        user_ids = sorted(set(interaction.user_id for interaction in interactions))
        wine_ids = sorted(set(interaction.wine_id for interaction in interactions))
        
        interaction_matrix = np.zeros((len(user_ids), len(wine_ids)))
        
        user_id_to_index = {user_id: idx for idx, user_id in enumerate(user_ids)}
        wine_id_to_index = {wine_id: idx for idx, wine_id in enumerate(wine_ids)}
        
        for interaction in interactions:
            user_idx = user_id_to_index[interaction.user_id]
            wine_idx = wine_id_to_index[interaction.wine_id]
            interaction_matrix[user_idx, wine_idx] = interaction.interaction_weight

        self.interaction_matrix = interaction_matrix
        self.user_ids = user_ids
        self.wine_ids = wine_ids

    def get_personalized_recommendations(
        self, 
        user_id: int, 
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized wine recommendations
        """
        try:
            # Content-based filtering
            user_interactions = UserWineInteraction.query\
                .filter_by(user_id=user_id)\
                .order_by(UserWineInteraction.interaction_weight.desc())\
                .limit(5)\
                .all()
            
            if not user_interactions:
                return self.get_popular_wines(top_n)
            
            # Get liked wine IDs
            liked_wine_ids = [interaction.wine_id for interaction in user_interactions]
            
            # Fetch similar wines based on interactions
            recommended_wines = self._find_similar_wines(liked_wine_ids, top_n)
            
            return recommended_wines
        
        except Exception as e:
            self.logger.error(f"Personalized recommendation error: {e}")
            return self.get_popular_wines(top_n)

    def _find_similar_wines(self, wine_ids: List[int], top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Find similar wines based on multiple wine IDs
        """
        try:
            # Filter wines similar to liked wines
            base_wines = Wine.query.filter(Wine.id.in_(wine_ids)).all()
            
            # Criteria for similarity
            similar_wines = Wine.query.filter(
                (Wine.type.in_([wine.type for wine in base_wines])) |
                (Wine.varietal_id.in_([wine.varietal_id for wine in base_wines])) |
                (Wine.region_id.in_([wine.region_id for wine in base_wines]))
            ).filter(~Wine.id.in_(wine_ids))\
             .order_by(func.random())\
             .limit(top_n)\
             .all()
            
            return [
                {
                    'id': wine.id,
                    'name': wine.name,
                    'type': wine.type,
                    'varietal': wine.varietal.name if wine.varietal else 'Unknown',
                    'region': wine.region.name if wine.region else 'Unknown',
                    'price': wine.price,
                    'avg_rating': self._calculate_average_rating(wine)
                } for wine in similar_wines
            ]
        
        except Exception as e:
            self.logger.error(f"Similar wine search error: {e}")
            return []

    def get_popular_wines(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Get most popular wines based on ratings and interactions
        """
        try:
            popular_wines = Wine.query\
                .join(WineReview, Wine.id == WineReview.wine_id, isouter=True)\
                .group_by(Wine.id)\
                .order_by(
                    func.avg(WineReview.rating).desc(), 
                    func.count(WineReview.id).desc()
                )\
                .limit(top_n)\
                .all()
            
            return [
                {
                    'id': wine.id,
                    'name': wine.name,
                    'type': wine.type,
                    'varietal': wine.varietal.name if wine.varietal else 'Unknown',
                    'region': wine.region.name if wine.region else 'Unknown',
                    'price': wine.price,
                    'avg_rating': self._calculate_average_rating(wine)
                } for wine in popular_wines
            ]
        
        except Exception as e:
            self.logger.error(f"Popular wines retrieval error: {e}")
            return []

def create_recommendation_engine():
    """
    Create and initialize recommendation engine
    """
    return RecommendationEngine().initialize()

# Global instance
recommendation_engine = create_recommendation_engine()