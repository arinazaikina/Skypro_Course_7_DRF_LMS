from typing import Any

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import View


class ProfilePermission(permissions.BasePermission):
    """
    Разрешения на просмотр профиля пользователя.

    Правила:
    - Авторизованный пользователь может просматривать любой профиль.
    - Пользователь может редактировать только свой профиль.
    """

    def has_permission(self, request: Request, view: View) -> bool:
        """
        Проверка общих прав доступа к представлению.

        :param request: Объект HttpRequest.
        :param view: Объект View.
        """
        return request.method in ['GET', 'PUT', 'PATCH']

    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        """
        Проверка прав на конкретный объект.

        :param request: Объект HttpRequest.
        :param view: Объект View.
        :param obj: Объект, для которого проверяется разрешение.
        """
        if request.method == 'GET':
            return True

        return request.user == obj


class PaymentPermission(permissions.BasePermission):
    """
    Разрешение на просмотр платежей.

    Правила:
    - Модератор может просматривать все платежи.
    - Пользователи могут просматривать только свои платежи.
    - Авторизованные пользователи могут создавать платежи.
    """

    def has_permission(self, request: Request, view: View) -> bool:
        """
        Проверка общих прав доступа к представлению.

        :param request: Объект HttpRequest.
        :param view: Объект View.
        """
        if request.method in ['GET', 'POST']:
            return True
        return False

    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        """
        Проверка прав на конкретный объект.

        :param request: Объект HttpRequest.
        :param view: Объект View.
        :param obj: Объект, для которого проверяется разрешение.
        """
        if request.method == 'GET':
            return obj.user == request.user or request.user.is_staff
        return False
