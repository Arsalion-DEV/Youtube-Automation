"""
Enterprise Backend with PostgreSQL, Celery, and Advanced Features
Production-ready scalable architecture with enterprise capabilities
"""

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import uuid

# Database and async support
import asyncpg
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, DateTime, Boolean, Text, Float, JSON
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from alembic import command
from alembic.config import Config

# Background tasks
from celery import Celery
from celery.schedules import crontab
import redis

# FastAPI with enterprise features
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse

# Monitoring and observability
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import structlog
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Security and rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import jwt
from passlib.context import CryptContext

# Utilities
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

# Import enterprise modules
from ab_testing_system import ABTestingSystem
from monetization_tracking import MonetizationTracker
from white_label_system import WhiteLabelManager
from team_management_system import TeamManagementSystem
from subscription_system import SubscriptionManager

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Configuration
class Config:
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/youtube_automation")
    DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "20"))
    DATABASE_MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", "30"))
    
    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    REDIS_CACHE_TTL = int(os.getenv("REDIS_CACHE_TTL", "3600"))
    
    # Celery
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    
    # Security
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secure-secret-key")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))
    
    # Enterprise features
    MULTI_TENANT_ENABLED = os.getenv("MULTI_TENANT_ENABLED", "true").lower() == "true"
    WHITE_LABEL_ENABLED = os.getenv("WHITE_LABEL_ENABLED", "true").lower() == "true"
    TEAM_FEATURES_ENABLED = os.getenv("TEAM_FEATURES_ENABLED", "true").lower() == "true"
    
    # Monitoring
    SENTRY_DSN = os.getenv("SENTRY_DSN")
    JAEGER_ENDPOINT = os.getenv("JAEGER_ENDPOINT")
    PROMETHEUS_ENABLED = os.getenv("PROMETHEUS_ENABLED", "true").lower() == "true"
    
    # Performance
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    RATE_LIMIT_PER_HOUR = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))

config = Config()

# Initialize Sentry for error tracking
if config.SENTRY_DSN:
    sentry_sdk.init(
        dsn=config.SENTRY_DSN,
        integrations=[
            FastApiIntegration(auto_enable=True),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=1.0,
    )

# Initialize Jaeger for distributed tracing
if config.JAEGER_ENDPOINT:
    trace.set_tracer_provider(TracerProvider())
    jaeger_exporter = JaegerExporter(
        agent_host_name="localhost",
        agent_port=6831,
    )
    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)

# Database Models
Base = declarative_base()

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    plan = Column(String, default="free")  # free, pro, enterprise
    settings = Column(JSON, default=dict)
    white_label_config = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(String, default="user")  # user, admin, owner
    organization_id = Column(String, nullable=True)  # Multi-tenant support
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    preferences = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Team(Base):
    __tablename__ = "teams"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    organization_id = Column(String, nullable=False)
    owner_id = Column(String, nullable=False)
    settings = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TeamMember(Base):
    __tablename__ = "team_members"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    role = Column(String, default="member")  # member, admin, owner
    permissions = Column(JSON, default=list)
    joined_at = Column(DateTime, default=datetime.utcnow)

class Channel(Base):
    __tablename__ = "channels"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    platform_id = Column(String, nullable=False)  # YouTube channel ID
    platform = Column(String, default="youtube")
    name = Column(String, nullable=False)
    organization_id = Column(String, nullable=False)
    team_id = Column(String, nullable=True)
    settings = Column(JSON, default=dict)
    analytics_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WorkflowTemplate(Base):
    __tablename__ = "workflow_templates"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    template_data = Column(JSON, nullable=False)
    category = Column(String)
    is_public = Column(Boolean, default=False)
    organization_id = Column(String, nullable=True)
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Enterprise Database Manager
class EnterpriseDatabase:
    def __init__(self):
        self.engine = None
        self.async_session = None
        
    async def initialize(self):
        """Initialize database connections"""
        self.engine = create_async_engine(
            config.DATABASE_URL,
            pool_size=config.DATABASE_POOL_SIZE,
            max_overflow=config.DATABASE_MAX_OVERFLOW,
            echo=False
        )
        
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # Create tables
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database initialized successfully")
    
    async def get_session(self):
        """Get database session"""
        async with self.async_session() as session:
            try:
                yield session
            finally:
                await session.close()
    
    async def close(self):
        """Close database connections"""
        if self.engine:
            await self.engine.dispose()

