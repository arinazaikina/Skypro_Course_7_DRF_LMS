from typing import Dict, Any

import requests
from django.conf import settings

from app_course.models import Course
from app_user.models import Payment, CustomUser


class StripeService:
    """
    Класс, описывающий работу с сервисом Stripe.
    Attrs:
        - api_key: Ключ для работы с API Stripe.
        - headers: Заголовки.
        - base_url: Базовый URL.
    """
    api_key = settings.STRIPE_API_KEY
    headers = {'Authorization': f'Bearer {api_key}'}
    base_url = 'https://api.stripe.com/v1'

    @classmethod
    def create_payment_intent(cls, course_id: int, user: CustomUser) -> Dict[str, Any]:
        """
        Создает платежное намерение и возвращает его данные.

        :param course_id: ID курса, который необходимо оплатить.
        :param user: Пользователь, совершающий платеж.
        """
        course = Course.get_by_id(course_id)
        amount = int(course.cost)

        data = [
            ('amount', amount * 100),
            ('currency', 'rub'),
            ('metadata[course_id]', course.id),
            ('metadata[user_id]', user.id)
        ]

        response = requests.post(f'{cls.base_url}/payment_intents', headers=cls.headers, data=data)

        if response.status_code != 200:
            raise Exception(f'Ошибка создания намерения платежа: {response.json()["error"]["message"]}')

        payment_intent = response.json()

        Payment.objects.create(
            user=user,
            paid_course=course,
            amount=course.cost,
            payment_intent_id=payment_intent['id'],
            status=payment_intent['status']
        )

        return payment_intent

    @classmethod
    def create_payment_method(cls, payment_token: str) -> Dict[str, Any]:
        """
        Создает способ платежа и возвращает его данные.

        :param payment_token: Токен платежа.
        """
        data = {
            'type': 'card',
            'card[token]': payment_token,
        }

        response = requests.post(f'{cls.base_url}/payment_methods', headers=cls.headers, data=data)
        payment_method = response.json()
        if response.status_code != 200:
            raise Exception(f'Ошибка создания способа платежа: {payment_method["error"]["message"]}')

        return payment_method

    @classmethod
    def attach_payment_method_to_intent(cls, payment_intent_id: str, payment_method_id: str) -> Dict[str, Any]:
        """
        Привязывает способ платежа к намерению платежа и возвращает данные ответа.

        :param payment_intent_id: ID намерения платежа.
        :param payment_method_id: ID способа платежа.
        """
        url = f'{cls.base_url}/payment_intents/{payment_intent_id}'
        data = {'payment_method': payment_method_id}
        response = requests.post(url, headers=cls.headers, data=data)
        response_data = response.json()

        if response.status_code != 200:
            raise Exception(f'Ошибка привязки метода платежа: {response_data["error"]["message"]}')

        payment = Payment.get_by_payment_intent_id(payment_intent_id)
        payment.status = response_data['status']
        payment.save()

        return response_data

    @classmethod
    def create_and_attach_payment_method(cls, payment_intent_id: str, payment_token: str) -> Dict[str, Any]:
        """
        Создает и привязывает способ платежа к намерению платежа и возвращает данные способа платежа.

        :param payment_intent_id: ID намерения платежа.
        :param payment_token: Токен платежа.
        :return: Данные способа платежа.
        """
        payment_method = cls.create_payment_method(payment_token)
        payment = Payment.get_by_payment_intent_id(payment_intent_id)
        payment.payment_method_id = payment_method['id']
        payment.save()

        cls.attach_payment_method_to_intent(payment_intent_id, payment_method['id'])
        return payment_method

    @classmethod
    def confirm_payment_intent(cls, payment_intent_id: str) -> Dict[str, Any]:
        """
        Подтверждает намерение платежа и возвращает данные ответа.

        :param payment_intent_id: ID намерения платежа.
        """
        payment = Payment.get_by_payment_intent_id(payment_intent_id)

        url = f'{cls.base_url}/payment_intents/{payment_intent_id}/confirm'
        data = {'payment_method': payment.payment_method_id}
        response = requests.post(url, headers=cls.headers, data=data)
        response_data = response.json()

        if response.status_code != 200:
            raise Exception(f'Ошибка подтверждения платежа: {response_data["error"]["message"]}')

        payment.status = response_data['status']
        payment.save()

        return response_data

    @classmethod
    def retrieve_payment_intent(cls, payment_intent_id: str) -> Dict[str, Any]:
        """
        Получает информацию о намерении платежа и возвращает его данные.

        :param payment_intent_id: ID намерения платежа.
        """
        url = f'{cls.base_url}/payment_intents/{payment_intent_id}'
        response = requests.get(url, headers=cls.headers)
        response_data = response.json()

        if response_data.get('error'):
            raise Exception(f'{response_data["error"]["message"]}')
        return response.json()

    @classmethod
    def confirm_payment(cls, payment_intent_id: str) -> None:
        """
        Подтверждает платеж с указанным ID намерения платежа.

        :param payment_intent_id: ID намерения платежа
        """
        payment = Payment.get_by_payment_intent_id(payment_intent_id)
        payment_intent = cls.retrieve_payment_intent(payment_intent_id)

        if payment_intent['status'] == 'succeeded' and payment:
            payment.confirm_payment()
