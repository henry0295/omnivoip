"""
OmniVoIP Dialer API - FastAPI Application
Marcador Predictivo para Contact Center

Funcionalidades:
- Gestión de campañas de marcación
- Originate calls via AMI
- Estadísticas en tiempo real
- Control de pacing (llamadas por agente)
- Integración con backend Django
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import redis.asyncio as aioredis
import httpx
import logging
import os

# Configuración
API_VERSION = "1.0.0"
API_TITLE = "OmniVoIP Dialer API"
API_DESCRIPTION = "API REST para marcador predictivo de llamadas salientes"

# Variables de entorno
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/1")
BACKEND_URL = os.getenv("BACKEND_URL", "http://django:8000")
ASTERISK_AMI_HOST = os.getenv("ASTERISK_AMI_HOST", "asterisk")
ASTERISK_AMI_PORT = int(os.getenv("ASTERISK_AMI_PORT", "5038"))
ASTERISK_AMI_USER = os.getenv("ASTERISK_AMI_USER", "dialer")
ASTERISK_AMI_SECRET = os.getenv("ASTERISK_AMI_SECRET", "dialerpass123")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection pool
redis_pool = None


# ==================== MODELS ====================

class CampaignStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CallStatus(str, Enum):
    PENDING = "pending"
    DIALING = "dialing"
    RINGING = "ringing"
    ANSWERED = "answered"
    BUSY = "busy"
    NO_ANSWER = "no_answer"
    FAILED = "failed"
    COMPLETED = "completed"


class DialMode(str, Enum):
    PREVIEW = "preview"      # Agente confirma antes de llamar
    PROGRESSIVE = "progressive"  # 1 llamada por agente disponible
    PREDICTIVE = "predictive"    # Múltiples llamadas por agente (ratio)
    POWER = "power"         # Marcación masiva


class CampaignCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    dial_mode: DialMode = DialMode.PROGRESSIVE
    queue_name: str = Field(..., example="sales")
    trunk: str = Field(..., example="trunk-out")
    caller_id: str = Field(..., example="5551234567")
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_delay: int = Field(default=300, ge=60, description="Segundos entre reintentos")
    pacing_ratio: float = Field(default=1.2, ge=1.0, le=5.0, description="Llamadas por agente")
    max_concurrent_calls: int = Field(default=50, ge=1, le=500)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    days_of_week: List[int] = Field(default=[0, 1, 2, 3, 4], description="0=Lun, 6=Dom")

    @validator('start_time', 'end_time')
    def validate_times(cls, v):
        if v and v < datetime.now():
            raise ValueError("Time cannot be in the past")
        return v


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[CampaignStatus] = None
    dial_mode: Optional[DialMode] = None
    pacing_ratio: Optional[float] = None
    max_concurrent_calls: Optional[int] = None


class ContactCreate(BaseModel):
    campaign_id: int
    phone_number: str = Field(..., regex=r'^\+?[0-9]{10,15}$')
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    custom_data: Optional[Dict[str, Any]] = None
    priority: int = Field(default=5, ge=1, le=10)
    timezone: str = Field(default="America/Bogota")


class CallOriginate(BaseModel):
    campaign_id: int
    contact_id: int
    phone_number: str
    context: str = "dialer-outbound"
    priority: int = 1
    timeout: int = 30
    variables: Optional[Dict[str, str]] = None


class CampaignStats(BaseModel):
    campaign_id: int
    total_contacts: int
    pending_calls: int
    active_calls: int
    completed_calls: int
    answered_calls: int
    no_answer: int
    busy: int
    failed: int
    answer_rate: float
    average_duration: float
    calls_per_hour: float
    agents_available: int
    agents_busy: int


# ==================== DEPENDENCIES ====================

async def get_redis():
    """Get Redis connection"""
    global redis_pool
    if redis_pool is None:
        redis_pool = await aioredis.from_url(
            REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=10
        )
    return redis_pool


async def get_backend_client():
    """Get HTTP client for backend"""
    async with httpx.AsyncClient(base_url=BACKEND_URL, timeout=10.0) as client:
        yield client


# ==================== AMI CONNECTION ====================

class AsteriskAMI:
    """Asterisk Manager Interface Client"""
    
    def __init__(self):
        self.host = ASTERISK_AMI_HOST
        self.port = ASTERISK_AMI_PORT
        self.username = ASTERISK_AMI_USER
        self.secret = ASTERISK_AMI_SECRET
        self.reader = None
        self.writer = None
        self.connected = False
    
    async def connect(self):
        """Connect to AMI"""
        try:
            self.reader, self.writer = await asyncio.open_connection(
                self.host, self.port
            )
            
            # Read welcome message
            await self.reader.readline()
            
            # Login
            login_action = (
                f"Action: Login\r\n"
                f"Username: {self.username}\r\n"
                f"Secret: {self.secret}\r\n"
                f"\r\n"
            )
            self.writer.write(login_action.encode())
            await self.writer.drain()
            
            # Read response
            response = await self._read_response()
            if "Success" in response.get("Response", ""):
                self.connected = True
                logger.info("AMI connected successfully")
                return True
            else:
                logger.error(f"AMI login failed: {response}")
                return False
                
        except Exception as e:
            logger.error(f"AMI connection error: {e}")
            return False
    
    async def _read_response(self) -> Dict[str, str]:
        """Read AMI response"""
        response = {}
        while True:
            line = await self.reader.readline()
            line = line.decode().strip()
            
            if not line:
                break
            
            if ": " in line:
                key, value = line.split(": ", 1)
                response[key] = value
        
        return response
    
    async def originate(self, channel: str, context: str, exten: str, 
                       priority: int = 1, timeout: int = 30, 
                       caller_id: str = "", variables: Dict[str, str] = None) -> Dict[str, Any]:
        """Originate a call"""
        if not self.connected:
            await self.connect()
        
        # Build variables string
        var_str = ""
        if variables:
            var_str = ",".join([f"{k}={v}" for k, v in variables.items()])
        
        action = (
            f"Action: Originate\r\n"
            f"Channel: {channel}\r\n"
            f"Context: {context}\r\n"
            f"Exten: {exten}\r\n"
            f"Priority: {priority}\r\n"
            f"Timeout: {timeout * 1000}\r\n"  # Milliseconds
        )
        
        if caller_id:
            action += f"CallerID: {caller_id}\r\n"
        
        if var_str:
            action += f"Variable: {var_str}\r\n"
        
        action += "\r\n"
        
        try:
            self.writer.write(action.encode())
            await self.writer.drain()
            
            response = await self._read_response()
            return response
            
        except Exception as e:
            logger.error(f"Originate error: {e}")
            return {"Response": "Error", "Message": str(e)}
    
    async def disconnect(self):
        """Disconnect from AMI"""
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
            self.connected = False
            logger.info("AMI disconnected")


# Global AMI instance
ami = AsteriskAMI()


# ==================== STARTUP/SHUTDOWN ====================

@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup"""
    logger.info("Starting Dialer API...")
    
    # Connect to AMI
    await ami.connect()
    
    # Initialize Redis
    await get_redis()
    
    logger.info("Dialer API started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Dialer API...")
    
    # Disconnect AMI
    await ami.disconnect()
    
    # Close Redis
    if redis_pool:
        await redis_pool.close()
    
    logger.info("Dialer API shutdown complete")


