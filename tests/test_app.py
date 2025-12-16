import pytest
from fastapi.testclient import TestClient
from src.app import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.mark.asyncio
def test_get_activities(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Basketball Team" in data
    assert "participants" in data["Basketball Team"]

def test_signup_for_activity(client):
    # Test successful signup
    response = client.post("/activities/Basketball%20Team/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "Signed up test@example.com for Basketball Team" in data["message"]

    # Verify participant was added
    response = client.get("/activities")
    data = response.json()
    assert "test@example.com" in data["Basketball Team"]["participants"]

def test_signup_already_signed_up(client):
    # First signup
    client.post("/activities/Soccer%20Club/signup?email=duplicate@example.com")
    
    # Try to signup again
    response = client.post("/activities/Soccer%20Club/signup?email=duplicate@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "Student already signed up for this activity" in data["detail"]

def test_signup_activity_not_found(client):
    response = client.post("/activities/Nonexistent%20Activity/signup?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]

def test_unregister_from_activity(client):
    # First signup
    client.post("/activities/Art%20Club/signup?email=unregister@example.com")
    
    # Unregister
    response = client.delete("/activities/Art%20Club/unregister?email=unregister@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered unregister@example.com from Art Club" in data["message"]

    # Verify participant was removed
    response = client.get("/activities")
    data = response.json()
    assert "unregister@example.com" not in data["Art Club"]["participants"]

def test_unregister_not_signed_up(client):
    response = client.delete("/activities/Drama%20Club/unregister?email=notsigned@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "Student not signed up for this activity" in data["detail"]

def test_unregister_activity_not_found(client):
    response = client.delete("/activities/Nonexistent%20Activity/unregister?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]

def test_root_redirect(client):
    response = client.get("/")
    assert response.status_code == 200
    # The root redirects to /static/index.html, and TestClient serves the static file
    assert "Mergington High School" in response.text