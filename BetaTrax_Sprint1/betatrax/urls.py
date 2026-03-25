from django.urls import path, include
from . import views

urlpatterns = [
    # path('open/', views.open_defects_list, name='open_defects'),
    # path('take/<int:defect_id>/', views.take_defect, name='take_defect'),
    path('assigned/', views.assigned_defects_list, name='assigned_defects'),
    path('new/', views.new_defects_list, name='new_defects'),
    path('<int:pk>/status/', views.change_defect_status, name='change_defect_status'),
    path('api/', include("defects.urls")),
]
