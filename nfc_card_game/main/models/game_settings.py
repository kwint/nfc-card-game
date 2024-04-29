from django.db import models


class GameSettings(models.Model):
    class GameMode(models.TextChoices):
        TRADING = "trading"
        ACTIVITIES = "activities"
        COLOR = "color"

    mode = models.CharField(choices=GameMode, default=GameMode.TRADING, max_length=50)

    @classmethod
    def object(cls):
        return cls._default_manager.all().first()  # Since only one item

    def __str__(self):
        return f"{self.mode=}"
