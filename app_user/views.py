from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .filters import PaymentFilter
from .models import CustomUser, Payment
from .permissions import ProfilePermission, PaymentPermission
from .serializers import (
    CustomUserSerializer,
    PaymentSerializer,
    RegisterUserSerializer,
    PaymentIntentCreateSerializer,
    PaymentMethodCreateSerializer,
    PaymentIntentConfirmSerializer,
)
from .services import StripeService


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


class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ['payment_date']
    permission_classes = [IsAuthenticated, PaymentPermission]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('paid_course', openapi.IN_QUERY, description="Оплаченный курс", type=openapi.TYPE_INTEGER),
        openapi.Parameter('ordering', openapi.IN_QUERY, description="Сортировка по дате", type=openapi.TYPE_STRING),
    ])
    def list(self, request: Request, *args, **kwargs) -> Response:
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        """
        Возвращает платежи, которые должны быть отображены для текущего пользователя.

        Если пользователь является модератором (is_staff=True), возвращает все платежи.
        Если пользователь не является модератором, возвращает только те платежи,
        которые были созданы этим пользователем.
        """
        user = self.request.user
        if user.is_staff:
            return Payment.get_all_payments()
        return Payment.get_all_payments().filter(user=user)


class PaymentRetrieveView(generics.RetrieveAPIView):
    queryset = Payment.get_all_payments()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, PaymentPermission]


class PaymentIntentCreateView(generics.CreateAPIView):
    serializer_class = PaymentIntentCreateSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            201: openapi.Response('Payment successful', PaymentSerializer),
            400: 'Payment failed'
        }
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        """Создает платежное намерение"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            course_id = serializer.validated_data['course_id']
            user = request.user
            try:
                payment_intent = StripeService.create_payment_intent(course_id, user)
                payment = Payment.get_by_payment_intent_id(payment_intent_id=payment_intent['id'])
                payment_serializer = PaymentSerializer(payment)
                return Response(payment_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as error:
                return Response({'error': str(error)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentMethodCreateView(generics.CreateAPIView):
    serializer_class = PaymentMethodCreateSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            201: openapi.Response('Payment method creation successful', PaymentSerializer),
            400: 'Payment method creation failed'
        }
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        """Создает способ платежа"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            payment_intent_id = serializer.validated_data['payment_intent_id']
            payment_token = serializer.validated_data['payment_token']
            try:
                StripeService.create_and_attach_payment_method(payment_intent_id, payment_token)
                payment = Payment.get_by_payment_intent_id(payment_intent_id=payment_intent_id)
                payment_serializer = PaymentSerializer(payment)
                return Response(payment_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as error:
                return Response({'error': str(error)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentIntentConfirmView(generics.CreateAPIView):
    serializer_class = PaymentIntentConfirmSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            201: openapi.Response('Payment intent confirmation successful', PaymentSerializer),
            400: 'Payment intent confirmation failed'
        }
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        """Создает подтверждение платежа"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            payment_intent_id = serializer.validated_data['payment_intent_id']
            try:
                StripeService.confirm_payment_intent(payment_intent_id)
                payment = Payment.get_by_payment_intent_id(payment_intent_id=payment_intent_id)
                payment_serializer = PaymentSerializer(payment)
                return Response(payment_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as error:
                return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
