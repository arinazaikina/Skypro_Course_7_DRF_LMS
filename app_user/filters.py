import django_filters

from .models import Payment


class PaymentFilter(django_filters.FilterSet):
    """
    Класс фильтров для модели Payment.

    Фильтры:
    - paid_course: Числовой фильтр по полю "paid_course" (оплаченный курс).
    - paid_lesson: Числовой фильтр по полю "paid_lesson" (оплаченный урок).
    - payment_method: Фильтр по полю "payment_method" (метод оплаты).
    """
    paid_course = django_filters.NumberFilter(field_name="paid_course")
    paid_lesson = django_filters.NumberFilter(field_name="paid_lesson")
    payment_method = django_filters.CharFilter(field_name="payment_method")

    class Meta:
        model = Payment
        fields = ['paid_course', 'paid_lesson', 'payment_method']
