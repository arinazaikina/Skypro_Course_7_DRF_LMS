from typing import Any

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import View


class CustomPermission(permissions.BasePermission):
    """
    Проверка прав на объекты Course и Lesson.

    Правила:
    - Все авторизованные пользователи, кроме модераторов (is_staff=True), могут создавать объекты.
    - Владельцы объектов могут просматривать и редактировать только свои объекты.
    - Модераторы (is_staff=True) могут просматривать и редактировать все объекты, но не могут их удалять или создавать.
    """

    def has_permission(self, request: Request, view: View) -> bool:
        """
        Проверка общих прав доступа к представлению.

        :param request: Объект HttpRequest.
        :param view: Объект View.
        """
        # Запрещаем модераторам создавать и удалять объекты
        if request.user.is_staff and request.method in ['POST', 'DELETE']:
            return False

        return True

    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        """
        Проверка прав на конкретный объект.

        :param request: Объект HttpRequest.
        :param view: Объект View.
        :param obj: Объект, для которого проверяется разрешение.
        """
        # Модераторы могут просматривать и редактировать все объекты
        if request.user.is_staff:
            return request.method in ['GET', 'PUT', 'PATCH']

        # Владельцы объектов могут просматривать, редактировать и удалять только свои объекты
        if request.user == obj.created_by:
            return request.method in ['GET', 'PUT', 'PATCH', 'DELETE']

        return False
