from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import CommentViewSet
from . import views

router = DefaultRouter()
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('', views.CommentListView.as_view(), name='comment-list'),       
    path('<int:pk>/', views.CommentDetailView.as_view(), name='comment-detail'),  
]