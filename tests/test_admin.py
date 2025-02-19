import pytest
from flask import json

def test_admin_create_wine(test_app, test_user):
    """Test admin wine creation"""
    # Simulate admin login
    login_response = test_app.post('/auth/login', json={
        'email': 'admin@example.com',
        'password': 'adminpassword'
    })
    token = json.loads(login_response.data)['access_token']

    # Create new wine
    new_wine_data = {
        'name': 'New Admin Wine',
        'variety': 'Admin Variety',
        'price': 39.99,
        'rating': 4.7
    }

    response = test_app.post('/admin/wines/create', 
        json=new_wine_data,
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['name'] == 'New Admin Wine'

def test_admin_update_wine(test_app, test_wines):
    """Test admin wine update"""
    # Simulate admin login
    login_response = test_app.post('/auth/login', json={
        'email': 'admin@example.com',
        'password': 'adminpassword'
    })
    token = json.loads(login_response.data)['access_token']

    # Update existing wine
    wine = test_wines[0]
    update_data = {
        'price': 49.99,
        'rating': 4.9
    }

    response = test_app.put(f'/admin/wines/{wine.id}', 
        json=update_data,
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['price'] == 49.99
    assert data['rating'] == 4.9

def test_admin_delete_wine(test_app, test_wines):
    """Test admin wine deletion"""
    # Simulate admin login
    login_response = test_app.post('/auth/login', json={
        'email': 'admin@example.com',
        'password': 'adminpassword'
    })
    token = json.loads(login_response.data)['access_token']

    # Delete wine
    wine = test_wines[0]
    response = test_app.delete(f'/admin/wines/{wine.id}', 
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200
    assert json.loads(response.data)['message'] == 'Wine deleted successfully'