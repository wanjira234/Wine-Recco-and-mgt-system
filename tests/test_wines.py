import pytest
from flask import json

def test_get_wine_catalog(test_app, test_wines):
    """Test retrieving wine catalog"""
    response = test_app.get('/wines/catalog')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['wines']) == len(test_wines)

def test_get_wine_details(test_app, test_wines):
    """Test retrieving specific wine details"""
    wine = test_wines[0]
    response = test_app.get(f'/wines/{wine.id}')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == wine.name
    assert data['id'] == wine.id

def test_search_wines(test_app, test_wines):
    """Test wine search functionality"""
    response = test_app.get('/wines/search?query=Test')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['wines']) > 0

def test_filter_wines(test_app, test_wines):
    """Test filtering wines by variety"""
    response = test_app.get('/wines/filter?variety=Test Variety')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert all(wine['variety'] == 'Test Variety' for wine in data['wines'])