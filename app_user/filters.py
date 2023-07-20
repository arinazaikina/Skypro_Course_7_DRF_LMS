import django_filters

from .models import Payment


class PaymentFilter(django_filters.FilterSet):
    """
    Класс фильтров для модели Payment.

    Фильтры:
    - paid_course: Числовой фильтр по полю "paid_course" (оплаченный курс).
    """
    paid_course = django_filters.NumberFilter(field_name="paid_course")

    class Meta:
        model = Payment
        fields = ['paid_course']
