from typing import Dict, Any

from django.core.validators import RegexValidator
from rest_framework import serializers

from app_image.models import UserImage
from app_image.serializers import UserImageSerializer
from .models import CustomUser, Payment


class PaymentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Payment.

    Поля:
    - id: Целочисленный идентификатор платежа.
    - user: Идентификатор пользователя, совершившего платеж.
    - payment_date: Дата платежа.
    - paid_course: Оплаченный курс.
    - paid_lesson: Оплаченный урок.
    - amount: Сумма платежа.
    - payment_method: Метод оплаты.

    Настроена проверка, что в платеже обязательно должен быть указан либо курс, либо урок.
    """

    class Meta:
        model = Payment
        fields = ['id', 'user', 'payment_date', 'paid_course', 'paid_lesson', 'amount', 'payment_method']

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Проверяет валидность данных платежа.
        Если не указаны ни 'paid_course', ни 'paid_lesson' выкидывается исключение.
        В противном случае возвращает словарь с проверенными данными платежа.

        :param data: Словарь с данными платежа.
        """
        paid_course = data.get('paid_course')
        paid_lesson = data.get('paid_lesson')

        if not (paid_course or paid_lesson):
            raise serializers.ValidationError("Either 'paid_course' or 'paid_lesson' must be provided.")
        return data


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели CustomUser.

    Поля:
    - id: Целочисленный идентификатор пользователя.
    - email: Строка с адресом электронной почты пользователя.
    - first_name: Строка с именем пользователя.
    - last_name: Строка с фамилией пользователя.
    - phone: Строка с номером телефона пользователя.
    - city: Строка с городом пользователя.
    - avatar: Идентификатор аватара пользователя (ссылка на модель UserImage).
    - payments: Список платежей пользователя (ссылки на модель Payment).

    Настроена проверка номера телефона.
    Телефонный номер должен быть в формате: +7(9**)***-**-**
    """
    phone_regex = RegexValidator(
        regex=r'^\+7\(9\d{2}\)\d{3}-\d{2}-\d{2}$',
        message="Телефонный номер должен быть в формате: +7(9**)***-**-**"
    )
    phone = serializers.CharField(validators=[phone_regex])
    avatar = serializers.PrimaryKeyRelatedField(
        queryset=UserImage.get_all_user_images(),
        required=False,
        default=UserImage.get_all_user_images().first()
    )
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'city', 'avatar', 'payments']

    def to_representation(self, instance: CustomUser) -> Dict[str, Any]:
        """
        Преобразует экземпляр модели CustomUser в словарь.
        Возвращает словарь с представлением пользователя.

        :param instance: Экземпляр модели CustomUser.
        """
        user_out = super().to_representation(instance)
        user_out['avatar'] = UserImageSerializer(instance.avatar).data
        return user_out
