import pytest
from app import create_app
from extensions import db
from models import User, Wine, Recommendation

@pytest.fixture(scope='module')
def test_app():
    """Create a Flask test client"""
    app = create_app('testing')
    
    with app.app_context():
        # Setup test database
        db.create_all()
        
        # Create test data
        create_test_data()
        
        yield app.test_client()
        
        # Cleanup after tests
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def test_user():
    """Create a test user for authentication tests"""
    user = User(
        username='testuser',
        email='test@example.com',
        password='testpassword123'
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture(scope='module')
def test_wines():
    """Create sample wines for testing"""
    wines = [
        Wine(
            name=f'Test Wine {i}', 
            variety='Test Variety', 
            price=19.99, 
            rating=4.5
        ) for i in range(5)
    ]
    db.session.add_all(wines)
    db.session.commit()
    return wines

def create_test_data():
    """Populate database with test data"""
    # Add initial test data if needed
    pass