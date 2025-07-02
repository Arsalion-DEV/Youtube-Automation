"""
Real-time Publishing Status System
Provides WebSocket support for live publishing updates and retry mechanisms
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from fastapi import WebSocket, WebSocketDisconnect
from dataclasses import dataclass, asdict
import uuid

from social_media_manager import SocialMediaManager, PublishingJob, SocialPlatform

logger = logging.getLogger(__name__)

@dataclass
class PublishingUpdate:
    """Real-time publishing status update"""
    job_id: str
    status: str
    platform: Optional[str] = None
    progress: int = 0
    message: str = ""
    error: Optional[str] = None
    platform_results: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> set of connection_ids
        
    async def connect(self, websocket: WebSocket, user_id: str) -> str:
        """Connect a new WebSocket client"""
        await websocket.accept()
        connection_id = str(uuid.uuid4())
        
        self.active_connections[connection_id] = websocket
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)
        
        logger.info(f"WebSocket connected: {connection_id} for user {user_id}")
        return connection_id
    
    def disconnect(self, connection_id: str, user_id: str):
        """Disconnect a WebSocket client"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        logger.info(f"WebSocket disconnected: {connection_id}")
    
    async def send_to_user(self, user_id: str, message: Dict[str, Any]):
        """Send message to all connections for a specific user"""
        if user_id not in self.user_connections:
            return
        
        disconnected_connections = []
        
        for connection_id in self.user_connections[user_id].copy():
            if connection_id in self.active_connections:
                try:
                    websocket = self.active_connections[connection_id]
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error sending to connection {connection_id}: {e}")
                    disconnected_connections.append(connection_id)
        
        # Clean up failed connections
        for connection_id in disconnected_connections:
            self.disconnect(connection_id, user_id)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        disconnected_connections = []
        
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to connection {connection_id}: {e}")
                disconnected_connections.append(connection_id)
        
        # Clean up failed connections
        for connection_id in disconnected_connections:
            # Find user_id for this connection
            user_id = None
            for uid, conn_ids in self.user_connections.items():
                if connection_id in conn_ids:
                    user_id = uid
                    break
            
            if user_id:
                self.disconnect(connection_id, user_id)

