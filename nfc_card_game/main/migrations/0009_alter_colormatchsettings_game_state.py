# Generated by Django 5.0.4 on 2024-09-23 21:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0008_colormatchsettings"),
    ]

    operations = [
        migrations.AlterField(
            model_name="colormatchsettings",
            name="game_state",
            field=models.CharField(
                choices=[("RUNNING", "Running"), ("STOPPED", "Stopped")],
                default="RUNNING",
            ),
        ),
    ]