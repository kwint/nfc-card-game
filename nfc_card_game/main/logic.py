from typing import Literal

from pydantic import BaseModel
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.forms.models import model_to_dict

from .models import Player, TeamMine, PlayerItem, PostRecipe

MINE_OFFLOAD = 200

channel_layer = get_channel_layer()


class ActionInfo(BaseModel):
    log: str = ""
    status: Literal["ok", "error"] = "ok"
    player: dict | None = None
    bought: dict | dict[str, int | float] | None = None
    costs: dict | None = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.broadcast_message()

    def broadcast_message(self):
        if self.status == "ok":
            data = {
                'type': 'websocket.send',
                'data': self.model_dump()
            }
            async_to_sync(channel_layer.group_send)('broadcast', {'type': 'action_message', 'data': data})


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
                print(player_item.item.name)
                return ActionInfo(log=f"Je hebt geen {player_item.item.name}'s om in de mine te plaatsen!", status='error')
            recipe.amount = player_item.amount
        if player_item.amount < recipe.amount:
            return ActionInfo(log=f"Niet genoeg {player_item.item.name}!", status='error')

    for recipe in post_recipes:
        # trans_cost[recipe.item.name] = recipe.amount 
        trans_cost[recipe.item.name] = model_to_dict(recipe.item)
        trans_cost[recipe.item.name]['amount'] = recipe.amount
        player_item = player_items.get(player=player, item=recipe.item)
        player_item.amount -= recipe.amount
        changes.append(player_item)


    # Check if post sells anything, if not assume it's a mine
    if post_recipes.first().post.sells is not None:
        sell_item, created = player_items.get_or_create(player=player, item=post_recipes.first().post.sells, defaults={'amount': 1})
        if not created:
            if post_recipes.first().post.sell_amount:
                sold_amount = post_recipes.first().post.sell_amount
                sell_item.amount = sell_item.amount + post_recipes.first().post.sell_amount
                changes.append(sell_item)

        commit_changes(changes)

        return ActionInfo(
            log="Spullen gekocht",
            status="ok",
            player=model_to_dict(player),
            # bought={sell_item.item.name: post_recipes.first().post.sell_amount},
            bought={'amount': sold_amount, 'item': model_to_dict(sell_item.item)},
            costs=trans_cost
        )
    else:
        team_mine = None
        for mine in team_mines:
            if mine.mine.currency == player_item.item.currency:
                team_mine = mine

        if not team_mine:
            return ActionInfo(log=f"Er bestaat geen {player_item.item.currency} mine voor {player.team}", status='error')

        team_mine.amount += list(trans_cost.values())[0]['amount']
        changes.append(team_mine)
        commit_changes(changes)

        return ActionInfo(
            log="Mine verkocht",
            status='ok',
            player=model_to_dict(player),
            costs=trans_cost,
        )

