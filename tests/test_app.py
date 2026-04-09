"""
Tests for the Mergington High School Activities API

Following the AAA (Arrange-Act-Assert) testing pattern:
- Arrange: Set up test data and preconditions
- Act: Perform the action being tested
- Assert: Verify the results
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


class TestActivities:
    """Test cases for the /activities endpoint"""

    def test_get_activities(self, client):
        """Test retrieving all activities"""
        # Arrange
        # (No setup needed for basic retrieval test)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        
        # Verify each activity has required fields
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_activities_contain_expected_activities(self, client):
        """Test that expected activities are present"""
        # Arrange
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", 
            "Basketball Team", "Tennis Club", "Art Studio",
            "Music Ensemble", "Debate Team", "Science Club"
        ]
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity in expected_activities:
            assert activity in activities


class TestSignup:
    """Test cases for the signup endpoint"""

    def test_signup_for_activity(self, client):
        """Test signing up for an activity"""
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert email in result["message"]
        assert activity in result["message"]

    def test_signup_duplicate_email(self, client):
        """Test that duplicate signups are rejected"""
        # Arrange
        email = "duplicate@mergington.edu"
        activity = "Chess Club"
        
        # Act - First signup
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert first signup succeeds
        assert response1.status_code == 200
        
        # Act - Second signup with same email
        response2 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert second signup fails
        assert response2.status_code == 400
        result = response2.json()
        assert "already signed up" in result["detail"].lower()

    def test_signup_nonexistent_activity(self, client):
        """Test signup for non-existent activity"""
        # Arrange
        email = "test@mergington.edu"
        activity = "Nonexistent Club"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "not found" in result["detail"].lower()

    def test_signup_activity_at_capacity(self, client):
        """Test signup fails when activity is at full capacity"""
        # Arrange
        activity = "Tennis Club"
        response = client.get("/activities")
        max_participants = response.json()[activity]["max_participants"]
        current_count = len(response.json()[activity]["participants"])
        available_spots = max_participants - current_count
        
        # Arrange - Fill all available spots
        for i in range(available_spots):
            client.post(
                f"/activities/{activity}/signup",
                params={"email": f"filler{i}@mergington.edu"}
            )
        
        # Act - Try to sign up when full
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": "overcapacity@mergington.edu"}
        )
        
        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "full capacity" in result["detail"].lower()

    def test_signup_adds_participant(self, client):
        """Test that signup actually adds the participant"""
        # Arrange
        email = "verify@mergington.edu"
        activity = "Tennis Club"
        response = client.get("/activities")
        initial_participants = response.json()[activity]["participants"].copy()
        
        # Act
        client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        response = client.get("/activities")
        updated_participants = response.json()[activity]["participants"]
        assert email in updated_participants
        assert len(updated_participants) == len(initial_participants) + 1


class TestUnregister:
    """Test cases for the unregister/delete endpoint"""

    def test_unregister_from_activity(self, client):
        """Test unregistering from an activity"""
        # Arrange
        email = "unregister@mergington.edu"
        activity = "Art Studio"
        
        # Arrange - Sign up first
        client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Act
        response = client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "Unregistered" in result["message"]

    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the participant"""
        # Arrange
        email = "remove@mergington.edu"
        activity = "Programming Class"
        
        # Arrange - Sign up first
        client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Act
        client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        assert email not in participants

    def test_unregister_nonexistent_participant(self, client):
        """Test unregistering a participant who wasn't signed up"""
        # Arrange
        email = "notregistered@mergington.edu"
        activity = "Music Ensemble"
        
        # Act
        response = client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "not signed up" in result["detail"].lower()

    def test_unregister_nonexistent_activity(self, client):
        """Test unregistering from non-existent activity"""
        # Arrange
        email = "test@mergington.edu"
        activity = "Nonexistent Club"
        
        # Act
        response = client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "not found" in result["detail"].lower()


class TestIntegration:
    """Integration tests for multiple operations"""

    def test_signup_and_unregister_flow(self, client):
        """Test complete signup and unregister flow"""
        # Arrange
        email = "flow@mergington.edu"
        activity = "Debate Team"
        response = client.get("/activities")
        initial_count = len(response.json()[activity]["participants"])
        
        # Act - Sign up
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert signup succeeded
        assert response.status_code == 200
        
        # Act - Verify participant count increased
        response = client.get("/activities")
        assert len(response.json()[activity]["participants"]) == initial_count + 1
        
        # Act - Unregister
        response = client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert unregister succeeded
        assert response.status_code == 200
        
        # Assert - Verify participant count back to initial
        response = client.get("/activities")
        assert len(response.json()[activity]["participants"]) == initial_count

    def test_multiple_signups_same_activity(self, client):
        """Test multiple different participants signing up for the same activity"""
        # Arrange
        activity = "Science Club"
        emails = [
            "user1@mergington.edu",
            "user2@mergington.edu",
            "user3@mergington.edu"
        ]
        response = client.get("/activities")
        initial_count = len(response.json()[activity]["participants"])
        
        # Act - Sign up all users
        for email in emails:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Assert - Verify all were added
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        assert len(participants) == initial_count + len(emails)
        for email in emails:
            assert email in participants

    def test_capacity_limits_respected(self, client):
        """Test that activities cannot exceed max participants"""
        # Arrange
        activity = "Tennis Club"
        response = client.get("/activities")
        max_participants = response.json()[activity]["max_participants"]
        current_participants = response.json()[activity]["participants"].copy()
        
        # Arrange - Calculate how many we can add
        available_spots = max_participants - len(current_participants)
        
        # Act - Sign up for all available spots (should succeed)
        successful_emails = []
        for i in range(available_spots):
            email = f"user{i}@mergington.edu"
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            if response.status_code == 200:
                successful_emails.append(email)
        
        # Assert - All available spots filled
        assert len(successful_emails) == available_spots
        response = client.get("/activities")
        assert len(response.json()[activity]["participants"]) == max_participants
        
        # Act - Try to sign up one more (should fail due to capacity)
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": "overfull@mergington.edu"}
        )
        
        # Assert - Signup rejected and capacity still respected
        assert response.status_code == 400
        result = response.json()
        assert "full capacity" in result["detail"].lower()
        
        response = client.get("/activities")
        assert len(response.json()[activity]["participants"]) == max_participants
