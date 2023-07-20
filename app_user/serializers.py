from typing import Dict, Any

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from app_course.models import Course
from app_image.models import UserImage
from app_image.serializers import UserImageSerializer
from .models import CustomUser, Payment
from .validators import PhoneValidator


class PaymentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Payment.

    Поля:
    - id: Целочисленный идентификатор платежа.
    - payment_intent_id: ID намерения платежа в сервисе Stripe
    - payment_method_id: ID метода платежа в сервисе Stripe
    - user: Идентификатор и email пользователя, совершившего платеж.
    - payment_date: Дата платежа.
    - paid_course: Оплаченный курс.
    - amount: Сумма платежа.
    - status: Статус платежа в сервисе Stripe.
    - is_confirmed: Платеж подтвержден
    """
    user = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = ['id', 'payment_intent_id', 'payment_method_id', 'user', 'payment_date', 'paid_course', 'amount',
                  'status', 'is_confirmed']

    @staticmethod
    def get_user(instance: Payment) -> Dict[str, Any]:
        """
        Возвращает информацию о создателе платежа (ID пользователя и почту).

        :param instance: Экземпляр модели Lesson.
        """
        user = instance.user
        return {
            'id': user.id,
            'email': user.email
        }


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

    Поле avatar не является обязательным для заполнения.
    """
    email = serializers.EmailField(read_only=True)
    avatar = serializers.PrimaryKeyRelatedField(
        queryset=UserImage.get_all_user_images(),
        required=False
    )
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'city', 'avatar', 'payments']

    def to_representation(self, instance: CustomUser) -> Dict[str, Any]:
        """
        Преобразует экземпляр модели CustomUser в словарь.
        Возвращает словарь с представлением пользователя.
        Если пользователь просматривает свой профиль, ему доступны все данные
        для просмотра.
        Если пользователь просматривает чужой профиль, он не видит
        фамилию и историю платежей.

        :param instance: Экземпляр модели CustomUser.
        """
        current_user = self.context['request'].user

        if current_user == instance:
            user_out = super().to_representation(instance)
            user_out['avatar'] = UserImageSerializer(instance.avatar).data
        else:
            user_out = super().to_representation(instance)
            user_out['avatar'] = UserImageSerializer(instance.avatar).data
            user_out.pop('last_name', None)
            user_out.pop('payments', None)

        return user_out


class RegisterUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации нового пользователя.

    Поля:
    - email: Строка с адресом электронной почты пользователя.
    - password: Строка с паролем пользователя.
    - password2: Строка с подтверждением пароля пользователя.
    - first_name: Строка с именем пользователя.
    - last_name: Строка с фамилией пользователя.
    - phone: Строка с номером телефона пользователя.
    - city: Строка с городом пользователя.

    Настроена проверка номера телефона.
    Телефонный номер должен быть в формате: +7(9**)***-**-**
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    phone = serializers.CharField(validators=[PhoneValidator()])

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'password', 'password2', 'first_name', 'last_name', 'phone', 'city']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Проверяет валидность данных сериализатора.
        Возвращает входные данные сериализатора после проверки валидности.

        :param attrs: Входные данные сериализатора.
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})

        return attrs

    def create(self, validated_data: Dict[str, Any]) -> CustomUser:
        """
        Создает новый экземпляр модели CustomUser с переданными данными.
        Устанавливает пароль пользователя.
        Сохраняет пользователя в базе данных.

        :param validated_data: Валидированные данные сериализатора.
        """
        user = CustomUser.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone=validated_data['phone'],
            city=validated_data['city']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class PaymentIntentCreateSerializer(serializers.Serializer):
    """
    Сериализатор для создания платежного намерения.

    Поля:
    - course_id: ID курса, который необходимо оплатить.
    """
    course_id: int = serializers.IntegerField()

    @staticmethod
    def validate_course_id(value: int) -> int:
        """
        Проверяет, существует ли курс с указанным ID.
        Если курс с указанным ID существует, то возвращает ID курса.

        :param value: ID курса
        """
        course = Course.get_by_id(course_id=value)
        if not course:
            raise serializers.ValidationError(f'Курс с ID {value} не найден.')
        return value


class PaymentMethodCreateSerializer(serializers.Serializer):
    """
    Сериализатор для создания платежного метода.

    Поля:
    - payment_intent_id: ID платежного намерения в системе Stripe.
    - payment_token: токен платежного метода в системе Stripe.
    """
    payment_intent_id: str = serializers.CharField(max_length=255)
    payment_token: str = serializers.CharField(max_length=255)

    def validate(self, data: Dict[str, str]) -> Dict[str, str]:
        """
        Проверяет существование платежа с указанным ID намерения платежа.
        Проверяет не является ли этот платеж уже подтвержденным.
        При успешной валидации возвращает словарь с данными.
        :param data: Входные данные.
        """
        payment_intent_id = data.get('payment_intent_id')
        payment = Payment.get_by_payment_intent_id(payment_intent_id)
        if payment is None:
            raise serializers.ValidationError(f"Платеж с ID {payment_intent_id} не найден")
        if payment.is_confirmed:
            raise serializers.ValidationError(f"Платеж с ID {payment_intent_id} уже подтвержден")
        return data


class PaymentIntentConfirmSerializer(serializers.Serializer):
    """
    Сериализатор для подтверждения платежа.

    Поля:
    - payment_intent_id: ID платежного намерения в системе Stripe.
    """
    payment_intent_id = serializers.CharField(max_length=255)

    def validate(self, data: Dict[str, str]) -> Dict[str, str]:
        """
        Проверяет существование платежа с указанным ID намерения платежа.
        Проверяет привязан ли к платежу способ оплаты.
        Проверяет не является ли этот платеж уже подтвержденным.
        При успешной валидации возвращает словарь с данными.
        :param data: Входные данные.
        """
        payment_intent_id = data.get('payment_intent_id')
        payment = Payment.get_by_payment_intent_id(payment_intent_id)
        if payment is None:
            raise serializers.ValidationError(f"Платеж с ID {payment_intent_id} не найден")
        if payment.payment_method_id is None:
            raise serializers.ValidationError(f"К платежу с ID {payment_intent_id} не привязан ни один способ оплаты")
        if payment.is_confirmed:
            raise serializers.ValidationError(f"Платеж с ID {payment_intent_id} уже подтвержден")
        return data
