"""
API URLs - Central routing for all apps
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import viewsets from each app (will be created)
# from apps.campaigns.views import CampaignViewSet
# from apps.contacts.views import ContactViewSet
# from apps.calls.views import CallViewSet
# from apps.agents.views import AgentStatusViewSet
# from apps.queues.views import QueueViewSet
# from apps.reports.views import ReportViewSet

router = DefaultRouter()

# Register routes (uncomment when viewsets are created)
# router.register(r'campaigns', CampaignViewSet, basename='campaign')
# router.register(r'contacts', ContactViewSet, basename='contact')
# router.register(r'calls', CallViewSet, basename='call')
# router.register(r'agents', AgentStatusViewSet, basename='agent')
# router.register(r'queues', QueueViewSet, basename='queue')
# router.register(r'reports', ReportViewSet, basename='report')

urlpatterns = [
    path('', include(router.urls)),
]
