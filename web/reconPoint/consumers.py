import json

from channels.generic.websocket import AsyncWebsocketConsumer


class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        # For now, just echo back
        await self.send(
            text_data=json.dumps({"message": "Real-time update placeholder"})
        )

class AICrewConsumer(AsyncWebsocketConsumer):
    """Consumer for AI Crew real-time updates."""
    
    async def connect(self):
        self.project_id = self.scope["url_route"]["kwargs"].get("project_id")
        self.room_group_name = f"ai_crew_{self.project_id}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def crew_update(self, event):
        """Receive message from room group."""
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event["data"]))
