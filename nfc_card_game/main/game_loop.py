from django.http import HttpResponse
from schedule import Scheduler
from asgiref.sync import async_to_sync
import channels
import threading
import time
from pydantic import BaseModel, Field
from nfc_card_game.main.models.trading import MinerType, TeamMine, TeamMineItem
import logging

from . import api_consumer

logger = logging.getLogger(__name__)


class GameSettings(BaseModel):
    # Base price of item
    base_price: float = 15
    # price increase factor (linear)
    unit_increase_factor: float = 0.01
    inbalance_inefficiency: float = 0.05
    miner_factors: dict[str, int] = Field(
        default={
            MinerType.A.value: 1,
            MinerType.B.value: 3,
            MinerType.C.value: 10,
        }
    )
    base_miner_per_sec: float = 1


SETTINGS = GameSettings()


def game_loop():
    update_team_mines()


def update_team_mines():
    team_mines = TeamMine.objects.all()
    for team_mine in team_mines:
        update_team_mine(team_mine)

    # Broadcast for API clients: tick game loop
    channel_layer = channels.layers.get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        api_consumer.CHANNEL_NAME,
        {
            "type": "event_handler",
            "event_id": api_consumer.ChannelEventType.GAME_LOOP_TICKED.value,
            "data": {},
        }
    )


def update_team_mine(team_mine: TeamMine):
    mine_items = TeamMineItem.objects.filter(team_mine=team_mine)

    miners = {
        mine_item.item: SETTINGS.miner_factors[mine_item.item.name] * mine_item.amount
        for mine_item in mine_items
    }

    balance = min(miners.values())
    profit = sum(get_profit(amount, balance) for amount in miners.values())
    team_mine.money += profit
    team_mine.save()

    # Broadcast for API clients: mine money update
    channel_layer = channels.layers.get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        api_consumer.CHANNEL_NAME,
        {
            "type": api_consumer.CHANNEL_EVENT_HANDLER,
            "event_id": api_consumer.ChannelEventType.MINE_MONEY_UPDATE.value,
            "data": {
                "mine_id": team_mine.mine_id,
                "team_id": team_mine.team_id,
                "money": team_mine.money,
            },
        }
    )


def get_profit(amount: int, balance: int):
    in_balance_profit = balance * SETTINGS.base_miner_per_sec

    if amount == balance:
        return in_balance_profit

    over_balance = (amount - balance) * SETTINGS.base_miner_per_sec

    over_balance_profit = (over_balance) / (
        over_balance**SETTINGS.inbalance_inefficiency
    )

    return in_balance_profit + over_balance_profit


cease_continuous_run: threading.Event | None = None


def start_scheduler(_):
    global cease_continuous_run
    if cease_continuous_run is not None:
        raise ValueError("Game loop is already running")

    logger.info("Started game loop")
    scheduler = Scheduler()
    scheduler.every().second.do(game_loop)
    cease_continuous_run = scheduler.run_continuously()
    return HttpResponse("started!")


def stop_scheduler(_):
    global cease_continuous_run
    if cease_continuous_run is None:
        raise ValueError("Game loop was not running")

    cease_continuous_run.set()
    logger.info("Stopped game loop")
    cease_continuous_run = None
    return HttpResponse("Stopped game loop")


def run_continuously(self, interval=1) -> threading.Event:
    """Continuously run, while executing pending jobs at each elapsed
    time interval.
    @return cease_continuous_run: threading.Event which can be set to
    cease continuous run.
    Please note that it is *intended behavior that run_continuously()
    does not run missed jobs*. For example, if you've registered a job
    that should run every minute and you set a continuous run interval
    of one hour then your job won't be run 60 times at each interval but
    only once.
    """

    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                self.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.setDaemon(True)
    continuous_thread.start()
    return cease_continuous_run


Scheduler.run_continuously = run_continuously
