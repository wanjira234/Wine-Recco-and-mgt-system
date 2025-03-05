# services/content_service.py
from extensions import db
from models import (
    WineKnowledgeContent, 
    WineContentCategory, 
    UserContentInteraction,
    ContentType
)
from sqlalchemy import func

class ContentService:
    @classmethod
    def create_content(cls, content_data):
        """
        Create new wine knowledge content
        """
        # Prepare content
        content = WineKnowledgeContent(
            title=content_data['title'],
            slug=cls._generate_slug(content_data['title']),
            content_type=ContentType(content_data.get('content_type', 'ARTICLE')),
            summary=content_data.get('summary'),
            main_content=content_data['main_content'],
            author_id=content_data.get('author_id'),
            tags=content_data.get('tags', []),
            cover_image_url=content_data.get('cover_image_url'),
            additional_media=content_data.get('additional_media'),
            interactive_data=content_data.get('interactive_data')
        )
        
        # Handle categories
        if content_data.get('categories'):
            categories = WineContentCategory.query.filter(
                WineContentCategory.name.in_(content_data['categories'])
            ).all()
            content.categories.extend(categories)
        
        db.session.add(content)
        db.session.commit()
        
        return content

    @classmethod
    def _generate_slug(cls, title):
        """
        Generate a unique slug for content
        """
        base_slug = title.lower().replace(' ', '-')
        unique_slug = base_slug
        counter = 1
        
        while WineKnowledgeContent.query.filter_by(slug=unique_slug).first():
            unique_slug = f"{base_slug}-{counter}"
            counter += 1
        
        return unique_slug

    @classmethod
    def get_content_list(cls, filters=None):
        """
        Retrieve content with advanced filtering
        """
        query = WineKnowledgeContent.query
        
        # Apply filters
        if filters:
            if filters.get('content_type'):
                query = query.filter(
                    WineKnowledgeContent.content_type == ContentType(filters['content_type'])
                )
            
            if filters.get('categories'):
                query = query.join(WineKnowledgeContent.categories).filter(
                    WineContentCategory.name.in_(filters['categories'])
                )
            
            if filters.get('tags'):
                query = query.filter(
                    WineKnowledgeContent.tags.contains(filters['tags'])
                )
        
        # Order by most recent
        query = query.order_by(WineKnowledgeContent.created_at.desc())
        
        return query.all()

    @classmethod
    def get_content_details(cls, content_id, user_id=None):
        """
        Get detailed content with user interaction
        """
        content = WineKnowledgeContent.query.get(content_id)
        
        if not content:
            raise ValueError("Content not found")
        
        # Increment view count
        content.views_count += 1
        
        # Track user interaction
        if user_id:
            interaction = UserContentInteraction.query.filter_by(
                user_id=user_id, 
                content_id=content_id
            ).first()
            
            if not interaction:
                interaction = UserContentInteraction(
                    user_id=user_id,
                    content_id=content_id,
                    viewed=True
                )
                db.session.add(interaction)
        
        db.session.commit()
        
        return {
            'id': content.id,
            'title': content.title,
            'slug': content.slug,
            'content_type': content.content_type.value,
            'summary': content.summary,
            'main_content': content.main_content,
            'cover_image_url': content.cover_image_url,
            'additional_media': content.additional_media,
            'interactive_data': content.interactive_data,
            'views_count': content.views_count,
            'likes_count': content.likes_count,
            'categories': [cat.name for cat in content.categories],
            'tags': content.tags
        }

    @classmethod
    def create_content_categories(cls):
        """
        Initialize default content categories
        """
        categories = [
            'Wine Basics',
            'Wine Regions',
            'Wine Tasting',
            'Wine Pairing',
            'Viticulture',
            'Wine History',
            'Sommelier Insights'
        ]
        
        existing_categories = WineContentCategory.query.all()
        existing_names = {cat.name for cat in existing_categories}
        
        for category_name in categories:
            if category_name not in existing_names:
                category = WineContentCategory(
                    name=category_name,
                    description=f"Explore {category_name.lower()} in depth"
                )
                db.session.add(category)
        
        db.session.commit()

    @classmethod
    def like_content(cls, content_id, user_id):
        """
        Like a piece of content
        """
        content = WineKnowledgeContent.query.get(content_id)
        
        if not content:
            raise ValueError("Content not found")
        
        # Update like count
        content.likes_count += 1
        
        # Track user interaction
        interaction = UserContentInteraction.query.filter_by(
            user_id=user_id, 
            content_id=content_id
        ).first()
        
        if not interaction:
            interaction = UserContentInteraction(
                user_id=user_id,
                content_id=content_id,
                liked=True
            )
            db.session.add(interaction)
        else:
            interaction.liked = True
        
        db.session.commit()
        
        return content.likes_count