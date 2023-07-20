from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    UserRegisterView,
    UserListAPIView,
    UserRetrieveUpdateDestroyAPIView,
    PaymentListView,
    PaymentRetrieveView,
    PaymentIntentCreateView,
    PaymentMethodCreateView,
    PaymentIntentConfirmView
)

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('users/', UserListAPIView.as_view(), name='user_list'),
    path('users/<int:pk>/', UserRetrieveUpdateDestroyAPIView.as_view(), name='user_detail'),
    path('payments/', PaymentListView.as_view(), name='payment_list'),
    path('payments/<int:pk>/', PaymentRetrieveView.as_view(), name='payment_detail'),
    path('payments/create/', PaymentIntentCreateView.as_view(), name='payment_create'),
    path('payments/method/create', PaymentMethodCreateView.as_view(), name='payment_method_create'),
    path('payments/confirm/', PaymentIntentConfirmView.as_view(), name='payments_confirm'),
]
