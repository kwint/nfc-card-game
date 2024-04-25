import uuid

from django.db import models
from django.core.exceptions import ValidationError

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

    card_uuid = models.CharField(default=short_uuid, max_length=10, unique=True)
    name = models.CharField(max_length=100, blank=True)
    section = models.CharField(max_length=4, choices=Section, default=Section.NONE)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.name} | {self.section}"


class Currency(models.TextChoices):
    COIN_BLUE = "BLUE", "Blauwe munt"
    COIN_RED = "RED", "Rode munt"
    COIN_GREEN = "GREEN", "Groene munt"


class ItemType(models.TextChoices):
    MINE = "MINE", "Mine"
    RESOURCE = "RESOURCE", "Resource"
    MINER = "MINER", "Miner"


class Item(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100, choices=ItemType)
    currency = models.CharField(null=True, blank=True, choices=Currency)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        unique_together = (("name", "type"), ("type", "currency", "team"))
        ordering = ["type", "name"]

    def __str__(self):
        return f"{self.name}"

    def clean(self):
        print(self.type == ItemType.MINE)
        if self.type == ItemType.MINE and (not self.currency or not self.team):
            msg = "This field is required"
            raise ValidationError({"currency": [msg], "team": [msg]})
        if self.type == ItemType.MINER and not self.currency:
            raise ValidationError({"currency": ["This field is required"]})
        if self.type == ItemType.RESOURCE and (self.currency or self.team):
            msg = "This field must be empty!"
            raise ValidationError({"currency": [msg], "team": [msg]})

    def save(self, *args, **kwrgs):
        super(Item, self).save(*args, **kwrgs)

        if self.type == "MINE":
            m_instance = TeamMine.objects.create(
                team=self.team,
                mine=self,
                amount=0,
            )
            m_instance.save()


class PlayerItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    amount = models.IntegerField()

    class Meta:
        unique_together = ("player", "item")

    def __str__(self):
        return f"Player: {self.player} with Item:  x {self.amount}"


class Post(models.Model):
    card_uuid = models.CharField(default=short_uuid, max_length=10)

    name = models.CharField(max_length=100)
    sells = models.ForeignKey(Item, on_delete=models.CASCADE, blank=True, null=True)
    sell_amount = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"Post {self.name}: "


class PostRecipe(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        unique_together = ("post", "item")


class TeamMine(models.Model):
    mine = models.ForeignKey(Item, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    amount = models.IntegerField()

    class Meta:
        unique_together = ("team", "mine")
        ordering = ["team", "mine"]

    def __str__(self):
        return f"{self.mine} of {self.team}"
