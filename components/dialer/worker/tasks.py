"""
OmniVoIP Dialer Worker - Celery Tasks
Worker para marcación automática de llamadas

Funcionalidades:
- Marcación automática (Progressive, Predictive)
- Gestión de reintentos
- Control de pacing
- Actualización de estadísticas
- Integración con AMI y backend
"""

import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import httpx
import redis
from celery import Celery, Task
from celery.schedules import crontab
import json

# Configuración
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
BACKEND_URL = os.getenv("BACKEND_URL", "http://django:8000")
DIALER_API_URL = os.getenv("DIALER_API_URL", "http://dialer-api:8001")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Celery app
app = Celery('dialer_worker')
app.conf.update(
    broker_url=REDIS_URL,
    result_backend=REDIS_URL,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Bogota',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Redis client
redis_client = redis.from_url(REDIS_URL, decode_responses=True)


# ==================== HELPER FUNCTIONS ====================

async def get_http_client():
    """Get HTTP client"""
    return httpx.AsyncClient(timeout=30.0)


async def get_campaign_config(campaign_id: int) -> Optional[Dict[str, Any]]:
    """Get campaign configuration from backend"""
    try:
        async with await get_http_client() as client:
            response = await client.get(f"{BACKEND_URL}/api/campaigns/{campaign_id}/")
            if response.status_code == 200:
                return response.json()
            return None
    except Exception as e:
        logger.error(f"Error getting campaign config: {e}")
        return None


async def get_available_agents(queue_name: str) -> int:
    """Get number of available agents in queue"""
    try:
        async with await get_http_client() as client:
            response = await client.get(f"{BACKEND_URL}/api/queues/{queue_name}/agents/")
            if response.status_code == 200:
                data = response.json()
                # Count agents with status "available" or "idle"
                available = sum(1 for agent in data if agent.get('status') in ['available', 'idle'])
                return available
            return 0
    except Exception as e:
        logger.error(f"Error getting available agents: {e}")
        return 0


async def get_pending_contacts(campaign_id: int, limit: int = 100) -> List[Dict[str, Any]]:
    """Get pending contacts for campaign"""
    try:
        async with await get_http_client() as client:
            response = await client.get(
                f"{BACKEND_URL}/api/contacts/",
                params={
                    'campaign_id': campaign_id,
                    'status': 'pending',
                    'limit': limit,
                    'ordering': '-priority,created_at'
                }
            )
            if response.status_code == 200:
                return response.json().get('results', [])
            return []
    except Exception as e:
        logger.error(f"Error getting contacts: {e}")
        return []


async def originate_call(campaign_id: int, contact_id: int, phone_number: str) -> bool:
    """Originate outbound call via Dialer API"""
    try:
        async with await get_http_client() as client:
            response = await client.post(
                f"{DIALER_API_URL}/calls/originate",
                json={
                    'campaign_id': campaign_id,
                    'contact_id': contact_id,
                    'phone_number': phone_number,
                    'context': 'dialer-outbound',
                    'priority': 1,
                    'timeout': 30
                }
            )
            
            if response.status_code == 200:
                logger.info(f"Call originated: {phone_number} (contact {contact_id})")
                return True
            else:
                logger.error(f"Originate failed: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        logger.error(f"Error originating call: {e}")
        return False


async def update_contact_status(contact_id: int, status: str, attempts: int = None):
    """Update contact status in backend"""
    try:
        data = {'status': status}
        if attempts is not None:
            data['attempts'] = attempts
        
        async with await get_http_client() as client:
            response = await client.patch(
                f"{BACKEND_URL}/api/contacts/{contact_id}/",
                json=data
            )
            return response.status_code == 200
            
    except Exception as e:
        logger.error(f"Error updating contact: {e}")
        return False


def is_campaign_active(campaign_id: int) -> bool:
    """Check if campaign is active in Redis"""
    try:
        status = redis_client.hget(f"campaign:{campaign_id}", "status")
        return status == "active"
    except Exception as e:
        logger.error(f"Error checking campaign status: {e}")
        return False


def get_active_calls_count(campaign_id: int) -> int:
    """Get current active calls count"""
    try:
        count = redis_client.hget(f"campaign:{campaign_id}", "active_calls")
        return int(count) if count else 0
    except Exception as e:
        logger.error(f"Error getting active calls: {e}")
        return 0


def should_dial(campaign_config: Dict[str, Any], available_agents: int, active_calls: int) -> bool:
    """Determine if we should dial more calls based on pacing"""
    dial_mode = campaign_config.get('dial_mode', 'progressive')
    pacing_ratio = campaign_config.get('pacing_ratio', 1.2)
    max_concurrent = campaign_config.get('max_concurrent_calls', 50)
    
    # Check max concurrent limit
    if active_calls >= max_concurrent:
        return False
    
    # Check if we have available agents
    if available_agents == 0:
        return False
    
    # Calculate how many calls we should have
    if dial_mode == 'preview':
        # Preview mode: no automatic dialing
        return False
    
    elif dial_mode == 'progressive':
        # Progressive: 1 call per available agent
        target_calls = available_agents
        return active_calls < target_calls
    
    elif dial_mode in ['predictive', 'power']:
        # Predictive/Power: ratio * available agents
        target_calls = int(available_agents * pacing_ratio)
        return active_calls < target_calls
    
    return False


# ==================== CELERY TASKS ====================

@app.task(bind=True, name='dialer.process_campaign')
def process_campaign_task(self, campaign_id: int):
    """
    Main task to process campaign dialing
    Runs periodically for each active campaign
    """
    logger.info(f"Processing campaign {campaign_id}")
    
    # Run async code
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(process_campaign(campaign_id))
    loop.close()
    
    return result


async def process_campaign(campaign_id: int) -> Dict[str, Any]:
    """Process campaign dialing logic"""
    
    # Check if campaign is active
    if not is_campaign_active(campaign_id):
        logger.info(f"Campaign {campaign_id} is not active, skipping")
        return {'status': 'skipped', 'reason': 'not_active'}
    
    # Get campaign configuration
    campaign_config = await get_campaign_config(campaign_id)
    if not campaign_config:
        logger.error(f"Campaign {campaign_id} configuration not found")
        return {'status': 'error', 'reason': 'config_not_found'}
    
    queue_name = campaign_config.get('queue_name')
    
    # Get available agents
    available_agents = await get_available_agents(queue_name)
    logger.info(f"Campaign {campaign_id}: {available_agents} agents available")
    
    # Get active calls count
    active_calls = get_active_calls_count(campaign_id)
    logger.info(f"Campaign {campaign_id}: {active_calls} active calls")
    
    # Check if we should dial more calls
    if not should_dial(campaign_config, available_agents, active_calls):
        logger.info(f"Campaign {campaign_id}: pacing limit reached or no agents available")
        return {
            'status': 'ok',
            'dialed': 0,
            'reason': 'pacing_limit',
            'available_agents': available_agents,
            'active_calls': active_calls
        }
    
    # Calculate how many calls to make
    dial_mode = campaign_config.get('dial_mode', 'progressive')
    pacing_ratio = campaign_config.get('pacing_ratio', 1.2)
    max_concurrent = campaign_config.get('max_concurrent_calls', 50)
    
    if dial_mode == 'progressive':
        calls_to_make = available_agents - active_calls
    else:  # predictive or power
        target_calls = int(available_agents * pacing_ratio)
        calls_to_make = min(target_calls - active_calls, max_concurrent - active_calls)
    
    calls_to_make = max(0, calls_to_make)
    
    if calls_to_make == 0:
        return {
            'status': 'ok',
            'dialed': 0,
            'available_agents': available_agents,
            'active_calls': active_calls
        }
    
    logger.info(f"Campaign {campaign_id}: attempting to dial {calls_to_make} calls")
    
    # Get pending contacts
    contacts = await get_pending_contacts(campaign_id, limit=calls_to_make)
    
    if not contacts:
        logger.info(f"Campaign {campaign_id}: no pending contacts")
        return {
            'status': 'ok',
            'dialed': 0,
            'reason': 'no_contacts',
            'available_agents': available_agents,
            'active_calls': active_calls
        }
    
    # Dial calls
    dialed = 0
    failed = 0
    
    for contact in contacts[:calls_to_make]:
        contact_id = contact['id']
        phone_number = contact['phone_number']
        
        # Update contact to "dialing"
        await update_contact_status(contact_id, 'dialing')
        
        # Originate call
        success = await originate_call(campaign_id, contact_id, phone_number)
        
        if success:
            dialed += 1
        else:
            failed += 1
            # Update contact back to pending or failed
            attempts = contact.get('attempts', 0) + 1
            max_retries = campaign_config.get('max_retries', 3)
            
            if attempts >= max_retries:
                await update_contact_status(contact_id, 'failed', attempts)
            else:
                await update_contact_status(contact_id, 'pending', attempts)
        
        # Small delay between calls
        await asyncio.sleep(0.1)
    
    logger.info(f"Campaign {campaign_id}: dialed {dialed} calls, {failed} failed")
    
    return {
        'status': 'ok',
        'dialed': dialed,
        'failed': failed,
        'available_agents': available_agents,
        'active_calls': active_calls
    }


@app.task(name='dialer.retry_contacts')
def retry_contacts_task(campaign_id: int):
    """
    Task to retry failed contacts
    Runs periodically to retry contacts that failed before
    """
    logger.info(f"Retrying contacts for campaign {campaign_id}")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(retry_contacts(campaign_id))
    loop.close()
    
    return result


async def retry_contacts(campaign_id: int) -> Dict[str, Any]:
    """Retry contacts that need retrying"""
    
    # Get campaign config
    campaign_config = await get_campaign_config(campaign_id)
    if not campaign_config:
        return {'status': 'error', 'reason': 'config_not_found'}
    
    retry_delay = campaign_config.get('retry_delay', 300)  # seconds
    max_retries = campaign_config.get('max_retries', 3)
    
    # Get contacts that need retry
    try:
        async with await get_http_client() as client:
            # Get contacts with status='no_answer' or 'busy' and last_attempt > retry_delay ago
            cutoff_time = (datetime.now() - timedelta(seconds=retry_delay)).isoformat()
            
            response = await client.get(
                f"{BACKEND_URL}/api/contacts/",
                params={
                    'campaign_id': campaign_id,
                    'status': 'no_answer,busy',
                    'last_attempt__lt': cutoff_time,
                    f'attempts__lt': max_retries,
                    'limit': 50
                }
            )
            
            if response.status_code != 200:
                return {'status': 'error', 'reason': 'backend_error'}
            
            contacts = response.json().get('results', [])
            
            # Reset to pending
            reset_count = 0
            for contact in contacts:
                success = await update_contact_status(contact['id'], 'pending')
                if success:
                    reset_count += 1
            
            logger.info(f"Campaign {campaign_id}: reset {reset_count} contacts for retry")
            
            return {
                'status': 'ok',
                'reset_count': reset_count
            }
            
    except Exception as e:
        logger.error(f"Error retrying contacts: {e}")
        return {'status': 'error', 'reason': str(e)}


@app.task(name='dialer.update_statistics')
def update_statistics_task(campaign_id: int):
    """
    Update campaign statistics
    Runs periodically to update stats in Redis and backend
    """
    logger.info(f"Updating statistics for campaign {campaign_id}")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(update_statistics(campaign_id))
    loop.close()
    
    return result


async def update_statistics(campaign_id: int) -> Dict[str, Any]:
    """Update campaign statistics"""
    
    try:
        async with await get_http_client() as client:
            # Get stats from Dialer API
            response = await client.get(f"{DIALER_API_URL}/campaigns/{campaign_id}/stats")
            
            if response.status_code == 200:
                stats = response.json()
                
                # Update in backend
                await client.post(
                    f"{BACKEND_URL}/api/campaigns/{campaign_id}/update_stats/",
                    json=stats
                )
                
                logger.info(f"Campaign {campaign_id}: stats updated")
                return {'status': 'ok', 'stats': stats}
            else:
                return {'status': 'error', 'reason': 'api_error'}
                
    except Exception as e:
        logger.error(f"Error updating statistics: {e}")
        return {'status': 'error', 'reason': str(e)}


@app.task(name='dialer.cleanup_campaign')
def cleanup_campaign_task(campaign_id: int):
    """
    Cleanup campaign when completed
    """
    logger.info(f"Cleaning up campaign {campaign_id}")
    
    try:
        # Remove from Redis
        redis_client.delete(f"campaign:{campaign_id}")
        
        # Could also archive CDRs, cleanup temp files, etc.
        
        logger.info(f"Campaign {campaign_id} cleanup completed")
        return {'status': 'ok'}
        
    except Exception as e:
        logger.error(f"Error cleaning up campaign: {e}")
        return {'status': 'error', 'reason': str(e)}


# ==================== PERIODIC TASKS ====================

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Setup periodic tasks"""
    
    # Process all active campaigns every 10 seconds
    sender.add_periodic_task(
        10.0,
        process_active_campaigns.s(),
        name='process_active_campaigns_every_10s'
    )
    
    # Retry failed contacts every 5 minutes
    sender.add_periodic_task(
        300.0,
        retry_all_campaigns.s(),
        name='retry_contacts_every_5m'
    )
    
    # Update statistics every minute
    sender.add_periodic_task(
        60.0,
        update_all_statistics.s(),
        name='update_statistics_every_1m'
    )


@app.task(name='dialer.process_active_campaigns')
def process_active_campaigns():
    """Process all active campaigns"""
    try:
        # Get all campaign keys from Redis
        campaign_keys = redis_client.keys("campaign:*")
        
        active_campaigns = []
        for key in campaign_keys:
            status = redis_client.hget(key, "status")
            if status == "active":
                campaign_id = int(key.split(":")[1])
                active_campaigns.append(campaign_id)
        
        logger.info(f"Processing {len(active_campaigns)} active campaigns")
        
        # Process each campaign
        for campaign_id in active_campaigns:
            process_campaign_task.delay(campaign_id)
        
        return {
            'status': 'ok',
            'active_campaigns': len(active_campaigns)
        }
        
    except Exception as e:
        logger.error(f"Error processing active campaigns: {e}")
        return {'status': 'error', 'reason': str(e)}


@app.task(name='dialer.retry_all_campaigns')
def retry_all_campaigns():
    """Retry contacts for all active campaigns"""
    try:
        campaign_keys = redis_client.keys("campaign:*")
        
        active_campaigns = []
        for key in campaign_keys:
            status = redis_client.hget(key, "status")
            if status == "active":
                campaign_id = int(key.split(":")[1])
                active_campaigns.append(campaign_id)
        
        for campaign_id in active_campaigns:
            retry_contacts_task.delay(campaign_id)
        
        return {
            'status': 'ok',
            'campaigns_processed': len(active_campaigns)
        }
        
    except Exception as e:
        logger.error(f"Error retrying campaigns: {e}")
        return {'status': 'error', 'reason': str(e)}


@app.task(name='dialer.update_all_statistics')
def update_all_statistics():
    """Update statistics for all active campaigns"""
    try:
        campaign_keys = redis_client.keys("campaign:*")
        
        for key in campaign_keys:
            campaign_id = int(key.split(":")[1])
            update_statistics_task.delay(campaign_id)
        
        return {
            'status': 'ok',
            'campaigns_updated': len(campaign_keys)
        }
        
    except Exception as e:
        logger.error(f"Error updating statistics: {e}")
        return {'status': 'error', 'reason': str(e)}


# ==================== EVENT HANDLERS ====================

@app.task(name='dialer.handle_call_event')
def handle_call_event(event_type: str, data: Dict[str, Any]):
    """
    Handle call events from Asterisk (via AMI/ARI)
    
    Event types:
    - call_answered
    - call_completed
    - call_failed
    - agent_available
    - agent_busy
    """
    logger.info(f"Handling call event: {event_type}")
    
    campaign_id = data.get('campaign_id')
    contact_id = data.get('contact_id')
    
    if event_type == 'call_answered':
        # Decrement active calls
        if campaign_id:
            redis_client.hincrby(f"campaign:{campaign_id}", "active_calls", -1)
            redis_client.hincrby(f"campaign:{campaign_id}", "answered_calls", 1)
        
        # Update contact status
        if contact_id:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(update_contact_status(contact_id, 'answered'))
            loop.close()
    
    elif event_type == 'call_completed':
        # Update contact
        if contact_id:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(update_contact_status(contact_id, 'completed'))
            loop.close()
    
    elif event_type == 'call_failed':
        # Decrement active calls
        if campaign_id:
            redis_client.hincrby(f"campaign:{campaign_id}", "active_calls", -1)
        
        # Update contact for retry
        if contact_id:
            disposition = data.get('disposition', 'failed')
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(update_contact_status(contact_id, disposition))
            loop.close()
    
    elif event_type in ['agent_available', 'agent_busy']:
        # Trigger campaign processing
        if campaign_id:
            process_campaign_task.delay(campaign_id)
    
    return {'status': 'ok', 'event': event_type}


if __name__ == '__main__':
    app.start()
