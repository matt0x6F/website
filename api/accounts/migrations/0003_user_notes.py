# Generated by Django 5.1.1 on 2024-10-10 01:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_user_avatar_link"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="notes",
            field=models.TextField(blank=True, null=True),
        ),
    ]
