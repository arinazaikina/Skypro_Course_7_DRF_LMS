from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import LessonImageViewSet, CourseImageViewSet, UserImageViewSet

router = DefaultRouter()
router.register(r'lesson-images', LessonImageViewSet, basename='lesson-images')
router.register(r'course-images', CourseImageViewSet, basename='course-images')
router.register(r'user-images', UserImageViewSet, basename='user-images')

urlpatterns = [
    path('', include(router.urls)),
]
