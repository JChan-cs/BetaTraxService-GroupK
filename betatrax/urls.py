from django.urls import path
from . import views

urlpatterns = [
    path('open/', views.open_defects_list, name='open_defects'),
    path('take/<int:defect_id>/', views.take_defect, name='take_defect'),
    path('assigned/', views.assigned_defects_list, name='assigned_defects'),
]