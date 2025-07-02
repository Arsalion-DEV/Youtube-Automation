"""
VEO3 Video Generation Routes
Complete API routes for Google VEO3 integration
"""

import asyncio
import logging
from typing import Dict, Any
from fastapi import HTTPException, BackgroundTasks

from modules.veo3_integration.generator import (
    GoogleVEO3Generator, 
    VEO3Config, 
    VEO3GenerationRequest, 
    VEO3Quality, 
    VEO3AudioMode, 
    VEO3Resolution
)

logger = logging.getLogger(__name__)

def setup_veo3_routes(app, modules):
    """Setup VEO3 routes on the FastAPI app"""
    
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
            
            # Parse request parameters
            prompt = request.get('prompt')
            quality = VEO3Quality(request.get('quality', 'veo-3'))
            duration = min(int(request.get('duration', 8)), 8)  # Max 8 seconds
            audio_mode = VEO3AudioMode(request.get('audio_mode', 'full'))
            resolution = VEO3Resolution(request.get('resolution', '720p'))
            
            # Create VEO3 configuration
            config = VEO3Config(
                quality=quality,
                duration=duration,
                audio_mode=audio_mode,
                resolution=resolution,
                temperature=float(request.get('temperature', 0.7)),
                aspect_ratio=request.get('aspect_ratio', '16:9')
            )
            
            # Create generation request
            veo3_request = VEO3GenerationRequest(
                prompt=prompt,
                config=config,
                negative_prompt=request.get('negative_prompt'),
                reference_image=request.get('reference_image'),
                motion_intensity=float(request.get('motion_intensity', 0.5))
            )
            
            # Generate video asynchronously
            task_id = f"veo3_gen_{int(asyncio.get_event_loop().time())}"
            background_tasks.add_task(
                process_veo3_generation,
                task_id,
                veo3_request,
                modules
            )
            
            return {
                "task_id": task_id,
                "status": "queued",
                "message": "VEO3 video generation started",
                "estimated_time": f"{duration * 15} seconds"  # Rough estimate
            }
            
        except Exception as e:
            logger.error(f"VEO3 generation error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/veo3/config")
    async def get_veo3_config():
        """Get VEO3 configuration options"""
        return {
            "qualities": [quality.value for quality in VEO3Quality],
            "resolutions": [res.value for res in VEO3Resolution],
            "audio_modes": [mode.value for mode in VEO3AudioMode],
            "max_duration": 8,
            "aspect_ratios": ["16:9", "9:16", "1:1", "4:3"],
            "temperature_range": [0.0, 1.0],
            "motion_intensity_range": [0.0, 1.0]
        }

    @app.get("/api/veo3/status/{task_id}")
    async def get_veo3_status(task_id: str):
        """Get VEO3 generation status"""
        try:
            veo3_generator = modules.get('veo3_generator')
            if not veo3_generator:
                raise HTTPException(status_code=503, detail="VEO3 generator not available")
            
            status = await veo3_generator.get_generation_status(task_id)
            return status
            
        except Exception as e:
            logger.error(f"Error getting VEO3 status: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/veo3/models")
    async def get_veo3_models():
        """Get available VEO3 models"""
        try:
            veo3_generator = modules.get('veo3_generator')
            if not veo3_generator:
                return {"models": []}
            
            models = await veo3_generator.list_models()
            return {"models": models}
            
        except Exception as e:
            logger.error(f"Error getting VEO3 models: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/veo3/estimate-cost")
    async def estimate_veo3_cost(request: Dict[str, Any]):
        """Estimate VEO3 generation cost"""
        try:
            veo3_generator = modules.get('veo3_generator')
            if not veo3_generator:
                raise HTTPException(status_code=503, detail="VEO3 generator not available")
            
            # Parse request parameters
            quality = VEO3Quality(request.get('quality', 'veo-3'))
            duration = min(int(request.get('duration', 8)), 8)
            resolution = VEO3Resolution(request.get('resolution', '720p'))
            
            config = VEO3Config(
                quality=quality,
                duration=duration,
                resolution=resolution
            )
            
            veo3_request = VEO3GenerationRequest(
                prompt=request.get('prompt', 'sample prompt'),
                config=config
            )
            
            cost_estimate = await veo3_generator.estimate_cost(veo3_request)
            return cost_estimate
            
        except Exception as e:
            logger.error(f"Error estimating VEO3 cost: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

async def process_veo3_generation(task_id: str, veo3_request: VEO3GenerationRequest, modules):
    """Process VEO3 video generation (background task)"""
    try:
        logger.info(f"Processing VEO3 generation task: {task_id}")
        
        # Get VEO3 generator
        veo3_generator = modules.get('veo3_generator')
        if not veo3_generator:
            raise ValueError("VEO3 generator not available")
        
        # Generate video
        result = await veo3_generator.generate_video(veo3_request)
        
        logger.info(f"VEO3 generation completed: {task_id}")
        
        return {
            "task_id": task_id,
            "status": "completed",
            "result": {
                "video_url": result.video_url,
                "audio_url": result.audio_url,
                "thumbnail_url": result.thumbnail_url,
                "duration": result.duration,
                "resolution": result.resolution,
                "generation_id": result.generation_id,
                "metadata": result.metadata
            }
        }
        
    except Exception as e:
        logger.error(f"VEO3 generation failed for task {task_id}: {str(e)}")
        return {
            "task_id": task_id,
            "status": "failed",
            "error": str(e)
        }