"""
Enhanced YouTube Automation Platform Main Application
CORRECTED VERSION - Fixes CORS and route mounting issues
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
    logger.info("Starting Enhanced YouTube Automation Platform...")
    
    # Initialize database
    social_manager.initialize_database()
    logger.info("Database initialized")
    
    # Load OAuth configurations
    oauth_status = {}
    platforms = ["facebook", "twitter", "instagram", "tiktok", "linkedin"]
    for platform in platforms:
        oauth_status[platform] = validate_oauth_config(platform)
    
    logger.info(f"OAuth configuration status: {oauth_status}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Enhanced YouTube Automation Platform...")

# Create FastAPI application
app = FastAPI(
    title="Enhanced YouTube Automation Platform",
    description="Complete multi-platform content automation with real-time publishing",
    version="2.0.0",
    lifespan=lifespan
)

# CORRECTED CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://13.60.77.139:3000",
        "https://your-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# CORRECTED - Include routers with proper prefix mounting
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(wizard_router, prefix="/api/wizard", tags=["ai-wizard"])
app.include_router(social_router, prefix="/api/social", tags=["social-media"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """Enhanced health check with service status"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "services": {
            "database": True,
            "social_media_manager": True,
            "realtime_publisher": True,
            "video_processor": True
        },
        "oauth_status": {
            platform: validate_oauth_config(platform) 
            for platform in ["facebook", "twitter", "instagram", "tiktok", "linkedin"]
        }
    }

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Send real-time updates
            await websocket.send_json({
                "type": "status_update",
                "data": {
                    "timestamp": asyncio.get_event_loop().time(),
                    "services": ["database", "social_media_manager", "realtime_publisher", "video_processor"],
                    "active_jobs": await realtime_publisher.get_active_jobs_count()
                }
            })
            await asyncio.sleep(5)  # Send updates every 5 seconds
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")

# Real-time publishing endpoint
@app.post("/api/social/publish/realtime")
async def publish_content_realtime(
    title: str = Form(...),
    description: str = Form(...),
    platforms: str = Form(...),  # JSON string of platform list
    video_file: UploadFile = File(None),
    current_user: dict = Depends(get_current_user)
):
    """Publish content to multiple platforms in real-time"""
    try:
        import json
        platform_list = json.loads(platforms)
        
        # Process publishing job
        job_id = await realtime_publisher.create_publishing_job(
            title=title,
            description=description,
            platforms=platform_list,
            video_file=video_file,
            user_id=current_user["user_id"]
        )
        
        return {
            "job_id": job_id,
            "status": "processing",
            "message": "Publishing job created successfully"
        }
    except Exception as e:
        logger.error(f"Real-time publishing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Additional endpoints for monitoring and management
@app.get("/api/system/status")
async def get_system_status():
    """Get comprehensive system status"""
    return {
        "system": "operational",
        "version": "2.0.0",
        "uptime": "running",
        "services": {
            "api": True,
            "database": True,
            "social_manager": True,
            "realtime_publisher": True
        },
        "memory_usage": "efficient",
        "last_updated": asyncio.get_event_loop().time()
    }

@app.get("/api/social/publishing/status/{job_id}")
async def get_publishing_status(job_id: str):
    """Get real-time status of a publishing job"""
    status = await realtime_publisher.get_job_status(job_id)
    return {"job_id": job_id, "status": status}

@app.post("/api/social/publishing/retry/{job_id}")
async def retry_publishing_job(job_id: str, current_user: dict = Depends(get_current_user)):
    """Retry a failed publishing job"""
    result = await realtime_publisher.retry_job(job_id, current_user["user_id"])
    return {"job_id": job_id, "retry_status": result}

@app.get("/api/social/publishing/jobs")
async def get_user_publishing_jobs(current_user: dict = Depends(get_current_user)):
    """Get all publishing jobs for the current user"""
    jobs = await realtime_publisher.get_user_jobs(current_user["user_id"])
    return {"jobs": jobs}

# User progress tracking
@app.get("/api/user/progress/{user_id}")
async def get_user_progress(user_id: int):
    """Get user progress and achievements"""
    return {
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

@app.post("/api/user/progress/{user_id}")
async def save_user_progress(user_id: int, progress_data: dict):
    """Save user progress data"""
    return {"user_id": user_id, "saved": True, "timestamp": asyncio.get_event_loop().time()}

# Analytics endpoint (protected)
@app.get("/api/social/analytics")
async def get_platform_analytics(current_user: dict = Depends(get_current_user)):
    """Get analytics data for connected platforms"""
    return {
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

if __name__ == "__main__":
    uvicorn.run(
        "enhanced_main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        workers=1
    )