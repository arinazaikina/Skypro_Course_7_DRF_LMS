from urllib.parse import urlparse

from django.core.exceptions import ValidationError


class YouTubeUrlValidator:

    def __init__(self, field: str):
        """
        Инициализатор для YoutubeUrlValidator.

        :param field: Имя поля модели, которое следует проверить.
        """
        self.field = field

    def __call__(self, value: dict) -> None:
        """
        Проверяет, является ли URL в указанном поле ссылкой на youtube.com.
        Если нет, вызывается исключение ValidationError.

        :param value: URL для проверки.
        """
        url = value.get(self.field)
        domain_name = urlparse(url).netloc

        if "youtube.com" not in domain_name:
            raise ValidationError(f'{url} не является ссылкой на YouTube')
