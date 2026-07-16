import pytest
from rest_framework import status
from users.models import User


# ── Registration tests ────────────────────────────────────────────────────────

class TestRegisterView:

    def test_student_can_register_with_valid_data(self, api_client, db):
        """
        A student providing all required fields should get
        a 201 response with their profile data.
        """
        payload = {
            'email':     'newstudent@example.com',
            'username':  'newstudent',
            'password':  'SecurePass123!',
            'password2': 'SecurePass123!',
            'role':      'student',
            'grade':     '10th',
        }
        response = api_client.post(
            '/api/auth/register/', payload, format='json'
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['email'] == 'newstudent@example.com'
        assert response.data['role']  == 'student'
        assert response.data['grade'] == '10th'
        assert 'password' not in response.data  # password never returned

    def test_teacher_can_register_with_valid_data(self, api_client, db):
        """A teacher providing all required fields should get a 201."""
        payload = {
            'email':     'newteacher@example.com',
            'username':  'newteacher',
            'password':  'SecurePass123!',
            'password2': 'SecurePass123!',
            'role':      'teacher',
            'subject':   'Mathematics',
        }
        response = api_client.post(
            '/api/auth/register/', payload, format='json'
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['role']    == 'teacher'
        assert response.data['subject'] == 'Mathematics'

    def test_register_fails_when_passwords_do_not_match(self, api_client, db):
        """Mismatched passwords should return 400 with a clear error."""
        payload = {
            'email':     'test@example.com',
            'username':  'testuser',
            'password':  'SecurePass123!',
            'password2': 'DifferentPass123!',
            'role':      'student',
            'grade':     '10th',
        }
        response = api_client.post(
            '/api/auth/register/', payload, format='json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data

    def test_register_fails_when_student_has_no_grade(self, api_client, db):
        """A student without a grade should get a 400 error."""
        payload = {
            'email':     'test@example.com',
            'username':  'testuser',
            'password':  'SecurePass123!',
            'password2': 'SecurePass123!',
            'role':      'student',
            # grade deliberately missing
        }
        response = api_client.post(
            '/api/auth/register/', payload, format='json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'grade' in response.data

    def test_register_fails_when_teacher_has_no_subject(self, api_client, db):
        """A teacher without a subject should get a 400 error."""
        payload = {
            'email':     'teacher@example.com',
            'username':  'teacheruser',
            'password':  'SecurePass123!',
            'password2': 'SecurePass123!',
            'role':      'teacher',
            # subject deliberately missing
        }
        response = api_client.post(
            '/api/auth/register/', payload, format='json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'subject' in response.data

    def test_register_fails_with_duplicate_email(self, api_client, student_user):
        """Registering with an already-used email should return 400."""
        payload = {
            'email':     'student@example.com',  # same as student_user fixture
            'username':  'differentusername',
            'password':  'SecurePass123!',
            'password2': 'SecurePass123!',
            'role':      'student',
            'grade':     '10th',
        }
        response = api_client.post(
            '/api/auth/register/', payload, format='json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data

    def test_register_fails_with_weak_password(self, api_client, db):
        """A password that is too short or too common should return 400."""
        payload = {
            'email':     'test@example.com',
            'username':  'testuser',
            'password':  '123',
            'password2': '123',
            'role':      'student',
            'grade':     '10th',
        }
        response = api_client.post(
            '/api/auth/register/', payload, format='json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ── Login tests ───────────────────────────────────────────────────────────────

class TestLoginView:

    def test_login_returns_tokens_with_correct_credentials(
        self, api_client, student_user
    ):
        """
        Valid email and password should return both
        access and refresh JWT tokens.
        """
        response = api_client.post('/api/auth/login/', {
            'email':    'student@example.com',
            'password': 'TestPass123!',
        }, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'access'  in response.data
        assert 'refresh' in response.data

    def test_login_fails_with_wrong_password(self, api_client, student_user):
        """Wrong password should return 401."""
        response = api_client.post('/api/auth/login/', {
            'email':    'student@example.com',
            'password': 'WrongPassword!',
        }, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_fails_with_nonexistent_email(self, api_client, db):
        """An email that doesn't exist should return 401."""
        response = api_client.post('/api/auth/login/', {
            'email':    'nobody@example.com',
            'password': 'SomePass123!',
        }, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ── Profile tests ─────────────────────────────────────────────────────────────

class TestProfileView:

    def test_authenticated_user_can_view_their_profile(
        self, api_client, student_user, student_token
    ):
        """
        A user with a valid token should get their
        profile data back from /api/auth/me/
        """
        api_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {student_token}'
        )
        response = api_client.get('/api/auth/me/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == 'student@example.com'
        assert response.data['role']  == 'student'
        assert 'password' not in response.data

    def test_unauthenticated_request_is_rejected(self, api_client):
        """
        A request with no token should get a 401.
        This confirms the endpoint is protected.
        """
        response = api_client.get('/api/auth/me/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_profile_returns_correct_user_not_another(
        self, api_client, student_user, teacher_user, student_token
    ):
        """
        The /me/ endpoint should always return the
        requesting user's data — never someone else's.
        """
        api_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {student_token}'
        )
        response = api_client.get('/api/auth/me/')

        assert response.data['email'] == 'student@example.com'
        assert response.data['email'] != 'teacher@example.com'


# ── User model tests ──────────────────────────────────────────────────────────

class TestUserModel:

    def test_student_user_is_student_property(self, student_user):
        """The is_student property should return True for students."""
        assert student_user.is_student is True
        assert student_user.is_teacher is False

    def test_teacher_user_is_teacher_property(self, teacher_user):
        """The is_teacher property should return True for teachers."""
        assert teacher_user.is_teacher is True
        assert teacher_user.is_student is False

    def test_user_str_representation(self, student_user):
        """__str__ should return email and role."""
        assert str(student_user) == 'student@example.com (student)'