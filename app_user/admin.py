from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Payment


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Класс, описывающий модель CustomUser в административном интерфейсе.
    """

    model = CustomUser
    list_display = ['pk', 'email', 'first_name', 'last_name', 'is_active']
    list_display_links = ['pk', 'email']
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'phone', 'city', 'avatar')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    readonly_fields = ('last_login', 'date_joined')

    def get_fieldsets(self, request, obj=None):
        """
        Возвращает кортеж кортежей, определяющих расположение полей на форме.
        """
        if not obj:
            fieldsets = (
                (None, {'fields': ('email', 'password1', 'password2')}),
                ('Персональная информация', {'fields': ('first_name', 'last_name', 'phone', 'city', 'avatar')}),
            )
        else:
            fieldsets = (
                (None, {'fields': ('email',)}),
                ('Персональная информация', {'fields': ('first_name', 'last_name', 'phone', 'city', 'avatar')}),
                ('Разрешения', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
                ('Важные даты', {'fields': ('last_login', 'date_joined')}),
            )
        return fieldsets


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    model = Payment
    list_display = ['pk', 'user', 'payment_date', 'paid_course', 'paid_lesson', 'amount', 'payment_method']
    list_display_links = ['pk']
