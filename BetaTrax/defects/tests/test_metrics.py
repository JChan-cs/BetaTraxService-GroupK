from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from defects.models import DefectReport, DeveloperMetrics
import defects.signals  
from rest_framework.test import APIRequestFactory
from defects.views import DefectReportViewSet

def test_direct_view_call(self):
    factory = APIRequestFactory()
    view = DefectReportViewSet.as_view({'get': 'developer_metrics'})
    request = factory.get('/')
    request.user = self.product_owner
    response = view(request, user_id=self.developer.id)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data['effectiveness'], 'Insufficient data')

class DeveloperMetricsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.developer = User.objects.create_user(username='dev1', password='testpass')
        self.product_owner = User.objects.create_user(username='po1', password='testpass')
        self.client.force_authenticate(user=self.product_owner)

    def create_defect(self, assigned_to, status):
        return DefectReport.objects.create(
            ProductID="P001",
            Version="1.0",
            ReportTitle="Test Defect",
            Description="Test description",
            Steps="Step1\nStep2",
            TesterID="T001",
            Status=status,
            assigned_to=assigned_to
        )

    def test_insufficient_data(self):
        DeveloperMetrics.objects.create(user=self.developer, defects_fixed=15, defects_reopened=0)
        response = self.client.get(f'/defects/reports/developer-metrics/{self.developer.id}/')
        print("Status:", response.status_code)          # <-- add this
        print("Response data:", response.data)    
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['effectiveness'], 'Insufficient data')
        self.assertIsNone(response.data['ratio'])

    def test_good_rating(self):
        DeveloperMetrics.objects.create(user=self.developer, defects_fixed=100, defects_reopened=2)
        response = self.client.get(f'/defects/reports/developer-metrics/{self.developer.id}/')
        self.assertEqual(response.data['effectiveness'], 'Good')
        self.assertLess(response.data['ratio'], 1/32)

    def test_fair_rating(self):
        DeveloperMetrics.objects.create(user=self.developer, defects_fixed=100, defects_reopened=5)
        response = self.client.get(f'/defects/reports/developer-metrics/{self.developer.id}/')
        self.assertEqual(response.data['effectiveness'], 'Fair')
        self.assertGreaterEqual(response.data['ratio'], 1/32)
        self.assertLess(response.data['ratio'], 1/8)

    def test_poor_rating(self):
        DeveloperMetrics.objects.create(user=self.developer, defects_fixed=100, defects_reopened=20)
        response = self.client.get(f'/defects/reports/developer-metrics/{self.developer.id}/')
        self.assertEqual(response.data['effectiveness'], 'Poor')
        self.assertGreaterEqual(response.data['ratio'], 1/8)

    def test_signal_fixed_increment(self):
        defect = self.create_defect(self.developer, 'Assigned')
        metrics = DeveloperMetrics.objects.get(user=self.developer)
        self.assertEqual(metrics.defects_fixed, 0)
        defect.Status = 'Fixed'
        defect.save()
        metrics.refresh_from_db()
        self.assertEqual(metrics.defects_fixed, 1)

    def test_signal_reopened_increment(self):
        defect = self.create_defect(self.developer, 'Fixed')
        metrics = DeveloperMetrics.objects.get(user=self.developer)
        self.assertEqual(metrics.defects_reopened, 0)
        defect.Status = 'Reopened'
        defect.save()
        metrics.refresh_from_db()
        self.assertEqual(metrics.defects_reopened, 1)

    def test_user_not_found(self):
        response = self.client.get('/defects/reports/developer-metrics/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)