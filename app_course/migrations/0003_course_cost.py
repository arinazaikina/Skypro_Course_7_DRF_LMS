# Generated by Django 4.2 on 2023-07-17 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_course', '0002_alter_course_created_by_alter_lesson_created_by_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='cost',
            field=models.DecimalField(decimal_places=2, default=50000, max_digits=10, verbose_name='Стоимость курса'),
        ),
    ]