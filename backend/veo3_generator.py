"""
VEO3 Video Generator Module
Main interface for VEO3 video generation
"""

import asyncio
import logging
import time
import json
from typing import Dict, Any, Optional
from modules.veo3_integration.generator_simple import (
    GoogleVEO3Generator,
    VEO3GenerationRequest,
    create_veo3_config,
    create_generation_request
)

logger = logging.getLogger(__name__)

class VEO3Generator:
    """Main VEO3 Generator Interface"""
    
    def __init__(self):
        self.generator = GoogleVEO3Generator()
        self.is_available = True
        logger.info("VEO3Generator initialized successfully")
    
    async def generate_video(self, prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate video using VEO3"""
        try:
            logger.info(f"Generating video with prompt: {prompt[:100]}...")
            
            # Extract configuration parameters
            quality = config.get('quality', 'veo-3')
            duration = int(config.get('duration', 5))
            resolution = config.get('resolution', '720p')
            
            # Create generation request
            request = create_generation_request(
                prompt=prompt,
                quality=quality,
                duration=duration,
                resolution=resolution
            )
            
            # Generate video
            result = await self.generator.generate_video(request)
            
            # Convert result to dict format expected by backend
            return {
                'status': 'completed',
                'video_url': f"https://cdn.youtube-automation.com/clips/{result.video_url.split('/')[-1]}",
                'duration': result.duration,
                'resolution': result.resolution,
                'file_size': result.file_size,
                'generation_time': result.generation_time,
                'metadata': result.metadata
            }
            
        except Exception as e:
            logger.error(f"VEO3 generation failed: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def validate_prompt(self, prompt: str) -> bool:
        """Validate video generation prompt"""
        return self.generator.validate_prompt(prompt)
    
    def get_available_models(self):
        """Get available VEO3 models"""
        return self.generator.get_available_models()
    
    def health_check(self) -> Dict[str, Any]:
        """Check VEO3 generator health"""
        return {
            'available': self.is_available,
            'models': self.get_available_models(),
            'timestamp': time.time()
        }

# Global instance
veo3_generator = VEO3Generator()

# Function-based interface for backward compatibility
async def generate_video(prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate video using VEO3 (function interface)"""
    return await veo3_generator.generate_video(prompt, config)

def is_available() -> bool:
    """Check if VEO3 generator is available"""
    return veo3_generator.is_available
