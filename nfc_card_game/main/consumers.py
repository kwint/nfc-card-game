import json
from channels.generic.websocket import AsyncWebsocketConsumer


class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("broadcast", self.channel_name)

    async def receive(self, text_data):
        if text_data:
            text_data_json = json.loads(text_data)
            message = text_data_json["message"]
            await self.send(text_data=json.dumps({"message": message + "ECHO"}))

    async def action_message(self, event):
        print(event)
        message = event.get("data")
        await self.send(text_data=json.dumps(message))

    async def disconnect(self, close_code):
        print(close_code)
        pass
