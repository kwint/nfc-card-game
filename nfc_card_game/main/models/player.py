from django.db import models

from nfc_card_game.main.models.activities import Activity
from .utils import short_uuid


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
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    activities = models.ManyToManyField(Activity)

    def __str__(self):
        return f"{self.name} | {self.section}"
