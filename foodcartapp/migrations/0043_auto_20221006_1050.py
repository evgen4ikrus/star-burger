# Generated by Django 3.2.15 on 2022-10-06 07:50

from django.db import migrations


def change_status(apps, schema_editor):
    Customer = apps.get_model('foodcartapp', 'Customer')
    for customer in Customer.objects.filter(order_status='0'):
        customer.order_status = 'Необработано'
        customer.save()


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0042_alter_customer_order_status'),
    ]

    operations = [
        migrations.RunPython(change_status),
    ]