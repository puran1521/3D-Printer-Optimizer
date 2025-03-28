import pytest
from flask import Flask
import requests
import numpy as np
from backend.api import app

BASE_URL = "http://localhost:5000/api"

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_api_healthcheck(client):
    """Test if the API is running and responds with status OK."""
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}

def test_api_optimization(client, mocker):
    """Test the optimization API endpoint."""
    # Mock the optimizer
    mock_optimization = mocker.patch(
        "backend.optimizer.TopologyOptimizer.optimize",
        return_value=[[1, 0], [0, 1]]
    )
    
    # Use test client instead of real HTTP request
    response = client.post('/optimize', json={"stl_path": "mock.stl"})
    assert response.status_code == 200
    assert 'result' in response.get_json()
