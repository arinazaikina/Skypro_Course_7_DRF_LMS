from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet, PaymentListCreateView, PaymentRetrieveView

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('payments/', PaymentListCreateView.as_view(), name='payment-list-create'),
    path('payments/<int:pk>/', PaymentRetrieveView.as_view(), name='payment_detail'),
]
