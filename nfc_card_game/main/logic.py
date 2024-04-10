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

    trans_cost={}
    for recipe in post_recipes:
        trans_cost[recipe.item.name] = recipe.amount 
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
        bought={sell_item.item.name: post_recipes.first().post.sell_amount},
        costs=trans_cost
    )


def handle_mine_scan(player_items: PlayerItem, player: Player, playermine: TeamMine) -> ActionInfo:

    mines = player_items.filter(item=playermine.mine)
    if not mines or mines.first().amount <= 0:
        return ActionInfo(log="Je hebt geen mine van deze munt!", status='error')

    for mine in mines:
        if playermine.mine.currency == mine.item.currency:
            mine_instance = mine
    
    if mine_instance.amount <= 0:
        return ActionInfo(log="Je hebt geen mines!", status='error')

    delivered_amount = mine_instance.amount
    playermine.amount += mine_instance.amount
    mine_instance.amount = 0
    mine_instance.save()
    playermine.save()

    return ActionInfo(log=f"{delivered_amount} Mines afgeleverd en saldo opgewaardeerd!", status="ok", costs={mine.item.name: delivered_amount}, bought={mine.item.name: delivered_amount})
