# Generated by Django 5.1.6 on 2025-02-25 20:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("auth_app", "0004_remove_customuser_role"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="fullname",
            field=models.CharField(blank=True, null=True),
        ),
    ]
