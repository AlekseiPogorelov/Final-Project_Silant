from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'machines', views.MachineViewSet)
router.register(r'maintenances', views.MaintenanceViewSet)
router.register(r'claims', views.ClaimViewSet)
router.register(r'directories', views.DirectoryViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/public_machine_search/', views.public_machine_search, name='api_public_machine_search'),
    path('machines/<int:pk>/', views.machine_detail, name='machine_detail'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.public_search_page, name='public_search_page'),
    path('machines/add/', views.machine_create, name='machine_add'),
    path('machines/<int:pk>/edit/', views.machine_update, name='machine_edit'),
    path('maintenances/add/', views.maintenance_create, name='maintenance_add'),
    path('maintenances/<int:pk>/edit/', views.maintenance_update, name='maintenance_edit'),
    path('claims/add/', views.claim_create, name='claim_add'),
    path('claims/<int:pk>/edit/', views.claim_update, name='claim_edit'),
    path('maintenance/<int:pk>/', views.maintenance_detail, name='maintenance_detail'),
    path('claim/<int:pk>/', views.claim_detail, name='claim_detail'),
]
