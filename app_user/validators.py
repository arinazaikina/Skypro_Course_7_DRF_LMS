import re

from django.core.exceptions import ValidationError


class PhoneValidator:
    phone_regex = r'^\+7\(9\d{2}\)\d{3}-\d{2}-\d{2}$'
    message = "Телефонный номер должен быть в формате: +7(9**)***-**-**"

    def __call__(self, value):
        """
        Проверяет, соответствует ли номер телефона формату '+7(9**)***-**-**'
        """
        if not re.match(self.phone_regex, value):
            raise ValidationError(message=self.message)
