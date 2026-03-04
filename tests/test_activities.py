"""
Tests for FastAPI activity endpoints using AAA (Arrange-Act-Assert) pattern.
"""
import pytest


class TestRootEndpoint:
    """Tests for GET / endpoint"""
    
    def test_root_redirect(self, client):
        """Test that GET / redirects to /static/index.html"""
        # Arrange
        expected_redirect = "/static/index.html"
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_redirect


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all 7 activities"""
        # Arrange
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Debate Club",
            "Science Club"
        ]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert len(data) == 7
        for activity in expected_activities:
            assert activity in data
    
    def test_get_activities_returns_correct_structure(self, client):
        """Test that activities have correct structure with required fields"""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        activity_name = "Chess Club"
        
        # Act
        response = client.get("/activities")
        data = response.json()
        activity = data[activity_name]
        
        # Assert
        assert response.status_code == 200
        for field in required_fields:
            assert field in activity
        assert isinstance(activity["participants"], list)
    
    def test_get_activities_chess_club_initial_participants(self, client):
        """Test that Chess Club has correct initial participants"""
        # Arrange
        expected_participants = ["michael@mergington.edu", "daniel@mergington.edu"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        
        # Assert
        assert response.status_code == 200
        assert len(chess_club["participants"]) == 2
        assert chess_club["participants"] == expected_participants


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successfully_adds_participant(self, client):
        """Test successful signup adds email to activity participants"""
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Programming Class"
        initial_params = {"email": email}
        
        # Act
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params=initial_params
        )
        verify_response = client.get("/activities")
        verify_data = verify_response.json()
        
        # Assert
        assert signup_response.status_code == 200
        assert signup_response.json()["message"] == f"Signed up {email} for {activity}"
        assert email in verify_data[activity]["participants"]
    
    def test_signup_returns_correct_message(self, client):
        """Test signup endpoint returns correct success message"""
        # Arrange
        email = "testuser@mergington.edu"
        activity = "Gym Class"
        params = {"email": email}
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params=params
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert data["message"] == f"Signed up {email} for {activity}"
    
    def test_signup_fails_with_nonexistent_activity(self, client):
        """Test signup returns 404 for nonexistent activity"""
        # Arrange
        email = "test@mergington.edu"
        nonexistent_activity = "Nonexistent Club"
        params = {"email": email}
        
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params=params
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 404
        assert data["detail"] == "Activity not found"
    
    def test_signup_increases_participant_count(self, client):
        """Test signup increments the participants count"""
        # Arrange
        email = "counttest@mergington.edu"
        activity = "Tennis Club"
        params = {"email": email}
        
        # Act - Get initial count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity]["participants"])
        
        # Act - Sign up
        client.post(f"/activities/{activity}/signup", params=params)
        
        # Act - Get new count
        final_response = client.get("/activities")
        final_count = len(final_response.json()[activity]["participants"])
        
        # Assert
        assert final_count == initial_count + 1


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/signup endpoint"""
    
    def test_unregister_successfully_removes_participant(self, client):
        """Test unregister removes email from activity participants"""
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"
        params = {"email": email}
        
        # Act
        unregister_response = client.delete(
            f"/activities/{activity}/signup",
            params=params
        )
        verify_response = client.get("/activities")
        verify_data = verify_response.json()
        
        # Assert
        assert unregister_response.status_code == 200
        assert email not in verify_data[activity]["participants"]
    
    def test_unregister_returns_correct_message(self, client):
        """Test unregister endpoint returns correct success message"""
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"
        params = {"email": email}
        
        # Act
        response = client.delete(
            f"/activities/{activity}/signup",
            params=params
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert data["message"] == f"Removed {email} from {activity}"
    
    def test_unregister_fails_with_nonexistent_activity(self, client):
        """Test unregister returns 404 for nonexistent activity"""
        # Arrange
        email = "test@mergington.edu"
        nonexistent_activity = "Nonexistent Club"
        params = {"email": email}
        
        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/signup",
            params=params
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 404
        assert data["detail"] == "Activity not found"
    
    def test_unregister_fails_with_nonexistent_participant(self, client):
        """Test unregister returns 404 when participant not in activity"""
        # Arrange
        email = "notinlist@mergington.edu"
        activity = "Chess Club"
        params = {"email": email}
        
        # Act
        response = client.delete(
            f"/activities/{activity}/signup",
            params=params
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 404
        assert data["detail"] == "Participant not found"
    
    def test_unregister_decreases_participant_count(self, client):
        """Test unregister decrements the participants count"""
        # Arrange
        email = "sarah@mergington.edu"
        activity = "Tennis Club"
        params = {"email": email}
        
        # Act - Get initial count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity]["participants"])
        
        # Act - Unregister
        client.delete(f"/activities/{activity}/signup", params=params)
        
        # Act - Get new count
        final_response = client.get("/activities")
        final_count = len(final_response.json()[activity]["participants"])
        
        # Assert
        assert final_count == initial_count - 1


class TestSignupAndUnregisterWorkflow:
    """Integration tests for signup and unregister workflows"""
    
    def test_multiple_signups_and_unregisters_sequence(self, client):
        """Test multiple signup and unregister operations in sequence"""
        # Arrange
        activity = "Tennis Club"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        # Act - Sign up first student
        signup1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email1}
        )
        
        # Act - Sign up second student
        signup2 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email2}
        )
        
        # Assert - Both signed up successfully
        assert signup1.status_code == 200
        assert signup2.status_code == 200
        
        # Act - Verify both are present
        verify1 = client.get("/activities")
        participants1 = verify1.json()[activity]["participants"]
        
        # Assert
        assert email1 in participants1
        assert email2 in participants1
        count_after_signups = len(participants1)
        
        # Act - Unregister first student
        unregister = client.delete(
            f"/activities/{activity}/signup",
            params={"email": email1}
        )
        
        # Assert - Unregister successful
        assert unregister.status_code == 200
        
        # Act - Verify only second student remains
        verify2 = client.get("/activities")
        participants2 = verify2.json()[activity]["participants"]
        
        # Assert
        assert email1 not in participants2
        assert email2 in participants2
        assert len(participants2) == count_after_signups - 1
    
    def test_signup_then_unregister_same_participant(self, client):
        """Test signup followed by unregister of the same participant"""
        # Arrange
        activity = "Debate Club"
        email = "roundtrip@mergington.edu"
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert - Signup successful
        assert signup_response.status_code == 200
        verify_after_signup = client.get("/activities")
        assert email in verify_after_signup.json()[activity]["participants"]
        
        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert - Unregister successful
        assert unregister_response.status_code == 200
        verify_after_unregister = client.get("/activities")
        assert email not in verify_after_unregister.json()[activity]["participants"]
