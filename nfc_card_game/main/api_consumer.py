import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ApiConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("broadcast", self.channel_name)
        print("Dashboard client connected to API socket")

        await self.send(text_data='{"data": "test packet"}')

    async def receive(self, text_data):
        if text_data:
            text_data_json = json.loads(text_data)
            message = text_data_json["message"]
            await self.send(text_data=json.dumps({"message": message + "ECHO"}))

    async def action_message(self, event):
        message = event.get("data")
        await self.send(text_data=json.dumps(message))

    async def disconnect(self, close_code):
        print(f"Dashboard client disconnected from API socket (code: {close_code})")
        pass