# ==================== HEALTH CHECK ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": API_VERSION,
        "timestamp": datetime.now().isoformat(),
        "ami_connected": ami.connected
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


# ==================== CAMPAIGNS ====================

@app.post("/campaigns", status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign: CampaignCreate,
    backend: httpx.AsyncClient = Depends(get_backend_client)
):
    """Create a new dialing campaign"""
    try:
        # Forward to Django backend
        response = await backend.post("/api/campaigns/", json=campaign.dict())
        response.raise_for_status()
        
        campaign_data = response.json()
        
        # Initialize campaign in Redis
        redis_client = await get_redis()
        campaign_key = f"campaign:{campaign_data['id']}"
        
        await redis_client.hset(campaign_key, mapping={
            "status": CampaignStatus.DRAFT,
            "active_calls": 0,
            "total_calls": 0,
            "answered_calls": 0,
            "created_at": datetime.now().isoformat()
        })
        
        logger.info(f"Campaign created: {campaign_data['id']}")
        return campaign_data
        
    except httpx.HTTPError as e:
        logger.error(f"Backend error: {e}")
        raise HTTPException(status_code=500, detail="Backend communication error")


@app.get("/campaigns/{campaign_id}")
async def get_campaign(
    campaign_id: int,
    backend: httpx.AsyncClient = Depends(get_backend_client)
):
    """Get campaign details"""
    try:
        response = await backend.get(f"/api/campaigns/{campaign_id}/")
        response.raise_for_status()
        return response.json()
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Campaign not found")
        raise HTTPException(status_code=500, detail="Backend error")


