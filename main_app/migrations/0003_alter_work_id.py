# Generated by Django 5.1.6 on 2025-02-17 22:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main_app", "0002_workimage"),
    ]

    operations = [
        migrations.AlterField(
            model_name="work",
            name="id",
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
