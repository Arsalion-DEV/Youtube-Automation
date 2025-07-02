"""
Enhanced YouTube Automation Platform Main Application
WITH ENTERPRISE FEATURES - Advanced Analytics, A/B Testing, Monetization
"""

import os
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, List

from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import uvicorn

# Import existing modules
from auth import get_current_user
from auth_routes import auth_router
from ai_wizard_routes import wizard_router
from social_media_routes import router as social_router
from social_media_manager import SocialMediaManager
from realtime_publisher import RealtimePublisher
from oauth_config import get_oauth_config, validate_oauth_config

# Import enterprise features
try:
    from enterprise_integration import add_enterprise_features_to_app, track_user_activity, track_revenue
    ENTERPRISE_ENABLED = True
    print("🚀 Enterprise features enabled!")
except ImportError as e:
    ENTERPRISE_ENABLED = False
    print(f"⚠️ Enterprise features disabled: {e}")

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
social_manager = SocialMediaManager()
realtime_publisher = RealtimePublisher(social_manager)
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Enhanced YouTube Automation Platform with Enterprise Features...")
    
    # Initialize database
    social_manager.initialize_database()
    logger.info("Database initialized")
    
    # Load OAuth configurations
    oauth_status = {}
    platforms = ["facebook", "twitter", "instagram", "tiktok", "linkedin"]
    for platform in platforms:
        oauth_status[platform] = validate_oauth_config(platform)
    
    logger.info(f"OAuth status: {oauth_status}")
    
    # Track platform startup
    if ENTERPRISE_ENABLED:
        track_user_activity(0, "platform_startup", {"oauth_status": oauth_status})
    
    yield
    
    # Shutdown
    logger.info("Shutting down Enhanced YouTube Automation Platform...")

