# Generated by Django 5.1.4 on 2025-03-09 16:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kriangle_app', '0003_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='seoresult',
            name='job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kriangle_app.seojob'),
        ),
    ]
