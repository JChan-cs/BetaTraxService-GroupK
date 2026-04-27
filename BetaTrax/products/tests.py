from datetime import timedelta

from django.contrib.auth.models import Group, User
from django.utils import timezone
from django_tenants.test.cases import TenantTestCase
from rest_framework import status
from rest_framework.test import APIClient

from products.models import DeveloperAssignment, Product


class ProductsEndpointConformanceTests(TenantTestCase):
	@classmethod
	def setup_tenant(cls, tenant):
		tenant.name = "Products Conformance Tenant"
		tenant.paid_until = timezone.now().date() + timedelta(days=30)
		tenant.on_trial = True

	@classmethod
	def get_test_tenant_domain(cls):
		return "testserver"

	def setUp(self):
		self.client = APIClient()

		po_group, _ = Group.objects.get_or_create(name="ProductOwner")
		dev_group, _ = Group.objects.get_or_create(name="Developer")

		self.owner = User.objects.create_user(username="po_products", password="testpass")
		self.owner_alt = User.objects.create_user(username="po_products_alt", password="testpass")
		self.developer = User.objects.create_user(username="dev_products", password="testpass")

		self.owner.groups.add(po_group)
		self.owner_alt.groups.add(po_group)
		self.developer.groups.add(dev_group)

	def _create_product(self, owner=None, developer=None):
		owner = owner or self.owner
		product = Product.objects.create(
			product_id="PROD-001",
			version="1.0.0",
			name="Search Service",
			status="In progress",
			product_owner=owner,
		)
		if developer:
			DeveloperAssignment.objects.create(developer=developer, product=product)
		return product

	def test_products_list_get_success(self):
		self._create_product(owner=self.owner, developer=self.developer)
		self.client.force_authenticate(user=self.owner)

		response = self.client.get("/product_reg/products/")

		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_products_create_post_success(self):
		self.client.force_authenticate(user=self.owner)

		payload = {
			"product_id": "PROD-NEW",
			"version": "2.0.0",
			"name": "Analytics Service",
			"status": "In progress",
			"product_owner": self.owner.id,
			"developers": [self.developer.id],
		}

		response = self.client.post("/product_reg/products/", payload, format="json")

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

	def test_products_detail_get_success(self):
		product = self._create_product(owner=self.owner, developer=self.developer)
		self.client.force_authenticate(user=self.owner)

		response = self.client.get(f"/product_reg/products/{product.id}/")

		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_products_detail_put_success(self):
		product = self._create_product(owner=self.owner, developer=self.developer)
		self.client.force_authenticate(user=self.owner)

		payload = {
			"product_id": product.product_id,
			"version": "1.1.0",
			"name": "Search Service Updated",
			"status": "Complete",
			"product_owner": self.owner.id,
			"developers": [self.developer.id],
		}

		response = self.client.put(f"/product_reg/products/{product.id}/", payload, format="json")

		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_products_detail_patch_success(self):
		product = self._create_product(owner=self.owner, developer=self.developer)
		self.client.force_authenticate(user=self.owner)

		payload = {
			"status": "Complete",
			"product_owner": self.owner.id,
			"developers": [self.developer.id],
		}

		response = self.client.patch(f"/product_reg/products/{product.id}/", payload, format="json")

		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_products_detail_delete_success(self):
		product = self._create_product(owner=self.owner, developer=self.developer)
		self.client.force_authenticate(user=self.owner)

		response = self.client.delete(f"/product_reg/products/{product.id}/")

		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

	def test_product_dashboard_get_success(self):
		self.client.login(username="po_products", password="testpass")

		response = self.client.get("/product_reg/dashboard/")

		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_product_dashboard_post_success(self):
		self.client.login(username="po_products", password="testpass")

		payload = {
			"product_id": "PROD-DASH",
			"version": "3.0.0",
			"name": "Dashboard Product",
			"status": "In progress",
			"product_owner": str(self.owner.id),
			"developer": [str(self.developer.id)],
		}

		response = self.client.post("/product_reg/dashboard/", payload)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
