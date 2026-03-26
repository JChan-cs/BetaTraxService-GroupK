from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .view import DefectReportViewSet

router = DefaultRouter()
router.register(r"reports", DefectReportViewSet)
urlpatterns = [
    path('',include(router.urls)),
    ]
