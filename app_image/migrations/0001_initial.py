# Generated by Django 4.2 on 2023-07-10 17:04

from django.db import migrations, models


def create_default_course_image(apps, schema_editor):
    CourseImage = apps.get_model('app_image', 'CourseImage')
    default_image = 'courses/default.png'
    CourseImage.objects.create(image=default_image)


def create_default_lesson_image(apps, schema_editor):
    LessonImage = apps.get_model('app_image', 'LessonImage')
    default_image = 'lessons/default.png'
    LessonImage.objects.create(image=default_image)


def create_default_user_image(apps, schema_editor):
    UserImage = apps.get_model('app_image', 'UserImage')
    default_image = 'users/default.png'
    UserImage.objects.create(image=default_image)


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CourseImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(default='courses/default.png', upload_to='courses/',
                                            verbose_name='Изображение курса')),
            ],
            options={
                'verbose_name': 'Изображение курса',
                'verbose_name_plural': 'Изображения курсов',
                'db_table': 'courses_images',
            },
        ),
        migrations.CreateModel(
            name='LessonImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(default='lessons/default.png', upload_to='lessons/',
                                            verbose_name='Изображение урока')),
            ],
            options={
                'verbose_name': 'Изображение урока',
                'verbose_name_plural': 'Изображения уроков',
                'db_table': 'lesson_images',
            },
        ),
        migrations.CreateModel(
            name='UserImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(default='users/default.png', upload_to='users/',
                                            verbose_name='Изображение пользователя')),
            ],
            options={
                'verbose_name': 'Изображение пользователя',
                'verbose_name_plural': 'Изображения пользователей',
                'db_table': 'user_images',
            },
        ),
        migrations.RunPython(create_default_course_image),
        migrations.RunPython(create_default_lesson_image),
        migrations.RunPython(create_default_user_image),
    ]
