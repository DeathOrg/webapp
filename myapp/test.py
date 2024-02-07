from django.test import SimpleTestCase
from django.urls import reverse

class PingAPITest(SimpleTestCase):
    def test_ping_view(self):
        url = reverse('ping')  # Assuming 'ping' is the name of your ping API endpoint
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'pong')
