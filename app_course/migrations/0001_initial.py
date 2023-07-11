# Generated by Django 4.2 on 2023-07-10 17:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('app_image', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('description', models.TextField(verbose_name='Описание')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_course.course', verbose_name='Создано пользователем')),
                ('preview', models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='courses', to='app_image.courseimage', verbose_name='Превью')),
            ],
            options={
                'verbose_name': 'Курс',
                'verbose_name_plural': 'Курсы',
                'db_table': 'courses',
            },
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Название')),
                ('description', models.TextField(verbose_name='Описание')),
                ('video_url', models.URLField(verbose_name='Ссылка на видео')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='app_course.course', verbose_name='Курс')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_course.course', verbose_name='Создано пользователем')),
                ('preview', models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='lessons', to='app_image.lessonimage', verbose_name='Превью')),
            ],
            options={
                'verbose_name': 'Урок',
                'verbose_name_plural': 'Уроки',
                'db_table': 'lessons',
            },
        ),
    ]
