from copy import copy
from typing import Literal

from pydantic import BaseModel

from .models import Currency, Player, Post, TeamMine

MINE_OFFLOAD = 200


class ActionInfo(BaseModel):
    log: str = ""
    status: Literal["ok", "error"] = "ok"
    bought: dict[str, int | float] = {}
    costs: dict[str, int | float] = {}


def handle_post_scan(player: Player, post: Post) -> ActionInfo:
    player_inv = copy(player.inventory)

    for item, amount in post.buys.items():
        player_inv[item] = player_inv.get(item, 0) - amount

    if any(val < 0 for val in player_inv.values()):
        return ActionInfo(log="Niet genoeg geld!", status="error")

    for item, amount in post.sells.items():
        player_inv[item] = player_inv.get(item, 0) + amount

    player.inventory = player_inv
    player.save()

    return ActionInfo(
        log="Spullen gekocht",
        bought=post.sells,
        costs=post.buys,
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
