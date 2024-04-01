from copy import copy

from .models import Player, Post

from .models import Player, Post


def execute_transaction(player: Player, post: Post):
    player_inv = copy(player.inventory)

    for item, amount in post.buys.items():
        player_inv[item] = player_inv.get(item, 0) - amount

    if any(val < 0 for val in player_inv.values()):
        return {"status": "Niet genoeg geld!"}

    for item, amount in post.sells.items():
        player_inv[item] = player_inv.get(item, 0) + amount

    player.inventory = player_inv
    player.save()

    return {"status": "ok", "bought": post.sells, "costs": post.buys}
