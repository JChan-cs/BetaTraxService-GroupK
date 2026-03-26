from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DefectReportViewSet

router = DefaultRouter()
router.register(r"reports", DefectReportViewSet)
urlpatterns = [
    path('',include(router.urls)),
    ]
