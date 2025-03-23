# Generated by Django 5.1.7 on 2025-03-22 14:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kriangle_app', '0005_contact'),
    ]

    operations = [
        migrations.AddField(
            model_name='seojob',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=50),
        ),
        migrations.AddField(
            model_name='seoresult',
            name='status',
            field=models.CharField(choices=[('success', 'Success'), ('failed', 'Failed'), ('pending', 'Pending')], default='success', max_length=50),
        ),
        migrations.AlterField(
            model_name='seoresult',
            name='job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='kriangle_app.seojob'),
        ),
        migrations.CreateModel(
            name='BlogPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('url', models.URLField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blog_posts', to='kriangle_app.seojob')),
            ],
        ),
        migrations.CreateModel(
            name='OffPageSEOAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_type', models.CharField(max_length=100)),
                ('platform', models.CharField(max_length=255)),
                ('url', models.URLField(blank=True, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed')], default='pending', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='offpage_actions', to='kriangle_app.seojob')),
            ],
        ),
    ]
