from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from defects.models import DefectReport, DeveloperMetrics
from defects.developer_metrics import (
    classify_effectiveness,
    build_metrics_response,
    apply_status_transition_metrics,
)

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
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['effectiveness'], 'Insufficient data')
        self.assertIsNone(response.data['ratio'])

    def test_insufficient_data_at_boundary_fixed_19(self):
        DeveloperMetrics.objects.create(user=self.developer, defects_fixed=19, defects_reopened=0)
        response = self.client.get(f'/defects/reports/developer-metrics/{self.developer.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['effectiveness'], 'Insufficient data')
        self.assertIsNone(response.data['ratio'])

    def test_good_rating(self):
        DeveloperMetrics.objects.create(user=self.developer, defects_fixed=100, defects_reopened=2)
        response = self.client.get(f'/defects/reports/developer-metrics/{self.developer.id}/')
        self.assertEqual(response.data['effectiveness'], 'Good')
        self.assertLess(response.data['ratio'], 1/32)

    def test_ratio_equal_one_over_32_is_fair(self):
        DeveloperMetrics.objects.create(user=self.developer, defects_fixed=32, defects_reopened=1)
        response = self.client.get(f'/defects/reports/developer-metrics/{self.developer.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['effectiveness'], 'Fair')
        self.assertEqual(response.data['ratio'], 0.03125)

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

    def test_ratio_equal_one_over_8_is_poor(self):
        DeveloperMetrics.objects.create(user=self.developer, defects_fixed=40, defects_reopened=5)
        response = self.client.get(f'/defects/reports/developer-metrics/{self.developer.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['effectiveness'], 'Poor')
        self.assertEqual(response.data['ratio'], 0.125)

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

    def test_signal_reopened_increment_uses_old_assignee_when_cleared(self):
        defect = self.create_defect(self.developer, 'Fixed')
        metrics = DeveloperMetrics.objects.get(user=self.developer)
        self.assertEqual(metrics.defects_reopened, 0)

        # Mirrors serializer behavior for Fixed -> Reopened transition.
        defect.Status = 'Reopened'
        defect.assigned_to = None
        defect.save()

        metrics.refresh_from_db()
        self.assertEqual(metrics.defects_reopened, 1)

    def test_signal_fixed_ignored_when_no_assignee(self):
        defect = self.create_defect(None, 'Open')
        defect.Status = 'Reopened'
        defect.save()
        self.assertEqual(DeveloperMetrics.objects.count(), 0)

    def test_signal_unchanged_status_does_not_increment(self):
        defect = self.create_defect(self.developer, 'Assigned')
        metrics = DeveloperMetrics.objects.get(user=self.developer)
        self.assertEqual(metrics.defects_fixed, 0)
        self.assertEqual(metrics.defects_reopened, 0)

        defect.ReportTitle = 'Updated title only'
        defect.save()

        metrics.refresh_from_db()
        self.assertEqual(metrics.defects_fixed, 0)
        self.assertEqual(metrics.defects_reopened, 0)

    def test_classify_effectiveness_helper(self):
        self.assertEqual(classify_effectiveness(19, 0), ('Insufficient data', None))
        self.assertEqual(classify_effectiveness(64, 1), ('Good', 0.015625))
        self.assertEqual(classify_effectiveness(32, 1), ('Fair', 0.03125))
        self.assertEqual(classify_effectiveness(40, 5), ('Poor', 0.125))
        self.assertEqual(classify_effectiveness(40, 6), ('Poor', 0.15))

    def test_build_metrics_response_helper(self):
        payload = build_metrics_response(self.developer, defects_fixed=100, defects_reopened=5)
        self.assertEqual(payload['user_id'], self.developer.id)
        self.assertEqual(payload['username'], self.developer.username)
        self.assertEqual(payload['effectiveness'], 'Fair')
        self.assertEqual(payload['ratio'], 0.05)

    def test_apply_status_transition_metrics_fixed_without_assignee(self):
        class DummyDefect:
            Status = 'Fixed'
            assigned_to = None

        apply_status_transition_metrics(instance=DummyDefect(), old_status='Assigned', old_assigned_to=None)
        self.assertEqual(DeveloperMetrics.objects.count(), 0)

    def test_user_not_found(self):
        response = self.client.get('/defects/reports/developer-metrics/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)