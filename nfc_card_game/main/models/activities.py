from django.db import models

from nfc_card_game.main.models.utils import short_uuid


class Activity(models.Model):
    name = models.CharField(max_length=100)
    card_uuid = models.CharField(default=short_uuid, max_length=10)

    def __str__(self):
        return self.name
