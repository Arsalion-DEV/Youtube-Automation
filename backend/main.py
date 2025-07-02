#!/usr/bin/env python3
"""
YouTube Automation Platform - Main Application
FastAPI backend with VEO3 integration
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
    description="AI-powered YouTube content automation with VEO3 integration",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Celery
celery = Celery(
    'youtube_automation',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379')
)

# Global modules container
modules = {}

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///youtube_automation.db')

@contextmanager
def get_db():
    """Database connection context manager"""
    conn = sqlite3.connect('youtube_automation.db')
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    """Initialize database with basic tables"""
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'pending',
                veo3_config TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS generation_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT UNIQUE NOT NULL,
                video_id INTEGER,
                status TEXT DEFAULT 'pending',
                progress INTEGER DEFAULT 0,
                result_data TEXT,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (video_id) REFERENCES videos (id)
            )
        ''')
        
        conn.commit()

def load_modules():
    """Load and initialize all modules"""
    global modules
    
    try:
        # Initialize VEO3 generator
        from modules.veo3_integration.generator_simple import GoogleVEO3Generator
        veo3_generator = GoogleVEO3Generator()
        modules['veo3_generator'] = veo3_generator
        logger.info("VEO3 generator initialized")
    except ImportError as e:
        logger.warning(f"VEO3 generator not available: {e}")
        modules['veo3_generator'] = None
    
    try:
        # Initialize TTS synthesizer
        from modules.tts.synthesizer import TTSSynthesizer
        tts_synthesizer = TTSSynthesizer()
        modules['tts_synthesizer'] = tts_synthesizer
        logger.info("TTS synthesizer initialized")
    except ImportError as e:
        logger.warning(f"TTS synthesizer not available: {e}")
        modules['tts_synthesizer'] = None
    
    try:
        # Initialize video editor
        from modules.video_editor.editor import VideoEditor
        video_editor = VideoEditor()
        modules['video_editor'] = video_editor
        logger.info("Video editor initialized")
    except ImportError as e:
        logger.warning(f"Video editor not available: {e}")
        modules['video_editor'] = None

# Import v2 API routes
from api_v2_routes import router as v2_router
app.include_router(v2_router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
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
        "version": "1.0.0",
        "description": "AI-powered YouTube content automation with VEO3 integration",
        "modules": list(modules.keys()),
        "endpoints": [
            "/api/veo3/generate",
            "/api/videos/create",
            "/api/videos/list",
            "/api/tasks/status"
        ]
    }

# VEO3 video generation endpoint
@app.post("/api/veo3/generate")
async def generate_veo3_video(request: Dict[str, Any], background_tasks: BackgroundTasks):
    """Generate video using Google VEO3"""
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
            conn.commit()
        
        # Start background task
        task = generate_video_task.delay(video_id, request)
        
        # Record task
        with get_db() as conn:
            conn.execute('''
                INSERT INTO generation_tasks (task_id, video_id, status)
                VALUES (?, ?, ?)
            ''', (task.id, video_id, 'started'))
            conn.commit()
        
        return {
            "video_id": video_id,
            "task_id": task.id,
            "status": "started",
            "message": "Video generation started"
        }
        
    except Exception as e:
        logger.error(f"Error starting video generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Video creation endpoint
@app.post("/api/videos/create")
async def create_video(request: Dict[str, Any]):
    """Create a new video project"""
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
            conn.commit()
        
        return {
            "video_id": video_id,
            "status": "created",
            "title": request.get('title', 'New Video')
        }
        
    except Exception as e:
        logger.error(f"Error creating video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# List videos endpoint
@app.get("/api/videos/list")
async def list_videos(limit: int = 10, offset: int = 0):
    """List all videos"""
    try:
        with get_db() as conn:
            rows = conn.execute('''
                SELECT * FROM videos
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            ''', (limit, offset)).fetchall()
        
        videos = [dict(row) for row in rows]
        return {
            "videos": videos,
            "total": len(videos)
        }
        
    except Exception as e:
        logger.error(f"Error listing videos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Task status endpoint
@app.get("/api/tasks/{task_id}/status")
async def get_task_status(task_id: str):
    """Get status of a background task"""
    try:
        with get_db() as conn:
            row = conn.execute('''
                SELECT * FROM generation_tasks WHERE task_id = ?
            ''', (task_id,)).fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Get Celery task status
        task = celery.AsyncResult(task_id)
        
        return {
            "task_id": task_id,
            "status": task.status,
            "progress": dict(row).get('progress', 0),
            "result": task.result if task.successful() else None,
            "error": task.traceback if task.failed() else dict(row).get('error_message')
        }
        
    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Celery task for video generation
@celery.task(bind=True)
def generate_video_task(self, video_id: int, config: Dict[str, Any]):
    """Background task for video generation"""
    try:
        # Update task status
        self.update_state(state='PROGRESS', meta={'progress': 10})
        
        # Mock VEO3 generation (replace with actual implementation)
        import time
        import json
        
        # Simulate generation process
        for i in range(10, 101, 10):
            time.sleep(1)  # Simulate work
            self.update_state(state='PROGRESS', meta={'progress': i})
        
        # Mock result
        result = {
            "video_url": f"https://example.com/generated_video_{video_id}.mp4",
            "duration": config.get('duration', 8),
            "resolution": config.get('resolution', '720p')
        }
        
        # Update database
        with get_db() as conn:
            conn.execute('''
                UPDATE videos SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', ('completed', video_id))
            
            conn.execute('''
                UPDATE generation_tasks 
                SET status = ?, progress = 100, result_data = ?, updated_at = CURRENT_TIMESTAMP
                WHERE video_id = ?
            ''', ('completed', json.dumps(result), video_id))
            
            conn.commit()
        
        return result
        
    except Exception as e:
        logger.error(f"Error in video generation task: {str(e)}")
        
        # Update database with error
        with get_db() as conn:
            conn.execute('''
                UPDATE videos SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', ('failed', video_id))
            
            conn.execute('''
                UPDATE generation_tasks 
                SET status = ?, error_message = ?, updated_at = CURRENT_TIMESTAMP
                WHERE video_id = ?
            ''', ('failed', str(e), video_id))
            
            conn.commit()
        
        raise

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    logger.info("Starting YouTube Automation Platform...")
    
    # Initialize database
    init_database()
    logger.info("Database initialized")
    
    # Load modules
    load_modules()
    logger.info("Modules loaded")
    
    # Create directories
    os.makedirs('assets/images', exist_ok=True)
    os.makedirs('assets/clips', exist_ok=True)
    os.makedirs('assets/audio', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    logger.info("Directories created")
    
    logger.info("YouTube Automation Platform started successfully!")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down YouTube Automation Platform...")

if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )