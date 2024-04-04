import uuid

from django.db import models

# Create your models here.


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

    card_uuid = models.CharField(default=short_uuid, max_length=10)
    name = models.CharField(max_length=100, blank=True)
    section = models.CharField(max_length=4, choices=Section, default=Section.NONE)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.name} | {self.section}"

class Item(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"

class PlayerItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    amount = models.IntegerField()

    class Meta:
        unique_together = ('player', 'item')


class Post(models.Model):
    card_uuid = models.CharField(default=short_uuid, max_length=10)

    name = models.CharField(max_length=100)
    buys = models.JSONField(default=dict)
    sells = models.JSONField(default=dict)

    def __str__(self):
        return f"Post {self.name}: Sells {self.sells} for {self.buys}"


class Currency(models.TextChoices):
    COIN_BLUE = "BLUE", "Blauwe munt"
    COIN_RED = "RED ", "Rode munt"
    COIN_GREEN = "GREEN", "Groene munt"


class Mine(models.Model):
    name = models.CharField(max_length=100)
    currency = models.CharField(choices=Currency)

    def __str__(self):
        return f"Mine {self.name} with {self.currency}"


class TeamMine(models.Model):
    card_uuid = models.CharField(default=short_uuid, max_length=10)

    mine = models.ForeignKey(Mine, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    inventory = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.mine} of {self.team}"
