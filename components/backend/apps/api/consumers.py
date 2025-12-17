"""
WebSocket consumers for real-time updates
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class DashboardConsumer(AsyncWebsocketConsumer):
    """Real-time dashboard updates"""
    
    async def connect(self):
        self.room_group_name = 'dashboard'
        
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
    
    async def receive(self, text_data):
        """Receive message from WebSocket"""
        pass
    
    async def dashboard_update(self, event):
        """Send dashboard update to WebSocket"""
        await self.send(text_data=json.dumps(event['data']))


class AgentConsumer(AsyncWebsocketConsumer):
    """Real-time agent updates"""
    
    async def connect(self):
        self.agent_id = self.scope['url_route']['kwargs']['agent_id']
        self.room_group_name = f'agent_{self.agent_id}'
        
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
    
    async def agent_update(self, event):
        """Send agent update"""
        await self.send(text_data=json.dumps(event['data']))


class QueueConsumer(AsyncWebsocketConsumer):
    """Real-time queue updates"""
    
    async def connect(self):
        self.queue_id = self.scope['url_route']['kwargs']['queue_id']
        self.room_group_name = f'queue_{self.queue_id}'
        
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
    
    async def queue_update(self, event):
        """Send queue update"""
        await self.send(text_data=json.dumps(event['data']))


class CampaignConsumer(AsyncWebsocketConsumer):
    """Real-time campaign updates"""
    
    async def connect(self):
        self.campaign_id = self.scope['url_route']['kwargs']['campaign_id']
        self.room_group_name = f'campaign_{self.campaign_id}'
        
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
    
    async def campaign_update(self, event):
        """Send campaign update"""
        await self.send(text_data=json.dumps(event['data']))
