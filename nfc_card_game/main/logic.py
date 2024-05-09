from typing import Literal

from django.db.transaction import commit
from pydantic import BaseModel
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.forms.models import model_to_dict
from django.db.models import Sum

from .models import Player, Mine, PlayerItem, PostRecipe
from .models import ResourceType, WorkerType, CoinType

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

    currencies = player_items.filter(item__type="COIN").exclude(item__currency=post_recipes.first().post.sells.currency)
    currency = currencies.order_by('-amount')
    if post_recipes.first().post.type == "RESOURCE":
        cost = post_recipes.first().price * buy_amount

        if cost > currency.aggregate(Sum('amount'))['amount__sum']:
            return ActionInfo(
                log="Niet genoeg geld!",
                status="error",
            )


        for currency in currencies.order_by('-amount'):
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


        money = player_items.get(player=player, item=post_recipes.first().item)
        buy_item = player_items.get(player=player, item=post_recipes.first().post.sells)
        if money.amount >= cost:
            money.amount -= cost
            buy_item.amount += buy_amount
            changes.append(money)
            changes.append(buy_item)
        else:
            return ActionInfo(
                log="Niet genoeg geld!",
                status="error",
            )

        commit_changes(changes)

        return ActionInfo(
            log="Spullen gekocht",
            status="ok",
            player=model_to_dict(player),
            bought={"amount": buy_amount, "item": post_recipes.first().post.sells},
            costs=trans_cost,
        )



        for recipe in post_recipes:
            money = player_items.get(player=player, item=recipe.item)
            if money.amount >= cost:
                money.amount -= cost
                trans_cost = {recipe.item: {"name": recipe.item, "amount": cost, "post_name": post_recipes[0].post.name}}
                trans_cost[recipe.item.name] = model_to_dict(recipe.item)
                trans_cost[recipe.item.name]["amount"] = recipe.price
                trans_cost[recipe.item.name]["post_name"]= post_recipes[0].post.name 
            elif money.amount < cost:
                cost = cost - money.amount
                money.amount = 0
            changes.append(money)

        commit_changes(changes)
        print(trans_cost)


        pass
            

    elif post_recipes.first().post.type == "MINER":
        pass

    return ActionInfo(
        log="Spullen gekocht",
        status="ok",
        player=model_to_dict(player),
        bought={"amount": buy_amount, "item": post_recipes.first().post.sells},
        costs=trans_cost,
    )

    for recipe in post_recipes:
        player_item = player_items.filter(player=player, item=recipe.item).first()
        if player_item is None:
            return ActionInfo(log=f"Geen {recipe.item} in inventory", status="error")

        if player_item.amount <= 0 or player_item.amount < buy_amount:
            return ActionInfo(log=f"Niet genoeg {player_item.item.name}!", status="error")

        recipe.amount = buy_amount

        if post_recipes.first().post.sell_amount == None:
            sold_amount = player_item.amount

        trans_cost = {recipe.item: {"name": recipe.item, "amount": recipe.amount, "post_name": post_recipes[0].post.name}}
        player_item = player_items.get(player=player, item=recipe.item)
        player_item.amount -= recipe.amount
        changes.append(player_item)


    print(post_recipes.first().post.sells)
    sell_item = player_items.get(player=player, item=post_recipes.first().post.sells)
    if post_recipes.first().post.sell_amount:
        sell_item.amount = (sell_item.amount + post_recipes.first().post.sell_amount)
        changes.append(sell_item)

    sold_amount = post_recipes.first().post.sell_amount

    commit_changes(changes)
    return ActionInfo(
        log="Spullen gekocht",
        status="ok",
        player=model_to_dict(player),
        bought={"amount": sold_amount, "item": sell_item.item},
        costs=trans_cost,
    )


def handle_mine_scan(
    player: Player,
    player_items: PlayerItem,
    mine: Mine,
) -> ActionInfo:
    trans_cost = {}
    changes = []

    print(mine) 
    # for item in player_items:
    #     if item == mine.
    return ActionInfo(log=f"TESTING", status="error")



# def check_buy_amount(recipe, player_item):
#     if not recipe.amount:
#         if player_item.amount <= 0
#             return ActionInfo(
#                 log=f"Je hebt geen {player_item.item.name}'s om in de mine te plaatsen!"
#                 statu="error"
#             )

def handle_post_scan_old(
    player: Player,
    post_recipes: PostRecipe,
    player_items: PlayerItem,
) -> ActionInfo:
    trans_cost = {}
    changes = []

    if post_recipes.first().post.type == "RESOURCE":
        print("RESOURCE")
        for recipe in post_recipes:
            print(recipe)

    elif post_recipes.first().post.type == "MINER":
        print("MINER")
        for recipe in post_recipes:
            print(recip)




    # for recipe in post_recipes:
    #     player_item = player_items.filter(player=player, item=recipe.item).first()
    #     print(player_item)
    #     if player_item is None:
    #         return ActionInfo(log=f"Geen {recipe.item} in inventory", status="error")
    #     if not recipe.amount:
    #         if player_item.amount <= 0:
    #             return ActionInfo(
    #                 log=f"Je hebt geen {player_item.item.name}'s om in de mine te plaatsen!",
    #                 status="error",
    #             )
    #         recipe.amount = player_item.amount
    #     if player_item.amount < recipe.amount:
    #         return ActionInfo(
    #             log=f"Niet genoeg {player_item.item.name}!", status="error"
    #         )
    #
    # for recipe in post_recipes:
    #     trans_cost[recipe.item.name] = model_to_dict(recipe.item)
    #     trans_cost[recipe.item.name]["amount"] = recipe.amount
    #     trans_cost[recipe.item.name]["post_name"] = post_recipes[0].post.name
    #     player_item = player_items.get(player=player, item=recipe.item)
    #     player_item.amount -= recipe.amount
    #     changes.append(player_item)
    #
    # # Check if post sells anything, if not assume it's a mine
    # if post_recipes.first().post.sells is not None:
    #     sell_item, created = player_items.get_or_create(
    #         player=player, item=post_recipes.first().post.sells, defaults={"amount": 1}
    #     )
    #     sold_amount = post_recipes.first().post.sell_amount
    #     if not created:
    #         if post_recipes.first().post.sell_amount:
    #             sell_item.amount = (
    #                 sell_item.amount + post_recipes.first().post.sell_amount
    #             )
    #             changes.append(sell_item)
    #
    #     commit_changes(changes)
    #
    #     return ActionInfo(
    #         log="Spullen gekocht",
    #         status="ok",
    #         player=model_to_dict(player),
    #         bought={"amount": sold_amount, "item": model_to_dict(sell_item.item)},
    #         costs=trans_cost,
    #     )
    # else:
    #     team_mine = None
    #     for mine in team_mines:
    #         if mine.mine.currency == player_item.item.currency:
    #             team_mine = mine
    #
    #     if not team_mine:
    #         return ActionInfo(
    #             log=f"Er bestaat geen {player_item.item.currency} mine voor {player.team}",
    #             status="error",
    #         )
    #
    #     team_mine.amount += list(trans_cost.values())[0]["amount"]
    #     changes.append(team_mine)
    #     commit_changes(changes)
    #     player_dict = model_to_dict(player)
    #     player_dict["team_name"] = player.team.name
    #
    #     return ActionInfo(
    #         log="Mine verkocht",
    #         status="ok",
    #         player=player_dict,
    #         costs=trans_cost,
    #     )
