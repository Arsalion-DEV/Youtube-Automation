"""
FastAPI routes for multi-platform social media publishing
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from social_media_manager import (
    SocialMediaManager, SocialPlatform, PublishingJob, PlatformConfig
)
from auth import get_current_user  # Assuming this exists from the auth system

router = APIRouter(tags=["social-media"])
security = HTTPBearer()

# Initialize the social media manager
social_manager = SocialMediaManager()
social_manager.initialize_database()

# Pydantic models for request/response
class PlatformConnectionRequest(BaseModel):
    platform: str
    oauth_tokens: Dict[str, str]
    configuration: Optional[Dict[str, Any]] = {}

class PublishingRequest(BaseModel):
    title: str
    description: str
    platforms: List[str]
    tags: Optional[List[str]] = []
    scheduled_time: Optional[datetime] = None

class PublishingJobResponse(BaseModel):
    id: str
    title: str
    platforms: List[str]
    status: str
    platform_results: Dict[str, Any]
    created_at: datetime
    completed_at: Optional[datetime]

class PlatformStatus(BaseModel):
    platform: str
    connected: bool
    last_updated: Optional[datetime]
    configuration: Dict[str, Any]

class PublishingAnalytics(BaseModel):
    total_posts: int
    successful_posts: int
    failed_posts: int
    platforms_connected: int
    recent_activity: List[Dict[str, Any]]

# OAuth configuration endpoints
@router.get("/platforms/available")
async def get_available_platforms():
    """Get list of available social media platforms"""
    platforms = [
        {
            "id": "facebook",
            "name": "Facebook",
            "description": "Share videos to Facebook pages and profiles",
            "oauth_url": "/api/social/oauth/facebook",
            "video_specs": {
                "max_size_mb": 4000,
                "max_duration_seconds": 240,
                "formats": ["mp4", "mov"],
                "aspect_ratios": ["16:9", "1:1", "4:5"]
            }
        },
        {
            "id": "twitter",
            "name": "Twitter/X",
            "description": "Post videos to Twitter timeline",
            "oauth_url": "/api/social/oauth/twitter",
            "video_specs": {
                "max_size_mb": 512,
                "max_duration_seconds": 140,
                "formats": ["mp4"],
                "aspect_ratios": ["16:9", "1:1"]
            }
        },
        {
            "id": "instagram",
            "name": "Instagram",
            "description": "Share to Instagram feed and stories",
            "oauth_url": "/api/social/oauth/instagram",
            "video_specs": {
                "max_size_mb": 4000,
                "max_duration_seconds": 60,
                "formats": ["mp4"],
                "aspect_ratios": ["9:16", "1:1", "4:5"]
            }
        },
        {
            "id": "tiktok",
            "name": "TikTok",
            "description": "Upload videos to TikTok",
            "oauth_url": "/api/social/oauth/tiktok",
            "video_specs": {
                "max_size_mb": 287,
                "max_duration_seconds": 180,
                "formats": ["mp4"],
                "aspect_ratios": ["9:16"]
            }
        },
        {
            "id": "linkedin",
            "name": "LinkedIn",
            "description": "Share professional video content",
            "oauth_url": "/api/social/oauth/linkedin",
            "video_specs": {
                "max_size_mb": 5000,
                "max_duration_seconds": 600,
                "formats": ["mp4"],
                "aspect_ratios": ["16:9", "1:1"]
            }
        }
    ]
    
    return {"platforms": platforms}

@router.get("/platforms/connected")
async def get_connected_platforms(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get user's connected social media platforms"""
    try:
        # Get current user
        user = await get_current_user(credentials.credentials)
        user_id = user["user_id"]
        
        # Get user's platform configurations
        platforms = social_manager.get_user_platforms(user_id)
        
        connected_platforms = []
        for platform_config in platforms:
            connected_platforms.append({
                "platform": platform_config.platform.value,
                "connected": platform_config.enabled,
                "configuration": platform_config.video_specs,
                "oauth_status": "connected" if platform_config.oauth_tokens else "disconnected"
            })
        
        return {"connected_platforms": connected_platforms}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching platforms: {str(e)}")