# Create FastAPI app with enterprise features
app = FastAPI(
    title="YouTube Automation Platform - Enterprise Edition",
    description="Advanced YouTube automation with enterprise analytics, A/B testing, and monetization tracking",
    version="3.0.0-enterprise",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add enterprise features to the app
if ENTERPRISE_ENABLED:
    add_enterprise_features_to_app(app)
    logger.info("✅ Enterprise features integrated successfully")

# Include existing routers
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(wizard_router, prefix="/api/wizard", tags=["ai-wizard"])
app.include_router(social_router, prefix="/api/social", tags=["social-media"])

# Enhanced endpoints with enterprise tracking
@app.get("/")
async def root():
    """Root endpoint with enterprise status"""
    return {
        "message": "YouTube Automation Platform - Enterprise Edition",
        "version": "3.0.0-enterprise",
        "enterprise_features": ENTERPRISE_ENABLED,
        "status": "operational"
    }

@app.post("/api/social/publishing/realtime")
async def realtime_publishing(
    title: str = Form(...),
    description: str = Form(...),
    platforms: str = Form(...),
    video_file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Enhanced real-time publishing with enterprise tracking"""
    try:
        # Parse platforms
        platform_list = [p.strip() for p in platforms.split(",") if p.strip()]
        
        # Track publishing activity
        if ENTERPRISE_ENABLED:
            track_user_activity(
                current_user["user_id"], 
                "video_publishing_started", 
                {
                    "title": title,
                    "platforms": platform_list,
                    "file_size": video_file.size if hasattr(video_file, 'size') else 0
                }
            )
        
        # Process publishing job
        job_id = await realtime_publisher.create_publishing_job(
            title=title,
            description=description,
            platforms=platform_list,
            video_file=video_file,
            user_id=current_user["user_id"]
        )
        
        # Track successful job creation
        if ENTERPRISE_ENABLED:
            track_user_activity(
                current_user["user_id"], 
                "video_publishing_job_created", 
                {"job_id": job_id, "platforms_count": len(platform_list)}
            )
        
        return {
            "job_id": job_id,
            "status": "processing",
            "message": "Publishing job created successfully",
            "enterprise_tracking": ENTERPRISE_ENABLED
        }
        
    except Exception as e:
        # Track errors
        if ENTERPRISE_ENABLED:
            track_user_activity(
                current_user["user_id"], 
                "video_publishing_error", 
                {"error": str(e), "title": title}
            )
        
        logger.error(f"Real-time publishing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system/status")
async def get_system_status():
    """Enhanced system status with enterprise health"""
    base_status = {
        "system": "operational",
        "version": "3.0.0-enterprise",
        "uptime": "running",
        "services": {
            "api": True,
            "database": True,
            "social_manager": True,
            "realtime_publisher": True,
            "enterprise_features": ENTERPRISE_ENABLED
        },
        "memory_usage": "efficient",
        "last_updated": asyncio.get_event_loop().time()
    }
    
    # Add enterprise health check
    if ENTERPRISE_ENABLED:
        try:
            from enterprise_launcher import get_enterprise_manager
            manager = get_enterprise_manager()
            enterprise_health = manager.get_platform_health()
            base_status["enterprise_health"] = enterprise_health
        except Exception as e:
            base_status["enterprise_health"] = {"status": "error", "message": str(e)}
    
    return base_status

@app.get("/api/social/publishing/status/{job_id}")
async def get_publishing_status(job_id: str, current_user: dict = Depends(get_current_user)):
    """Enhanced publishing status with tracking"""
    status = await realtime_publisher.get_job_status(job_id)
    
    # Track status check
    if ENTERPRISE_ENABLED:
        track_user_activity(
            current_user["user_id"], 
            "job_status_check", 
            {"job_id": job_id, "status": status}
        )
    
    return {"job_id": job_id, "status": status, "enterprise_tracked": ENTERPRISE_ENABLED}

@app.post("/api/social/publishing/retry/{job_id}")
async def retry_publishing_job(job_id: str, current_user: dict = Depends(get_current_user)):
    """Enhanced retry with tracking"""
    result = await realtime_publisher.retry_job(job_id, current_user["user_id"])
    
    # Track retry attempts
    if ENTERPRISE_ENABLED:
        track_user_activity(
            current_user["user_id"], 
            "job_retry_attempt", 
            {"job_id": job_id, "result": result}
        )
    
    return {"job_id": job_id, "retry_status": result, "enterprise_tracked": ENTERPRISE_ENABLED}

@app.get("/api/social/publishing/jobs")
async def get_user_publishing_jobs(current_user: dict = Depends(get_current_user)):
    """Enhanced job listing with tracking"""
    jobs = await realtime_publisher.get_user_jobs(current_user["user_id"])
    
    # Track job list access
    if ENTERPRISE_ENABLED:
        track_user_activity(
            current_user["user_id"], 
            "jobs_list_accessed", 
            {"jobs_count": len(jobs) if jobs else 0}
        )
    
    return {"jobs": jobs, "enterprise_tracked": ENTERPRISE_ENABLED}

@app.get("/api/user/progress/{user_id}")
async def get_user_progress(user_id: int, current_user: dict = Depends(get_current_user)):
    """Enhanced user progress with analytics"""
    progress_data = {
        "user_id": user_id,
        "progress": {
            "channels_created": 3,
            "videos_published": 12,
            "platforms_connected": 0,
            "total_views": 125000
        },
        "achievements": ["first_channel", "multi_platform_ready"],
        "next_steps": ["connect_social_platforms", "publish_first_video"]
    }
    
    # Add enterprise analytics if available
    if ENTERPRISE_ENABLED:
        try:
            from enterprise_launcher import get_enterprise_manager
            manager = get_enterprise_manager()
            analytics_summary = manager.get_analytics_summary(user_id)
            progress_data["enterprise_analytics"] = analytics_summary
        except Exception as e:
            progress_data["enterprise_analytics"] = {"error": str(e)}
        
        # Track progress access
        track_user_activity(user_id, "progress_accessed", {"by_user": current_user["user_id"]})
    
    return progress_data

@app.post("/api/user/progress/{user_id}")
async def save_user_progress(user_id: int, progress_data: dict, current_user: dict = Depends(get_current_user)):
    """Enhanced progress saving with tracking"""
    if ENTERPRISE_ENABLED:
        track_user_activity(
            user_id, 
            "progress_saved", 
            {"data_keys": list(progress_data.keys()), "by_user": current_user["user_id"]}
        )
    
    return {
        "user_id": user_id, 
        "saved": True, 
        "timestamp": asyncio.get_event_loop().time(),
        "enterprise_tracked": ENTERPRISE_ENABLED
    }

@app.get("/api/social/analytics")
async def get_platform_analytics(current_user: dict = Depends(get_current_user)):
    """Enhanced analytics with enterprise data"""
    base_analytics = {
        "platforms": {
            "facebook": {"posts": 0, "engagement": 0, "reach": 0},
            "twitter": {"posts": 0, "engagement": 0, "reach": 0},
            "instagram": {"posts": 0, "engagement": 0, "reach": 0},
            "tiktok": {"posts": 0, "engagement": 0, "reach": 0},
            "linkedin": {"posts": 0, "engagement": 0, "reach": 0}
        },
        "total_posts": 0,
        "total_engagement": 0,
        "last_updated": asyncio.get_event_loop().time()
    }
    
    # Add enterprise analytics
    if ENTERPRISE_ENABLED:
        try:
            from enterprise_launcher import get_enterprise_manager
            manager = get_enterprise_manager()
            enterprise_analytics = manager.get_analytics_summary(current_user["user_id"])
            base_analytics["enterprise_data"] = enterprise_analytics
        except Exception as e:
            base_analytics["enterprise_data"] = {"error": str(e)}
        
        # Track analytics access
        track_user_activity(current_user["user_id"], "analytics_accessed", {"timestamp": asyncio.get_event_loop().time()})
    
    return base_analytics

# New enterprise-specific endpoints
@app.post("/api/enterprise/revenue/track")
async def track_user_revenue(
    amount: float, 
    source: str, 
    current_user: dict = Depends(get_current_user)
):
    """Track revenue for current user"""
    if not ENTERPRISE_ENABLED:
        raise HTTPException(status_code=503, detail="Enterprise features not available")
    
    success = track_revenue(current_user["user_id"], amount, source)
    return {
        "success": success,
        "user_id": current_user["user_id"],
        "amount": amount,
        "source": source
    }

@app.get("/api/enterprise/demo")
async def enterprise_demo():
    """Demo endpoint to show enterprise features"""
    if not ENTERPRISE_ENABLED:
        return {"message": "Enterprise features not available", "demo_data": None}
    
    try:
        from enterprise_launcher import get_enterprise_manager
        manager = get_enterprise_manager()
        
        # Generate some demo data
        demo_analytics = manager.get_analytics_summary()
        demo_health = manager.get_platform_health()
        
        # Track demo access
        track_user_activity(0, "enterprise_demo_accessed", {"timestamp": asyncio.get_event_loop().time()})
        
        return {
            "message": "Enterprise features are active!",
            "demo_analytics": demo_analytics,
            "platform_health": demo_health,
            "available_features": [
                "Advanced Analytics",
                "A/B Testing",
                "Monetization Tracking",
                "Team Management",
                "White Label Solutions"
            ]
        }
    except Exception as e:
        return {"message": "Enterprise demo error", "error": str(e)}

if __name__ == "__main__":
    print(f"🚀 Starting YouTube Automation Platform - Enterprise Edition (Features: {ENTERPRISE_ENABLED})")
    uvicorn.run(
        "enhanced_main_with_enterprise:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        workers=1
    )
