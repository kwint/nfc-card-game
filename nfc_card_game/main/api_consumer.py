import asyncio
import json
from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from enum import Enum

from .models.trading import Mine
from . import api

CHANNEL_NAME = "api-state-broadcast"
CHANNEL_EVENT_HANDLER = "event_handler"

class PacketServerType(Enum):
    SET_MINE = 1

class PacketClientType(Enum):
    GAME_STATE = 1
    MINE_STATE = 2
    MINE_MONEY_UPDATE = 3
    MINE_MINERS_ADDED = 4

class ChannelEventType(Enum):
    GAME_LOOP_TICKED = 1
    MINE_MONEY_UPDATE = 2
    MINE_MINERS_ADDED = 3


class ApiConsumer(AsyncJsonWebsocketConsumer):
    # Selected mine ID by client
    mine_id = None

    async def connect(self):
        await self.accept()

        # Connect to API state broadcasting channel
        await self.channel_layer.group_add(CHANNEL_NAME, self.channel_name)

        print("Dashboard client connected to API socket")

        # Share current game state over websocket
        # TODO: remove this? only send mine state after selecting mine?
        await self.send_game_state()


    async def receive_json(self, content):
        await self.handle_raw_packet(content)


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(CHANNEL_NAME, self.channel_name)
        print(f"Dashboard client disconnected from API socket (code: {close_code})")


    async def send_packet(self, packet_id: PacketClientType, data: dict):
        await self.send_json({"packet_id": packet_id.value, "data": data})


    async def send_game_state(self):
        async_describe_mines = sync_to_async(api.describe_mines)
        mines = await async_describe_mines()
        await self.send_packet(PacketClientType.GAME_STATE, mines)


    async def send_mine_state(self, mine_id: int = None):
        async_describe_mine = sync_to_async(api.describe_mine)
        mines = await async_describe_mine(mine_id or self.mine_id)
        await self.send_packet(PacketClientType.MINE_STATE, mines)


    async def send_mine_money_update(self, data: dict):
        await self.send_packet(PacketClientType.MINE_MONEY_UPDATE, data)


    async def send_mine_miners_added(self, data: dict):
        await self.send_packet(PacketClientType.MINE_MINERS_ADDED, data)


    async def handle_raw_packet(self, data: dict):
        if "packet_id" not in data:
            print(f"Got malformed packet, no packet_id: f{data}")
            return
        if "data" not in data:
            print(f"Got malformed packet, no data: f{data}")
            return
        await self.handle_packet(data["packet_id"], data["data"])


    async def handle_packet(self, packet_id: PacketServerType, data: dict):
        if packet_id not in [p.value for p in PacketServerType]:
            print(f"Got malformed packet, unknown packet ID: {packet_id}")

        match packet_id:
            case PacketServerType.SET_MINE.value:
                await self.handle_set_mine(data)
            case _:
                print(f"Failed to handle packet with ID {packet_id}, missing handler?")
                return


    async def handle_set_mine(self, data: dict):
        self.mine_id = data["mine_id"]
        print(f"Client selected mine {self.mine_id}")

        # Update client with latest mine state
        await self.send_mine_state()


    async def event_handler(self, event):
        await self.handle_raw_event(event)


    async def handle_raw_event(self, event):
        if "event_id" not in event:
            print(f"Got malformed channel event, no event_id: f{event}")
            return
        if "data" not in event:
            print(f"Got malformed channel event, no data: f{event}")
            return
        await self.handle_event(event["event_id"], event["data"])


    async def handle_event(self, event_id: ChannelEventType, data: dict):
        if event_id not in [p.value for p in ChannelEventType]:
            print(f"Got malformed channel event, unknown event ID: {event_id}")

        match event_id:
            case ChannelEventType.GAME_LOOP_TICKED.value:
                #await self.send_mine_state()
                pass
            case ChannelEventType.MINE_MONEY_UPDATE.value:
                if self.mine_id == data["mine_id"]:
                    await self.send_mine_money_update(data)
            case ChannelEventType.MINE_MINERS_ADDED.value:
                if self.mine_id == data["mine_id"]:
                    await self.send_mine_miners_added(data)
            case _:
                print(f"Ignored event with ID {event_id}, no handler configured")
                return
