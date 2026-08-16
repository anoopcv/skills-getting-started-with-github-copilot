"""
Tests for FastAPI backend endpoints.
Tests cover happy-path scenarios for all endpoints.
"""

import pytest


def test_get_activities(client, reset_activities):
    """Test GET /activities returns all activities with correct structure."""
    response = client.get("/activities")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check that response is a dictionary
    assert isinstance(data, dict)
    
    # Check that known activities exist
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data
    
    # Check activity structure
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_for_activity_success(client, reset_activities):
    """Test POST /activities/{activity}/signup successfully registers a new student."""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "newstudent@mergington.edu" in data["message"]


def test_signup_updates_participants(client, reset_activities):
    """Test that participants list is updated after successful signup."""
    # Get initial state
    initial = client.get("/activities").json()
    initial_count = len(initial["Programming Class"]["participants"])
    
    # Signup new student
    response = client.post(
        "/activities/Programming Class/signup",
        params={"email": "newcomer@mergington.edu"}
    )
    assert response.status_code == 200
    
    # Verify participant was added
    updated = client.get("/activities").json()
    new_count = len(updated["Programming Class"]["participants"])
    assert new_count == initial_count + 1
    assert "newcomer@mergington.edu" in updated["Programming Class"]["participants"]


def test_unregister_from_activity_success(client, reset_activities):
    """Test DELETE /activities/{activity}/unregister successfully removes a student."""
    # First, get an existing participant
    activities = client.get("/activities").json()
    chess_club = activities["Chess Club"]
    existing_participant = chess_club["participants"][0]
    
    # Unregister that participant
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": existing_participant}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert existing_participant in data["message"]


def test_unregister_updates_participants(client, reset_activities):
    """Test that participants list is updated after successful unregister."""
    # Get initial state
    initial = activities = client.get("/activities").json()
    gym_class = initial["Gym Class"]
    initial_count = len(gym_class["participants"])
    participant_to_remove = gym_class["participants"][0]
    
    # Unregister student
    response = client.delete(
        "/activities/Gym Class/unregister",
        params={"email": participant_to_remove}
    )
    assert response.status_code == 200
    
    # Verify participant was removed
    updated = client.get("/activities").json()
    new_count = len(updated["Gym Class"]["participants"])
    assert new_count == initial_count - 1
    assert participant_to_remove not in updated["Gym Class"]["participants"]


def test_signup_duplicate_student_error(client, reset_activities):
    """Test that signing up the same student twice returns 400 error."""
    # Get an existing participant
    activities = client.get("/activities").json()
    existing_participant = activities["Tennis Club"]["participants"][0]
    
    # Try to sign them up again
    response = client.post(
        "/activities/Tennis Club/signup",
        params={"email": existing_participant}
    )
    
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_activity_not_found_error(client, reset_activities):
    """Test that signing up for non-existent activity returns 404 error."""
    response = client.post(
        "/activities/Nonexistent Activity/signup",
        params={"email": "student@mergington.edu"}
    )
    
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_signup_at_capacity_error(client, reset_activities):
    """Test that signing up for full activity returns 400 error."""
    # Create an activity that's at capacity
    from app import activities
    test_activity = "Tennis Club"
    activity = activities[test_activity]
    original_count = len(activity["participants"])
    
    # Fill the activity to capacity
    activity["participants"] = [f"participant{i}@mergington.edu" for i in range(activity["max_participants"])]
    
    # Try to sign up when at capacity
    response = client.post(
        f"/activities/{test_activity}/signup",
        params={"email": "newstudent@mergington.edu"}
    )
    
    assert response.status_code == 400
    assert "full" in response.json()["detail"]


def test_unregister_not_registered_error(client, reset_activities):
    """Test that unregistering a student who isn't signed up returns 400 error."""
    response = client.delete(
        "/activities/Art Studio/unregister",
        params={"email": "notregistered@mergington.edu"}
    )
    
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]


def test_unregister_activity_not_found_error(client, reset_activities):
    """Test that unregistering from non-existent activity returns 404 error."""
    response = client.delete(
        "/activities/Nonexistent Activity/unregister",
        params={"email": "student@mergington.edu"}
    )
    
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]
