"""
Pytest configuration and fixtures for the test suite
"""

import pytest
from src.app import activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to their initial state before each test"""
    # Store initial state
    initial_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team for interscholastic play",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis techniques and participate in matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["sarah@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and sculpture techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["lucas@mergington.edu", "maya@mergington.edu"]
        },
        "Music Ensemble": {
            "description": "Learn and perform music in a group setting",
            "schedule": "Mondays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 25,
            "participants": ["aisha@mergington.edu", "james@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Tuesdays and Fridays, 3:30 PM - 4:45 PM",
            "max_participants": 12,
            "participants": ["ryan@mergington.edu", "ava@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore scientific experiments and research projects",
            "schedule": "Wednesdays, 4:00 PM - 5:15 PM",
            "max_participants": 18,
            "participants": ["noah@mergington.edu", "isabella@mergington.edu"]
        }
    }
    
    # Clear current activities
    activities.clear()
    
    # Restore initial state with deep copies
    for name, data in initial_activities.items():
        activities[name] = {
            "description": data["description"],
            "schedule": data["schedule"],
            "max_participants": data["max_participants"],
            "participants": data["participants"].copy()
        }
    
    yield
    
    # Cleanup after test (optional, will be reset again on next test)
