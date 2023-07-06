from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, generics
from rest_framework.filters import OrderingFilter
from rest_framework.request import Request
from rest_framework.response import Response

from .filters import PaymentFilter
from .models import CustomUser, Payment
from .serializers import CustomUserSerializer, PaymentSerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class PaymentListCreateView(generics.ListCreateAPIView):
    queryset = Payment.get_all_payments()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ['payment_date']

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('paid_course', openapi.IN_QUERY, description="Оплаченный курс", type=openapi.TYPE_INTEGER),
        openapi.Parameter('paid_lesson', openapi.IN_QUERY, description="Оплаченный урок", type=openapi.TYPE_INTEGER),
        openapi.Parameter('payment_method', openapi.IN_QUERY, description="Способ оплаты", type=openapi.TYPE_STRING),
        openapi.Parameter('ordering', openapi.IN_QUERY, description="Сортировка по дате", type=openapi.TYPE_STRING),
    ])
    def list(self, request: Request, *args, **kwargs) -> Response:
        return super().list(request, *args, **kwargs)


class PaymentRetrieveView(generics.RetrieveAPIView):
    queryset = Payment.get_all_payments()
    serializer_class = PaymentSerializer
