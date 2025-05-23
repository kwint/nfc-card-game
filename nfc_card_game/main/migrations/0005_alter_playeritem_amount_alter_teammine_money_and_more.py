# Generated by Django 5.0.4 on 2024-05-16 06:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0004_alter_item_currency_alter_item_name_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="playeritem",
            name="amount",
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name="teammine",
            name="money",
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name="teammineitem",
            name="amount",
            field=models.BigIntegerField(default=0),
        ),
    ]
