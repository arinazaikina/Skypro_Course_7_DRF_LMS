from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response

from .models import LessonImage, CourseImage, UserImage
from .serializers import LessonImageSerializer, CourseImageSerializer, UserImageSerializer


class BaseImageViewSet(viewsets.ModelViewSet):
    """
    Базовый класс для представлений изображений.

    Attrs:
        - parser_classes: Список парсеров, используемых для обработки запросов с изображениями.
    """
    parser_classes = [MultiPartParser]

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """
        Удалить дефолтное изображение (pk = 1) нельзя.
        """
        instance = self.get_object()
        if instance.id == 1:
            return Response(status=status.HTTP_403_FORBIDDEN,
                            data={'message': 'Deleting image with id 1 is not allowed.'})
        return super().destroy(request, *args, **kwargs)


class LessonImageViewSet(BaseImageViewSet):
    queryset = LessonImage.get_all_lesson_images()
    serializer_class = LessonImageSerializer


class CourseImageViewSet(BaseImageViewSet):
    queryset = CourseImage.get_all_course_images()
    serializer_class = CourseImageSerializer


class UserImageViewSet(BaseImageViewSet):
    queryset = UserImage.get_all_user_images()
    serializer_class = UserImageSerializer
