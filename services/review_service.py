# services/review_service.py
from models import WineReview, Wine
from extensions import db
from sqlalchemy import func

class WineReviewService:
    @classmethod
    def create_review(cls, user_id, wine_id, rating, comment=None):
        """
        Create a wine review
        """
        # Check if review already exists
        existing_review = WineReview.query.filter_by(
            user_id=user_id, 
            wine_id=wine_id
        ).first()

        if existing_review:
            existing_review.rating = rating
            existing_review.comment = comment
        else:
            review = WineReview(
                user_id=user_id,
                wine_id=wine_id,
                rating=rating,
                comment=comment
            )
            db.session.add(review)
        
        db.session.commit()
        return review

    @classmethod
    def get_wine_reviews(cls, wine_id):
        """
        Get reviews for a specific wine
        """
        reviews = WineReview.query.filter_by(wine_id=wine_id).all()
        return reviews

    @classmethod
    def get_user_reviews(cls, user_id):
        """
        Get reviews by a specific user
        """
        reviews = WineReview.query.filter_by(user_id=user_id).all()
        return reviews

    @classmethod
    def calculate_wine_rating(cls, wine_id):
        """
        Calculate average rating for a wine
        """
        rating_data = db.session.query(
            func.avg(WineReview.rating).label('avg_rating'),
            func.count(WineReview.id).label('review_count')
        ).filter_by(wine_id=wine_id).first()

        return {
            'average_rating': rating_data.avg_rating or 0,
            'review_count': rating_data.review_count or 0
        }