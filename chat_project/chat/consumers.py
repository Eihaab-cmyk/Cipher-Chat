import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f"chat_{self.chat_id}"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        
        # typing handling
        if data.get("type") == "typing":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                     "type": "typing_indicator",
                    "username": self.scope["user"].username,
                }
            )
            return
        
        # message handling
        from chat.models import Message, Chat
        message = data['message']
        iv = data.get('iv')
        username = self.scope["user"].username
       
        chat = await database_sync_to_async(Chat.objects.get)(id=self.chat_id)
        sender = self.scope['user']
        await database_sync_to_async(Message.objects.create)(
            chat=chat, sender=sender, content=data['message'], iv=data['iv']
        )
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'iv': iv,
            }
        )

    async def typing_indicator(self, event):
        await self.send(text_data=json.dumps({
            "type": "typing",
            "username": event["username"]
        }))

    async def chat_message(self, event):
        message = event['message']
        iv = event.get('iv')
        username = event['username']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'iv': iv,
            'username': username
        }))