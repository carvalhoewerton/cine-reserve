from rest_framework.routers import DefaultRouter

from apps.room.views import RoomViewSet

router = DefaultRouter()
router.register(r'rooms', RoomViewSet, basename='room')

urlpatterns = router.urls