from typing import Literal

from pydantic import BaseModel

from .models import Player, TeamMine, PlayerItem, PostRecipe

MINE_OFFLOAD = 200


class ActionInfo(BaseModel):
    log: str = ""
    status: Literal["ok", "error"] = "ok"
    bought: dict[str, int | float] | None = None
    costs: dict[str, int | float] | None = None


def handle_post_scan(player: Player, post_recipes: PostRecipe, player_items: PlayerItem, team_mines: TeamMine) -> ActionInfo:

    for recipe in post_recipes:
        player_item = player_items.filter(player=player, item=recipe.item).first()
        if player_item== None:
            return ActionInfo(log=f"Geen {recipe.item} in inventory", status='error')
        if not recipe.amount:
            if player_item.amount <= 0:
                return ActionInfo(log=f"Je hebt geen {player_item.item.name}'s om in de mine te plaatsen!", status='error')
            recipe.amount = player_item.amount
        if player_item.amount < recipe.amount:
            return ActionInfo(log=f"Niet genoeg {player_item.item.name}!", status='error')

    trans_cost={}
    for recipe in post_recipes:
        trans_cost[recipe.item.name] = recipe.amount 
        player_item = player_items.get(player=player, item=recipe.item)
        player_item.amount -= recipe.amount


    # Add sell item to players inventory
    if post_recipes.first().post.sells != None:
        sell_item, created = player_items.get_or_create(player=player, item=post_recipes.first().post.sells, defaults={'amount': 1})
    else:
        team_mine = None
        for mine in team_mines:
            if mine.mine.currency == player_item.item.currency:
                team_mine = mine
        if not team_mine:
            print(team_mine)
            return ActionInfo(log=f"Er bestaat geen {player_item.item.currency} mine voor {team_mines.first().team}", status='error')
        team_mine.amount += recipe.amount
        mine.save()
        player_item.save()
        return ActionInfo(
            log="Mine verkocht",
            status='ok',
            costs=trans_cost
        )

    # update the mine amount when present
    if not created:
        if post_recipes.first().post.sell_amount:
            sell_item.amount = sell_item.amount + post_recipes.first().post.sell_amount
            sell_item.save()

    return ActionInfo(
        log="Spullen gekocht",
        status="ok",
        bought={sell_item.item.name: post_recipes.first().post.sell_amount},
        costs=trans_cost
    )

