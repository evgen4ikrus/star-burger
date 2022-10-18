# Generated by Django 3.2.15 on 2022-10-18 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0051_alter_customer_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='order_status',
            field=models.CharField(choices=[('Не обработан', 'Не обработан'), ('Готовится', 'Готовится'), ('Доставляется', 'Доставляется'), ('Выполнен', 'Выполнен')], db_index=True, default='Необработан', max_length=15, verbose_name='статус'),
        ),
    ]
