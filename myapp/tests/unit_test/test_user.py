import base64

from django.test import TestCase, Client
from myapp.models import User
import json

from myapp.views import get_user_from_credentials


class UserViewsTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.test_user = User.objects.create(
            username='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpassword123'
        )

        # Create a test client
        self.client = Client()

    def test_healthz_view(self):
        response = self.client.get('/healthz')
        self.assertEqual(response.status_code, 200)

    def test_ping_view(self):
        response = self.client.get('/ping')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'message': 'pong'})

    def test_create_user_view(self):
        # Test valid POST request
        data = {
            'username': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newuserpassword123'
        }
        response = self.client.post('/v1/user', data=json.dumps(data), content_type='application/json')  # Updated URL
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username='newuser@example.com').exists())

        # Test invalid POST request (missing required field)
        invalid_data = {
            'first_name': 'Invalid',
            'last_name': 'User'
        }
        response = self.client.post('/v1/user', data=json.dumps(invalid_data), content_type='application/json')  # Updated URL
        self.assertEqual(response.status_code, 400)

    def test_get_user_from_credentials(self):
        # Test valid credentials
        auth_header = 'Basic ' + base64.b64encode(b'test@example.com:testpassword123').decode('utf-8')
        request = self.client.get('/', HTTP_AUTHORIZATION=auth_header)
        user, password = get_user_from_credentials(request)
        self.assertEqual(user.username, 'test@example.com')
        self.assertEqual(password, 'testpassword123')

        # Test invalid credentials
        invalid_auth_header = 'Basic ' + base64.b64encode(b'invalid@example.com:invalidpassword').decode('utf-8')
        invalid_request = self.client.get('/', HTTP_AUTHORIZATION=invalid_auth_header)
        user, password = get_user_from_credentials(invalid_request)
        self.assertIsNone(user)
        self.assertIsNone(password)

    def test_user_info_view(self):
        # Test GET request with valid credentials
        auth_header = 'Basic ' + base64.b64encode(b'test@example.com:testpassword123').decode('utf-8')
        response = self.client.get('/v1/user/self', HTTP_AUTHORIZATION=auth_header)  # Updated URL
        self.assertEqual(response.status_code, 200)

        # Test PUT request with valid credentials
        data = {
            'first_name': 'Updated',
            'last_name': 'User'
        }
        response = self.client.put('/v1/user/self', data=json.dumps(data), content_type='application/json', HTTP_AUTHORIZATION=auth_header)  # Updated URL
        self.assertEqual(response.status_code, 204)
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.first_name, 'Updated')

        # Test PUT request with invalid credentials
        invalid_auth_header = 'Basic ' + base64.b64encode(b'invalid@example.com:invalidpassword').decode('utf-8')
        invalid_response = self.client.put('/v1/user/self', data=json.dumps(data), content_type='application/json', HTTP_AUTHORIZATION=invalid_auth_header)  # Updated URL
        self.assertEqual(invalid_response.status_code, 401)
