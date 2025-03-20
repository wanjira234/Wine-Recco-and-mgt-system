import logging
import numpy as np
import pandas as pd
from typing import List, Optional, Dict, Any

from flask import current_app
from sqlalchemy import func, case

from extensions import db
from models import (
    Wine, 
    WineReview, 
    User, 
    UserWineInteraction, 
    WineVarietal, 
    WineRegion,
    WineTrait
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

    def get_personalized_recommendations(self, user_id, limit=10):
        """
        Get personalized wine recommendations for a user based on their preferences and interactions
        """
        user = User.query.get(user_id)
        if not user:
            return []
        
        # Get user's preferred traits
        user_traits = set(user.preferred_traits)
        
        # Base query for wines
        query = Wine.query
        
        if user_traits:
            # Join with wine traits and count matches with user preferences
            query = query.outerjoin(wine_traits)\
                .outerjoin(WineTrait)\
                .group_by(Wine.id)\
                .order_by(
                    func.count(case([(WineTrait.id.in_([t.id for t in user_traits]), 1)], else_=0)).desc()
                )
        
        # Get wines the user has already interacted with
        interacted_wines = db.session.query(UserWineInteraction.wine_id)\
            .filter_by(user_id=user_id).all()
        interacted_wine_ids = [w[0] for w in interacted_wines]
        
        # Exclude wines the user has already interacted with
        if interacted_wine_ids:
            query = query.filter(~Wine.id.in_(interacted_wine_ids))
        
        return query.limit(limit).all()

    def get_similar_user_recommendations(self, user_id, limit=6):
        """
        Get recommendations based on similar users' preferences
        """
        user = User.query.get(user_id)
        if not user:
            return []
        
        # Get users with similar trait preferences
        similar_users = User.query\
            .join(user_traits)\
            .filter(User.id != user_id)\
            .filter(WineTrait.id.in_([t.id for t in user.preferred_traits]))\
            .group_by(User.id)\
            .order_by(func.count(WineTrait.id).desc())\
            .limit(5)\
            .all()
        
        # Get wines that similar users have interacted with positively
        similar_user_ids = [u.id for u in similar_users]
        recommended_wines = Wine.query\
            .join(UserWineInteraction)\
            .filter(
                UserWineInteraction.user_id.in_(similar_user_ids),
                UserWineInteraction.interaction_weight > 0
            )\
            .group_by(Wine.id)\
            .order_by(func.avg(UserWineInteraction.interaction_weight).desc())\
            .limit(limit)\
            .all()
        
        return recommended_wines

def create_recommendation_engine():
    """
    Create and initialize recommendation engine
    """
    engine = RecommendationEngine()
    try:
        engine.initialize()
    except Exception as e:
        logging.error(f"Failed to initialize recommendation engine: {e}")
        # Don't raise the exception, just return the uninitialized engine
    return engine

# Global instance
recommendation_engine = None

def get_recommendation_engine():
    """
    Get or create recommendation engine instance
    """
    global recommendation_engine
    if recommendation_engine is None:
        recommendation_engine = create_recommendation_engine()
    return recommendation_engine