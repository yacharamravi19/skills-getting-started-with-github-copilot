"""
Pytest configuration and fixtures for FastAPI tests.
"""
import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test.
    
    This ensures test isolation by restoring the activities dict
    to its original state after each test modifies it.
    """
    original_activities = copy.deepcopy(activities)
    yield
    # Restore original state after test
    activities.clear()
    activities.update(original_activities)
