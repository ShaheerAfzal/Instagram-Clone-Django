# Generated by Django 4.2.16 on 2024-12-06 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0003_auto_20220214_1319'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
