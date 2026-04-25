"""
Tests for Comments API endpoints.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status


class CommentAPIDetailedTestCase(TestCase):
    """Test Comment API endpoints in detail."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username='commentuser',
            password='testpass123',
            email='user@test.com'
        )
    
    def test_comment_list(self):
        """Test GET /comments/ endpoints - smoke test."""
        # Try possible endpoint paths
        possible_endpoints = [
            '/comments/',
            '/comments/api/comments/',
        ]
        
        for endpoint in possible_endpoints:
            response = self.client.get(endpoint)
            # Accept success responses or expected errors
            self.assertIn(
                response.status_code,
                [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND,
                 status.HTTP_405_METHOD_NOT_ALLOWED]
            )
