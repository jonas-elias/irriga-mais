import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.pivo_key = self.scope["url_route"]["kwargs"]["pivo_key"]
        self.group_name = "pivo_%s" % self.pivo_key

        if self.channel_layer:
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            print("Erro: self.channel_layer não está definido corretamente.")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "pivo_message",
                "pivo_key": text_data['pivo_key'],
                "evento_id": text_data['evento_id']
            },
        )

    async def pivo_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "pivo_key": event['pivo_key'],
                    "evento_id": event['evento_id'],
                }
            )
        )
