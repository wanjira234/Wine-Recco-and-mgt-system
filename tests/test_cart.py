import pytest
from flask import json

def test_add_to_cart(test_app, test_user, test_wines):
    """Test adding wine to cart"""
    # Simulate user authentication
    login_response = test_app.post('/auth/login', json={
        'email': test_user.email,
        'password': 'testpassword123'
    })
    token = json.loads(login_response.data)['access_token']

    # Add wine to cart
    response = test_app.post('/cart/add', json={
        'wine_id': test_wines[0].id,
        'quantity': 2
    }, headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 200
    assert json.loads(response.data)['message'] == 'Wine added to cart'

def test_remove_from_cart(test_app, test_user, test_wines):
    """Test removing wine from cart"""
    # Simulate user authentication
    login_response = test_app.post('/auth/login', json={
        'email': test_user.email,
        'password': 'testpassword123'
    })
    token = json.loads(login_response.data)['access_token']

    # First add wine to cart
    test_app.post('/cart/add', json={
        'wine_id': test_wines[0].id,
        'quantity': 2
    }, headers={'Authorization': f'Bearer {token}'})

    # Remove wine from cart
    response = test_app.delete(f'/cart/remove/{test_wines[0].id}', 
        headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 200
    assert json.loads(response.data)['message'] == 'Wine removed from cart'

def test_cart_checkout(test_app, test_user, test_wines):
    """Test cart checkout process"""
    # Simulate user authentication
    login_response = test_app.post('/auth/login', json={
        'email': test_user.email,
        'password': 'testpassword123'
    })
    token = json.loads(login_response.data)['access_token']

    # Add wines to cart
    for wine in test_wines[:2]:
        test_app.post('/cart/add', json={
            'wine_id': wine.id,
            'quantity': 1
        }, headers={'Authorization': f'Bearer {token}'})

    # Checkout
    response = test_app.post('/cart/checkout', 
        headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 200
    assert 'order_id' in json.loads(response.data)