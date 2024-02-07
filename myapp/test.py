import base64

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from .views import healthz, ping, create_user, user_info

User = get_user_model()

class HealthzViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_healthz_view(self):
        request = self.factory.get(reverse('healthz'))
        response = healthz(request)
        self.assertEqual(response.status_code, 200)

class PingViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_ping_view(self):
        response = self.client.get('/ping')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'pong')

#
# class CreateUserViewTest(TestCase):
#     def setUp(self):
#         self.factory = RequestFactory()
#
#     def test_create_user_view(self):
#         request_data = {'username': 'testuser', 'password': 'testpass'}
#         request = self.factory.post(reverse('create_user'), data=request_data, content_type='application/json')
#         response = create_user(request)
#         self.assertEqual(response.status_code, 201)
#         # Add more assertions as needed
#
# class UserInfoViewTest(TestCase):
#     def setUp(self):
#         self.factory = RequestFactory()
#         self.user = User.objects.create_user(username='testuser', password='testpass')
#
#     def test_user_info_view(self):
#         request = self.factory.get(reverse('user_info'))
#         request.headers['Authorization'] = 'Basic ' + base64.b64encode(b'testuser:testpass').decode('utf-8')
#         response = user_info(request)
#         self.assertEqual(response.status_code, 200)
#         # Add more assertions as needed
