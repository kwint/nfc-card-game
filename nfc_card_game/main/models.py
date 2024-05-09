from enum import unique
from random import choices
import uuid
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.transaction import on_commit


def short_uuid() -> str:
    return str(uuid.uuid4())[:8]

class Team(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Player(models.Model):
    class Section(models.TextChoices):
        OBV = "OBV", "Ochtendbevers"
        MBV = "MBV", "Middagbevers"

        MAL = "MAL", "Malicetehorde"
        SJH = "SJH", "Sint Jorishorde"
        COM = "COM", "Commoosiehorde"
        STH = "STH", "Sterrenhorde"

        DOB = "DOB", "Donkerblauwe troep"
        SJV = "SJV", "Sint Jorisvendel"
        LIB = "LIB", "Lichtblauwe troep"
        STV = "STV", "Sterrenvendel"

        EXP = "EXP", "Explorers"
        STAF = "STAF", "Leiding"

        NONE = "", "Not set"

    card_uuid = models.CharField(default=short_uuid, max_length=10, unique=True)
    name = models.CharField(max_length=100, blank=True)
    section = models.CharField(max_length=4, choices=Section, default=Section.NONE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.name} | {self.section}"

class TypeType(models.TextChoices):
    COIN = "COIN", "Coin"
    RESOURCE = "RESOURCE", "Resource"
    WORKER = "WORKER", "Worker"

class CoinType(models.TextChoices):
    BLAUW = "BLAUW", "Blauw"
    GROEN = "GROEN", "Groen"
    ROOD = "ROOD", "Rood"

class ResourceType(models.TextChoices):
    A = "BIJL", "Bijl"
    B = "BOOR", "Boor"
    C = "RUPSBAND", "Rupsband"

class WorkerType(models.TextChoices):
    A = "MIJNWERKER", "Mijnwerker"
    B = "DRILBOOR", "Drilboor"
    C = "TUNNELBOOR", "Tunnelboor"

class Item(models.Model):
    name = models.CharField(choices=list(ResourceType.choices) + list(CoinType.choices)+ list(WorkerType.choices))
    type = models.CharField(choices=TypeType)
    currency = models.CharField(choices=CoinType)

    def save(self, *args, **kwargs):
        if self.name in dict(ResourceType.choices):
            self.type = TypeType.RESOURCE
        elif self.name in dict(CoinType.choices):
            self.type = TypeType.COIN
        elif self.name in dict(WorkerType.choices):
            self.type = TypeType.WORKER
        super(Item, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.currency}: {self.name}"

class PlayerItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    amount = models.IntegerField()

    class Meta:
        unique_together = ("player", "item")

    def __str__(self):
        return f"Player: {self.player} with Item: {self.item} x {self.amount}"



class Mine(models.Model):
    card_uuid = models.CharField(default=short_uuid, max_length=10)
    name = models.CharField(max_length=100, choices=CoinType)
    currency = models.CharField(max_length=100, choices=CoinType)

    class Meta:
        unique_together = ("currency", )

    def save(self, *args, **kwargs):
        created = not self.pk
        super().save(*args, **kwargs)
        if created:
            for team in Team.objects.all():
                TeamMine.objects.create(team=team, mine=self, amount=0)

    def __str__(self):
        return f"{self.name} currency: {self.currency}"


class TeamMine(models.Model):
    mine = models.ForeignKey(Mine, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    amount = models.IntegerField()

    class Meta:
        unique_together = ('mine', 'team')


class ItemType(models.TextChoices):
    RESOURCE = "RESOURCE", "Resource"
    MINER = "MINER", "Miner"

class Post(models.Model):
    card_uuid = models.CharField(default=short_uuid, max_length=10)
    name = models.CharField(max_length=100)
    type = models.CharField(choices=ItemType)
    sells = models.ForeignKey(Item, on_delete=models.CASCADE)
    sell_amount = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"Post {self.name}: "

class PostRecipe(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    price = models.IntegerField()

    class Meta:
        unique_together = ("post", "item")





