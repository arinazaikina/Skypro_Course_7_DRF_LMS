from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from .filters import PaymentFilter
from .models import CustomUser, Payment
from .permissions import ProfilePermission, PaymentPermission
from .serializers import CustomUserSerializer, PaymentSerializer, RegisterUserSerializer


class UserRegisterView(generics.CreateAPIView):
    queryset = CustomUser.get_all_users()
    permission_classes = (AllowAny,)
    serializer_class = RegisterUserSerializer


class UserListAPIView(generics.ListAPIView):
    queryset = CustomUser.get_all_users()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated, ProfilePermission]


class UserRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.get_all_users()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated, ProfilePermission]


class PaymentListCreateView(generics.ListCreateAPIView):
    queryset = Payment.get_all_payments()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ['payment_date']
    permission_classes = [IsAuthenticated, PaymentPermission]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('paid_course', openapi.IN_QUERY, description="Оплаченный курс", type=openapi.TYPE_INTEGER),
        openapi.Parameter('paid_lesson', openapi.IN_QUERY, description="Оплаченный урок", type=openapi.TYPE_INTEGER),
        openapi.Parameter('payment_method', openapi.IN_QUERY, description="Способ оплаты", type=openapi.TYPE_STRING),
        openapi.Parameter('ordering', openapi.IN_QUERY, description="Сортировка по дате", type=openapi.TYPE_STRING),
    ])
    def list(self, request: Request, *args, **kwargs) -> Response:
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        """
        Возвращает платежи, которые должны быть отображены для текущего пользователя.

        Если пользователь является модератором (is_staff=True), возвращает все платежи.
        Если пользователь не является модератором, возвращает только те платежии,
        которые были созданы этим пользователем.
        """
        user = self.request.user
        if user.is_staff:
            return Payment.get_all_payments()
        return Payment.get_all_payments().filter(user=user)

    def perform_create(self, serializer: Serializer) -> None:
        """
        Сохраняет новый объект при помощи сериализатора,
        устанавливая атрибут 'user' как текущий пользователь.

        :param serializer: Сериализатор для сохранения объекта.
        """
        serializer.save(user=self.request.user)


class PaymentRetrieveView(generics.RetrieveAPIView):
    queryset = Payment.get_all_payments()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, PaymentPermission]
