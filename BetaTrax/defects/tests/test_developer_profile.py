from datetime import timedelta

from django.contrib.auth.models import Group, User
from django.utils import timezone
from django_tenants.test.cases import TenantTestCase
from rest_framework import status
from rest_framework.test import APIClient

from defects.models import DeveloperMetrics


class DeveloperProfileViewTests(TenantTestCase):
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.name = "Developer Profile Tenant"
        tenant.paid_until = timezone.now().date() + timedelta(days=30)
        tenant.on_trial = True

    @classmethod
    def get_test_tenant_domain(cls):
        return "testserver"

    def setUp(self):
        self.client = APIClient()

        po_group, _ = Group.objects.get_or_create(name="ProductOwner")
        dev_group, _ = Group.objects.get_or_create(name="Developer")

        self.product_owner = User.objects.create_user(username="po_profile", password="testpass")
        self.developer = User.objects.create_user(username="dev_profile", password="testpass")
        self.product_owner.groups.add(po_group)
        self.developer.groups.add(dev_group)

        DeveloperMetrics.objects.create(user=self.developer, defects_fixed=32, defects_reopened=1)

    def test_product_owner_can_open_developer_ratings_page(self):
        self.client.force_authenticate(user=self.product_owner)
        response = self.client.get("/defects/reports/developers/", HTTP_ACCEPT="text/html")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "dev_profile")

    def test_product_owner_can_open_developer_profile_page(self):
        self.client.force_authenticate(user=self.product_owner)
        response = self.client.get(
            f"/defects/reports/developer-profile/{self.developer.id}/",
            HTTP_ACCEPT="text/html",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Name:")
        self.assertContains(response, "dev_profile")
        self.assertContains(response, "Account Creation Date:")
        self.assertContains(response, "Developer Rating:")

    def test_non_product_owner_cannot_open_developer_profile_page(self):
        self.client.force_authenticate(user=self.developer)
        response = self.client.get(f"/defects/reports/developer-profile/{self.developer.id}/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
