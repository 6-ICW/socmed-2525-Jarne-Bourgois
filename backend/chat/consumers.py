import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from .models import Channel, Message, UserProfile, ServerMember
from .serializers import MessageSerializer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.channel_id = self.scope['url_route']['kwargs']['channel_id']
        self.room_group_name = f'chat_{self.channel_id}'
        user = self.scope.get('user')

        if not user or isinstance(user, AnonymousUser):
            await self.close()
            return

        has_access = await self.check_access(user, self.channel_id)
        if not has_access:
            await self.close()
            return

        self.user = user
        await self.update_online_status(user, True)
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        if hasattr(self, 'user'):
            await self.update_online_status(self.user, False)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action')

            if action == 'heartbeat':
                await self.update_online_status(self.user, True)
                return

            if action == 'send_message':
                content = data.get('content', '').strip()
                if not content:
                    return
                message = await self.create_message(self.user, self.channel_id, content)
                msg_data = await self.serialize_message(message)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {'type': 'chat_message', 'message': msg_data}
                )

            elif action == 'edit_message':
                message_id = data.get('message_id')
                content = data.get('content', '').strip()
                if not content or not message_id:
                    return
                message = await self.edit_message(self.user, message_id, content)
                if message:
                    msg_data = await self.serialize_message(message)
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {'type': 'message_edited', 'message': msg_data}
                    )

            elif action == 'delete_message':
                message_id = data.get('message_id')
                if not message_id:
                    return
                deleted = await self.delete_message(self.user, message_id, self.channel_id)
                if deleted:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {'type': 'message_deleted', 'message_id': message_id}
                    )
            elif action == "restore_message":
                await self.restore_message(data["message_id"] )
        except Exception as e:
            print(f'WebSocket error: {e}')

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({'type': 'message', 'message': event['message']}))

    async def message_edited(self, event):
        await self.send(text_data=json.dumps({'type': 'message_edited', 'message': event['message']}))

    async def message_deleted(self, event):
        await self.send(text_data=json.dumps({'type': 'message_deleted', 'message_id': event['message_id']}))

    async def message_restored(self, event):
        await self.send(
            text_data=json.dumps({
                'type': 'message_restored',
                'message': event['message']
            })
        )

    @database_sync_to_async
    def check_access(self, user, channel_id):
        try:
            channel = Channel.objects.get(pk=channel_id)
            return ServerMember.objects.filter(server=channel.server, user=user).exists()
        except Channel.DoesNotExist:
            return False

    @database_sync_to_async
    def update_online_status(self, user, online):
        profile, _ = UserProfile.objects.get_or_create(user=user)
        if online:
            profile.last_seen = timezone.now()
        else:
            from datetime import timedelta
            profile.last_seen = timezone.now() - timedelta(minutes=10)
        profile.save(update_fields=['last_seen'])

    @database_sync_to_async
    def create_message(self, user, channel_id, content):
        channel = Channel.objects.get(pk=channel_id)
        return Message.objects.create(channel=channel, author=user, content=content)

    @database_sync_to_async
    def edit_message(self, user, message_id, content):
        try:
            msg = Message.objects.get(pk=message_id, author=user)
            msg.content = content
            msg.is_edited = True
            msg.save()
            return msg
        except Message.DoesNotExist:
            return None

    @database_sync_to_async
    def delete_message(self, user, message_id, channel_id):
        try:
            msg = Message.objects.select_related('channel__server').get(pk=message_id)
            is_author = msg.author == user
            is_admin = ServerMember.objects.filter(
                server=msg.channel.server, user=user, role__in=['owner', 'admin']
            ).exists()
            if is_author or is_admin:
                msg.is_deleted = True
                msg.deleted_at = timezone.now()
                msg.save()
                return True
            return False
        except Message.DoesNotExist:
            return False

    @database_sync_to_async
    def restore_message_db(self, message_id):

         msg = Message.objects.get(id=message_id)

         if msg.author != self.scope["user"]:
            return None

         msg.is_deleted = False
         msg.deleted_at = None
         msg.save()

         return msg

    async def restore_message(self, message_id):

        msg = await self.restore_message_db(message_id)

        if not msg:
            return

        msg_data = await self.serialize_message(msg)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'message_restored',
                'message': msg_data
            }
        )
    @database_sync_to_async
    def serialize_message(self, message):
        message.refresh_from_db()
        msg = Message.objects.select_related('author').get(pk=message.pk)
        return MessageSerializer(msg).data