@router.post("/platforms/connect")
async def connect_platform(
    request: PlatformConnectionRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Connect a social media platform"""
    try:
        # Get current user
        user = await get_current_user(credentials.credentials)
        user_id = user["user_id"]
        
        # Validate platform
        try:
            platform = SocialPlatform(request.platform)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid platform: {request.platform}")
        
        # Validate required OAuth tokens for each platform
        required_tokens = {
            "facebook": ["access_token", "page_id"],
            "twitter": ["api_key", "api_secret", "access_token", "access_secret"],
            "instagram": ["access_token", "account_id"],
            "tiktok": ["access_token"],
            "linkedin": ["access_token", "person_id"]
        }
        
        required = required_tokens.get(request.platform, [])
        missing_tokens = [token for token in required if token not in request.oauth_tokens]
        
        if missing_tokens:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required tokens for {request.platform}: {missing_tokens}"
            )
        
        # Save platform configuration
        social_manager.add_platform_config(
            user_id,
            platform,
            request.oauth_tokens,
            request.configuration
        )
        
        return {
            "success": True,
            "message": f"Successfully connected {request.platform}",
            "platform": request.platform
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting platform: {str(e)}")

@router.delete("/platforms/{platform}/disconnect")
async def disconnect_platform(
    platform: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Disconnect a social media platform"""
    try:
        # Get current user
        user = await get_current_user(credentials.credentials)
        user_id = user["user_id"]
        
        # Validate platform
        try:
            platform_enum = SocialPlatform(platform)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid platform: {platform}")
        
        # Remove platform configuration
        import sqlite3
        conn = sqlite3.connect(social_manager.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE social_platforms 
                SET enabled = 0, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ? AND platform = ?
            ''', (user_id, platform))
            
            conn.commit()
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail=f"Platform {platform} not found")
            
        finally:
            conn.close()
        
        return {
            "success": True,
            "message": f"Successfully disconnected {platform}",
            "platform": platform
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error disconnecting platform: {str(e)}")

# Publishing endpoints
@router.post("/publish")
async def create_publishing_job(
    video: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(...),
    platforms: str = Form(...),  # JSON string of platform list
    tags: str = Form("[]"),  # JSON string of tags
    scheduled_time: Optional[str] = Form(None),  # ISO string
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a new multi-platform publishing job"""
    try:
        # Get current user
        user = await get_current_user(credentials.credentials)
        user_id = user["user_id"]
        
        # Parse platforms and tags
        try:
            platform_list = json.loads(platforms)
            tag_list = json.loads(tags)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in platforms or tags")
        
        # Validate platforms
        platform_enums = []
        for platform_name in platform_list:
            try:
                platform_enums.append(SocialPlatform(platform_name))
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid platform: {platform_name}")
        
        # Parse scheduled time
        scheduled_datetime = None
        if scheduled_time:
            try:
                scheduled_datetime = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid scheduled_time format")
        
        # Save uploaded video
        import tempfile
        import shutil
        
        temp_dir = tempfile.mkdtemp()
        video_filename = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{video.filename}"
        video_path = os.path.join(temp_dir, video_filename)
        
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
        
        # Create publishing job
        job_id = await social_manager.create_publishing_job(
            user_id=user_id,
            video_path=video_path,
            title=title,
            description=description,
            platforms=platform_enums,
            tags=tag_list,
            scheduled_time=scheduled_datetime
        )
        
        return {
            "success": True,
            "job_id": job_id,
            "message": "Publishing job created successfully",
            "platforms": platform_list,
            "scheduled": scheduled_datetime is not None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating publishing job: {str(e)}")

@router.get("/jobs")
async def get_publishing_jobs(
    limit: int = 50,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get user's publishing job history"""
    try:
        # Get current user
        user = await get_current_user(credentials.credentials)
        user_id = user["user_id"]
        
        # Get publishing history
        history = social_manager.get_publishing_history(user_id, limit)
        
        return {
            "jobs": history,
            "total": len(history)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching jobs: {str(e)}")

@router.get("/jobs/{job_id}")
async def get_publishing_job(
    job_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get specific publishing job details"""
    try:
        # Get current user
        user = await get_current_user(credentials.credentials)
        user_id = user["user_id"]
        
        # Get job details
        import sqlite3
        conn = sqlite3.connect(social_manager.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, title, description, platforms, status, platform_results, 
                       created_at, completed_at, scheduled_time
                FROM publishing_jobs
                WHERE id = ? AND user_id = ?
            ''', (job_id, user_id))
            
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Publishing job not found")
            
            job_data = {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "platforms": json.loads(row[3]),
                "status": row[4],
                "platform_results": json.loads(row[5]) if row[5] else {},
                "created_at": row[6],
                "completed_at": row[7],
                "scheduled_time": row[8]
            }
            
            return {"job": job_data}
            
        finally:
            conn.close()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching job: {str(e)}")

@router.delete("/jobs/{job_id}")
async def cancel_publishing_job(
    job_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Cancel a scheduled publishing job"""
    try:
        # Get current user
        user = await get_current_user(credentials.credentials)
        user_id = user["user_id"]
        
        # Update job status
        import sqlite3
        conn = sqlite3.connect(social_manager.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE publishing_jobs 
                SET status = 'cancelled', completed_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ? AND status = 'pending'
            ''', (job_id, user_id))
            
            conn.commit()
            
            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=404, 
                    detail="Job not found or cannot be cancelled"
                )
            
        finally:
            conn.close()
        
        return {
            "success": True,
            "message": "Publishing job cancelled successfully",
            "job_id": job_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cancelling job: {str(e)}")

# Analytics endpoints
@router.get("/analytics")
async def get_publishing_analytics(
    days: int = 30,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get publishing analytics for the user"""
    try:
        # Get current user
        user = await get_current_user(credentials.credentials)
        user_id = user["user_id"]
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        import sqlite3
        conn = sqlite3.connect(social_manager.db_path)
        cursor = conn.cursor()
        
        try:
            # Get publishing stats
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_jobs,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_jobs,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_jobs,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_jobs
                FROM publishing_jobs
                WHERE user_id = ? AND created_at >= ?
            ''', (user_id, start_date.isoformat()))
            
            stats = cursor.fetchone()
            
            # Get platform performance
            cursor.execute('''
                SELECT 
                    platforms,
                    status,
                    platform_results,
                    created_at
                FROM publishing_jobs
                WHERE user_id = ? AND created_at >= ?
                ORDER BY created_at DESC
            ''', (user_id, start_date.isoformat()))
            
            jobs = cursor.fetchall()
            
            # Process platform statistics
            platform_stats = {}
            recent_activity = []
            
            for job in jobs:
                platforms = json.loads(job[0])
                status = job[1]
                platform_results = json.loads(job[2]) if job[2] else {}
                created_at = job[3]
                
                # Add to recent activity
                recent_activity.append({
                    "date": created_at,
                    "platforms": platforms,
                    "status": status,
                    "success_count": sum(1 for r in platform_results.values() if r.get("success", False))
                })
                
                # Update platform stats
                for platform in platforms:
                    if platform not in platform_stats:
                        platform_stats[platform] = {"total": 0, "successful": 0, "failed": 0}
                    
                    platform_stats[platform]["total"] += 1
                    
                    if platform in platform_results:
                        if platform_results[platform].get("success", False):
                            platform_stats[platform]["successful"] += 1
                        else:
                            platform_stats[platform]["failed"] += 1
            
            # Get connected platforms count
            cursor.execute('''
                SELECT COUNT(*) FROM social_platforms
                WHERE user_id = ? AND enabled = 1
            ''', (user_id,))
            
            connected_platforms = cursor.fetchone()[0]
            
            analytics = {
                "period_days": days,
                "total_jobs": stats[0] or 0,
                "completed_jobs": stats[1] or 0,
                "failed_jobs": stats[2] or 0,
                "pending_jobs": stats[3] or 0,
                "success_rate": (stats[1] / stats[0] * 100) if stats[0] > 0 else 0,
                "connected_platforms": connected_platforms,
                "platform_performance": platform_stats,
                "recent_activity": recent_activity[:10]  # Last 10 activities
            }
            
            return {"analytics": analytics}
            
        finally:
            conn.close()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching analytics: {str(e)}")

# OAuth callback endpoints (simplified - in production, these would handle full OAuth flows)
@router.get("/oauth/facebook/callback")
async def facebook_oauth_callback(code: str, state: str):
    """Handle Facebook OAuth callback"""
    # In production, this would exchange the code for access tokens
    return {
        "platform": "facebook",
        "status": "callback_received",
        "code": code,
        "next_step": "exchange_for_tokens"
    }

@router.get("/oauth/twitter/callback")
async def twitter_oauth_callback(oauth_token: str, oauth_verifier: str):
    """Handle Twitter OAuth callback"""
    # In production, this would complete the OAuth 1.0a flow
    return {
        "platform": "twitter",
        "status": "callback_received",
        "oauth_token": oauth_token,
        "next_step": "exchange_for_access_tokens"
    }

@router.get("/oauth/instagram/callback")
async def instagram_oauth_callback(code: str, state: str):
    """Handle Instagram OAuth callback"""
    # In production, this would exchange the code for access tokens
    return {
        "platform": "instagram",
        "status": "callback_received",
        "code": code,
        "next_step": "exchange_for_tokens"
    }

@router.get("/oauth/tiktok/callback")
async def tiktok_oauth_callback(code: str, state: str):
    """Handle TikTok OAuth callback"""
    # In production, this would exchange the code for access tokens
    return {
        "platform": "tiktok",
        "status": "callback_received",
        "code": code,
        "next_step": "exchange_for_tokens"
    }

@router.get("/oauth/linkedin/callback")
async def linkedin_oauth_callback(code: str, state: str):
    """Handle LinkedIn OAuth callback"""
    # In production, this would exchange the code for access tokens
    return {
        "platform": "linkedin",
        "status": "callback_received",
        "code": code,
        "next_step": "exchange_for_tokens"
    }

# Video format optimization endpoint
@router.post("/optimize-video")
async def optimize_video_for_platforms(
    video: UploadFile = File(...),
    platforms: str = Form(...),  # JSON string of platform list
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Optimize video for specific platforms without publishing"""
    try:
        # Get current user
        user = await get_current_user(credentials.credentials)
        
        # Parse platforms
        try:
            platform_list = json.loads(platforms)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in platforms")
        
        # Validate platforms
        platform_enums = []
        for platform_name in platform_list:
            try:
                platform_enums.append(SocialPlatform(platform_name))
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid platform: {platform_name}")
        
        # Save uploaded video temporarily
        import tempfile
        import shutil
        
        temp_dir = tempfile.mkdtemp()
        video_filename = f"optimize_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{video.filename}"
        video_path = os.path.join(temp_dir, video_filename)
        
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
        
        # Get video info
        video_info = social_manager.video_processor.get_video_info(video_path)
        
        # Generate optimization recommendations
        optimizations = []
        for platform in platform_enums:
            # Get platform-specific requirements
            platform_specs = {
                SocialPlatform.YOUTUBE: {"max_size": 128000, "max_duration": None, "aspect_ratio": "16:9"},
                SocialPlatform.FACEBOOK: {"max_size": 4000, "max_duration": 240, "aspect_ratio": "16:9"},
                SocialPlatform.TWITTER: {"max_size": 512, "max_duration": 140, "aspect_ratio": "16:9"},
                SocialPlatform.INSTAGRAM: {"max_size": 4000, "max_duration": 60, "aspect_ratio": "9:16"},
                SocialPlatform.TIKTOK: {"max_size": 287, "max_duration": 180, "aspect_ratio": "9:16"},
                SocialPlatform.LINKEDIN: {"max_size": 5000, "max_duration": 600, "aspect_ratio": "16:9"}
            }
            
            specs = platform_specs[platform]
            
            # Analyze current video vs requirements
            current_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
            current_duration = float(video_info.get('format', {}).get('duration', 0))
            
            recommendations = []
            
            if current_size > specs["max_size"]:
                recommendations.append(f"Reduce file size from {current_size:.1f}MB to under {specs['max_size']}MB")
            
            if specs["max_duration"] and current_duration > specs["max_duration"]:
                recommendations.append(f"Trim duration from {current_duration:.1f}s to under {specs['max_duration']}s")
            
            optimizations.append({
                "platform": platform.value,
                "current_size_mb": current_size,
                "max_size_mb": specs["max_size"],
                "current_duration_s": current_duration,
                "max_duration_s": specs["max_duration"],
                "recommended_aspect_ratio": specs["aspect_ratio"],
                "recommendations": recommendations,
                "requires_optimization": len(recommendations) > 0
            })
        
        # Clean up temp file
        os.unlink(video_path)
        
        return {
            "video_info": video_info,
            "platform_optimizations": optimizations,
            "overall_recommendations": [
                opt for optimization in optimizations 
                for opt in optimization["recommendations"]
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error optimizing video: {str(e)}")