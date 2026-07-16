import pytest
from rest_framework.test import APIClient
from users.models import User


@pytest.fixture
def api_client():
    """
    A DRF test client — like a fake browser that makes API calls.
    Every test that needs to make HTTP requests gets this.
    """
    return APIClient()


@pytest.fixture
def student_user(db):
    """
    A ready-made student user for tests that need an existing user.
    The db fixture gives the test access to the database.
    """
    return User.objects.create_user(
        email    = 'student@example.com',
        username = 'teststudent',
        password = 'TestPass123!',
        role     = 'student',
        grade    = '10th',
    )


@pytest.fixture
def teacher_user(db):
    """A ready-made teacher user."""
    return User.objects.create_user(
        email    = 'teacher@example.com',
        username = 'testteacher',
        password = 'TestPass123!',
        role     = 'teacher',
        subject  = 'Mathematics',
    )


@pytest.fixture
def student_token(api_client, student_user):
    """
    A valid JWT access token for the student user.
    Tests that need an authenticated request get this.
    """
    response = api_client.post('/api/auth/login/', {
        'email':    'student@example.com',
        'password': 'TestPass123!',
    }, format='json')
    return response.data['access']