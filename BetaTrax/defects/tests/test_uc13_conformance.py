from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User

from defects.models import DefectReport


class DefectsEndpointMethodConformanceTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.product_owner = User.objects.create_user(username="po_uc13", password="testpass")

    def defect_payload(self):
        return {
            "ProductID": "P001",
            "Version": "1.0",
            "ReportTitle": "Conformance defect",
            "Description": "Conformance description",
            "Steps": "Step1\nStep2",
            "TesterID": "T001",
        }

    def test_reports_list_get_success(self):
        response = self.client.get("/defects/reports/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reports_list_post_success(self):
        response = self.client.post("/defects/reports/", self.defect_payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_reports_detail_delete_success(self):
        defect = DefectReport.objects.create(**self.defect_payload())
        response = self.client.delete(f"/defects/reports/{defect.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_developer_metrics_get_success(self):
        self.client.force_authenticate(user=self.product_owner)
        response = self.client.get(f"/defects/reports/developer-metrics/{self.product_owner.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
