import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Discussion, Message
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.discussion_id = self.scope['url_route']['kwargs']['discussion_id']
        self.room_group_name = f'chat_{self.discussion_id}'

        # Rejoindre le groupe de discussion
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Quitter le groupe de discussion
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_id = text_data_json['sender_id']

        # Sauvegarder le message dans la base de données
        await self.save_message(sender_id, message)

        # Envoyer le message au groupe de discussion
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': sender_id
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender_id = event['sender_id']

        # Envoyer le message au WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender_id': sender_id
        }))

    @database_sync_to_async
    def save_message(self, sender_id, content):
        discussion = Discussion.objects.get(id=self.discussion_id)
        sender = User.objects.get(id=sender_id)
        Message.objects.create(
            discussion=discussion,
            sender=sender,
            content=content
        )
