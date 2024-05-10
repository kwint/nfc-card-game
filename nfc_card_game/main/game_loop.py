from schedule import Scheduler
import threading
import time
from dataclasses import dataclass
from nfc_card_game.main.models.trading import TeamMine, Item


@dataclass
class GameSettings:
    # Base price of item
    base_price: float = 15
    # price increase factor (linear)
    unit_increase_factor: float = 0.01
    inbalance_inefficiency: float = 0.01


def game_loop():
    # update_team_mines()
    pass


def update_team_mines():
    team_mines = TeamMine.objects.all()
    for team_mine in team_mines:
        a, b, c = get_team_mine_workers(team_mine)


def get_team_mine_workers(team_mine: TeamMine) -> tuple[Item, Item, Item]:
    return


def start_scheduler():
    scheduler = Scheduler()
    scheduler.every().second.do(game_loop)
    scheduler.run_continuously()


def run_continuously(self, interval=1):
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
