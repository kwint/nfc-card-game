from typing import Literal

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Sum
from django.forms.models import model_to_dict
from pydantic import BaseModel

from .models.player import Player
from .models.trading import (
    Mine,
    PlayerItem,
    PostRecipe,
    TeamMine,
    TeamMineItem,
)

MINE_OFFLOAD_PERCENT = 0.10

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
            data = {"type": "websocket.send", "data": self.model_dump()}
            async_to_sync(channel_layer.group_send)(
                "broadcast", {"type": "action_message", "data": data}
            )


def commit_changes(changes: list):
    for obj in changes:
        obj.save()


def handle_post_scan(
    player: Player,
    post_recipes: PostRecipe,
    player_items: PlayerItem,
    team_mines: Mine,
    buy_amount: int,
) -> ActionInfo:
    trans_cost = {}
    changes = []

    currencies = player_items.filter(item__type="COIN").exclude(
        item__currency=post_recipes.first().post.sells.currency
    )
    currency = currencies.order_by("-amount")
    cost = post_recipes.first().price * buy_amount

    if cost > currency.aggregate(Sum("amount"))["amount__sum"]:
        return ActionInfo(
            log="Niet genoeg geld!",
            status="error",
        )

    for currency in currencies.order_by("-amount"):
        if cost <= 0:
            break
        if currency.amount > 0:
            deducted_amount = min(currency.amount, cost)
            currency.amount -= deducted_amount
            cost -= deducted_amount

            trans_cost[currency.item.name] = {
                "name": currency.item.name,
                "amount": deducted_amount,
            }
            changes.append(currency)

    buy_item = player_items.get(player=player, item=post_recipes.first().post.sells)
    buy_item.amount += buy_amount
    changes.append(buy_item)
    commit_changes(changes)

    return ActionInfo(
        log="Spullen gekocht",
        status="ok",
        player=model_to_dict(player),
        bought={"amount": buy_amount, "item": post_recipes.first().post.sells},
        costs=trans_cost,
    )


def handle_miner_scan(
    player: Player,
    post_recipes: PostRecipe,
    player_items: PlayerItem,
    team_mines: Mine,
    buy_amount: int,
) -> ActionInfo:
    changes = []
    trans_cost = {}
    for recipe in post_recipes:
        print(recipe.item.name)
        player_item = player_items.filter(player=player, item=recipe.item).first()
        cost = recipe.price * buy_amount
        if player_item is None:
            return ActionInfo(log=f"Geen {recipe.item} in inventory", status="error")

        if player_item.amount <= 0 or player_item.amount < buy_amount:
            return ActionInfo(
                log=f"Niet genoeg {player_item.item.name}!", status="error"
            )

        if post_recipes.first().post.sell_amount is None:
            sold_amount = player_item.amount

        trans_cost[recipe.item.name] = {
            "name": recipe.item.name,
            "amount": cost,
            "post_name": post_recipes[0].post.name,
        }
        player_item.amount -= cost
        changes.append(player_item)

    sell_item = player_items.get(player=player, item=post_recipes.first().post.sells)
    sell_item.amount = sell_item.amount + buy_amount

    changes.append(sell_item)
    commit_changes(changes)

    return ActionInfo(
        log="Spullen gekocht",
        status="ok",
        player=model_to_dict(player),
        bought={"amount": buy_amount, "item": sell_item.item},
        costs=trans_cost,
    )


def handle_mine_scan(
    player: Player,
    player_items: PlayerItem,
    team_mines: TeamMine,
    mine_items: TeamMineItem,
) -> ActionInfo:
    changes = []
    trans_cost = {}
    mine = team_mines.get()
    print(mine_items)

    curr_miners = player_items.filter(
        item__type="MINER", item__currency=mine.mine.currency
    )

    for item in curr_miners:
        if (
            item.item.type == "MINER"
            and item.item.currency == team_mines[0].mine.currency
            and item.amount > 0
        ):
            mine_item = mine_items.get(item=item.item, team_mine__team=player.team)
            player_item = player_items.get(item=item.item)
            mine_item.amount += item.amount
            player_item.amount -= item.amount

            trans_cost[mine_item.item.name] = {
                "name": mine_item.item.name,
                "amount": item.amount,
            }

            changes.append(mine_item)
            changes.append(player_item)

    commit_changes(changes)

    n = player_items.get(item__currency=team_mines[0].mine.currency, item__type="COIN")
    n.amount += round(team_mines[0].money * MINE_OFFLOAD_PERCENT)
    received_money = round(team_mines[0].money * MINE_OFFLOAD_PERCENT)
    n.amount += received_money
    mine.money = mine.money - received_money

    changes.append(n)
    changes.append(mine)
    commit_changes(changes)

    return ActionInfo(
        log="Miner's afgeleverd",
        status="ok",
        bought={"amount": received_money, "item": n},
        costs=trans_cost,
    )
