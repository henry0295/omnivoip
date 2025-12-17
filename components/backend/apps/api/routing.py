"""
WebSocket routing for real-time updates
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/dashboard/$', consumers.DashboardConsumer.as_asgi()),
    re_path(r'ws/agent/(?P<agent_id>\w+)/$', consumers.AgentConsumer.as_asgi()),
    re_path(r'ws/queue/(?P<queue_id>\w+)/$', consumers.QueueConsumer.as_asgi()),
    re_path(r'ws/campaign/(?P<campaign_id>\w+)/$', consumers.CampaignConsumer.as_asgi()),
]
