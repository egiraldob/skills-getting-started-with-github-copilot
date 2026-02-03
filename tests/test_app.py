"""
Tests for the Mergington High School API

These tests verify the functionality of the FastAPI application for managing
extracurricular activities and student signups.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


class TestActivities:
    """Test cases for activities endpoints"""

    def test_get_activities(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Verify at least one expected activity exists
        assert "Chess Club" in data
        assert "Basketball" in data
        assert "Programming Class" in data

    def test_activity_structure(self, client):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        # Check Chess Club structure
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_activities_have_participants(self, client):
        """Test that some activities have existing participants"""
        response = client.get("/activities")
        data = response.json()
        
        # Verify at least one activity has participants
        has_participants = any(
            len(activity["participants"]) > 0 
            for activity in data.values()
        )
        assert has_participants, "At least one activity should have participants"


class TestSignup:
    """Test cases for student signup endpoints"""

    def test_signup_for_activity(self, client):
        """Test signing up a student for an activity"""
        email = "test.student@mergington.edu"
        activity = "Art Studio"
        
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_signup_appears_in_activity(self, client):
        """Test that signed up student appears in the activity participants list"""
        email = "new.student@mergington.edu"
        activity = "Debate Team"
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify in activities list
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert email in data[activity]["participants"]

    def test_duplicate_signup_rejected(self, client):
        """Test that duplicate signup is rejected"""
        email = "michael@mergington.edu"  # Already signed up for Chess Club
        activity = "Chess Club"
        
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()

    def test_signup_nonexistent_activity(self, client):
        """Test that signup for non-existent activity fails"""
        email = "test@mergington.edu"
        activity = "Nonexistent Activity"
        
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_signup_multiple_activities(self, client):
        """Test that a student can sign up for multiple activities"""
        email = "multi.student@mergington.edu"
        
        # Sign up for two different activities
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        response2 = client.post(
            "/activities/Basketball/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify both signups
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert email in data["Chess Club"]["participants"]
        assert email in data["Basketball"]["participants"]


class TestUnregister:
    """Test cases for student unregister endpoints"""

    def test_unregister_from_activity(self, client):
        """Test unregistering a student from an activity"""
        email = "test.unregister@mergington.edu"
        activity = "Science Club"
        
        # First, sign up
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Then unregister
        unregister_response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        data = unregister_response.json()
        assert data["success"] is True

    def test_unregistered_student_not_in_participants(self, client):
        """Test that unregistered student is removed from participants"""
        email = "temp.student@mergington.edu"
        activity = "Tennis"
        
        # Sign up
        client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Verify signup
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]
        
        # Unregister
        client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        
        # Verify removal
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]

    def test_unregister_nonexistent_activity(self, client):
        """Test that unregister from non-existent activity fails"""
        email = "test@mergington.edu"
        activity = "Nonexistent Activity"
        
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_unregister_nonexistent_student(self, client):
        """Test that unregistering non-existent student fails"""
        email = "nonexistent@mergington.edu"
        activity = "Drama Club"
        
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"].lower()


class TestRootRedirect:
    """Test cases for root endpoint"""

    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static HTML"""
        response = client.get("/", follow_redirects=True)
        assert response.status_code == 200
        # The response should contain HTML content
        assert "html" in response.text.lower() or "Mergington" in response.text
