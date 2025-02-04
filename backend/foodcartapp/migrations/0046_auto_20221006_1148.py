# Generated by Django 3.2.15 on 2022-10-06 08:48

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0045_customer_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='called_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='звонок совершен'),
        ),
        migrations.AddField(
            model_name='customer',
            name='delivered_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='доставлено'),
        ),
        migrations.AddField(
            model_name='customer',
            name='registered_at',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='заказ создан'),
        ),
    ]
