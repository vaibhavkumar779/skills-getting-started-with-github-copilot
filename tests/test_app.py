import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_all_activities(client):
    # Arrange: no setup required for retrieving activities

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == activities


def test_signup_for_activity_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    new_email = "nina@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": new_email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_email} for {activity_name}"}
    assert new_email in activities[activity_name]["participants"]


def test_signup_for_activity_duplicate_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": existing_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_for_unknown_activity_returns_404(client):
    # Arrange
    activity_name = "Nonexistent Club"
    email = "luke@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_removes_existing_participant(client):
    # Arrange
    activity_name = "Basketball Team"
    participant_email = "alex@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": participant_email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {participant_email} from {activity_name}"}
    assert participant_email not in activities[activity_name]["participants"]


def test_remove_participant_unknown_activity_returns_404(client):
    # Arrange
    activity_name = "Nonexistent Club"
    email = "max@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_nonexistent_participant_returns_404(client):
    # Arrange
    activity_name = "Chess Club"
    email = "unknown@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
