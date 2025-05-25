from rest_framework.routers import DefaultRouter
from .views import MachineViewSet, MaintenanceViewSet, ClaimViewSet, DirectoryViewSet

router = DefaultRouter()
router.register(r'machines', MachineViewSet, basename='machine')
router.register(r'maintenances', MaintenanceViewSet, basename='maintenance')
router.register(r'claims', ClaimViewSet, basename='claim')
router.register(r'directories', DirectoryViewSet, basename='directory')

urlpatterns = router.urls
