from typing import Literal

from pydantic import BaseModel

from .models import Player, TeamMine, PlayerItem, PostRecipe

MINE_OFFLOAD = 200


class ActionInfo(BaseModel):
    log: str = ""
    status: Literal["ok", "error"] = "ok"
    bought: dict[str, int | float] | None = None
    costs: dict[str, int | float] | None = None


def handle_post_scan(player: Player, post_recipes: PostRecipe, player_items: PlayerItem) -> ActionInfo:

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


def handle_mine_scan(player_items: PlayerItem, player: Player, playermine: TeamMine) -> ActionInfo:

    mines = player_items.filter(item=playermine.mine)
    if not mines:
        return ActionInfo(log="Geen mines in inventory!", status='error')
    
    mine_instance = mines.first()
    delivered_amount = mine_instance.amount
    playermine.amount += mine_instance.amount
    mine_instance.amount = 0
    mine_instance.save()
    playermine.save()

    return ActionInfo(log=f"{delivered_amount} Mines afgeleverd en saldo opgewaardeerd!", status="ok")
