# Generated by Django 4.2 on 2023-07-18 05:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_user', '0002_remove_payment_paid_lesson_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='stripe_payment_intent_id',
        ),
        migrations.AddField(
            model_name='payment',
            name='payment_intent_id',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='ID намерения платежа Stripe'),
        ),
        migrations.AddField(
            model_name='payment',
            name='payment_method_id',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='ID метода платежа Stripe'),
        ),
        migrations.AddField(
            model_name='payment',
            name='status',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Статус платежа'),
        ),
    ]