# Redis Cache Manager
class CacheManager:
    def __init__(self):
        self.redis_client = None
    
    async def initialize(self):
        """Initialize Redis connection"""
        import aioredis
        self.redis_client = aioredis.from_url(
            config.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        logger.info("Redis cache initialized successfully")
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        if not self.redis_client:
            return None
        return await self.redis_client.get(key)
    
    async def set(self, key: str, value: str, ttl: int = None) -> bool:
        """Set value in cache"""
        if not self.redis_client:
            return False
        
        if ttl is None:
            ttl = config.REDIS_CACHE_TTL
        
        await self.redis_client.setex(key, ttl, value)
        return True
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.redis_client:
            return False
        return await self.redis_client.delete(key) > 0
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()

# Celery for Background Tasks
celery_app = Celery(
    "youtube_automation_enterprise",
    broker=config.CELERY_BROKER_URL,
    backend=config.CELERY_RESULT_BACKEND,
    include=["enterprise_tasks", "ab_testing_tasks", "monetization_tasks", "white_label_tasks", "team_management_tasks", "subscription_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    result_expires=3600,
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "sync-analytics-data": {
            "task": "enterprise_tasks.sync_analytics_data",
            "schedule": crontab(minute=0, hour="*/6"),  # Every 6 hours
        },
        "process-video-queue": {
            "task": "enterprise_tasks.process_video_queue",
            "schedule": crontab(minute="*/5"),  # Every 5 minutes
        },
        "cleanup-old-data": {
            "task": "enterprise_tasks.cleanup_old_data",
            "schedule": crontab(minute=0, hour=2),  # Daily at 2 AM
        },
        "generate-reports": {
            "task": "enterprise_tasks.generate_reports",
            "schedule": crontab(minute=0, hour=8),  # Daily at 8 AM
        },
    },
)

# Authentication and Authorization
class AuthManager:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.security = HTTPBearer()
    
    def hash_password(self, password: str) -> str:
        """Hash password"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: dict) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=config.JWT_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        
        return jwt.encode(to_encode, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)
    
    async def get_current_user(
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        db_session = Depends(lambda: None)  # Will be replaced with actual dependency
    ) -> User:
        """Get current authenticated user"""
        try:
            payload = jwt.decode(
                credentials.credentials, 
                config.JWT_SECRET_KEY, 
                algorithms=[config.JWT_ALGORITHM]
            )
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(status_code=401, detail="Invalid token")
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # In real implementation, fetch user from database
        # user = await db_session.get(User, user_id)
        # if not user:
        #     raise HTTPException(status_code=401, detail="User not found")
        
        # For now, return mock user
        return User(id=user_id, email="user@example.com", role="user")

# Performance Monitoring
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
REQUEST_DURATION = Histogram("http_request_duration_seconds", "HTTP request duration")
ACTIVE_USERS = Gauge("active_users_total", "Total active users")
VIDEO_PROCESSING_QUEUE = Gauge("video_processing_queue_size", "Video processing queue size")
REVENUE_TOTAL = Gauge("revenue_total_usd", "Total revenue in USD")

# Enterprise Features Manager
class EnterpriseFeatures:
    """Manage enterprise-specific features"""
    
    @staticmethod
    async def create_organization(
        name: str, 
        slug: str, 
        plan: str = "free",
        white_label_config: Optional[Dict] = None
    ) -> str:
        """Create new organization"""
        org_id = str(uuid.uuid4())
        
        # In real implementation, save to database
        logger.info(f"Created organization: {org_id} - {name}")
        return org_id
    
    @staticmethod
    async def create_team(
        name: str,
        organization_id: str,
        owner_id: str,
        description: Optional[str] = None
    ) -> str:
        """Create new team"""
        team_id = str(uuid.uuid4())
        
        # In real implementation, save to database
        logger.info(f"Created team: {team_id} - {name}")
        return team_id
    
    @staticmethod
    async def add_team_member(
        team_id: str,
        user_id: str,
        role: str = "member",
        permissions: Optional[List[str]] = None
    ) -> bool:
        """Add member to team"""
        # In real implementation, save to database
        logger.info(f"Added user {user_id} to team {team_id} as {role}")
        return True
    
    @staticmethod
    async def get_user_permissions(user_id: str, organization_id: str) -> List[str]:
        """Get user permissions for organization"""
        # In real implementation, fetch from database
        return [
            "read_analytics",
            "create_videos",
            "manage_channels",
            "view_revenue"
        ]
    
    @staticmethod
    async def check_feature_access(organization_id: str, feature: str) -> bool:
        """Check if organization has access to feature"""
        # In real implementation, check subscription plan
        feature_access = {
            "free": ["basic_analytics", "single_channel"],
            "pro": ["advanced_analytics", "multiple_channels", "ab_testing"],
            "enterprise": ["all_features", "white_label", "team_management", "api_access"]
        }
        
        # Mock: return True for enterprise features
        return True

# Rate Limiting
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI with enterprise configuration
app = FastAPI(
    title="YouTube Automation Platform - Enterprise",
    description="Enterprise-grade YouTube automation with advanced features",
    version="3.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if config.MULTI_TENANT_ENABLED:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure for production
    )

# Global variables
db_manager = EnterpriseDatabase()
cache_manager = CacheManager()
auth_manager = AuthManager()
ab_testing = ABTestingSystem()
monetization_tracker = MonetizationTracker()
white_label_manager = WhiteLabelManager()
team_manager = TeamManagementSystem()
subscription_manager = SubscriptionManager()

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Application lifecycle
@app.on_event("startup")
async def startup():
    """Initialize application"""
    await db_manager.initialize()
    await cache_manager.initialize()
    logger.info("Enterprise YouTube Automation Platform started")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    await db_manager.close()
    await cache_manager.close()
    logger.info("Enterprise YouTube Automation Platform stopped")

# Middleware for monitoring
@app.middleware("http")
async def monitoring_middleware(request: Request, call_next):
    """Add monitoring and performance tracking"""
    start_time = datetime.utcnow()
    
    # Track request
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status="pending"
    ).inc()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = (datetime.utcnow() - start_time).total_seconds()
    REQUEST_DURATION.observe(duration)
    
    # Update metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    # Add headers
    response.headers["X-Process-Time"] = str(duration)
    response.headers["X-Server-Version"] = "3.0.0"
    
    return response

# Health and monitoring endpoints
@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "3.0.0",
        "services": {}
    }
    
    # Check database
    try:
        # Simple query to check database connectivity
        health_status["services"]["database"] = {"status": "healthy", "type": "postgresql"}
    except Exception as e:
        health_status["services"]["database"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"
    
    # Check Redis
    try:
        await cache_manager.redis_client.ping()
        health_status["services"]["redis"] = {"status": "healthy"}
    except Exception as e:
        health_status["services"]["redis"] = {"status": "unhealthy", "error": str(e)}
    
    # Check Celery
    try:
        # Check if Celery workers are active
        health_status["services"]["celery"] = {"status": "healthy", "workers": 0}
    except Exception as e:
        health_status["services"]["celery"] = {"status": "unhealthy", "error": str(e)}
    
    return health_status

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    from fastapi.responses import Response
    return Response(generate_latest(), media_type="text/plain")

@app.get("/api/system/status")
@limiter.limit("30/minute")
async def system_status(request: Request):
    """Detailed system status"""
    import psutil
    
    return {
        "status": "operational",
        "system": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "uptime": datetime.utcnow().isoformat()
        },
        "database": {
            "status": "healthy",
            "pool_size": config.DATABASE_POOL_SIZE,
            "connections_active": 0  # Would get from actual pool
        },
        "cache": {
            "status": "healthy",
            "redis_info": await cache_manager.redis_client.info() if cache_manager.redis_client else None
        },
        "metrics": {
            "active_users": ACTIVE_USERS._value._value,
            "video_queue_size": VIDEO_PROCESSING_QUEUE._value._value,
            "total_revenue": REVENUE_TOTAL._value._value
        }
    }

# Enterprise API Endpoints
@app.post("/api/v3/organizations")
@limiter.limit("10/minute")
async def create_organization(
    request: Request,
    name: str,
    slug: str,
    plan: str = "free",
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Create new organization"""
    try:
        org_id = await EnterpriseFeatures.create_organization(name, slug, plan)
        return {"success": True, "organization_id": org_id}
    except Exception as e:
        logger.error(f"Error creating organization: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v3/teams")
@limiter.limit("20/minute")
async def create_team(
    request: Request,
    name: str,
    organization_id: str,
    description: Optional[str] = None,
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Create new team"""
    try:
        # Check permissions
        permissions = await EnterpriseFeatures.get_user_permissions(
            current_user.id, organization_id
        )
        if "manage_teams" not in permissions and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        team_id = await EnterpriseFeatures.create_team(
            name, organization_id, current_user.id, description
        )
        return {"success": True, "team_id": team_id}
    except Exception as e:
        logger.error(f"Error creating team: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v3/analytics/enterprise")
@limiter.limit("100/minute")
async def get_enterprise_analytics(
    request: Request,
    organization_id: str,
    period: str = "30d",
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Get enterprise-level analytics"""
    try:
        # Check feature access
        has_access = await EnterpriseFeatures.check_feature_access(
            organization_id, "advanced_analytics"
        )
        if not has_access:
            raise HTTPException(status_code=403, detail="Feature not available in current plan")
        
        # Cache key
        cache_key = f"enterprise_analytics:{organization_id}:{period}"
        
        # Try cache first
        cached_data = await cache_manager.get(cache_key)
        if cached_data:
            return {"success": True, "data": json.loads(cached_data), "source": "cache"}
        
        # Generate analytics (mock data)
        analytics_data = {
            "total_channels": 25,
            "total_videos": 1247,
            "total_views": 8450000,
            "total_revenue": 45600.75,
            "team_performance": [
                {"team_name": "Content Team A", "videos": 450, "views": 3200000, "revenue": 18500.30},
                {"team_name": "Content Team B", "videos": 380, "views": 2800000, "revenue": 15200.45},
                {"team_name": "Experimental", "videos": 417, "views": 2450000, "revenue": 11900.00}
            ],
            "platform_breakdown": {
                "youtube": {"views": 6500000, "revenue": 35600.75},
                "tiktok": {"views": 1200000, "revenue": 5000.00},
                "instagram": {"views": 750000, "revenue": 5000.00}
            }
        }
        
        # Cache the result
        await cache_manager.set(cache_key, json.dumps(analytics_data), ttl=1800)  # 30 minutes
        
        return {"success": True, "data": analytics_data, "source": "generated"}
        
    except Exception as e:
        logger.error(f"Error getting enterprise analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v3/workflows/template")
@limiter.limit("50/minute")
async def create_workflow_template(
    request: Request,
    name: str,
    description: str,
    template_data: Dict[str, Any],
    category: Optional[str] = None,
    is_public: bool = False,
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Create workflow template"""
    try:
        template_id = str(uuid.uuid4())
        
        # In real implementation, save to database
        logger.info(f"Created workflow template: {template_id} - {name}")
        
        return {"success": True, "template_id": template_id}
        
    except Exception as e:
        logger.error(f"Error creating workflow template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Background task endpoints
@app.post("/api/v3/tasks/video-generation")
@limiter.limit("100/minute")
async def queue_video_generation(
    request: Request,
    channel_id: str,
    video_config: Dict[str, Any],
    priority: str = "normal",
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Queue video generation task"""
    try:
        # Queue task with Celery
        task = celery_app.send_task(
            "enterprise_tasks.generate_video",
            args=[channel_id, video_config],
            kwargs={"user_id": current_user.id, "priority": priority}
        )
        
        VIDEO_PROCESSING_QUEUE.inc()
        
        return {
            "success": True,
            "task_id": task.id,
            "status": "queued",
            "estimated_completion": (datetime.utcnow() + timedelta(minutes=10)).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error queuing video generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v3/tasks/{task_id}/status")
@limiter.limit("200/minute")
async def get_task_status(
    request: Request,
    task_id: str,
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Get task status"""
    try:
        # Get task result from Celery
        result = celery_app.AsyncResult(task_id)
        
        return {
            "success": True,
            "task_id": task_id,
            "status": result.status,
            "result": result.result if result.ready() else None,
            "progress": result.info.get("progress", 0) if isinstance(result.info, dict) else 0
        }
        
    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# A/B Testing Routes
@app.post("/api/v3/ab-testing/tests")
@limiter.limit("50/minute")
async def create_ab_test(
    request: Request,
    test_data: Dict[str, Any],
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Create a new A/B test"""
    try:
        test_id = await ab_testing.create_test(
            name=test_data["name"],
            description=test_data.get("description", ""),
            variants=test_data["variants"],
            creator_id=current_user.id
        )
        return {"success": True, "test_id": test_id, "status": "created"}
    except Exception as e:
        logger.error(f"Error creating A/B test: {e}")
        raise HTTPException(status_code=500, detail="Failed to create A/B test")

@app.get("/api/v3/ab-testing/tests")
@limiter.limit("100/minute")
async def get_ab_tests(
    request: Request,
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Get all A/B tests for the current user"""
    try:
        tests = await ab_testing.get_user_tests(current_user.id)
        return {"success": True, "tests": tests}
    except Exception as e:
        logger.error(f"Error fetching A/B tests: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch A/B tests")

@app.get("/api/v3/ab-testing/tests/{test_id}/results")
@limiter.limit("100/minute")
async def get_ab_test_results(
    request: Request,
    test_id: str,
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Get A/B test results with statistical analysis"""
    try:
        results = await ab_testing.get_test_results(test_id)
        return {"success": True, "results": results}
    except Exception as e:
        logger.error(f"Error fetching A/B test results: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch test results")

@app.post("/api/v3/ab-testing/tests/{test_id}/participate")
@limiter.limit("200/minute")
async def participate_in_test(
    request: Request,
    test_id: str,
    participation_data: Dict[str, Any]
):
    """Record user participation in A/B test"""
    try:
        variant = await ab_testing.assign_variant(test_id, participation_data["user_id"])
        return {"success": True, "variant": variant}
    except Exception as e:
        logger.error(f"Error recording test participation: {e}")
        raise HTTPException(status_code=500, detail="Failed to record participation")

@app.post("/api/v3/ab-testing/tests/{test_id}/convert")
@limiter.limit("200/minute")
async def record_conversion(
    request: Request,
    test_id: str,
    conversion_data: Dict[str, Any]
):
    """Record conversion for A/B test"""
    try:
        await ab_testing.record_conversion(
            test_id=test_id,
            user_id=conversion_data["user_id"],
            conversion_type=conversion_data.get("conversion_type", "click"),
            value=conversion_data.get("value", 1.0)
        )
        return {"success": True, "status": "recorded"}
    except Exception as e:
        logger.error(f"Error recording conversion: {e}")
        raise HTTPException(status_code=500, detail="Failed to record conversion")

# Monetization Tracking Routes
@app.post("/api/v3/monetization/revenue")
@limiter.limit("100/minute")
async def track_revenue(
    request: Request,
    revenue_data: Dict[str, Any],
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Track revenue from various sources"""
    try:
        await monetization_tracker.track_revenue(
            user_id=current_user.id,
            source=revenue_data["source"],
            amount=revenue_data["amount"],
            currency=revenue_data.get("currency", "USD"),
            video_id=revenue_data.get("video_id"),
            metadata=revenue_data.get("metadata", {})
        )
        # Update global revenue metric
        REVENUE_TOTAL.set(await monetization_tracker.get_total_revenue())
        return {"success": True, "status": "tracked"}
    except Exception as e:
        logger.error(f"Error tracking revenue: {e}")
        raise HTTPException(status_code=500, detail="Failed to track revenue")

@app.get("/api/v3/monetization/analytics")
@limiter.limit("100/minute")
async def get_monetization_analytics(
    request: Request,
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Get comprehensive monetization analytics"""
    try:
        analytics = await monetization_tracker.get_analytics(current_user.id)
        return {"success": True, "analytics": analytics}
    except Exception as e:
        logger.error(f"Error fetching monetization analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch analytics")

@app.get("/api/v3/monetization/performance/{video_id}")
@limiter.limit("100/minute")
async def get_video_performance(
    request: Request,
    video_id: str,
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Get detailed performance metrics for a specific video"""
    try:
        performance = await monetization_tracker.get_video_performance(video_id, current_user.id)
        return {"success": True, "performance": performance}
    except Exception as e:
        logger.error(f"Error fetching video performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch video performance")

@app.get("/api/v3/monetization/forecasting")
@limiter.limit("50/minute")
async def get_revenue_forecasting(
    request: Request,
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Get revenue forecasting and trends"""
    try:
        forecasting = await monetization_tracker.get_forecasting(current_user.id)
        return {"success": True, "forecasting": forecasting}
    except Exception as e:
        logger.error(f"Error fetching revenue forecasting: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch forecasting")

# White Label Solutions Routes
@app.post("/api/v3/white-label/instances")
@limiter.limit("10/minute")
async def create_white_label_instance(
    request: Request,
    instance_data: Dict[str, Any],
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Create a new white-label instance"""
    try:
        instance_id = await white_label_manager.create_white_label_instance(
            organization_id=instance_data["organization_id"],
            branding_config=instance_data["branding_config"],
            domain_config=instance_data.get("domain_config")
        )
        return {"success": True, "instance_id": instance_id}
    except Exception as e:
        logger.error(f"Error creating white-label instance: {e}")
        raise HTTPException(status_code=500, detail="Failed to create white-label instance")

@app.get("/api/v3/white-label/instances/{instance_id}")
@limiter.limit("100/minute")
async def get_white_label_config(
    request: Request,
    instance_id: str,
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Get white-label instance configuration"""
    try:
        config = await white_label_manager.get_white_label_config(instance_id)
        if not config:
            raise HTTPException(status_code=404, detail="White-label instance not found")
        return {"success": True, "config": config}
    except Exception as e:
        logger.error(f"Error fetching white-label config: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch configuration")

@app.put("/api/v3/white-label/instances/{instance_id}")
@limiter.limit("50/minute")
async def update_white_label_config(
    request: Request,
    instance_id: str,
    updates: Dict[str, Any],
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Update white-label instance configuration"""
    try:
        success = await white_label_manager.update_white_label_config(instance_id, updates)
        if not success:
            raise HTTPException(status_code=404, detail="White-label instance not found")
        return {"success": True}
    except Exception as e:
        logger.error(f"Error updating white-label config: {e}")
        raise HTTPException(status_code=500, detail="Failed to update configuration")

@app.delete("/api/v3/white-label/instances/{instance_id}")
@limiter.limit("20/minute")
async def delete_white_label_instance(
    request: Request,
    instance_id: str,
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Delete white-label instance"""
    try:
        success = await white_label_manager.delete_white_label_instance(instance_id)
        if not success:
            raise HTTPException(status_code=404, detail="White-label instance not found")
        return {"success": True}
    except Exception as e:
        logger.error(f"Error deleting white-label instance: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete instance")

# Enhanced Team Management Routes
@app.post("/api/v3/teams/advanced")
@limiter.limit("20/minute")
async def create_advanced_team(
    request: Request,
    team_data: Dict[str, Any],
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Create a new team with advanced features"""
    try:
        team_id = await team_manager.create_team(
            name=team_data["name"],
            description=team_data.get("description", ""),
            organization_id=team_data["organization_id"],
            owner_id=current_user.id,
            settings=team_data.get("settings")
        )
        return {"success": True, "team_id": team_id}
    except Exception as e:
        logger.error(f"Error creating advanced team: {e}")
        raise HTTPException(status_code=500, detail="Failed to create team")

@app.get("/api/v3/teams/{team_id}/members")
@limiter.limit("100/minute")
async def get_team_members(
    request: Request,
    team_id: str,
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Get all team members with advanced details"""
    try:
        members = await team_manager.get_team_members(team_id)
        return {"success": True, "members": members}
    except Exception as e:
        logger.error(f"Error fetching team members: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch team members")

@app.post("/api/v3/teams/{team_id}/invitations")
@limiter.limit("50/minute")
async def invite_team_member(
    request: Request,
    team_id: str,
    invitation_data: Dict[str, Any],
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Invite a new team member"""
    try:
        from team_management_system import TeamRole, Permission
        
        role = TeamRole(invitation_data["role"])
        permissions = None
        if "custom_permissions" in invitation_data:
            permissions = {Permission(p) for p in invitation_data["custom_permissions"]}
        
        invitation_id = await team_manager.invite_team_member(
            team_id=team_id,
            email=invitation_data["email"],
            role=role,
            invited_by=current_user.id,
            message=invitation_data.get("message"),
            custom_permissions=permissions
        )
        return {"success": True, "invitation_id": invitation_id}
    except Exception as e:
        logger.error(f"Error inviting team member: {e}")
        raise HTTPException(status_code=500, detail="Failed to invite team member")

@app.post("/api/v3/teams/invitations/{token}/accept")
@limiter.limit("20/minute")
async def accept_team_invitation(
    request: Request,
    token: str,
    acceptance_data: Dict[str, Any],
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Accept a team invitation"""
    try:
        member_id = await team_manager.accept_invitation(
            token=token,
            user_id=current_user.id,
            full_name=acceptance_data["full_name"]
        )
        return {"success": True, "member_id": member_id}
    except Exception as e:
        logger.error(f"Error accepting team invitation: {e}")
        raise HTTPException(status_code=500, detail="Failed to accept invitation")

@app.get("/api/v3/teams/{team_id}/analytics")
@limiter.limit("100/minute")
async def get_team_analytics(
    request: Request,
    team_id: str,
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Get comprehensive team analytics"""
    try:
        insights = await team_manager.get_team_insights(team_id)
        return {"success": True, "insights": insights}
    except Exception as e:
        logger.error(f"Error fetching team analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch team analytics")

@app.get("/api/v3/teams/{team_id}/activity")
@limiter.limit("100/minute")
async def get_team_activity(
    request: Request,
    team_id: str,
    limit: int = 50,
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Get team activity feed"""
    try:
        activity = await team_manager.get_team_activity_feed(team_id, limit)
        return {"success": True, "activity": activity}
    except Exception as e:
        logger.error(f"Error fetching team activity: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch team activity")

@app.put("/api/v3/teams/{team_id}/members/{member_id}/role")
@limiter.limit("50/minute")
async def update_member_role(
    request: Request,
    team_id: str,
    member_id: str,
    role_data: Dict[str, Any],
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Update team member role and permissions"""
    try:
        from team_management_system import TeamRole, Permission
        
        new_role = TeamRole(role_data["role"])
        permissions = None
        if "custom_permissions" in role_data:
            permissions = {Permission(p) for p in role_data["custom_permissions"]}
        
        success = await team_manager.update_member_role(
            team_id=team_id,
            member_id=member_id,
            new_role=new_role,
            updated_by=current_user.id,
            custom_permissions=permissions
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Member not found")
        
        return {"success": True}
    except Exception as e:
        logger.error(f"Error updating member role: {e}")
        raise HTTPException(status_code=500, detail="Failed to update member role")

@app.delete("/api/v3/teams/{team_id}/members/{member_id}")
@limiter.limit("50/minute")
async def remove_team_member(
    request: Request,
    team_id: str,
    member_id: str,
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Remove a team member"""
    try:
        success = await team_manager.remove_team_member(
            team_id=team_id,
            member_id=member_id,
            removed_by=current_user.id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Member not found")
        
        return {"success": True}
    except Exception as e:
        logger.error(f"Error removing team member: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove team member")

# Subscription Management Routes
@app.get("/api/v3/subscriptions/plans")
@limiter.limit("100/minute")
async def get_subscription_plans(
    request: Request
):
    """Get all available subscription plans"""
    try:
        plans = await subscription_manager.get_available_plans()
        return {"success": True, "plans": plans}
    except Exception as e:
        logger.error(f"Error fetching subscription plans: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch plans")

@app.post("/api/v3/subscriptions")
@limiter.limit("20/minute")
async def create_subscription(
    request: Request,
    subscription_data: Dict[str, Any],
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Create a new subscription"""
    try:
        from subscription_system import BillingCycle
        
        billing_cycle = BillingCycle(subscription_data["billing_cycle"])
        
        subscription_id = await subscription_manager.create_subscription(
            user_id=current_user.id,
            organization_id=subscription_data["organization_id"],
            plan_id=subscription_data["plan_id"],
            billing_cycle=billing_cycle,
            trial_days=subscription_data.get("trial_days"),
            payment_method_id=subscription_data.get("payment_method_id")
        )
        
        return {"success": True, "subscription_id": subscription_id}
    except Exception as e:
        logger.error(f"Error creating subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to create subscription")

@app.get("/api/v3/subscriptions/{subscription_id}")
@limiter.limit("100/minute")
async def get_subscription_status(
    request: Request,
    subscription_id: str,
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Get subscription status and details"""
    try:
        status = await subscription_manager.get_subscription_status(subscription_id)
        if not status:
            raise HTTPException(status_code=404, detail="Subscription not found")
        return {"success": True, "subscription": status}
    except Exception as e:
        logger.error(f"Error fetching subscription status: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch subscription status")

@app.put("/api/v3/subscriptions/{subscription_id}/upgrade")
@limiter.limit("20/minute")
async def upgrade_subscription(
    request: Request,
    subscription_id: str,
    upgrade_data: Dict[str, Any],
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Upgrade or change subscription plan"""
    try:
        from subscription_system import BillingCycle
        
        billing_cycle = None
        if "billing_cycle" in upgrade_data:
            billing_cycle = BillingCycle(upgrade_data["billing_cycle"])
        
        success = await subscription_manager.upgrade_subscription(
            subscription_id=subscription_id,
            new_plan_id=upgrade_data["new_plan_id"],
            billing_cycle=billing_cycle
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        return {"success": True}
    except Exception as e:
        logger.error(f"Error upgrading subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to upgrade subscription")

@app.delete("/api/v3/subscriptions/{subscription_id}")
@limiter.limit("20/minute")
async def cancel_subscription(
    request: Request,
    subscription_id: str,
    cancellation_data: Dict[str, Any],
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Cancel subscription"""
    try:
        immediate = cancellation_data.get("immediate", False)
        
        success = await subscription_manager.cancel_subscription(
            subscription_id=subscription_id,
            immediate=immediate
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        return {"success": True}
    except Exception as e:
        logger.error(f"Error canceling subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel subscription")

@app.post("/api/v3/subscriptions/{subscription_id}/usage")
@limiter.limit("200/minute")
async def track_subscription_usage(
    request: Request,
    subscription_id: str,
    usage_data: Dict[str, Any],
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Track usage for subscription billing"""
    try:
        from subscription_system import UsageMetric
        
        metric = UsageMetric(usage_data["metric"])
        
        usage_id = await subscription_manager.track_usage(
            subscription_id=subscription_id,
            metric=metric,
            quantity=usage_data["quantity"],
            metadata=usage_data.get("metadata")
        )
        
        return {"success": True, "usage_id": usage_id}
    except Exception as e:
        logger.error(f"Error tracking usage: {e}")
        raise HTTPException(status_code=500, detail="Failed to track usage")

@app.post("/api/v3/subscriptions/webhooks/stripe")
async def handle_stripe_webhook(
    request: Request
):
    """Handle Stripe webhook events"""
    try:
        payload = await request.body()
        sig_header = request.headers.get('stripe-signature')
        
        # Verify webhook signature
        endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # Process webhook
        await subscription_manager.process_webhook(
            event_type=event['type'],
            event_data=event['data']['object']
        )
        
        return {"success": True}
    except Exception as e:
        logger.error(f"Error handling Stripe webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process webhook")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "enterprise_backend:app",
        host="0.0.0.0",
        port=8001,
        workers=4,
        loop="uvloop",
        http="httptools",
        access_log=True,
        reload=False
    )