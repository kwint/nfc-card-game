from typing import Literal

from pydantic import BaseModel

from .models import Player, TeamMine, PlayerItem, PostRecipe

MINE_OFFLOAD = 200


class ActionInfo(BaseModel):
    log: str = ""
    status: Literal["ok", "error"] = "ok"
    bought: dict[str, int | float] | None = None
    costs: dict[str, int | float] | None = None

def commit_changes(changes: list):
    for obj in changes:
        obj.save()


def handle_post_scan(player: Player, post_recipes: PostRecipe, player_items: PlayerItem, team_mines: TeamMine) -> ActionInfo:
    trans_cost = {}
    changes = []

    for recipe in post_recipes:
        player_item = player_items.filter(player=player, item=recipe.item).first()
        if player_item is None:
            return ActionInfo(log=f"Geen {recipe.item} in inventory", status='error')
        if not recipe.amount:
            if player_item.amount <= 0:
                return ActionInfo(log=f"Je hebt geen {player_item.item.name}'s om in de mine te plaatsen!", status='error')
            recipe.amount = player_item.amount
        if player_item.amount < recipe.amount:
            return ActionInfo(log=f"Niet genoeg {player_item.item.name}!", status='error')

    for recipe in post_recipes:
        trans_cost[recipe.item.name] = recipe.amount 
        player_item = player_items.get(player=player, item=recipe.item)
        player_item.amount -= recipe.amount
        changes.append(player_item)


    # Check if post sells anything, if not assume it's a mine
    if post_recipes.first().post.sells is not None:
        sell_item, created = player_items.get_or_create(player=player, item=post_recipes.first().post.sells, defaults={'amount': 1})
        if not created:
            if post_recipes.first().post.sell_amount:
                sell_item.amount = sell_item.amount + post_recipes.first().post.sell_amount
                changes.append(sell_item)

        commit_changes(changes)

        return ActionInfo(
            log="Spullen gekocht",
            status="ok",
            bought={sell_item.item.name: post_recipes.first().post.sell_amount},
            costs=trans_cost
        )
    else:
        team_mine = None
        for mine in team_mines:
            if mine.mine.currency == player_item.item.currency:
                team_mine = mine

        if not team_mine:
            return ActionInfo(log=f"Er bestaat geen {player_item.item.currency} mine voor {team_mine.first().post.name}", status='error')

        team_mine.amount += list(trans_cost.values())[0]
        changes.append(team_mine)
        commit_changes(changes)

        return ActionInfo(
            log="Mine verkocht",
            status='ok',
            costs=trans_cost
        )

