# Generated by Django 4.2 on 2023-07-20 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_course', '0003_course_cost'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Время обновления'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Время обновления'),
        ),
    ]
