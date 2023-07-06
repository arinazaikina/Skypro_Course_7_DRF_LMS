from django.contrib import admin

from .models import CourseImage, LessonImage, UserImage


@admin.register(CourseImage)
class CourseImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'image']
    list_display_links = ['image']


@admin.register(LessonImage)
class LessonImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'image']
    list_display_links = ['image']


@admin.register(UserImage)
class UserImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'image']
    list_display_links = ['image']
