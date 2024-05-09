# Generated by Django 5.0.4 on 2024-05-09 15:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_rename_amount_postrecipe_price_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='teammine',
            old_name='amount',
            new_name='money',
        ),
        migrations.CreateModel(
            name='TeamMineItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(default=0)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.item')),
                ('team_mine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.teammine')),
            ],
            options={
                'unique_together': {('team_mine', 'item')},
            },
        ),
    ]