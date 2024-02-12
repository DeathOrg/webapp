# tests.py

from django.test import TestCase, Client
from django.urls import reverse
from myapp.models import User
import base64
import json


class HealthzViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_healthz_get(self):
        response = self.client.get(reverse('healthz'))
        self.assertEqual(response.status_code, 200)

    def test_healthz_post(self):
        response = self.client.post(reverse('healthz'))
        self.assertEqual(response.status_code, 405)


class PingViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_ping_get(self):
        response = self.client.get(reverse('ping'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'message': 'pong'})

    def test_ping_post(self):
        response = self.client.post(reverse('ping'))
        self.assertEqual(response.status_code, 405)


class CreateUserViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {'username': 'testuser@example.com', 'password': 'testpassword', 'first_name': 'Rahul',
                          'last_name': 'Kumar',
                          }

    def test_create_user_success(self):
        response = self.client.post(reverse('create_user'), data=json.dumps(self.user_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username='testuser@example.com').exists())

    def test_create_user_missing_data(self):
        response = self.client.post(reverse('create_user'), data=json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.filter(username='').exists())
