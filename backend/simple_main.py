#!/usr/bin/env python3
"""
Simple YouTube Automation Platform - Simplified Backend
FastAPI backend without Celery for testing
"""

import os
import sys
import asyncio
import logging
import json
import time
from typing import Dict, Any, Optional
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.staticfiles import StaticFiles
# FastAPI imports
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

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
# Import and include v2 API routes
from api_v2_routes import router as v2_router
from auth_routes import auth_router
from ai_wizard_routes import wizard_router
from social_media_routes import router as social_router
app.include_router(wizard_router)
app.include_router(social_router)
app.include_router(auth_router)
app.include_router(v2_router)
# Mount static files for video assets
app.mount("/assets", StaticFiles(directory="/home/ubuntu/Veo-3-Automation/backend/assets"), name="assets")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
                result_url TEXT,
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
        from modules.veo3_integration.generator_simple_v2 import GoogleVEO3Generator
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
async def generate_veo3_video(request: Dict[str, Any]):
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
                json.dumps(request)
            ))
            video_id = cursor.lastrowid
            conn.commit()
        
        # Generate video immediately (no background task)
        from modules.veo3_integration.generator_simple_v2 import create_generation_request
        
        veo3_request = create_generation_request(
            prompt=request['prompt'],
            quality=request.get('quality', 'veo-3'),
            duration=int(request.get('duration', 8)),
            resolution=request.get('resolution', '720p')
        )
        
        # Generate video
        result = await veo3_generator.generate_video(veo3_request)
        
        # Update database with result
        with get_db() as conn:
            conn.execute('''
                UPDATE videos 
                SET status = ?, result_url = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', ('completed', result.video_url, video_id))
            conn.commit()
        
        return {
            "video_id": video_id,
            "status": "completed",
            "message": "Video generation completed",
            "result": {
                "video_url": result.video_url,
                "duration": result.duration,
                "resolution": result.resolution,
                "metadata": result.metadata
            }
        }
        
    except Exception as e:
        logger.error(f"Error in video generation: {str(e)}")
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

# Get video by ID
@app.get("/api/videos/{video_id}")
async def get_video(video_id: int):
    """Get video by ID"""
    try:
        with get_db() as conn:
            row = conn.execute('''
                SELECT * FROM videos WHERE id = ?
            ''', (video_id,)).fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Video not found")
        
        return dict(row)
        
    except Exception as e:
        logger.error(f"Error getting video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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
        "simple_main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
# Fixed Task Status Management endpoints

@app.get("/api/tasks/status")
async def get_all_tasks_status():
    """Get status of all tasks"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT task_id, video_id, status, created_at, updated_at, progress, error_message
                FROM generation_tasks 
                ORDER BY created_at DESC 
                LIMIT 50
            """)
            
            tasks = []
            for row in cursor.fetchall():
                task_data = dict(row)
                tasks.append(task_data)
        
        return {
            "tasks": tasks,
            "total": len(tasks),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error getting all tasks status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks/{task_id}/status")
async def get_task_status(task_id: str):
    """Get status of a specific task"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM generation_tasks WHERE task_id = ?
            """, (task_id,))
            
            row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task_data = dict(row)
        
        return {
            "task_id": task_id,
            "status": task_data.get("status", "unknown"),
            "progress": task_data.get("progress", 0),
            "video_id": task_data.get("video_id"),
            "created_at": task_data.get("created_at"),
            "updated_at": task_data.get("updated_at"),
            "error_message": task_data.get("error_message")
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
