# Generated by Django 3.2.15 on 2022-10-30 14:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0061_rename_customer_orderelement_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='restaurant',
        ),
        migrations.AddField(
            model_name='order',
            name='cooking_restaurant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='foodcartapp.restaurant', verbose_name='готовящий ресторан'),
        ),
    ]
