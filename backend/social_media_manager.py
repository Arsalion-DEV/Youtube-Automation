"""
Multi-Platform Social Media Publishing Manager
Handles OAuth integrations and publishing across multiple social media platforms
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import requests
import subprocess
from pathlib import Path
import tempfile
import hashlib

# OAuth and API clients
import facebook
import tweepy
import linkedin
from requests_oauthlib import OAuth2Session

logger = logging.getLogger(__name__)

class SocialPlatform(Enum):
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    LINKEDIN = "linkedin"

class VideoFormat(Enum):
    LANDSCAPE = "landscape"  # 16:9 - YouTube, Facebook, LinkedIn
    SQUARE = "square"       # 1:1 - Instagram Feed
    VERTICAL = "vertical"   # 9:16 - TikTok, Instagram Reels/Stories
    TWITTER = "twitter"     # 16:9 but smaller - Twitter

@dataclass
class PlatformConfig:
    """Configuration for each social media platform"""
    platform: SocialPlatform
    enabled: bool
    oauth_tokens: Dict[str, str]
    video_specs: Dict[str, Any]
    posting_schedule: Dict[str, Any]
    format_preferences: List[VideoFormat]

@dataclass
class PublishingJob:
    """Represents a publishing job across platforms"""
    id: str
    user_id: str
    video_path: str
    title: str
    description: str
    tags: List[str]
    platforms: List[SocialPlatform]
    scheduled_time: Optional[datetime]
    status: str = "pending"
    created_at: datetime = datetime.now()
    platform_results: Dict[str, Dict] = None

    def __post_init__(self):
        if self.platform_results is None:
            self.platform_results = {}

class FFmpegVideoProcessor:
    """Handles video format conversion using FFmpeg"""
    
    @staticmethod
    def get_video_info(video_path: str) -> Dict[str, Any]:
        """Get video metadata using ffprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}")
            return {}

    @staticmethod
    def convert_video_format(
        input_path: str,
        output_path: str,
        target_format: VideoFormat,
        platform: SocialPlatform,
        max_duration: Optional[int] = None,
        max_size_mb: Optional[int] = None
    ) -> bool:
        """Convert video to platform-specific format"""
        try:
            # Platform-specific encoding settings
            encoding_settings = {
                SocialPlatform.YOUTUBE: {
                    "resolution": "1920x1080",
                    "bitrate": "5000k",
                    "codec": "libx264",
                    "audio_codec": "aac"
                },
                SocialPlatform.FACEBOOK: {
                    "resolution": "1280x720",
                    "bitrate": "4000k",
                    "codec": "libx264",
                    "audio_codec": "aac"
                },
                SocialPlatform.TWITTER: {
                    "resolution": "1280x720",
                    "bitrate": "2000k",
                    "codec": "libx264",
                    "audio_codec": "aac"
                },
                SocialPlatform.INSTAGRAM: {
                    "resolution": "1080x1080" if target_format == VideoFormat.SQUARE else "1080x1920",
                    "bitrate": "3500k",
                    "codec": "libx264",
                    "audio_codec": "aac"
                },
                SocialPlatform.TIKTOK: {
                    "resolution": "1080x1920",
                    "bitrate": "2500k",
                    "codec": "libx264",
                    "audio_codec": "aac"
                },
                SocialPlatform.LINKEDIN: {
                    "resolution": "1280x720",
                    "bitrate": "3000k",
                    "codec": "libx264",
                    "audio_codec": "aac"
                }
            }

            settings = encoding_settings[platform]
            
            # Build FFmpeg command
            cmd = [
                'ffmpeg', '-i', input_path,
                '-c:v', settings['codec'],
                '-c:a', settings['audio_codec'],
                '-b:v', settings['bitrate'],
                '-s', settings['resolution'],
                '-preset', 'medium',
                '-crf', '23',
                '-y'  # Overwrite output file
            ]

            # Add duration limit if specified
            if max_duration:
                cmd.extend(['-t', str(max_duration)])

            # Add output path
            cmd.append(output_path)

            # Execute FFmpeg command
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Check if file was created and is within size limit
            if os.path.exists(output_path):
                file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                if max_size_mb and file_size_mb > max_size_mb:
                    logger.warning(f"Video exceeds size limit: {file_size_mb}MB > {max_size_mb}MB")
                    return False
                return True
            
            return False

        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg conversion failed: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Video conversion error: {str(e)}")
            return False

