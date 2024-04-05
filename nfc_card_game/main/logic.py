from copy import copy
from typing import Literal

from pydantic import BaseModel
from django.db.models import F

from .models import Currency, Player, Post, TeamMine, PlayerItem, PostRecipe

MINE_OFFLOAD = 200


class ActionInfo(BaseModel):
    log: str = ""
    status: Literal["ok", "error"] = "ok"
    bought: dict[str, int | float] | None = None
    costs: dict[str, int | float] | None = None


def handle_post_scan(player: PlayerItem, post_recipes: PostRecipe, player_items: PlayerItem) -> ActionInfo:

    for recipe in post_recipes:
        player_item = player_items.filter(player=player, item=recipe.item).first()
        if player_item.amount < recipe.amount:
            return ActionInfo(log=f"Niet genoeg {player_item.item.name}!", status='error')

    for recipe in post_recipes:
        player_item = player_items.get(player=player, item=recipe.item)
        player_item.amount -= recipe.amount
        player_item.save()

    sell_item, created = player_items.get_or_create(player=player, item=post_recipes.first().post.sells, defaults={'amount': 1})

    print(sell_item.item, "created", created, player_item.amount)
    if not created:
        sell_item.amount = sell_item.amount + post_recipes.first().post.sell_amount
        sell_item.save()

    return ActionInfo(
        log="Spullen gekocht",
        status="ok",
    )


def handle_mine_scan(player: Player, mine: TeamMine) -> ActionInfo:
    for key in mine.inventory.keys():
        if key in Currency.values:
            continue
        mine.inventory[key] += player.inventory.pop(key, 0)

    # TODO: handle negative case
    # TODO: add timeout between offloads
    mine.inventory[mine.mine.currency] -= MINE_OFFLOAD
    player.inventory[mine.mine.currency] = player.inventory.get(mine.mine.currency, 0) + MINE_OFFLOAD

    player.save()
    mine.save()

    return ActionInfo(log="Goederen afgeleverd en saldo opgewaardeerd!", status="ok")