@app.patch("/campaigns/{campaign_id}")
async def update_campaign(
    campaign_id: int,
    campaign_update: CampaignUpdate,
    backend: httpx.AsyncClient = Depends(get_backend_client)
):
    """Update campaign"""
    try:
        response = await backend.patch(
            f"/api/campaigns/{campaign_id}/",
            json=campaign_update.dict(exclude_unset=True)
        )
        response.raise_for_status()
        
        # Update Redis if status changed
        if campaign_update.status:
            redis_client = await get_redis()
            await redis_client.hset(
                f"campaign:{campaign_id}",
                "status",
                campaign_update.status
            )
        
        return response.json()
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Campaign not found")
        raise HTTPException(status_code=500, detail="Backend error")


@app.post("/campaigns/{campaign_id}/start")
async def start_campaign(
    campaign_id: int,
    backend: httpx.AsyncClient = Depends(get_backend_client)
):
    """Start campaign"""
    try:
        # Update status to active
        response = await backend.patch(
            f"/api/campaigns/{campaign_id}/",
            json={"status": CampaignStatus.ACTIVE}
        )
        response.raise_for_status()
        
        # Update Redis
        redis_client = await get_redis()
        await redis_client.hset(
            f"campaign:{campaign_id}",
            mapping={
                "status": CampaignStatus.ACTIVE,
                "started_at": datetime.now().isoformat()
            }
        )
        
        # Trigger dialer worker (via Celery task)
        await redis_client.publish(
            "dialer:events",
            f"campaign:started:{campaign_id}"
        )
        
        logger.info(f"Campaign {campaign_id} started")
        return {"status": "success", "message": "Campaign started"}
        
    except Exception as e:
        logger.error(f"Error starting campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/campaigns/{campaign_id}/pause")
async def pause_campaign(campaign_id: int):
    """Pause campaign"""
    redis_client = await get_redis()
    
    await redis_client.hset(
        f"campaign:{campaign_id}",
        "status",
        CampaignStatus.PAUSED
    )
    
    await redis_client.publish(
        "dialer:events",
        f"campaign:paused:{campaign_id}"
    )
    
    logger.info(f"Campaign {campaign_id} paused")
    return {"status": "success", "message": "Campaign paused"}


@app.post("/campaigns/{campaign_id}/stop")
async def stop_campaign(campaign_id: int):
    """Stop campaign"""
    redis_client = await get_redis()
    
    await redis_client.hset(
        f"campaign:{campaign_id}",
        mapping={
            "status": CampaignStatus.COMPLETED,
            "completed_at": datetime.now().isoformat()
        }
    )
    
    await redis_client.publish(
        "dialer:events",
        f"campaign:stopped:{campaign_id}"
    )
    
    logger.info(f"Campaign {campaign_id} stopped")
    return {"status": "success", "message": "Campaign stopped"}


# ==================== STATISTICS ====================

