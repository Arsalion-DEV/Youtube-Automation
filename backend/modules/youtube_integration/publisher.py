"""
YouTube Integration Module
Handles OAuth 2.0 authentication, video publishing, and YouTube API interactions
"""

import asyncio
import logging
import os
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import secrets
import base64
from urllib.parse import urlencode, parse_qs, urlparse

# Google APIs
try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
    import google.auth.exceptions
    GOOGLE_APIS_AVAILABLE = True
except ImportError:
    GOOGLE_APIS_AVAILABLE = False
    logging.warning("Google APIs not available")

import httpx
from PIL import Image
import io

from ..base import BaseModule

logger = logging.getLogger(__name__)

class YouTubePublisher(BaseModule):
    """YouTube API integration with OAuth 2.0 and publishing capabilities"""
    
    def __init__(self):
        super().__init__()
        self.module_name = "youtube_integration"
        
        # OAuth configuration
        self.oauth_config = {
            "client_id": os.getenv("YOUTUBE_CLIENT_ID"),
            "client_secret": os.getenv("YOUTUBE_CLIENT_SECRET"),
            "redirect_uri": "http://localhost:8000/api/auth/youtube/callback",
            "scopes": [
                "https://www.googleapis.com/auth/youtube.upload",
                "https://www.googleapis.com/auth/youtube.force-ssl",
                "https://www.googleapis.com/auth/youtube.readonly",
                "https://www.googleapis.com/auth/youtubepartner"
            ]
        }
        
        # API endpoints
        self.youtube_api_version = "v3"
        self.oauth_base_url = "https://accounts.google.com/o/oauth2/v2"
        
        # Token storage
        self.tokens_dir = "configs/youtube_tokens"
        self.channel_credentials = {}  # channel_id -> credentials
        
        # Publishing settings
        self.default_publish_settings = {
            "privacy_status": "public",  # public, unlisted, private
            "category_id": "22",  # People & Blogs
            "default_language": "en",
            "made_for_kids": False,
            "license": "youtube",  # youtube or creativeCommon
            "public_stats_viewable": True,
            "embeddable": True,
            "notify_subscribers": True
        }
        
        # Video categories mapping
        self.video_categories = {
            "education": "27",  # Education
            "entertainment": "24",  # Entertainment
            "gaming": "20",  # Gaming
            "howto": "26",  # Howto & Style
            "music": "10",  # Music
            "news": "25",  # News & Politics
            "science": "28",  # Science & Technology
            "sports": "17",  # Sports
            "travel": "19",  # Travel & Events
            "people": "22",  # People & Blogs
            "autos": "2",   # Autos & Vehicles
            "comedy": "23", # Comedy
            "film": "1",    # Film & Animation
            "nonprofit": "29"  # Nonprofits & Activism
        }
        
        # Upload status tracking
        self.upload_statuses = {}
        
        # Analytics fields to track
        self.analytics_metrics = [
            "views", "likes", "dislikes", "comments", "shares",
            "subscribersGained", "subscribersLost", "estimatedMinutesWatched",
            "averageViewDuration", "averageViewPercentage", "clickThroughRate",
            "impressions", "impressionClickThroughRate"
        ]
    
    async def _setup_module(self):
        """Initialize YouTube integration"""
        await super()._setup_module()
        
        try:
            if not GOOGLE_APIS_AVAILABLE:
                raise RuntimeError("Google APIs not available - install google-api-python-client")
            
            # Create tokens directory
            Path(self.tokens_dir).mkdir(parents=True, exist_ok=True)
            
            # Validate OAuth configuration
            if not self.oauth_config["client_id"] or not self.oauth_config["client_secret"]:
                self.logger.warning("YouTube OAuth not configured - publishing will be unavailable")
            
            # Load existing channel credentials
            await self._load_channel_credentials()
            
            self.logger.info("YouTube Publisher initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize YouTube publisher: {str(e)}")
            raise
    
    async def _load_channel_credentials(self):
        """Load stored channel credentials"""
        
        try:
            tokens_dir = Path(self.tokens_dir)
            
            for token_file in tokens_dir.glob("*.json"):
                try:
                    channel_id = token_file.stem
                    
                    with open(token_file, 'r') as f:
                        token_data = json.load(f)
                    
                    # Create credentials object
                    credentials = Credentials.from_authorized_user_info(
                        token_data,
                        scopes=self.oauth_config["scopes"]
                    )
                    
                    # Refresh if needed
                    if credentials.expired and credentials.refresh_token:
                        credentials.refresh(Request())
                        await self._save_channel_credentials(channel_id, credentials)
                    
                    self.channel_credentials[channel_id] = credentials
                    self.logger.info(f"Loaded credentials for channel: {channel_id}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to load credentials from {token_file}: {str(e)}")
                    
        except Exception as e:
            self.logger.error(f"Failed to load channel credentials: {str(e)}")
    
    async def _save_channel_credentials(self, channel_id: str, credentials: Credentials):
        """Save channel credentials to file"""
        
        try:
            token_file = Path(self.tokens_dir) / f"{channel_id}.json"
            
            token_data = {
                "token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scopes": credentials.scopes
            }
            
            with open(token_file, 'w') as f:
                json.dump(token_data, f, indent=2)
                
            self.logger.info(f"Saved credentials for channel: {channel_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to save credentials: {str(e)}")
    
    def get_oauth_url(self, channel_id: str, state: Optional[str] = None) -> str:
        """Generate OAuth authorization URL"""
        
        try:
            if not state:
                state = secrets.token_urlsafe(32)
            
            # Store state for verification
            self.upload_statuses[state] = {
                "channel_id": channel_id,
                "created_at": datetime.utcnow(),
                "status": "pending_auth"
            }
            
            params = {
                "client_id": self.oauth_config["client_id"],
                "redirect_uri": self.oauth_config["redirect_uri"],
                "scope": " ".join(self.oauth_config["scopes"]),
                "response_type": "code",
                "access_type": "offline",
                "prompt": "consent",
                "state": state
            }
            
            auth_url = f"{self.oauth_base_url}/auth?" + urlencode(params)
            
            self.logger.info(f"Generated OAuth URL for channel: {channel_id}")
            return auth_url
            
        except Exception as e:
            self.logger.error(f"OAuth URL generation failed: {str(e)}")
            raise
    
    async def handle_oauth_callback(self, code: str, state: str) -> Dict[str, Any]:
        """Handle OAuth callback and exchange code for tokens"""
        
        try:
            # Verify state
            if state not in self.upload_statuses:
                raise ValueError("Invalid state parameter")
            
            channel_id = self.upload_statuses[state]["channel_id"]
            
            # Exchange code for tokens
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.oauth_config["client_id"],
                        "client_secret": self.oauth_config["client_secret"],
                        "auth_uri": f"{self.oauth_base_url}/auth",
                        "token_uri": f"{self.oauth_base_url}/token",
                        "redirect_uris": [self.oauth_config["redirect_uri"]]
                    }
                },
                scopes=self.oauth_config["scopes"]
            )
            
            flow.redirect_uri = self.oauth_config["redirect_uri"]
            
            # Fetch tokens
            flow.fetch_token(code=code)
            credentials = flow.credentials
            
            # Get channel information
            youtube_service = build("youtube", self.youtube_api_version, credentials=credentials)
            
            # Get channel details
            channels_response = youtube_service.channels().list(
                part="snippet,statistics,contentDetails",
                mine=True
            ).execute()
            
            if not channels_response.get("items"):
                raise RuntimeError("No YouTube channel found for authenticated user")
            
            channel_info = channels_response["items"][0]
            actual_channel_id = channel_info["id"]
            
            # Store credentials
            self.channel_credentials[actual_channel_id] = credentials
            await self._save_channel_credentials(actual_channel_id, credentials)
            
            # Update status
            self.upload_statuses[state]["status"] = "authenticated"
            self.upload_statuses[state]["actual_channel_id"] = actual_channel_id
            
            await self.log_activity("oauth_completed", {
                "channel_id": actual_channel_id,
                "channel_title": channel_info["snippet"]["title"]
            })
            
            return {
                "success": True,
                "channel_id": actual_channel_id,
                "channel_info": channel_info,
                "message": "OAuth authentication successful"
            }
            
        except Exception as e:
            self.logger.error(f"OAuth callback handling failed: {str(e)}")
            if state in self.upload_statuses:
                self.upload_statuses[state]["status"] = "auth_failed"
                self.upload_statuses[state]["error"] = str(e)
            raise
    
    async def upload_video(
        self,
        channel_id: str,
        video_path: str,
        title: str,
        description: str,
        tags: Optional[List[str]] = None,
        thumbnail_path: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Upload video to YouTube"""
        
        try:
            if channel_id not in self.channel_credentials:
                raise ValueError(f"No credentials found for channel: {channel_id}")
            
            if not Path(video_path).exists():
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            self.logger.info(f"Uploading video to YouTube: {title}")
            
            credentials = self.channel_credentials[channel_id]
            
            # Refresh credentials if needed
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                await self._save_channel_credentials(channel_id, credentials)
            
            # Build YouTube service
            youtube_service = build("youtube", self.youtube_api_version, credentials=credentials)
            
            # Prepare video metadata
            video_metadata = await self._prepare_video_metadata(
                title, description, tags, **kwargs
            )
            
            # Create media upload
            media = MediaFileUpload(
                video_path,
                chunksize=-1,  # Upload entire file at once
                resumable=True,
                mimetype="video/*"
            )
            
            # Start upload
            insert_request = youtube_service.videos().insert(
                part=",".join(video_metadata.keys()),
                body=video_metadata,
                media_body=media
            )
            
            # Execute upload with retry logic
            upload_response = await self._execute_upload_with_retry(insert_request)
            
            video_id = upload_response["id"]
            
            # Upload thumbnail if provided
            if thumbnail_path and Path(thumbnail_path).exists():
                await self._upload_thumbnail(youtube_service, video_id, thumbnail_path)
            
            await self.log_activity("video_uploaded", {
                "channel_id": channel_id,
                "video_id": video_id,
                "title": title,
                "file_size": Path(video_path).stat().st_size
            })
            
            return {
                "success": True,
                "video_id": video_id,
                "video_url": f"https://www.youtube.com/watch?v={video_id}",
                "upload_response": upload_response
            }
            
        except Exception as e:
            self.logger.error(f"Video upload failed: {str(e)}")
            raise
    
    async def _prepare_video_metadata(
        self,
        title: str,
        description: str,
        tags: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare video metadata for upload"""
        
        # Get settings
        settings = {**self.default_publish_settings, **kwargs}
        
        # Determine category
        category = kwargs.get("category", "people")
        category_id = self.video_categories.get(category, self.video_categories["people"])
        
        metadata = {
            "snippet": {
                "title": title[:100],  # YouTube title limit
                "description": description[:5000],  # YouTube description limit
                "tags": tags[:500] if tags else [],  # Limit tags
                "categoryId": category_id,
                "defaultLanguage": settings["default_language"],
                "defaultAudioLanguage": settings["default_language"]
            },
            "status": {
                "privacyStatus": settings["privacy_status"],
                "madeForKids": settings["made_for_kids"],
                "embeddable": settings["embeddable"],
                "license": settings["license"],
                "publicStatsViewable": settings["public_stats_viewable"]
            }
        }
        
        # Add optional fields
        if settings.get("publish_at"):
            metadata["status"]["publishAt"] = settings["publish_at"]
        
        if settings.get("playlist_id"):
            metadata["snippet"]["playlistId"] = settings["playlist_id"]
        
        return metadata
    
    async def _execute_upload_with_retry(self, insert_request, max_retries: int = 3) -> Dict[str, Any]:
        """Execute upload with retry logic"""
        
        for attempt in range(max_retries):
            try:
                response = None
                error = None
                retry = 0
                
                while response is None:
                    try:
                        status, response = insert_request.next_chunk()
                        if response is not None:
                            if 'id' in response:
                                return response
                            else:
                                raise HttpError(resp=None, content=f"Upload failed: {response}")
                    except HttpError as e:
                        if e.resp.status in [500, 502, 503, 504]:
                            # Retriable error
                            retry += 1
                            if retry > 3:
                                raise
                            await asyncio.sleep(2 ** retry)
                        else:
                            raise
                
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                self.logger.warning(f"Upload attempt {attempt + 1} failed: {str(e)}")
                await asyncio.sleep(2 ** attempt)
        
        raise RuntimeError("Upload failed after all retries")
    
    async def _upload_thumbnail(self, youtube_service, video_id: str, thumbnail_path: str):
        """Upload custom thumbnail"""
        
        try:
            # Verify thumbnail dimensions and format
            with Image.open(thumbnail_path) as img:
                width, height = img.size
                
                # YouTube requirements: 1280x720, under 2MB, JPG/PNG
                if width < 1280 or height < 720:
                    self.logger.warning(f"Thumbnail resolution too low: {width}x{height}")
                
                # Convert to RGB if needed and resize
                if img.mode != "RGB":
                    img = img.convert("RGB")
                
                # Ensure proper aspect ratio
                if width / height != 16 / 9:
                    # Crop to 16:9 aspect ratio
                    target_width = width
                    target_height = width * 9 // 16
                    
                    if target_height > height:
                        target_height = height
                        target_width = height * 16 // 9
                    
                    left = (width - target_width) // 2
                    top = (height - target_height) // 2
                    right = left + target_width
                    bottom = top + target_height
                    
                    img = img.crop((left, top, right, bottom))
                
                # Save optimized thumbnail
                optimized_path = thumbnail_path.replace(".png", "_optimized.jpg").replace(".jpg", "_optimized.jpg")
                img.save(optimized_path, "JPEG", quality=90, optimize=True)
                thumbnail_path = optimized_path
            
            # Upload thumbnail
            youtube_service.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
            ).execute()
            
            self.logger.info(f"Thumbnail uploaded for video: {video_id}")
            
        except Exception as e:
            self.logger.error(f"Thumbnail upload failed: {str(e)}")
    
    async def get_video_analytics(
        self,
        channel_id: str,
        video_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get analytics for a specific video"""
        
        try:
            if channel_id not in self.channel_credentials:
                raise ValueError(f"No credentials found for channel: {channel_id}")
            
            credentials = self.channel_credentials[channel_id]
            youtube_service = build("youtube", self.youtube_api_version, credentials=credentials)
            
            # Get basic video statistics
            video_response = youtube_service.videos().list(
                part="statistics,snippet",
                id=video_id
            ).execute()
            
            if not video_response.get("items"):
                raise ValueError(f"Video not found: {video_id}")
            
            video_data = video_response["items"][0]
            
            # Get YouTube Analytics (requires YouTube Analytics API)
            # For now, we'll return basic statistics
            analytics = {
                "video_id": video_id,
                "title": video_data["snippet"]["title"],
                "published_at": video_data["snippet"]["publishedAt"],
                "statistics": video_data["statistics"],
                "basic_metrics": {
                    "views": int(video_data["statistics"].get("viewCount", 0)),
                    "likes": int(video_data["statistics"].get("likeCount", 0)),
                    "comments": int(video_data["statistics"].get("commentCount", 0))
                }
            }
            
            # Calculate derived metrics
            views = analytics["basic_metrics"]["views"]
            likes = analytics["basic_metrics"]["likes"]
            
            if views > 0:
                analytics["derived_metrics"] = {
                    "engagement_rate": (likes / views) * 100,
                    "likes_per_view": likes / views
                }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Analytics retrieval failed: {str(e)}")
            raise
    
    async def get_channel_analytics(
        self,
        channel_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get channel-wide analytics"""
        
        try:
            if channel_id not in self.channel_credentials:
                raise ValueError(f"No credentials found for channel: {channel_id}")
            
            credentials = self.channel_credentials[channel_id]
            youtube_service = build("youtube", self.youtube_api_version, credentials=credentials)
            
            # Get channel statistics
            channel_response = youtube_service.channels().list(
                part="statistics,snippet",
                mine=True
            ).execute()
            
            if not channel_response.get("items"):
                raise ValueError("Channel not found")
            
            channel_data = channel_response["items"][0]
            
            # Get recent videos
            search_response = youtube_service.search().list(
                part="snippet",
                channelId=channel_id,
                maxResults=50,
                order="date",
                type="video"
            ).execute()
            
            recent_videos = search_response.get("items", [])
            
            analytics = {
                "channel_id": channel_id,
                "channel_title": channel_data["snippet"]["title"],
                "period_days": days,
                "channel_statistics": channel_data["statistics"],
                "recent_videos_count": len(recent_videos),
                "total_videos": int(channel_data["statistics"].get("videoCount", 0)),
                "total_subscribers": int(channel_data["statistics"].get("subscriberCount", 0)),
                "total_views": int(channel_data["statistics"].get("viewCount", 0))
            }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Channel analytics retrieval failed: {str(e)}")
            raise
    
    async def update_video_metadata(
        self,
        channel_id: str,
        video_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Update video metadata"""
        
        try:
            if channel_id not in self.channel_credentials:
                raise ValueError(f"No credentials found for channel: {channel_id}")
            
            credentials = self.channel_credentials[channel_id]
            youtube_service = build("youtube", self.youtube_api_version, credentials=credentials)
            
            # Get current video data
            video_response = youtube_service.videos().list(
                part="snippet",
                id=video_id
            ).execute()
            
            if not video_response.get("items"):
                raise ValueError(f"Video not found: {video_id}")
            
            current_snippet = video_response["items"][0]["snippet"]
            
            # Update fields
            updated_snippet = current_snippet.copy()
            if title:
                updated_snippet["title"] = title[:100]
            if description:
                updated_snippet["description"] = description[:5000]
            if tags:
                updated_snippet["tags"] = tags[:500]
            
            # Update video
            update_response = youtube_service.videos().update(
                part="snippet",
                body={
                    "id": video_id,
                    "snippet": updated_snippet
                }
            ).execute()
            
            await self.log_activity("video_metadata_updated", {
                "channel_id": channel_id,
                "video_id": video_id,
                "updated_fields": [
                    field for field, value in [
                        ("title", title),
                        ("description", description),
                        ("tags", tags)
                    ] if value is not None
                ]
            })
            
            return {
                "success": True,
                "video_id": video_id,
                "updated_snippet": update_response["snippet"]
            }
            
        except Exception as e:
            self.logger.error(f"Video metadata update failed: {str(e)}")
            raise
    
    def get_authenticated_channels(self) -> List[str]:
        """Get list of authenticated channel IDs"""
        return list(self.channel_credentials.keys())
    
    def is_channel_authenticated(self, channel_id: str) -> bool:
        """Check if channel is authenticated"""
        return channel_id in self.channel_credentials
    
    def get_video_categories(self) -> Dict[str, str]:
        """Get available video categories"""
        return self.video_categories
    
    def get_integration_stats(self) -> Dict[str, Any]:
        """Get YouTube integration statistics"""
        stats = super().get_status()
        stats.update({
            "google_apis_available": GOOGLE_APIS_AVAILABLE,
            "oauth_configured": bool(self.oauth_config["client_id"] and self.oauth_config["client_secret"]),
            "authenticated_channels": len(self.channel_credentials),
            "available_categories": len(self.video_categories),
            "pending_uploads": len([s for s in self.upload_statuses.values() if s.get("status") == "uploading"])
        })
        return stats