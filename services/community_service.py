# services/community_service.py
from extensions import db
from models import (
    CommunityPost, 
    CommunityComment, 
    UserConnection, 
    User, 
    WineReview, 
    Wine
)
from sqlalchemy import func, or_
from datetime import datetime, timedelta

class CommunityService:
    @classmethod
    def create_post(cls, user_id, content, wine_id=None, image_url=None):
        """
        Create a new community post
        """
        post = CommunityPost(
            user_id=user_id,
            content=content,
            wine_id=wine_id,
            image_url=image_url,
            created_at=datetime.utcnow()
        )
        db.session.add(post)
        db.session.commit()
        return post

    @classmethod
    def add_comment(cls, user_id, post_id, content):
        """
        Add a comment to a post
        """
        comment = CommunityComment(
            user_id=user_id,
            post_id=post_id,
            content=content,
            created_at=datetime.utcnow()
        )
        db.session.add(comment)
        db.session.commit()
        return comment

    @classmethod
    def get_community_feed(cls, user_id, page=1, per_page=20):
        """
        Get community feed with advanced filtering
        """
        # Get user's connections
        connections = UserConnection.query.filter_by(
            user_id=user_id, 
            status='accepted'
        ).all()
        
        connection_ids = [
            conn.connected_user_id for conn in connections
        ] + [user_id]

        # Fetch posts
        posts = CommunityPost.query.filter(
            or_(
                CommunityPost.user_id.in_(connection_ids),
                CommunityPost.is_public == True
            )
        ).order_by(
            CommunityPost.created_at.desc()
        ).paginate(page=page, per_page=per_page)

        return {
            'posts': [
                {
                    'id': post.id,
                    'user_id': post.user_id,
                    'username': post.user.username,
                    'content': post.content,
                    'wine_id': post.wine_id,
                    'wine_name': post.wine.name if post.wine else None,
                    'image_url': post.image_url,
                    'created_at': post.created_at,
                    'likes_count': post.likes_count,
                    'comments_count': post.comments.count(),
                    'comments': [
                        {
                            'id': comment.id,
                            'user_id': comment.user_id,
                            'username': comment.user.username,
                            'content': comment.content,
                            'created_at': comment.created_at
                        } for comment in post.comments.limit(3)
                    ]
                } for post in posts.items
            ],
            'pagination': {
                'total_pages': posts.pages,
                'current_page': posts.page,
                'total_items': posts.total
            }
        }

    @classmethod
    def connect_users(cls, user_id, target_user_id):
        """
        Send or accept a connection request
        """
        # Check if connection already exists
        existing_connection = UserConnection.query.filter(
            or_(
                (UserConnection.user_id == user_id) & 
                (UserConnection.connected_user_id == target_user_id),
                (UserConnection.user_id == target_user_id) & 
                (UserConnection.connected_user_id == user_id)
            )
        ).first()

        if existing_connection:
            if existing_connection.status == 'pending':
                existing_connection.status = 'accepted'
                db.session.commit()
                return existing_connection
            return existing_connection

        # Create new connection request
        connection = UserConnection(
            user_id=user_id,
            connected_user_id=target_user_id,
            status='pending'
        )
        db.session.add(connection)
        db.session.commit()
        return connection

    @classmethod
    def get_user_connections(cls, user_id, status='accepted'):
        """
        Get user's connections
        """
        connections = UserConnection.query.filter(
            or_(
                (UserConnection.user_id == user_id),
                (UserConnection.connected_user_id == user_id)
            ),
            UserConnection.status == status
        ).all()

        connected_users = []
        for conn in connections:
            if conn.user_id == user_id:
                user = conn.connected_user
            else:
                user = conn.user

            # Get user's wine expertise
            wine_reviews = WineReview.query.filter_by(user_id=user.id).count()
            favorite_wines = Wine.query.join(WineReview).filter(
                WineReview.user_id == user.id
            ).count()

            connected_users.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'wine_expertise': {
                    'reviews_count': wine_reviews,
                    'favorite_wines_count': favorite_wines
                }
            })

        return connected_users

    @classmethod
    def get_wine_social_insights(cls, wine_id):
        """
        Get social insights for a specific wine
        """
        # Recent reviews
        recent_reviews = WineReview.query.filter_by(
            wine_id=wine_id
        ).order_by(
            WineReview.created_at.desc()
        ).limit(10).all()

        # Community posts
        community_posts = CommunityPost.query.filter_by(
            wine_id=wine_id
        ).order_by(
            CommunityPost.created_at.desc()
        ).limit(10).all()

        # Aggregate review data
        review_insights = db.session.query(
            func.avg(WineReview.rating).label('avg_rating'),
            func.count(WineReview.id).label('review_count')
        ).filter_by(wine_id=wine_id).first()

        return {
            'recent_reviews': [
                {
                    'user_id': review.user_id,
                    'username': review.user.username,
                    'rating': review.rating,
                    'comment': review.comment,
                    'created_at': review.created_at
                } for review in recent_reviews
            ],
            'community_posts': [
                {
                    'user_id': post.user_id,
                    'username': post.user.username,
                    'content': post.content,
                    'created_at': post.created_at
                } for post in community_posts
            ],
            'review_insights': {
                'average_rating': float(review_insights.avg_rating or 0),
                'review_count': review_insights.review_count
            }
        }