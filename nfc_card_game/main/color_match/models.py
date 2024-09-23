from django.db import models


class ColorMatchGameState(models.TextChoices):
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"


class ColorMatchSettings(models.Model):
    game_state = models.CharField(
        choices=ColorMatchGameState, default=ColorMatchGameState.RUNNING
    )
    auto_rotate_colors = models.BooleanField(default=False)

    @classmethod
    def object(cls):
        return cls._default_manager.all().first()  # Since only one item
