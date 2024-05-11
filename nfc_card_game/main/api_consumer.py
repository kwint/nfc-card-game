import asyncio
import json
from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from . import api

PACKET_CLIENT_GAME_STATE = 1

class ApiConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("broadcast", self.channel_name)
        print("Dashboard client connected to API socket")

        # Share current game state over websocket
        await self.send_game_state()


    async def receive_json(self, content):
        print("Received JSON message over API websocket: ", content)


    async def action_message(self, event):
        message = event.get("data")
        await self.send(text_data=json.dumps(message))


    async def disconnect(self, close_code):
        print(f"Dashboard client disconnected from API socket (code: {close_code})")
        pass


    async def send_packet(self, packet_id: int, data: dict):
        await self.send_json({"packet_id": packet_id, "data": data})


    async def send_game_state(self):
        async_describe_mines = sync_to_async(api.describe_mines)
        mines = await async_describe_mines()
        await self.send_packet(PACKET_CLIENT_GAME_STATE, mines)
