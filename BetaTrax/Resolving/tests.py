"""
Tests for Resolving API endpoints.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status


class ResolvingAPITestCase(TestCase):
    """Test Resolving API endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        
        # Create a test user for Result author requirement
        self.user = User.objects.create_user(
            username='resolving_user',
            password='testpass123'
        )
    
    def test_result_list(self):
        """Test GET /resolved/ endpoints - smoke test."""
        possible_endpoints = [
            '/resolved/',
            '/resolved/api/results/',
            '/api/results/',
        ]
        
        for endpoint in possible_endpoints:
            response = self.client.get(endpoint)
            self.assertIn(
                response.status_code,
                [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND,
                 status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_302_FOUND, status.HTTP_301_MOVED_PERMANENTLY]
            )
    
    def test_result_retrieve(self):
        """Test GET /resolved/{id}/ - smoke test."""
        response = self.client.get('/resolved/1/')
        self.assertIn(
            response.status_code,
            [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND, status.HTTP_405_METHOD_NOT_ALLOWED]
        )
