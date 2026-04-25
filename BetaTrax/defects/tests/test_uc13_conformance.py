from datetime import timedelta

from django.utils import timezone
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from django_tenants.test.cases import TenantTestCase

from defects.models import DefectReport


class DefectsEndpointMethodConformanceTests(TenantTestCase):
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.name = "UC13 Tenant"
        tenant.paid_until = timezone.now().date() + timedelta(days=30)
        tenant.on_trial = True

    @classmethod
    def get_test_tenant_domain(cls):
        # Match Django test client's default host.
        return "testserver"

    def setUp(self):
        self.client = APIClient()
        self.product_owner = User.objects.create_user(username="po_uc13", password="testpass")
        self.developer = User.objects.create_user(username="dev_uc13", password="testpass")

        po_group, _ = Group.objects.get_or_create(name="ProductOwner")
        dev_group, _ = Group.objects.get_or_create(name="Developer")
        self.product_owner.groups.add(po_group)
        self.developer.groups.add(dev_group)

    def defect_payload(self):
        return {
            "ProductID": "P001",
            "Version": "1.0",
            "ReportTitle": "Conformance defect",
            "Description": "Conformance description",
            "Steps": "Step1\nStep2",
            "TesterID": "T001",
        }

    def create_defect(self, **overrides):
        payload = self.defect_payload()
        payload.update(overrides)
        return DefectReport.objects.create(**payload)

    def test_reports_list_get_success(self):
        response = self.client.get("/defects/reports/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reports_list_post_success(self):
        response = self.client.post("/defects/reports/", self.defect_payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_reports_detail_get_success(self):
        defect = self.create_defect()
        response = self.client.get(f"/defects/reports/{defect.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reports_detail_delete_success(self):
        defect = DefectReport.objects.create(**self.defect_payload())
        response = self.client.delete(f"/defects/reports/{defect.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_submit_get_success(self):
        response = self.client.get("/defects/reports/submit/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_submit_post_success(self):
        response = self.client.post("/defects/reports/submit/", self.defect_payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_dashboard_get_success(self):
        response = self.client.get("/defects/reports/dashboard/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_open_defects_get_success(self):
        self.create_defect(Status="Open")
        response = self.client.get("/defects/reports/open/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_new_defects_get_success(self):
        self.client.force_authenticate(user=self.product_owner)
        self.create_defect(Status="New")
        response = self.client.get("/defects/reports/new/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_my_assigned_get_success(self):
        self.client.force_authenticate(user=self.developer)
        self.create_defect(Status="Assigned", assigned_to=self.developer)
        response = self.client.get("/defects/reports/my-assigned/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_my_tasks_get_success(self):
        self.client.force_authenticate(user=self.developer)
        self.create_defect(Status="Assigned", assigned_to=self.developer)
        response = self.client.get("/defects/reports/my-tasks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_take_post_success(self):
        self.client.force_authenticate(user=self.developer)
        defect = self.create_defect(Status="Open")
        response = self.client.post(f"/defects/reports/{defect.id}/take/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_evaluate_get_success(self):
        self.client.force_authenticate(user=self.product_owner)
        defect = self.create_defect(Status="New")
        response = self.client.get(f"/defects/reports/{defect.id}/evaluate/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_evaluate_post_success(self):
        self.client.force_authenticate(user=self.product_owner)
        defect = self.create_defect(Status="New")
        payload = {"action": "reject"}
        response = self.client.post(f"/defects/reports/{defect.id}/evaluate/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_mark_fixed_get_success(self):
        self.client.force_authenticate(user=self.developer)
        defect = self.create_defect(Status="Assigned", assigned_to=self.developer)
        response = self.client.get(f"/defects/reports/{defect.id}/mark_fixed/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_mark_fixed_post_success(self):
        self.client.force_authenticate(user=self.developer)
        defect = self.create_defect(Status="Assigned", assigned_to=self.developer)
        response = self.client.post(f"/defects/reports/{defect.id}/mark_fixed/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_retest_get_success(self):
        self.client.force_authenticate(user=self.product_owner)
        defect = self.create_defect(Status="Resolved", assigned_to=self.developer)
        response = self.client.get(f"/defects/reports/{defect.id}/retest/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retest_post_success(self):
        self.client.force_authenticate(user=self.product_owner)
        defect = self.create_defect(Status="Resolved", assigned_to=self.developer)
        response = self.client.post(
            f"/defects/reports/{defect.id}/retest/",
            {"action": "fail"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_developer_metrics_get_success(self):
        self.client.force_authenticate(user=self.product_owner)
        response = self.client.get(f"/defects/reports/developer-metrics/{self.product_owner.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
