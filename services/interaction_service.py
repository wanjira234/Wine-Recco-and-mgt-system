# services/interaction_service.py
from models import UserInteraction, Wine
from extensions import db
from sqlalchemy import func

class UserInteractionService:
    @classmethod
    def log_wine_view(cls, user_id, wine_id):
        """
        Log when a user views a wine
        """
        interaction = UserInteraction(
            user_id=user_id,
            wine_id=wine_id,
            interaction_type='view'
        )
        db.session.add(interaction)
        db.session.commit()
        return interaction

    @classmethod
    def log_wine_favorite(cls, user_id, wine_id):
        """
        Log when a user favorites a wine
        """
        # Check if already favorited
        existing = UserInteraction.query.filter_by(
            user_id=user_id, 
            wine_id=wine_id, 
            interaction_type='favorite'
        ).first()

        if existing:
            return existing

        interaction = UserInteraction(
            user_id=user_id,
            wine_id=wine_id,
            interaction_type='favorite'
        )
        db.session.add(interaction)
        db.session.commit()
        return interaction

    @classmethod
    def get_user_favorite_wines(cls, user_id):
        """
        Retrieve user's favorite wines
        """
        favorites = UserInteraction.query.filter_by(
            user_id=user_id, 
            interaction_type='favorite'
        ).all()

        # Get full wine details
        wine_ids = [fav.wine_id for fav in favorites]
        wines = Wine.query.filter(Wine.id.in_(wine_ids)).all()
        
        return wines

    @classmethod
    def get_most_viewed_wines(cls, limit=10):
        """
        Get most viewed wines
        """
        most_viewed = db.session.query(
            UserInteraction.wine_id, 
            func.count(UserInteraction.id).label('view_count')
        ).filter_by(
            interaction_type='view'
        ).group_by(
            UserInteraction.wine_id
        ).order_by(
            func.count(UserInteraction.id).desc()
        ).limit(limit).all()

        wine_ids = [wine_id for wine_id, _ in most_viewed]
        wines = Wine.query.filter(Wine.id.in_(wine_ids)).all()
        
        return wines