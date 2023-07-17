from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet,
    LessonListCreateAPIView,
    LessonRetrieveUpdateDestroyAPIView,
    SubscriptionCreateView,
    SubscriptionDeleteView
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')

urlpatterns = [
    path('', include(router.urls)),
    path('lessons/', LessonListCreateAPIView.as_view(), name='lesson-list'),
    path('lessons/<int:pk>/', LessonRetrieveUpdateDestroyAPIView.as_view(), name='lesson-detail'),
    path('course-subscriptions/', SubscriptionCreateView.as_view(), name='course_subscription_create'),
    path('course-unsubscribe/', SubscriptionDeleteView.as_view(), name='course_subscription_delete')
]
