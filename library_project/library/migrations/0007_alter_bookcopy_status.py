# Generated by Django 5.2.1 on 2025-05-12 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0006_customer_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookcopy',
            name='status',
            field=models.CharField(choices=[('available', 'Available'), ('unavailable', 'Unavailable'), ('lost', 'Lost')], db_column='STATUS', max_length=20),
        ),
    ]
