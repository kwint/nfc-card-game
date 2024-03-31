import uuid

from django.contrib import admin
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
        OBV = "OBV", "Ochtend Bevers"
        MBV = "MBV", "Middag Bevers"

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

    card_uuid = models.CharField(default=short_uuid, max_length=10)
    name = models.CharField(max_length=100)
    section = models.CharField(max_length=4, choices=Section)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True)
    # inventory

    def __str__(self):
        return f"{self.name} | {self.section}"
