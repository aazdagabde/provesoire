# Generated by Django 5.0.6 on 2025-01-10 01:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DHT', '0007_globalalertsettings_alerts_enabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='globalalertsettings',
            name='telegram_bot_link',
            field=models.CharField(blank=True, help_text='Lien du bot Telegram', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='telegram_bot_link',
            field=models.CharField(blank=True, help_text='Lien du bot Telegram', max_length=255, null=True),
        ),
    ]
