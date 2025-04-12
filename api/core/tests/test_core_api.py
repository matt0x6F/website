from django.test import Client, TestCase


class HealthCheckTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_health_endpoint(self):
        """Test that the health endpoint returns OK status"""
        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