class RealtimePublisher:
    """Real-time publishing coordinator with retry mechanisms"""
    
    def __init__(self, social_manager: SocialMediaManager):
        self.social_manager = social_manager
        self.connection_manager = ConnectionManager()
        self.active_jobs: Dict[str, PublishingJob] = {}
        self.retry_counts: Dict[str, int] = {}
        self.max_retries = 3
        
    async def start_publishing_job(
        self, 
        user_id: str,
        video_path: str,
        title: str,
        description: str,
        platforms: List[str],
        tags: List[str] = None,
        scheduled_time: Optional[datetime] = None
    ) -> str:
        """Start a new publishing job with real-time updates"""
        
        job_id = str(uuid.uuid4())
        
        # Create publishing job
        job = PublishingJob(
            id=job_id,
            user_id=user_id,
            video_path=video_path,
            title=title,
            description=description,
            platforms=[SocialPlatform(p) for p in platforms],
            tags=tags or [],
            scheduled_time=scheduled_time,
            status="processing",
            platform_results={},
            created_at=datetime.now()
        )
        
        self.active_jobs[job_id] = job
        self.retry_counts[job_id] = 0
        
        # Send initial update
        await self.send_update(user_id, PublishingUpdate(
            job_id=job_id,
            status="processing",
            progress=5,
            message="Starting video processing..."
        ))
        
        # Start async publishing
        asyncio.create_task(self._execute_publishing_job(job))
        
        return job_id
    
    async def _execute_publishing_job(self, job: PublishingJob):
        """Execute the publishing job with progress updates"""
        
        try:
            user_id = job.user_id
            
            # Step 1: Process video for all platforms
            await self.send_update(user_id, PublishingUpdate(
                job_id=job.id,
                status="processing",
                progress=10,
                message="Processing video for platforms..."
            ))
            
            processed_videos = await self._process_videos_for_platforms(job)
            
            # Step 2: Publish to each platform
            total_platforms = len(job.platforms)
            completed_platforms = 0
            
            for i, platform in enumerate(job.platforms):
                platform_name = platform.value
                
                await self.send_update(user_id, PublishingUpdate(
                    job_id=job.id,
                    status="publishing",
                    platform=platform_name,
                    progress=20 + (i * 60 // total_platforms),
                    message=f"Publishing to {platform_name}..."
                ))
                
                try:
                    # Get platform-specific video
                    video_path = processed_videos.get(platform_name, job.video_path)
                    
                    # Publish to platform
                    result = await self.social_manager.publish_to_platform(
                        platform=platform,
                        video_path=video_path,
                        title=job.title,
                        description=job.description,
                        tags=job.tags
                    )
                    
                    job.platform_results[platform_name] = result
                    completed_platforms += 1
                    
                    if result.get("success"):
                        await self.send_update(user_id, PublishingUpdate(
                            job_id=job.id,
                            status="publishing",
                            platform=platform_name,
                            progress=20 + ((i + 1) * 60 // total_platforms),
                            message=f"Successfully published to {platform_name}",
                            platform_results={platform_name: result}
                        ))
                    else:
                        await self.send_update(user_id, PublishingUpdate(
                            job_id=job.id,
                            status="publishing",
                            platform=platform_name,
                            progress=20 + ((i + 1) * 60 // total_platforms),
                            message=f"Failed to publish to {platform_name}",
                            error=result.get("error"),
                            platform_results={platform_name: result}
                        ))
                        
                except Exception as e:
                    logger.error(f"Error publishing to {platform_name}: {e}")
                    job.platform_results[platform_name] = {
                        "success": False,
                        "error": str(e),
                        "message": f"Publishing to {platform_name} failed"
                    }
                    
                    await self.send_update(user_id, PublishingUpdate(
                        job_id=job.id,
                        status="publishing",
                        platform=platform_name,
                        progress=20 + ((i + 1) * 60 // total_platforms),
                        message=f"Error publishing to {platform_name}",
                        error=str(e),
                        platform_results={platform_name: job.platform_results[platform_name]}
                    ))
            
            # Step 3: Complete job
            successful_platforms = sum(1 for result in job.platform_results.values() 
                                     if result.get("success"))
            
            if successful_platforms == total_platforms:
                job.status = "completed"
                await self.send_update(user_id, PublishingUpdate(
                    job_id=job.id,
                    status="completed",
                    progress=100,
                    message=f"Successfully published to all {total_platforms} platforms!",
                    platform_results=job.platform_results
                ))
            elif successful_platforms > 0:
                job.status = "partial"
                await self.send_update(user_id, PublishingUpdate(
                    job_id=job.id,
                    status="partial",
                    progress=100,
                    message=f"Published to {successful_platforms}/{total_platforms} platforms",
                    platform_results=job.platform_results
                ))
            else:
                job.status = "failed"
                await self.send_update(user_id, PublishingUpdate(
                    job_id=job.id,
                    status="failed",
                    progress=100,
                    message="Publishing failed on all platforms",
                    error="All platform publishing attempts failed",
                    platform_results=job.platform_results
                ))
            
            job.completed_at = datetime.now()
            
        except Exception as e:
            logger.error(f"Publishing job {job.id} failed: {e}")
            job.status = "failed"
            job.completed_at = datetime.now()
            
            await self.send_update(user_id, PublishingUpdate(
                job_id=job.id,
                status="failed",
                progress=100,
                message="Publishing job failed",
                error=str(e)
            ))
        
        finally:
            # Save job to database
            self.social_manager.save_publishing_job(job)
            
            # Clean up
            if job.id in self.active_jobs:
                del self.active_jobs[job.id]
    
    async def _process_videos_for_platforms(self, job: PublishingJob) -> Dict[str, str]:
        """Process video for each platform's requirements"""
        processed_videos = {}
        
        for platform in job.platforms:
            try:
                # Use FFmpeg processor to convert video
                processed_path = await self.social_manager.video_processor.convert_video_format(
                    input_path=job.video_path,
                    output_path=f"/tmp/{job.id}_{platform.value}.mp4",
                    target_format=self._get_platform_format(platform),
                    platform=platform
                )
                
                if processed_path:
                    processed_videos[platform.value] = processed_path
                else:
                    # Fallback to original video
                    processed_videos[platform.value] = job.video_path
                    
            except Exception as e:
                logger.error(f"Error processing video for {platform.value}: {e}")
                processed_videos[platform.value] = job.video_path
        
        return processed_videos
    
    def _get_platform_format(self, platform: SocialPlatform):
        """Get optimal video format for platform"""
        from social_media_manager import VideoFormat
        
        format_mapping = {
            SocialPlatform.YOUTUBE: VideoFormat.LANDSCAPE,
            SocialPlatform.FACEBOOK: VideoFormat.LANDSCAPE,
            SocialPlatform.TWITTER: VideoFormat.TWITTER,
            SocialPlatform.INSTAGRAM: VideoFormat.SQUARE,
            SocialPlatform.TIKTOK: VideoFormat.VERTICAL,
            SocialPlatform.LINKEDIN: VideoFormat.LANDSCAPE
        }
        
        return format_mapping.get(platform, VideoFormat.LANDSCAPE)
    
    async def retry_failed_job(self, job_id: str, user_id: str) -> bool:
        """Retry a failed publishing job"""
        
        if self.retry_counts.get(job_id, 0) >= self.max_retries:
            await self.send_update(user_id, PublishingUpdate(
                job_id=job_id,
                status="failed",
                message=f"Maximum retries ({self.max_retries}) exceeded",
                error="Too many retry attempts"
            ))
            return False
        
        # Get job from database
        job = self.social_manager.get_publishing_job(job_id)
        if not job:
            return False
        
        # Increment retry count
        self.retry_counts[job_id] = self.retry_counts.get(job_id, 0) + 1
        
        # Reset job status
        job.status = "retrying"
        job.platform_results = {}
        
        await self.send_update(user_id, PublishingUpdate(
            job_id=job_id,
            status="retrying",
            progress=0,
            message=f"Retrying publishing (attempt {self.retry_counts[job_id]})..."
        ))
        
        # Restart publishing
        self.active_jobs[job_id] = job
        asyncio.create_task(self._execute_publishing_job(job))
        
        return True
    
    async def send_update(self, user_id: str, update: PublishingUpdate):
        """Send real-time update to user"""
        message = {
            "type": "publishing_update",
            "data": asdict(update)
        }
        
        # Convert datetime to ISO string for JSON serialization
        if message["data"]["timestamp"]:
            message["data"]["timestamp"] = update.timestamp.isoformat()
        
        await self.connection_manager.send_to_user(user_id, message)
        
        # Also log the update
        logger.info(f"Publishing update for job {update.job_id}: {update.message}")
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a publishing job"""
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            return {
                "id": job.id,
                "status": job.status,
                "progress": getattr(job, 'progress', 0),
                "platform_results": job.platform_results,
                "created_at": job.created_at.isoformat(),
                "completed_at": job.completed_at.isoformat() if job.completed_at else None
            }
        
        # Try to get from database
        job = self.social_manager.get_publishing_job(job_id)
        if job:
            return {
                "id": job.id,
                "status": job.status,
                "progress": 100 if job.status in ["completed", "failed", "partial"] else 0,
                "platform_results": job.platform_results,
                "created_at": job.created_at.isoformat(),
                "completed_at": job.completed_at.isoformat() if job.completed_at else None
            }
        
        return None
    
    def get_connection_manager(self) -> ConnectionManager:
        """Get the connection manager for WebSocket handling"""
        return self.connection_manager