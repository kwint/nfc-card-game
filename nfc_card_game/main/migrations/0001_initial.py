# Generated by Django 5.0.4 on 2024-05-09 23:48

import django.db.models.deletion
import nfc_card_game.main.models.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('card_uuid', models.CharField(default=nfc_card_game.main.models.utils.short_uuid, max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='GameSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mode', models.CharField(choices=[('trading', 'Trading'), ('activities', 'Activities'), ('color', 'Color')], default='trading', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('BIJL', 'Bijl'), ('BOOR', 'Boor'), ('RUPSBAND', 'Rupsband'), ('BLAUW', 'Blauw'), ('GROEN', 'Groen'), ('ROOD', 'Rood'), ('MIJNWERKER', 'Mijnwerker'), ('DRILBOOR', 'Drilboor'), ('TUNNELBOOR', 'Tunnelboor')])),
                ('type', models.CharField(choices=[('COIN', 'Coin'), ('RESOURCE', 'Resource'), ('MINER', 'Miner')])),
                ('currency', models.CharField(choices=[('BLAUW', 'Blauw'), ('GROEN', 'Groen'), ('ROOD', 'Rood')])),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Mine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_uuid', models.CharField(default=nfc_card_game.main.models.utils.short_uuid, max_length=10)),
                ('name', models.CharField(choices=[('BLAUW', 'Blauw'), ('GROEN', 'Groen'), ('ROOD', 'Rood')], max_length=100)),
                ('currency', models.CharField(choices=[('BLAUW', 'Blauw'), ('GROEN', 'Groen'), ('ROOD', 'Rood')], max_length=100)),
            ],
            options={
                'unique_together': {('currency',)},
            },
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_uuid', models.CharField(default=nfc_card_game.main.models.utils.short_uuid, max_length=10, unique=True)),
                ('name', models.CharField(blank=True, max_length=100)),
                ('section', models.CharField(choices=[('OBV', 'Ochtendbevers'), ('MBV', 'Middagbevers'), ('MAL', 'Malicetehorde'), ('SJH', 'Sint Jorishorde'), ('COM', 'Commoosiehorde'), ('STH', 'Sterrenhorde'), ('DOB', 'Donkerblauwe troep'), ('SJV', 'Sint Jorisvendel'), ('LIB', 'Lichtblauwe troep'), ('STV', 'Sterrenvendel'), ('EXP', 'Explorers'), ('STAF', 'Leiding'), ('', 'Not set')], default='', max_length=4)),
                ('color', models.CharField(blank=True, choices=[('RED', 'Red'), ('BLUE', 'Blue'), ('GREEN', 'Green'), ('YELLOW', 'Yellow')], default=None, max_length=20, null=True)),
                ('color_points', models.IntegerField(blank=True, default=0)),
                ('activities', models.ManyToManyField(blank=True, to='main.activity')),
                ('team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.team')),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_uuid', models.CharField(default=nfc_card_game.main.models.utils.short_uuid, max_length=10)),
                ('name', models.CharField(max_length=100)),
                ('type', models.CharField(choices=[('RESOURCE', 'Resource'), ('MINER', 'Miner')])),
                ('sell_amount', models.PositiveIntegerField(blank=True, null=True)),
                ('sells', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.item')),
            ],
        ),
        migrations.CreateModel(
            name='TeamMine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('money', models.IntegerField()),
                ('mine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.mine')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.team')),
            ],
            options={
                'unique_together': {('mine', 'team')},
            },
        ),
        migrations.CreateModel(
            name='PlayerItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField()),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.item')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.player')),
            ],
            options={
                'unique_together': {('player', 'item')},
            },
        ),
        migrations.CreateModel(
            name='PostRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.IntegerField()),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.item')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.post')),
            ],
            options={
                'unique_together': {('post', 'item')},
            },
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
