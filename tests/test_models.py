import pytest
from models import User, Wine, Order, Review
from extensions import db

def test_user_model_creation():
    """Test user model creation and validation"""
    user = User(
        username='testuser',
        email='test@example.com',
        password='securepassword123'
    )
    db.session.add(user)
    db.session.commit()

    assert user.id is not None
    assert user.username == 'testuser'
    assert user.check_password('securepassword123') is True

def test_wine_model_creation(test_wines):
    """Test wine model creation"""
    wine = test_wines[0]
    
    assert wine.id is not None
    assert wine.name.startswith('Test Wine')
    assert wine.price == 19.99
    assert wine.rating == 4.5

def test_order_model():
    """Test order model creation"""
    user = User(
        username='orderuser',
        email='order@example.com',
        password='orderpassword123'
    )
    db.session.add(user)
    
    wine = Wine(
        name='Order Test Wine',
        variety='Test',
        price=24.99,
        rating=4.0
    )
    db.session.add(wine)
    
    order = Order(user_id=user.id)
    order.wines.append(wine)
    
    db.session.add(order)
    db.session.commit()

    assert order.id is not None
    assert len(order.wines) == 1
    assert order.wines[0].name == 'Order Test Wine'

def test_review_model():
    """Test review model creation"""
    user = User(
        username='reviewuser',
        email='review@example.com',
        password='reviewpassword123'
    )
    db.session.add(user)
    
    wine = Wine(
        name='Review Test Wine',
        variety='Test',
        price=29.99,
        rating=4.5
    )
    db.session.add(wine)
    
    review = Review(
        user_id=user.id,
        wine_id=wine.id,
        rating=4,
        comment='Great wine!'
    )
    db.session.add(review)
    db.session.commit()

    assert review.id is not None
    assert review.rating == 4
    assert review.comment == 'Great wine!'