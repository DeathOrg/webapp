from django.test import TestCase, Client
from django.urls import reverse


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
