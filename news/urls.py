from rest_framework.routers import DefaultRouter
from .viewsets import NewsViewSet


app_name = "news"
router = DefaultRouter()
router.register(r"news", NewsViewSet, "news")
urlpatterns = router.urls
