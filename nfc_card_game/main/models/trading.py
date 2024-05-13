from django.db import models

from .player import Player, Team
from .utils import short_uuid


class TypeType(models.TextChoices):
    COIN = "COIN", "Coin"
    RESOURCE = "RESOURCE", "Resource"
    MINER = "MINER", "Miner"


class CoinType(models.TextChoices):
    BLAUW = "Blauw", "\U0001f535"
    GROEN = "Groen", "\U0001f7e2"
    ROOD = "Rood", "\U0001f534"


class ResourceType(models.TextChoices):
    A = "BIJL", "Bijl"
    B = "TANDWIEL", "Tandwiel"
    C = "RUPSBAND", "Rupsband"


class MinerType(models.TextChoices):
    A = "MIJNWERKER", "Mijnwerker"
    B = "DRILBOOR", "Drilboor"
    C = "BULLDOZER", "Bulldozer"


class Item(models.Model):
    name = models.CharField(
        choices=list(ResourceType.choices)
        + list(CoinType.choices)
        + list(MinerType.choices)
    )
    type = models.CharField(choices=TypeType)
    currency = models.CharField(choices=CoinType)

    def save(self, *args, **kwargs):
        if self.name in dict(ResourceType.choices):
            self.type = TypeType.RESOURCE
        elif self.name in dict(CoinType.choices):
            self.type = TypeType.COIN
        elif self.name in dict(MinerType.choices):
            self.type = TypeType.MINER
        super(Item, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.currency}: {self.name}"


class PlayerItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    amount = models.BigIntegerField()

    class Meta:
        unique_together = ("player", "item")

    def __str__(self):
        return f"Player: {self.player} with Item: {self.item} x {self.amount}"


class Mine(models.Model):
    card_uuid = models.CharField(default=short_uuid, max_length=10)
    name = models.CharField(max_length=100, choices=CoinType)
    currency = models.CharField(max_length=100, choices=CoinType)

    class Meta:
        unique_together = ("currency",)

    def save(self, *args, **kwargs):
        created = not self.pk
        super().save(*args, **kwargs)
        if created:
            for team in Team.objects.all():
                TeamMine.objects.create(team=team, mine=self, amount=100)

    def __str__(self):
        return f"{self.name} currency: {self.currency}"


class TeamMine(models.Model):
    mine = models.ForeignKey(Mine, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    money = models.BigIntegerField()

    class Meta:
        unique_together = ("mine", "team")

    def __str__(self):
        return f"{self.team}: {self.mine}"


class TeamMineItem(models.Model):
    team_mine = models.ForeignKey(TeamMine, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    amount = models.BigIntegerField(default=0)

    class Meta:
        unique_together = ("team_mine", "item")


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