@app.get("/campaigns/{campaign_id}/stats", response_model=CampaignStats)
async def get_campaign_stats(
    campaign_id: int,
    backend: httpx.AsyncClient = Depends(get_backend_client)
):
    """Get campaign statistics"""
    try:
        redis_client = await get_redis()
        
        # Get from Redis
        campaign_data = await redis_client.hgetall(f"campaign:{campaign_id}")
        
        if not campaign_data:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Get detailed stats from backend
        response = await backend.get(f"/api/campaigns/{campaign_id}/stats/")
        backend_stats = response.json() if response.status_code == 200 else {}
        
        # Get queue stats from Asterisk (via backend)
        queue_response = await backend.get(f"/api/queues/stats/")
        queue_stats = queue_response.json() if queue_response.status_code == 200 else {}
        
        # Calculate rates
        total_calls = int(campaign_data.get("total_calls", 0))
        answered = int(campaign_data.get("answered_calls", 0))
        answer_rate = (answered / total_calls * 100) if total_calls > 0 else 0.0
        
        return CampaignStats(
            campaign_id=campaign_id,
            total_contacts=backend_stats.get("total_contacts", 0),
            pending_calls=backend_stats.get("pending_calls", 0),
            active_calls=int(campaign_data.get("active_calls", 0)),
            completed_calls=total_calls,
            answered_calls=answered,
            no_answer=backend_stats.get("no_answer", 0),
            busy=backend_stats.get("busy", 0),
            failed=backend_stats.get("failed", 0),
            answer_rate=round(answer_rate, 2),
            average_duration=backend_stats.get("avg_duration", 0.0),
            calls_per_hour=backend_stats.get("calls_per_hour", 0.0),
            agents_available=queue_stats.get("available", 0),
            agents_busy=queue_stats.get("busy", 0)
        )
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== CALL ORIGINATION ====================

@app.post("/calls/originate")
async def originate_call(call: CallOriginate):
    """Originate outbound call"""
    try:
        # Build channel (trunk)
        channel = f"PJSIP/{call.phone_number}@trunk-out"
        
        # Build variables
        variables = {
            "CAMPAIGN_ID": str(call.campaign_id),
            "CONTACT_ID": str(call.contact_id),
            "CALLERID(num)": call.phone_number
        }
        
        if call.variables:
            variables.update(call.variables)
        
        # Originate via AMI
        response = await ami.originate(
            channel=channel,
            context=call.context,
            exten=call.phone_number,
            priority=call.priority,
            timeout=call.timeout,
            variables=variables
        )
        
        # Update Redis counter
        redis_client = await get_redis()
        await redis_client.hincrby(f"campaign:{call.campaign_id}", "total_calls", 1)
        await redis_client.hincrby(f"campaign:{call.campaign_id}", "active_calls", 1)
        
        if response.get("Response") == "Success":
            logger.info(f"Call originated: {call.phone_number}")
            return {
                "status": "success",
                "message": "Call originated",
                "response": response
            }
        else:
            logger.error(f"Originate failed: {response}")
            raise HTTPException(
                status_code=500,
                detail=f"Originate failed: {response.get('Message', 'Unknown error')}"
            )
            
    except Exception as e:
        logger.error(f"Originate error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== CONTACTS ====================

@app.post("/contacts", status_code=status.HTTP_201_CREATED)
async def add_contact(
    contact: ContactCreate,
    backend: httpx.AsyncClient = Depends(get_backend_client)
):
    """Add contact to campaign"""
    try:
        response = await backend.post("/api/contacts/", json=contact.dict())
        response.raise_for_status()
        
        logger.info(f"Contact added to campaign {contact.campaign_id}")
        return response.json()
        
    except httpx.HTTPError as e:
        logger.error(f"Backend error: {e}")
        raise HTTPException(status_code=500, detail="Backend communication error")


@app.post("/contacts/bulk")
async def bulk_import_contacts(
    campaign_id: int,
    contacts: List[ContactCreate],
    backend: httpx.AsyncClient = Depends(get_backend_client)
):
    """Bulk import contacts"""
    try:
        response = await backend.post(
            f"/api/campaigns/{campaign_id}/contacts/bulk/",
            json=[c.dict() for c in contacts]
        )
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"Bulk import: {result.get('imported', 0)} contacts")
        
        return result
        
    except httpx.HTTPError as e:
        logger.error(f"Bulk import error: {e}")
        raise HTTPException(status_code=500, detail="Bulk import failed")


# ==================== WEBSOCKET EVENTS ====================

@app.get("/events/stream")
async def event_stream():
    """SSE endpoint for real-time events"""
    # TODO: Implement Server-Sent Events for real-time updates
    return {"message": "Use WebSocket endpoint for real-time events"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
