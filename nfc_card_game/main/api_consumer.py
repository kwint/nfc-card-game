import asyncio
import json
from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from enum import Enum

from . import api


class PacketServerType(Enum):
    SET_MINE = 1

class PacketClientType(Enum):
    GAME_STATE = 1


class ApiConsumer(AsyncJsonWebsocketConsumer):
    # Selected mine ID by client
    mine_id = None

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("broadcast", self.channel_name)
        print("Dashboard client connected to API socket")

        # Share current game state over websocket
        await self.send_game_state()


    async def receive_json(self, content):
        await self.handle_raw_packet(content)


    async def action_message(self, event):
        message = event.get("data")
        await self.send(text_data=json.dumps(message))


    async def disconnect(self, close_code):
        print(f"Dashboard client disconnected from API socket (code: {close_code})")
        pass


    async def send_packet(self, packet_id: PacketClientType, data: dict):
        await self.send_json({"packet_id": packet_id.value, "data": data})


    async def send_game_state(self):
        async_describe_mines = sync_to_async(api.describe_mines)
        mines = await async_describe_mines()
        await self.send_packet(PacketClientType.GAME_STATE, mines)


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
                return;


    async def handle_set_mine(self, data: dict):
        self.mine_id = data["mine_id"]
        print(f"Client selected mine {self.mine_id}")
