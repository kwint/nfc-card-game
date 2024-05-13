from typing import Any, Literal

from asgiref.sync import async_to_sync
import channels
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db.models import Sum
from django.forms.models import model_to_dict
from pydantic import BaseModel
from django.db.models.query import QuerySet
from .models.player import Player, Team
from .models.trading import (
    CoinType,
    Item,
    Mine,
    MinerType,
    PlayerItem,
    PostRecipe,
    ResourceType,
    TeamMine,
    TeamMineItem,
    TypeType
)
from .game_loop import SETTINGS
from . import api_consumer

MINE_OFFLOAD_PERCENT = 0.10

channel_layer = get_channel_layer()


class ActionInfo(BaseModel):
    log: str = ""
    status: Literal["ok", "error"] = "ok"
    team: str | None = None
    player: Any | None = None
    bought: dict | dict[str, int | float] | None = None
    costs: dict | None = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.broadcast_message()

    def clean_message(self, data):
        model_types = [Item, Mine, PlayerItem, Player, TeamMine, TeamMineItem]
        for key, value in data.items():
            if any(isinstance(value, type) for type in model_types):
                data[key] = model_to_dict(value)
            elif isinstance(value, dict):
                self.clean_message(value)
        return data


    def broadcast_message(self):
        if self.status == "ok":
            data = {"type": "websocket.send", "data": self.model_dump()}
            data = self.clean_message(data)
            print(data)
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
    price: int,
    buy_amount: int,
) -> ActionInfo:
    trans_cost = {}
    changes = []

    currencies = player_items.filter(item__type=TypeType.COIN).exclude(
        item__currency=post_recipes.first().post.sells.currency
    )
    currency = currencies.order_by("-amount")
    cost = price * buy_amount

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

            trans_cost[currency.item.get_name_display()] = {
                "name": currency.item.name,
                "amount": deducted_amount,
                "currency": currency.item.get_currency_display(),
            }
            changes.append(currency)

    buy_item = player_items.get(player=player, item=post_recipes.first().post.sells)
    buy_item.amount += buy_amount
    changes.append(buy_item)
    commit_changes(changes)

    return ActionInfo(
        log="Spullen gekocht",
        status="ok",
        team=player.team.name,
        player=player,
        bought={
            "amount": buy_amount,
            "item": post_recipes.first().post.sells,
        },
        costs=trans_cost,
    )


def handle_miner_scan(
    player: Player,
    post_recipes: PostRecipe,
    player_items: PlayerItem,
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

        trans_cost[recipe.item.get_name_display()] = {
            "name": recipe.item.get_name_display(),
            "amount": cost,
            "post_name": post_recipes[0].post.name,
            "currency": recipe.item.get_currency_display(),
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
        player=player,
        team=player.team.name,
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
        item__type=TypeType.MINER, item__currency=mine.mine.currency
    )

    for item in curr_miners:
        if (
            item.item.type == TypeType.MINER
            and item.item.currency == team_mines[0].mine.currency
            and item.amount > 0
        ):
            mine_item = mine_items.get(item=item.item, team_mine__team=player.team)
            player_item = player_items.get(item=item.item)
            mine_item.amount += item.amount
            player_item.amount -= item.amount

            trans_cost[mine_item.item.get_name_display()] = {
                "name": mine_item.item.get_name_display(),
                "post": str(mine_item.item),
                "amount": item.amount,
                "currency": item.item.get_currency_display(),
            }

            # Broadcast for API clients: miners added
            channel_layer = channels.layers.get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                api_consumer.CHANNEL_NAME,
                {
                    "type": api_consumer.CHANNEL_EVENT_HANDLER,
                    "event_id": api_consumer.ChannelEventType.MINE_MINERS_ADDED.value,
                    "data": {
                        "mine_id": mine_item.team_mine.mine_id,
                        "team_id": mine_item.team_mine.team_id,
                        "miner_type": SETTINGS.miner_type_ids[mine_item.item.name],
                        "miner_type_name": mine_item.item.get_name_display(),
                        "amount": item.amount,
                        "effective": SETTINGS.miner_factors[mine_item.item.name] * item.amount,
                    },
                }
            )

            changes.append(mine_item)
            changes.append(player_item)

    player_wallet = player_items.get(
        item__currency=team_mines[0].mine.currency, item__type=TypeType.COIN
    )
    mine_money = round(team_mines[0].money * MINE_OFFLOAD_PERCENT)
    received_money = mine_money - player_wallet.amount if mine_money > player_wallet.amount else 0
    player_wallet.amount += received_money
    mine.money = mine.money - received_money

    # Broadcast for API clients: mine money update
    channel_layer = channels.layers.get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        api_consumer.CHANNEL_NAME,
        {
            "type": api_consumer.CHANNEL_EVENT_HANDLER,
            "event_id": api_consumer.ChannelEventType.MINE_MONEY_UPDATE.value,
            "data": {
                "mine_id": mine.mine_id,
                "team_id": mine.team_id,
                "money": mine.money,
            },
        }
    )

    changes.append(player_wallet)
    changes.append(mine)
    commit_changes(changes)

    return ActionInfo(
        log="Miner's afgeleverd",
        status="ok",
        team=player.team.name,
        player=player,
        bought={"amount": received_money, "item": mine.mine},
        costs=trans_cost,
    )


def get_miner_price(team_mine: TeamMine, item_name: str):
    team_mine_item = TeamMineItem.objects.get(
        team_mine=team_mine,
        item__name=item_name,
        item__currency=team_mine.mine.currency,
    )

    base_price = SETTINGS.base_price * SETTINGS.miner_factors[item_name]
    price_increase = team_mine_item.amount * base_price * SETTINGS.unit_increase_factor
    return int(base_price + price_increase)


def get_resource_price(team_mines: QuerySet[TeamMine], resource: Item) -> int:
    team_mine = team_mines.get(mine__currency=resource.currency)
    bijl_price = get_miner_price(team_mine, MinerType.A.value)
    if resource.name == ResourceType.A:
        return bijl_price

    tandwiel_price = get_miner_price(team_mine, MinerType.B.value) - bijl_price
    if resource.name == ResourceType.B:
        return tandwiel_price

    return get_miner_price(team_mine, MinerType.C.value) - tandwiel_price
