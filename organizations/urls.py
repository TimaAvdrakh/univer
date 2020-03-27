from rest_framework.routers import DefaultRouter
from .views import *

app_name = "organizations"
router = DefaultRouter()
router.register(r"prep-levels", PreparationLevelViewSet, "prep_levels")
router.register(r"study-forms", StudyFormViewSet)
urlpatterns = router.urls
