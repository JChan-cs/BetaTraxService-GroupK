from django.urls import path, include
from . import views

urlpatterns = [
    # path('open/', views.open_defects_list, name='open_defects'),
    # path('take/<int:defect_id>/', views.take_defect, name='take_defect'),
    path('assigned/', views.assigned_defects_list, name='assigned_defects'),
    path('new/', views.new_defects_list, name='new_defects'),
    path('<int:pk>/fix/', views.fix_defect, name='fix_defect'),
    path('<int:pk>/resolve/', views.resolve_defect, name='resolve_defect'),
    path('api/', include("defects.urls")),
]
