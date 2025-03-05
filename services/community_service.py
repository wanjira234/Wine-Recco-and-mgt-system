# services/community_service.py
from extensions import db
from models import (
    CommunityPost, 
    PostComment, 
    UserConnection, 
    PostType, 
    User
)
from services.notification_service import NotificationService
from sqlalchemy import or_

class CommunityService:
    @classmethod
    def create_post(cls, user_id, post_data):
        """
        Create a new community post
        """
        post = CommunityPost(
            user_id=user_id,
            post_type=PostType(post_data['post_type']),
            content=post_data['content'],
            wine_id=post_data.get('wine_id'),
            event_id=post_data.get('event_id'),
            image_url=post_data.get('image_url')
        )
        
        db.session.add(post)
        db.session.commit()
        
        # Notify followers
        cls.notify_followers(user_id, post)
        
        return post

    @classmethod
    def add_comment(cls, user_id, post_id, content):
        """
        Add a comment to a post
        """
        comment = PostComment(
            post_id=post_id,
            user_id=user_id,
            content=content
        )
        
        db.session.add(comment)
        
        # Update post comment count
        post = CommunityPost.query.get(post_id)
        post.comments_count += 1
        
        db.session.commit()
        
        # Notify post owner
        NotificationService.create_notification(
            user_id=post.user_id,
            notification_type='post_comment',
            content=f"New comment on your post",
            metadata={
                'post_id': post_id,
                'commenter_id': user_id
            }
        )
        
        return comment

    @classmethod
    def like_post(cls, user_id, post_id):
        """
        Like a post
        """
        post = CommunityPost.query.get(post_id)
        
        if not post:
            raise ValueError("Post not found")
        
        post.likes_count += 1
        db.session.commit()
        
        # Notify post owner
        NotificationService.create_notification(
            user_id=post.user_id,
            notification_type='post_like',
            content=f"Someone liked your post",
            metadata={
                'post_id': post_id,
                'liker_id': user_id
            }
        )
        
        return post

    @classmethod
    def send_connection_request(cls, requester_id, receiver_id):
        """
        Send a connection request
        """
        # Check if connection already exists
        existing_connection = UserConnection.query.filter(
            or_(
                (UserConnection.requester_id == requester_id and UserConnection.receiver_id == receiver_id),
                (UserConnection.requester_id == receiver_id and UserConnection.receiver_id == requester_id)
            )
        ).first()
        
        if existing_connection:
            raise ValueError("Connection request already exists")
        
        connection = UserConnection(
            requester_id=requester_id,
            receiver_id=receiver_id,
            status='pending'
        )
        
        db.session.add(connection)
        db.session.commit()
        
        # Notify receiver
        NotificationService.create_notification(
            user_id=receiver_id,
            notification_type='connection_request',
            content=f"New connection request",
            metadata={
                'requester_id': requester_id,
                'connection_id': connection.id
            }
        )
        
        return connection

    @classmethod
    def accept_connection_request(cls, connection_id, receiver_id):
        """
        Accept a connection request
        """
        connection = UserConnection.query.get(connection_id)
        
        if not connection or connection.receiver_id != receiver_id:
            raise ValueError("Invalid connection request")
        
        connection.status = 'accepted'
        db.session.commit()
        
        # Notify requester
        NotificationService.create_notification(
            user_id=connection.requester_id,
            notification_type='connection_accepted',
            content=f"Connection request accepted",
            metadata={
                'receiver_id': receiver_id
            }
        )
        
        return connection

    @classmethod
    def get_community_feed(cls, user_id, page=1, per_page=20):
        """
        Get community feed with pagination
        """
        # Get user's connections
        connections = UserConnection.query.filter(
            or_(
                UserConnection.requester_id == user_id,
                UserConnection.receiver_id == user_id
            ),
            UserConnection.status == 'accepted'
        ).all()
        
        # Get connected user IDs
        connected_user_ids = [
            conn.requester_id if conn.receiver_id == user_id else conn.receiver_id
            for conn in connections
        ]
        
        # Include user's own posts
        connected_user_ids.append(user_id)
        
        # Query posts from connected users
        posts = CommunityPost.query.filter(
            CommunityPost.user_id.in_(connected_user_ids)
        ).order_by(
            CommunityPost.created_at.desc()
        ).paginate(page=page, per_page=per_page)
        
        return {
            'posts': [
                {
                    'id': post.id,
                    'user_id': post.user_id,
                    'post_type': post.post_type.value,
                    'content': post.content,
                    'likes_count': post.likes_count,
                    'comments_count': post.comments_count,
                    'created_at': post.created_at.isoformat(),
                    'user': {
                        'id': post.user.id,
                        'username': post.user.username,
                        'profile_picture': post.user.profile_picture
                    }
                } for post in posts.items
            ],
            'pagination': {
                'total_pages': posts.pages,
                'current_page': posts.page,
                'total_items': posts.total
            }
        }

    @classmethod
    def notify_followers(cls, user_id, post):
        """
        Notify user's followers about a new post
        """
        # Get user's connections
        connections = UserConnection.query.filter(
            or_(
                UserConnection.requester_id == user_id,
                UserConnection.receiver_id == user_id
            ),
            UserConnection.status == 'accepted'
        ).all()
        
        # Get follower IDs
        follower_ids = [
            conn.requester_id if conn.receiver_id == user_id else conn.receiver_id
            for conn in connections
        ]
        
        # Send notifications to followers
        for follower_id in follower_ids:
            NotificationService.create_notification(
                user_id=follower_id,
                notification_type='new_post',
                content=f"New post from a connection",
                metadata={
                    'post_id': post.id,
                    'poster_id': user_id
                }
            )