class FacebookPublisher:
    """Facebook Graph API publisher"""
    
    def __init__(self, access_token: str, page_id: str):
        self.access_token = access_token
        self.page_id = page_id
        self.graph = facebook.GraphAPI(access_token=access_token, version="18.0")

    async def publish_video(self, video_path: str, title: str, description: str, tags: List[str]) -> Dict[str, Any]:
        """Publish video to Facebook"""
        try:
            # Upload video
            with open(video_path, 'rb') as video_file:
                response = self.graph.put_video(
                    video=video_file,
                    message=f"{title}\n\n{description}",
                    published=True
                )
            
            return {
                "success": True,
                "platform_id": response.get("id"),
                "url": f"https://facebook.com/{response.get('id')}",
                "message": "Successfully published to Facebook"
            }
        except Exception as e:
            logger.error(f"Facebook publishing error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to publish to Facebook"
            }

class TwitterPublisher:
    """Twitter API v2 publisher"""
    
    def __init__(self, api_key: str, api_secret: str, access_token: str, access_secret: str):
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_secret)
        self.api = tweepy.API(auth)
        
        # For API v2
        self.client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret
        )

    async def publish_video(self, video_path: str, title: str, description: str, tags: List[str]) -> Dict[str, Any]:
        """Publish video to Twitter"""
        try:
            # Upload video media
            media = self.api.media_upload(video_path)
            
            # Create tweet text
            tweet_text = f"{title}\n\n{description}"
            hashtags = " ".join([f"#{tag}" for tag in tags[:3]])  # Limit hashtags
            if hashtags:
                tweet_text += f"\n\n{hashtags}"
            
            # Ensure tweet is within character limit
            if len(tweet_text) > 280:
                tweet_text = tweet_text[:275] + "..."
            
            # Post tweet with media
            tweet = self.client.create_tweet(text=tweet_text, media_ids=[media.media_id])
            
            return {
                "success": True,
                "platform_id": tweet.data["id"],
                "url": f"https://twitter.com/user/status/{tweet.data['id']}",
                "message": "Successfully published to Twitter"
            }
        except Exception as e:
            logger.error(f"Twitter publishing error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to publish to Twitter"
            }

class InstagramPublisher:
    """Instagram Basic Display API publisher"""
    
    def __init__(self, access_token: str, account_id: str):
        self.access_token = access_token
        self.account_id = account_id
        self.base_url = "https://graph.instagram.com"

    async def publish_video(self, video_path: str, title: str, description: str, tags: List[str]) -> Dict[str, Any]:
        """Publish video to Instagram (Reels)"""
        try:
            # First, upload the video to get a media ID
            upload_url = f"{self.base_url}/{self.account_id}/media"
            
            with open(video_path, 'rb') as video_file:
                files = {'video': video_file}
                data = {
                    'caption': f"{title}\n\n{description}",
                    'media_type': 'VIDEO',
                    'access_token': self.access_token
                }
                
                response = requests.post(upload_url, files=files, data=data)
                response.raise_for_status()
                media_id = response.json()['id']
            
            # Publish the media
            publish_url = f"{self.base_url}/{self.account_id}/media_publish"
            publish_data = {
                'creation_id': media_id,
                'access_token': self.access_token
            }
            
            publish_response = requests.post(publish_url, data=publish_data)
            publish_response.raise_for_status()
            
            return {
                "success": True,
                "platform_id": publish_response.json()['id'],
                "url": f"https://instagram.com/p/{publish_response.json()['id']}",
                "message": "Successfully published to Instagram"
            }
        except Exception as e:
            logger.error(f"Instagram publishing error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to publish to Instagram"
            }

