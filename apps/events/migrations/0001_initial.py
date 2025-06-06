# Generated by Django 5.2.2 on 2025-06-05 12:02

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('start_time', models.DateTimeField()),
                ('location', models.CharField(max_length=255)),
                ('seats_number', models.PositiveIntegerField()),
                ('status', models.CharField(choices=[('upcoming', 'Ожидается'), ('cancelled', 'Отменено'), ('finished', 'Завершено')], default='upcoming', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('organizer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='organized_events', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
