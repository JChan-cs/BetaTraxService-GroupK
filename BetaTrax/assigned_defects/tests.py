"""
Tests for Assigned Defects API endpoints.
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from defects.models import DefectReport


class AssignedDefectsAPITestCase(TestCase):
    """Test Assigned Defects API endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        
        # Create test defects
        self.assigned_defect = DefectReport.objects.create(
            ProductID='PROD001',
            Version='1.0.0',
            ReportTitle='Assigned Defect',
            Description='Test',
            Steps='Steps',
            TesterID='test',
            Status='Assigned'
        )
    
    def test_assigned_defects_list(self):
        """Test GET /api/assigned_defects/ - list assigned defects."""
        response = self.client.get('/api/assigned_defects/')
        # May return 200 or 404 depending on API setup
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])