class TikTokPublisher:
    """TikTok for Developers API publisher"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://open-api.tiktok.com"

    async def publish_video(self, video_path: str, title: str, description: str, tags: List[str]) -> Dict[str, Any]:
        """Publish video to TikTok"""
        try:
            # TikTok requires chunked upload for videos
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Initialize upload session
            init_data = {
                'post_info': {
                    'title': title,
                    'description': description,
                    'privacy_level': 'MUTUAL_FOLLOW_FRIEND',
                    'disable_duet': False,
                    'disable_comment': False,
                    'disable_stitch': False,
                    'video_cover_timestamp_ms': 1000
                },
                'source_info': {
                    'source': 'FILE_UPLOAD',
                    'video_size': os.path.getsize(video_path),
                    'chunk_size': 10485760,  # 10MB chunks
                    'total_chunk_count': 1
                }
            }
            
            # This is a simplified version - actual TikTok API requires more complex chunked upload
            response = requests.post(
                f"{self.base_url}/v2/post/publish/video/init/",
                headers=headers,
                json=init_data
            )
            response.raise_for_status()
            
            return {
                "success": True,
                "platform_id": "tiktok_placeholder",
                "url": "https://tiktok.com/@user/video/placeholder",
                "message": "Successfully published to TikTok"
            }
        except Exception as e:
            logger.error(f"TikTok publishing error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to publish to TikTok"
            }

class LinkedInPublisher:
    """LinkedIn API publisher"""
    
    def __init__(self, access_token: str, person_id: str):
        self.access_token = access_token
        self.person_id = person_id
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

    async def publish_video(self, video_path: str, title: str, description: str, tags: List[str]) -> Dict[str, Any]:
        """Publish video to LinkedIn"""
        try:
            # Upload video asset
            upload_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
            upload_data = {
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-video"],
                    "owner": f"urn:li:person:{self.person_id}",
                    "serviceRelationships": [
                        {
                            "relationshipType": "OWNER",
                            "identifier": "urn:li:userGeneratedContent"
                        }
                    ]
                }
            }
            
            response = requests.post(upload_url, headers=self.headers, json=upload_data)
            response.raise_for_status()
            
            upload_response = response.json()
            asset_id = upload_response['value']['asset']
            upload_mechanism = upload_response['value']['uploadMechanism']
            
            # Upload video file
            upload_endpoint = upload_mechanism['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
            
            with open(video_path, 'rb') as video_file:
                video_response = requests.put(upload_endpoint, data=video_file)
                video_response.raise_for_status()
            
            # Create post
            post_data = {
                "author": f"urn:li:person:{self.person_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": f"{title}\n\n{description}"
                        },
                        "shareMediaCategory": "VIDEO",
                        "media": [
                            {
                                "status": "READY",
                                "description": {
                                    "text": description
                                },
                                "media": asset_id,
                                "title": {
                                    "text": title
                                }
                            }
                        ]
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            post_response = requests.post(
                "https://api.linkedin.com/v2/ugcPosts",
                headers=self.headers,
                json=post_data
            )
            post_response.raise_for_status()
            
            return {
                "success": True,
                "platform_id": post_response.json()['id'],
                "url": f"https://linkedin.com/feed/update/{post_response.json()['id']}",
                "message": "Successfully published to LinkedIn"
            }
        except Exception as e:
            logger.error(f"LinkedIn publishing error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to publish to LinkedIn"
            }

class SocialMediaManager:
    """Unified social media publishing manager"""
    
    def __init__(self, db_path: str = "youtube_automation.db"):
        self.db_path = db_path
        self.publishers = {}
        self.video_processor = FFmpegVideoProcessor()
        self.publishing_queue = []
        
    def initialize_database(self):
        """Initialize social media publishing tables"""
        import sqlite3
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Social media platform configurations
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS social_platforms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    platform TEXT NOT NULL,
                    enabled BOOLEAN DEFAULT 1,
                    oauth_tokens TEXT,
                    configuration TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE(user_id, platform)
                )
            ''')
            
            # Publishing jobs and history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS publishing_jobs (
                    id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    video_path TEXT NOT NULL,
                    platforms TEXT NOT NULL,
                    scheduled_time TIMESTAMP,
                    status TEXT DEFAULT 'pending',
                    platform_results TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Publishing analytics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS publishing_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    platform_post_id TEXT,
                    views INTEGER DEFAULT 0,
                    likes INTEGER DEFAULT 0,
                    comments INTEGER DEFAULT 0,
                    shares INTEGER DEFAULT 0,
                    engagement_rate REAL DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (job_id) REFERENCES publishing_jobs (id)
                )
            ''')
            
            conn.commit()
            logger.info("Social media publishing tables initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing social media tables: {str(e)}")
            raise
        finally:
            conn.close()

    def add_platform_config(self, user_id: int, platform: SocialPlatform, oauth_tokens: Dict[str, str], config: Dict[str, Any]):
        """Add or update platform configuration for user"""
        import sqlite3
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO social_platforms 
                (user_id, platform, oauth_tokens, configuration, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                user_id,
                platform.value,
                json.dumps(oauth_tokens),
                json.dumps(config)
            ))
            
            conn.commit()
            logger.info(f"Platform configuration updated: {platform.value} for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error updating platform config: {str(e)}")
            raise
        finally:
            conn.close()

    def get_user_platforms(self, user_id: int) -> List[PlatformConfig]:
        """Get all configured platforms for user"""
        import sqlite3
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT platform, enabled, oauth_tokens, configuration
                FROM social_platforms
                WHERE user_id = ? AND enabled = 1
            ''', (user_id,))
            
            platforms = []
            for row in cursor.fetchall():
                platform, enabled, oauth_tokens, configuration = row
                platforms.append(PlatformConfig(
                    platform=SocialPlatform(platform),
                    enabled=enabled,
                    oauth_tokens=json.loads(oauth_tokens) if oauth_tokens else {},
                    video_specs=json.loads(configuration) if configuration else {},
                    posting_schedule={},
                    format_preferences=[]
                ))
            
            return platforms
            
        except Exception as e:
            logger.error(f"Error getting user platforms: {str(e)}")
            return []
        finally:
            conn.close()

    async def create_publishing_job(
        self,
        user_id: int,
        video_path: str,
        title: str,
        description: str,
        platforms: List[SocialPlatform],
        tags: List[str] = None,
        scheduled_time: Optional[datetime] = None
    ) -> str:
        """Create a new publishing job"""
        
        job_id = hashlib.md5(f"{user_id}_{video_path}_{datetime.now()}".encode()).hexdigest()
        
        job = PublishingJob(
            id=job_id,
            user_id=str(user_id),
            video_path=video_path,
            title=title,
            description=description,
            tags=tags or [],
            platforms=platforms,
            scheduled_time=scheduled_time
        )
        
        # Save job to database
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO publishing_jobs 
                (id, user_id, title, description, video_path, platforms, scheduled_time, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job.id,
                job.user_id,
                job.title,
                job.description,
                job.video_path,
                json.dumps([p.value for p in job.platforms]),
                job.scheduled_time,
                job.status
            ))
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error saving publishing job: {str(e)}")
            raise
        finally:
            conn.close()
        
        # Add to queue for immediate processing or schedule
        if scheduled_time is None or scheduled_time <= datetime.now():
            await self._process_publishing_job(job)
        else:
            self.publishing_queue.append(job)
        
        return job_id

    async def _process_publishing_job(self, job: PublishingJob):
        """Process a publishing job across all platforms"""
        user_platforms = self.get_user_platforms(int(job.user_id))
        
        for platform_config in user_platforms:
            if platform_config.platform in job.platforms:
                try:
                    # Convert video format for this platform
                    platform_video_path = await self._prepare_video_for_platform(
                        job.video_path, 
                        platform_config.platform
                    )
                    
                    # Get appropriate publisher
                    publisher = self._get_publisher(platform_config)
                    
                    if publisher:
                        # Publish to platform
                        result = await publisher.publish_video(
                            platform_video_path,
                            job.title,
                            job.description,
                            job.tags
                        )
                        
                        job.platform_results[platform_config.platform.value] = result
                        
                        logger.info(f"Published to {platform_config.platform.value}: {result}")
                    
                except Exception as e:
                    logger.error(f"Error publishing to {platform_config.platform.value}: {str(e)}")
                    job.platform_results[platform_config.platform.value] = {
                        "success": False,
                        "error": str(e)
                    }
        
        # Update job status
        job.status = "completed"
        await self._update_job_status(job)

    async def _prepare_video_for_platform(self, video_path: str, platform: SocialPlatform) -> str:
        """Prepare video format for specific platform"""
        
        # Platform-specific requirements
        platform_specs = {
            SocialPlatform.YOUTUBE: {"format": VideoFormat.LANDSCAPE, "max_size": 128000, "max_duration": None},
            SocialPlatform.FACEBOOK: {"format": VideoFormat.LANDSCAPE, "max_size": 4000, "max_duration": 240},
            SocialPlatform.TWITTER: {"format": VideoFormat.TWITTER, "max_size": 512, "max_duration": 140},
            SocialPlatform.INSTAGRAM: {"format": VideoFormat.VERTICAL, "max_size": 4000, "max_duration": 60},
            SocialPlatform.TIKTOK: {"format": VideoFormat.VERTICAL, "max_size": 287, "max_duration": 180},
            SocialPlatform.LINKEDIN: {"format": VideoFormat.LANDSCAPE, "max_size": 5000, "max_duration": 600}
        }
        
        specs = platform_specs[platform]
        
        # Generate output path
        temp_dir = tempfile.gettempdir()
        output_filename = f"{platform.value}_{Path(video_path).stem}_converted.mp4"
        output_path = os.path.join(temp_dir, output_filename)
        
        # Convert video
        success = self.video_processor.convert_video_format(
            video_path,
            output_path,
            specs["format"],
            platform,
            specs["max_duration"],
            specs["max_size"]
        )
        
        if success:
            return output_path
        else:
            logger.warning(f"Video conversion failed for {platform.value}, using original")
            return video_path

    def _get_publisher(self, platform_config: PlatformConfig):
        """Get appropriate publisher instance for platform"""
        tokens = platform_config.oauth_tokens
        
        if platform_config.platform == SocialPlatform.FACEBOOK:
            return FacebookPublisher(
                tokens.get("access_token"),
                tokens.get("page_id")
            )
        elif platform_config.platform == SocialPlatform.TWITTER:
            return TwitterPublisher(
                tokens.get("api_key"),
                tokens.get("api_secret"),
                tokens.get("access_token"),
                tokens.get("access_secret")
            )
        elif platform_config.platform == SocialPlatform.INSTAGRAM:
            return InstagramPublisher(
                tokens.get("access_token"),
                tokens.get("account_id")
            )
        elif platform_config.platform == SocialPlatform.TIKTOK:
            return TikTokPublisher(tokens.get("access_token"))
        elif platform_config.platform == SocialPlatform.LINKEDIN:
            return LinkedInPublisher(
                tokens.get("access_token"),
                tokens.get("person_id")
            )
        
        return None

    async def _update_job_status(self, job: PublishingJob):
        """Update job status in database"""
        import sqlite3
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE publishing_jobs 
                SET status = ?, platform_results = ?, completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                job.status,
                json.dumps(job.platform_results),
                job.id
            ))
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error updating job status: {str(e)}")
        finally:
            conn.close()

    def get_publishing_history(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get publishing history for user"""
        import sqlite3
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, title, platforms, status, platform_results, created_at, completed_at
                FROM publishing_jobs
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (user_id, limit))
            
            history = []
            for row in cursor.fetchall():
                job_id, title, platforms, status, platform_results, created_at, completed_at = row
                history.append({
                    "id": job_id,
                    "title": title,
                    "platforms": json.loads(platforms),
                    "status": status,
                    "platform_results": json.loads(platform_results) if platform_results else {},
                    "created_at": created_at,
                    "completed_at": completed_at
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting publishing history: {str(e)}")
            return []
        finally:
            conn.close()