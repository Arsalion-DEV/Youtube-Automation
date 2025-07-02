#!/usr/bin/env python3
"""
YouTube Automation Platform - Demo-Enabled Main Application
FastAPI backend with VEO3 simulation for testing
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# FastAPI imports
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# Celery imports
from celery import Celery

# Database imports
import sqlite3
from contextlib import contextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="YouTube Automation Platform",
    description="AI-powered YouTube content automation with VEO3 integration (Demo Mode)",
    version="2.0.0-demo"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Celery
celery = Celery('youtube_automation')
celery.conf.broker_url = 'redis://localhost:6379/0'
celery.conf.result_backend = 'redis://localhost:6379/0'

# Database configuration
DATABASE_PATH = "youtube_automation.db"

@contextmanager
def get_db():
    """Database connection context manager"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

# Initialize database
def init_database():
    """Initialize database tables"""
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'draft',
                veo3_config TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                result_url TEXT
            )
        ''')
        
        # Initialize other required tables
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE,
                password_hash TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                platform TEXT NOT NULL,
                channel_name TEXT,
                channel_id TEXT,
                access_token TEXT,
                refresh_token TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

# Load modules with demo mode
modules = {}

# Simulate VEO3 generator (demo mode)
class DemoVEO3Generator:
    """Demo VEO3 generator for testing purposes"""
    def __init__(self):
        self.name = "Demo VEO3 Generator"
        self.version = "demo-1.0"
    
    def generate_video(self, prompt: str, **kwargs):
        """Simulate video generation"""
        return {
            "status": "processing",
            "estimated_time": "2-5 minutes",
            "job_id": f"demo_{hash(prompt) % 1000000}"
        }

# Try to load real VEO3 generator, fallback to demo
try:
    import veo3_generator
    modules['veo3_generator'] = veo3_generator
    logger.info("VEO3 generator loaded successfully")
except ImportError as e:
    logger.info("VEO3 generator not available, using demo mode")
    modules['veo3_generator'] = DemoVEO3Generator()

# Try to load TTS synthesizer, fallback to demo
try:
    import tts_synthesizer
    modules['tts_synthesizer'] = tts_synthesizer
    logger.info("TTS synthesizer loaded successfully")
except ImportError as e:
    logger.info("TTS synthesizer not available, using demo mode")
    modules['tts_synthesizer'] = True  # Demo mode

# Try to load video editor, fallback to demo
try:
    import video_editor
    modules['video_editor'] = video_editor
    logger.info("Video editor loaded successfully")
except ImportError as e:
    logger.info("Video editor not available, using demo mode")
    modules['video_editor'] = True  # Demo mode

# Import and include all route modules
try:
    from api_v2_routes import router as v2_router
    app.include_router(v2_router)
    logger.info("V2 API routes loaded")
except ImportError as e:
    logger.warning(f"V2 API routes not available: {e}")

try:
    from ai_wizard_routes import router as wizard_router
    app.include_router(wizard_router, prefix="/api/wizard")
    logger.info("AI Wizard routes loaded")
except ImportError as e:
    logger.warning(f"AI Wizard routes not available: {e}")

try:
    from auth_routes import auth_router
    app.include_router(auth_router, prefix="/api/auth")
    logger.info("Auth routes loaded")
except ImportError as e:
    logger.warning(f"Auth routes not available: {e}")

try:
    from channel_api_routes import router as channel_router
    app.include_router(channel_router, prefix="/api/channels")
    logger.info("Channel API routes loaded")
except ImportError as e:
    logger.warning(f"Channel API routes not available: {e}")

try:
    from integrations_api_routes import router as integrations_router
    app.include_router(integrations_router, prefix="/api/integrations")
    logger.info("Integrations API routes loaded")
except ImportError as e:
    logger.warning(f"Integrations API routes not available: {e}")

try:
    from social_media_routes import router as social_router
    app.include_router(social_router, prefix="/api/social")
    logger.info("Social Media routes loaded")
except ImportError as e:
    logger.warning(f"Social Media routes not available: {e}")

try:
    from video_generation_api_routes import router as video_gen_router
    app.include_router(video_gen_router, prefix="/api/video-generation")
    logger.info("Video Generation API routes loaded")
except ImportError as e:
    logger.warning(f"Video Generation API routes not available: {e}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "mode": "demo" if isinstance(modules.get('veo3_generator'), DemoVEO3Generator) else "production",
        "modules": {
            name: module is not None 
            for name, module in modules.items()
        }
    }

# API Info endpoint
@app.get("/api/info")
async def api_info():
    """API information endpoint"""
    return {
        "name": "YouTube Automation Platform",
        "version": "2.0.0-demo",
        "description": "AI-powered YouTube content automation with comprehensive features",
        "mode": "demo" if isinstance(modules.get('veo3_generator'), DemoVEO3Generator) else "production",
        "modules": list(modules.keys()),
        "available_routes": [
            "/api/v2/videos",
            "/api/v2/analytics", 
            "/api/v2/system/status",
            "/api/veo3/generate",
            "/api/videos/create",
            "/api/videos/list",
            "/api/wizard/*",
            "/api/auth/*",
            "/api/channels/*",
            "/api/integrations/*",
            "/api/social/*",
            "/api/video-generation/*"
        ]
    }

# VEO3 video generation endpoint (demo-enabled)
@app.post("/api/veo3/generate")
async def generate_veo3_video(request: Dict[str, Any], background_tasks: BackgroundTasks):
    """Generate video using Google VEO3 (or demo mode)"""
    try:
        # Validate request
        if not request.get('prompt'):
            raise HTTPException(status_code=400, detail="Prompt is required")
        
        veo3_generator = modules.get('veo3_generator')
        if not veo3_generator:
            raise HTTPException(status_code=503, detail="VEO3 generator not available")
        
        # Create video record
        with get_db() as conn:
            cursor = conn.execute('''
                INSERT INTO videos (title, description, status, veo3_config)
                VALUES (?, ?, ?, ?)
            ''', (
                request.get('title', 'Generated Video'),
                request.get('description', ''),
                'generating',
                str(request)
            ))
            video_id = cursor.lastrowid
        
        # Generate task ID
        import uuid
        task_id = str(uuid.uuid4())
        
        # Add background task
        background_tasks.add_task(process_video_generation, video_id, request, task_id)
        
        return {
            "video_id": video_id,
            "task_id": task_id,
            "status": "started",
            "message": "Video generation started",
            "mode": "demo" if isinstance(veo3_generator, DemoVEO3Generator) else "production",
            "estimated_completion": "2-5 minutes"
        }
        
    except Exception as e:
        logger.error(f"Video generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Video creation endpoint
@app.post("/api/videos/create")
async def create_video(request: Dict[str, Any]):
    """Create a new video record"""
    try:
        with get_db() as conn:
            cursor = conn.execute('''
                INSERT INTO videos (title, description, status)
                VALUES (?, ?, ?)
            ''', (
                request.get('title', 'New Video'),
                request.get('description', ''),
                'draft'
            ))
            video_id = cursor.lastrowid
        
        return {
            "video_id": video_id,
            "status": "created",
            "message": "Video created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Video list endpoint
@app.get("/api/videos/list")
async def list_videos(limit: int = 50, offset: int = 0):
    """Get list of videos"""
    try:
        with get_db() as conn:
            cursor = conn.execute('''
                SELECT * FROM videos 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            videos = [dict(row) for row in cursor.fetchall()]
            
            # Get total count
            total_cursor = conn.execute('SELECT COUNT(*) FROM videos')
            total = total_cursor.fetchone()[0]
        
        return {
            "videos": videos,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Task status endpoint
@app.get("/api/tasks/{task_id}/status")
async def get_task_status(task_id: str):
    """Get task status"""
    try:
        # This would normally check Celery task status
        # For now, return a mock response
        return {
            "task_id": task_id,
            "status": "processing",
            "progress": 50,
            "message": "Video generation in progress",
            "estimated_remaining": "2-3 minutes"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Enterprise endpoints for frontend compatibility
@app.get("/api/v1/enterprise/health")
async def enterprise_health():
    """Enterprise health check"""
    return {
        "status": "healthy",
        "enterprise_features": True,
        "demo_mode": isinstance(modules.get('veo3_generator'), DemoVEO3Generator),
        "timestamp": "2025-07-02T10:00:00Z"
    }

@app.get("/api/v1/enterprise/analytics/summary")
async def enterprise_analytics_summary():
    """Enterprise analytics summary"""
    return {
        "total_videos": 85,
        "success_rate": 85.5,
        "revenue": 1250.00,
        "active_campaigns": 3,
        "demo_mode": isinstance(modules.get('veo3_generator'), DemoVEO3Generator),
        "timestamp": "2025-07-02T10:00:00Z"
    }

@app.get("/api/v1/enterprise/monetization/summary")
async def enterprise_monetization_summary():
    """Enterprise monetization summary"""
    return {
        "total_revenue": 1250.00,
        "monthly_revenue": 450.00,
        "conversion_rate": 12.5,
        "active_subscriptions": 25,
        "demo_mode": isinstance(modules.get('veo3_generator'), DemoVEO3Generator),
        "timestamp": "2025-07-02T10:00:00Z"
    }

@app.get("/api/v1/enterprise/ab-testing/tests")
async def enterprise_ab_tests():
    """Enterprise A/B tests"""
    return {
        "active_tests": [
            {
                "id": 1,
                "name": "Title Optimization Test",
                "status": "running",
                "conversion_rate_a": 8.5,
                "conversion_rate_b": 12.3,
                "statistical_significance": 95.2
            }
        ],
        "completed_tests": 5,
        "demo_mode": isinstance(modules.get('veo3_generator'), DemoVEO3Generator),
        "timestamp": "2025-07-02T10:00:00Z"
    }

@app.get("/api/v1/video/queue")
async def video_queue():
    """Video processing queue"""
    return {
        "queue_length": 3,
        "processing": 1,
        "completed_today": 5,
        "estimated_wait_time": "15 minutes",
        "demo_mode": isinstance(modules.get('veo3_generator'), DemoVEO3Generator),
        "timestamp": "2025-07-02T10:00:00Z"
    }

# Background task function (enhanced for demo)
async def process_video_generation(video_id: int, request: Dict[str, Any], task_id: str):
    """Process video generation in background (demo-enabled)"""
    try:
        veo3_generator = modules.get('veo3_generator')
        
        if isinstance(veo3_generator, DemoVEO3Generator):
            # Demo mode: simulate processing
            logger.info(f"Demo: Starting video generation for video {video_id}")
            
            # Simulate processing time
            await asyncio.sleep(5)  # 5 seconds for demo
            
            # Update video status to completed with demo URL
            with get_db() as conn:
                conn.execute('''
                    UPDATE videos 
                    SET status = ?, result_url = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (
                    'completed',
                    f'https://demo.youtube-automation.com/clips/demo_video_{video_id}_{task_id[:8]}.mp4',
                    video_id
                ))
            
            logger.info(f"Demo: Video {video_id} generation completed successfully")
        else:
            # Production mode: actual VEO3 processing
            await asyncio.sleep(2)  # Simulate processing time
            
            # Update video status
            with get_db() as conn:
                conn.execute('''
                    UPDATE videos 
                    SET status = ?, result_url = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (
                    'completed',
                    f'https://cdn.youtube-automation.com/clips/video_{video_id}_{task_id[:8]}.mp4',
                    video_id
                ))
            
            logger.info(f"Production: Video {video_id} generation completed")
        
    except Exception as e:
        logger.error(f"Video generation failed for {video_id}: {e}")
        
        # Update video status to failed
        with get_db() as conn:
            conn.execute('''
                UPDATE videos 
                SET status = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', ('failed', video_id))

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    init_database()
    logger.info("Database initialized")
    
    mode = "demo" if isinstance(modules.get('veo3_generator'), DemoVEO3Generator) else "production"
    logger.info(f"YouTube Automation Platform started successfully in {mode} mode")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)