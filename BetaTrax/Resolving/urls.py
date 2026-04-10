from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import ResultViewSet
from . import views

router = DefaultRouter()
router.register(r'result', ResultViewSet, basename='api-results')

urlpatterns = [
    path('', views.ResultListView.as_view(), name='result-list'),
    path('<int:pk>/update/', views.update_retest_status, name='update-retest-status'),        
    path('api/', include(router.urls)),
]