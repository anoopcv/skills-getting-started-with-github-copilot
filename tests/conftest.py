"""
Pytest configuration and fixtures for FastAPI backend tests.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to Python path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """
    Provide a TestClient for making requests to the app.
    """
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Reset activities to a known state before each test.
    This ensures test isolation and prevents test interdependencies.
    """
    # Import here to get fresh state
    from app import activities
    
    # Store original state
    original_activities = {
        key: {
            "description": value["description"],
            "schedule": value["schedule"],
            "max_participants": value["max_participants"],
            "participants": value["participants"].copy()
        }
        for key, value in activities.items()
    }
    
    yield
    
    # Restore original state after test
    activities.clear()
    activities.update(original_activities)
