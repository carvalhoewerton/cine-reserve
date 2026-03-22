from rest_framework.routers import DefaultRouter
from apps.movie.views import MovieViewSet

router = DefaultRouter()
router.register(r'movies', MovieViewSet, basename='movie')

urlpatterns = router.urls