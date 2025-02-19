import pytest
from flask import json

def test_user_registration(test_app):
    """Test user registration endpoint"""
    registration_data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'securepassword123'
    }
    
    response = test_app.post('/auth/register', 
        data=json.dumps(registration_data),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    assert 'user_id' in json.loads(response.data)

def test_user_login(test_app, test_user):
    """Test user login functionality"""
    login_data = {
        'email': test_user.email,
        'password': 'testpassword123'
    }
    
    response = test_app.post('/auth/login', 
        data=json.dumps(login_data),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    assert 'access_token' in json.loads(response.data)