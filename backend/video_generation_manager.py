"""
Video Generation and Content Management System
Comprehensive video creation, scheduling, and publishing automation
"""

import asyncio
import logging
import json
import uuid
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

class VideoStatus(Enum):
    PENDING = "pending"
    SCRIPT_GENERATION = "script_generation"
    CONTENT_CREATION = "content_creation"
    VIDEO_GENERATION = "video_generation"
    EDITING = "editing"
    THUMBNAIL_CREATION = "thumbnail_creation"
    READY_FOR_REVIEW = "ready_for_review"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"

class ContentType(Enum):
    TUTORIAL = "tutorial"
    REVIEW = "review"
    NEWS = "news"
    ENTERTAINMENT = "entertainment"
    EDUCATIONAL = "educational"
    VLOG = "vlog"
    SHORTS = "shorts"

@dataclass
class VideoRequest:
    id: str
    channel_id: str
    title: str
    description: str
    content_type: ContentType
    target_duration: int  # in seconds
    topic: str
    keywords: List[str]
    status: VideoStatus = VideoStatus.PENDING
    created_at: str = ""
    scheduled_publish_time: Optional[str] = None
    thumbnail_url: Optional[str] = None
    video_url: Optional[str] = None
    script_content: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self):
        return asdict(self)

@dataclass
class ContentTemplate:
    template_id: str
    name: str
    content_type: ContentType
    script_template: str
    duration_range: tuple
    required_elements: List[str]
    optimization_tips: List[str]
    
    def to_dict(self):
        return asdict(self)

class VideoGenerationManager:
    """Comprehensive video generation and content management system"""
    
    def __init__(self, database_path: str = "youtube_automation.db"):
        self.db_path = database_path
        self.video_requests: Dict[str, VideoRequest] = {}
        self.content_templates: Dict[str, ContentTemplate] = {}
        self.processing_queue: List[str] = []
        self.logger = logging.getLogger(f"{__name__}.VideoGenerationManager")
        
        # Initialize content templates
        self._initialize_content_templates()
        
    async def initialize(self):
        """Initialize the video generation system"""
        try:
            await self._create_database_tables()
            await self._load_video_requests()
            await self._setup_processing_queue()
            self.logger.info("Video Generation Manager initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Video Generation Manager: {str(e)}")
            raise
    
    async def _create_database_tables(self):
        """Create necessary database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Video requests table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS video_requests (
            id TEXT PRIMARY KEY,
            channel_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            content_type TEXT,
            target_duration INTEGER,
            topic TEXT,
            keywords TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            scheduled_publish_time TEXT,
            thumbnail_url TEXT,
            video_url TEXT,
            script_content TEXT,
            metadata TEXT DEFAULT '{}',
            FOREIGN KEY (channel_id) REFERENCES channels (channel_id)
        )
        ''')
        
        # Content generation history
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS content_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_request_id TEXT,
            generation_step TEXT,
            status TEXT,
            result_data TEXT,
            processing_time REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (video_request_id) REFERENCES video_requests (id)
        )
        ''')
        
        # Thumbnail generation table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS thumbnails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_request_id TEXT,
            thumbnail_url TEXT,
            style_options TEXT,
            performance_metrics TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (video_request_id) REFERENCES video_requests (id)
        )
        ''')
        
        # Publishing schedule
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS publishing_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_request_id TEXT,
            channel_id TEXT,
            scheduled_time TEXT,
            published_time TEXT,
            status TEXT DEFAULT 'scheduled',
            platform_response TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (video_request_id) REFERENCES video_requests (id),
            FOREIGN KEY (channel_id) REFERENCES channels (channel_id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def _initialize_content_templates(self):
        """Initialize predefined content templates"""
        templates = [
            ContentTemplate(
                template_id="tutorial_basic",
                name="Basic Tutorial",
                content_type=ContentType.TUTORIAL,
                script_template="""
                Hook: {hook}
                Introduction: Welcome to {topic}
                Main Content:
                1. {step_1}
                2. {step_2}
                3. {step_3}
                Conclusion: {conclusion}
                Call to Action: {cta}
                """,
                duration_range=(300, 900),  # 5-15 minutes
                required_elements=["hook", "steps", "conclusion", "cta"],
                optimization_tips=[
                    "Start with a strong hook",
                    "Break content into clear steps",
                    "Use visual aids for complex concepts",
                    "Include timestamps in description"
                ]
            ),
            ContentTemplate(
                template_id="review_product",
                name="Product Review",
                content_type=ContentType.REVIEW,
                script_template="""
                Introduction: {product_intro}
                Unboxing/First Impressions: {unboxing}
                Key Features: {features}
                Pros and Cons: {pros_cons}
                Final Verdict: {verdict}
                Where to Buy: {purchase_info}
                """,
                duration_range=(480, 1200),  # 8-20 minutes
                required_elements=["product_intro", "features", "pros_cons", "verdict"],
                optimization_tips=[
                    "Show product clearly in thumbnail",
                    "Include pricing information",
                    "Compare with alternatives",
                    "Use honest opinions for credibility"
                ]
            ),
            ContentTemplate(
                template_id="shorts_viral",
                name="Viral Shorts",
                content_type=ContentType.SHORTS,
                script_template="""
                Hook (0-3s): {hook}
                Main Content (3-30s): {main_content}
                Call to Action (30-60s): {cta}
                """,
                duration_range=(15, 60),  # 15-60 seconds
                required_elements=["hook", "main_content", "cta"],
                optimization_tips=[
                    "Grab attention in first 3 seconds",
                    "Use trending audio/music",
                    "Include text overlays",
                    "Vertical 9:16 format"
                ]
            )
        ]
        
        for template in templates:
            self.content_templates[template.template_id] = template
    
    async def _load_video_requests(self):
        """Load existing video requests from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM video_requests")
        rows = cursor.fetchall()
        
        for row in rows:
            request_data = {
                'id': row[0],
                'channel_id': row[1],
                'title': row[2],
                'description': row[3],
                'content_type': ContentType(row[4]),
                'target_duration': row[5],
                'topic': row[6],
                'keywords': json.loads(row[7]) if row[7] else [],
                'status': VideoStatus(row[8]),
                'created_at': row[9],
                'scheduled_publish_time': row[10],
                'thumbnail_url': row[11],
                'video_url': row[12],
                'script_content': row[13],
                'metadata': json.loads(row[14]) if row[14] else {}
            }
            
            request = VideoRequest(**request_data)
            self.video_requests[request.id] = request
        
        conn.close()
        self.logger.info(f"Loaded {len(self.video_requests)} video requests")
    
    async def _setup_processing_queue(self):
        """Setup processing queue for pending videos"""
        self.processing_queue = [
            req_id for req_id, req in self.video_requests.items()
            if req.status in [VideoStatus.PENDING, VideoStatus.SCRIPT_GENERATION, VideoStatus.CONTENT_CREATION]
        ]
        self.logger.info(f"Setup processing queue with {len(self.processing_queue)} items")
    
    async def create_video_request(self, channel_id: str, title: str, description: str,
                                 content_type: str, topic: str, keywords: List[str],
                                 target_duration: int = 600,
                                 scheduled_publish_time: Optional[str] = None) -> str:
        """Create a new video generation request"""
        try:
            request_id = str(uuid.uuid4())
            
            request = VideoRequest(
                id=request_id,
                channel_id=channel_id,
                title=title,
                description=description,
                content_type=ContentType(content_type),
                target_duration=target_duration,
                topic=topic,
                keywords=keywords,
                scheduled_publish_time=scheduled_publish_time
            )
            
            # Save to database
            await self._save_video_request(request)
            
            # Add to memory and queue
            self.video_requests[request_id] = request
            self.processing_queue.append(request_id)
            
            # Start processing in background
            asyncio.create_task(self._process_video_request(request_id))
            
            self.logger.info(f"Created video request: {request_id}")
            return request_id
            
        except Exception as e:
            self.logger.error(f"Failed to create video request: {str(e)}")
            raise
    
    async def _save_video_request(self, request: VideoRequest):
        """Save video request to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO video_requests 
        (id, channel_id, title, description, content_type, target_duration, topic,
         keywords, status, created_at, scheduled_publish_time, thumbnail_url,
         video_url, script_content, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            request.id,
            request.channel_id,
            request.title,
            request.description,
            request.content_type.value,
            request.target_duration,
            request.topic,
            json.dumps(request.keywords),
            request.status.value,
            request.created_at,
            request.scheduled_publish_time,
            request.thumbnail_url,
            request.video_url,
            request.script_content,
            json.dumps(request.metadata)
        ))
        
        conn.commit()
        conn.close()
    
    async def _process_video_request(self, request_id: str):
        """Process a video request through all generation stages"""
        try:
            request = self.video_requests[request_id]
            
            # Stage 1: Script Generation
            await self._update_request_status(request_id, VideoStatus.SCRIPT_GENERATION)
            script = await self._generate_script(request)
            request.script_content = script
            
            # Stage 2: Content Creation
            await self._update_request_status(request_id, VideoStatus.CONTENT_CREATION)
            content_assets = await self._create_content_assets(request)
            
            # Stage 3: Video Generation
            await self._update_request_status(request_id, VideoStatus.VIDEO_GENERATION)
            video_url = await self._generate_video(request, content_assets)
            request.video_url = video_url
            
            # Stage 4: Editing
            await self._update_request_status(request_id, VideoStatus.EDITING)
            edited_video_url = await self._edit_video(request, video_url)
            request.video_url = edited_video_url
            
            # Stage 5: Thumbnail Creation
            await self._update_request_status(request_id, VideoStatus.THUMBNAIL_CREATION)
            thumbnail_url = await self._generate_thumbnail(request)
            request.thumbnail_url = thumbnail_url
            
            # Stage 6: Ready for Review
            await self._update_request_status(request_id, VideoStatus.READY_FOR_REVIEW)
            
            # Stage 7: Schedule if auto-publish is enabled
            if request.scheduled_publish_time:
                await self._schedule_video(request)
            
            await self._save_video_request(request)
            self.logger.info(f"Completed processing video request: {request_id}")
            
        except Exception as e:
            await self._update_request_status(request_id, VideoStatus.FAILED)
            self.logger.error(f"Failed to process video request {request_id}: {str(e)}")
    
    async def _update_request_status(self, request_id: str, status: VideoStatus):
        """Update video request status"""
        if request_id in self.video_requests:
            self.video_requests[request_id].status = status
            await self._save_video_request(self.video_requests[request_id])
            
            # Log to content history
            await self._log_generation_step(request_id, status.value, "in_progress")
    
    async def _log_generation_step(self, request_id: str, step: str, status: str, 
                                 result_data: Optional[Dict] = None, processing_time: float = 0.0):
        """Log generation step to history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO content_history 
        (video_request_id, generation_step, status, result_data, processing_time)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            request_id,
            step,
            status,
            json.dumps(result_data) if result_data else None,
            processing_time
        ))
        
        conn.commit()
        conn.close()
    
    async def _generate_script(self, request: VideoRequest) -> str:
        """Generate video script using AI"""
        try:
            # Use the content creation module
            from content_creation.generator import ContentCreationEngine
            
            content_engine = ContentCreationEngine()
            await content_engine.initialize()
            
            script_request = {
                'topic': request.topic,
                'target_duration': request.target_duration,
                'tone': 'engaging',
                'target_audience': 'general',
                'key_points': request.keywords,
                'include_hook': True,
                'include_cta': True
            }
            
            script_result = await content_engine.generate_video_script(script_request)
            
            if script_result and 'script_content' in script_result:
                return script_result['script_content']
            else:
                # Fallback script generation
                return await self._generate_fallback_script(request)
                
        except Exception as e:
            self.logger.error(f"Script generation failed: {str(e)}")
            return await self._generate_fallback_script(request)
    
    async def _generate_fallback_script(self, request: VideoRequest) -> str:
        """Generate fallback script using templates"""
        template = self.content_templates.get(f"{request.content_type.value}_basic")
        
        if not template:
            # Generic script
            return f"""
            Welcome to this video about {request.topic}!
            
            In today's video, we'll be covering everything you need to know about {request.topic}.
            
            {' '.join([f"- {keyword}" for keyword in request.keywords])}
            
            Thanks for watching! Don't forget to like and subscribe for more content like this.
            """
        
        # Use template with basic substitutions
        script = template.script_template.format(
            topic=request.topic,
            hook=f"Are you ready to learn about {request.topic}?",
            step_1=f"Understanding {request.keywords[0] if request.keywords else request.topic}",
            step_2=f"Practical applications",
            step_3=f"Tips and best practices",
            conclusion=f"That's everything about {request.topic}!",
            cta="Like and subscribe for more!"
        )
        
        return script
    
    async def _create_content_assets(self, request: VideoRequest) -> Dict[str, Any]:
        """Create content assets (images, audio, etc.)"""
        try:
            assets = {
                'images': [],
                'audio': None,
                'b_roll': [],
                'graphics': []
            }
            
            # Generate TTS audio from script
            if request.script_content:
                from tts.synthesizer import TextToSpeechEngine
                
                tts_engine = TextToSpeechEngine()
                await tts_engine.initialize()
                
                audio_result = await tts_engine.synthesize_speech({
                    'text': request.script_content,
                    'voice': 'en-US-Standard-A',
                    'speed': 1.0,
                    'language': 'en-US'
                })
                
                if audio_result and 'audio_url' in audio_result:
                    assets['audio'] = audio_result['audio_url']
            
            # Generate images using AI
            from t2i_sdxl_controlnet.generator import ImageGenerationEngine
            
            image_engine = ImageGenerationEngine()
            await image_engine.initialize()
            
            # Generate cover image
            cover_image = await image_engine.generate_image({
                'prompt': f"High quality image representing {request.topic}, professional, YouTube thumbnail style",
                'width': 1920,
                'height': 1080,
                'style': 'professional'
            })
            
            if cover_image and 'image_url' in cover_image:
                assets['images'].append(cover_image['image_url'])
            
            return assets
            
        except Exception as e:
            self.logger.error(f"Content asset creation failed: {str(e)}")
            return {'images': [], 'audio': None, 'b_roll': [], 'graphics': []}
    
    async def _generate_video(self, request: VideoRequest, assets: Dict[str, Any]) -> str:
        """Generate video using VEO3 or other video generation"""
        try:
            from veo3_integration.generator import VEO3VideoGenerator
            
            veo3_generator = VEO3VideoGenerator()
            await veo3_generator.initialize()
            
            video_request = {
                'prompt': f"Create a {request.target_duration} second video about {request.topic}",
                'duration': min(request.target_duration, 30),  # VEO3 limit
                'style': 'professional',
                'resolution': '720p',
                'audio': assets.get('audio'),
                'images': assets.get('images', [])
            }
            
            video_result = await veo3_generator.generate_video(video_request)
            
            if video_result and 'video_url' in video_result:
                return video_result['video_url']
            else:
                raise Exception("Video generation failed")
                
        except Exception as e:
            self.logger.error(f"Video generation failed: {str(e)}")
            # Return placeholder video URL
            return f"generated_video_{request.id}.mp4"
    
    async def _edit_video(self, request: VideoRequest, video_url: str) -> str:
        """Edit and enhance the generated video"""
        try:
            from video_editor.editor import VideoEditingEngine
            
            editor = VideoEditingEngine()
            await editor.initialize()
            
            editing_request = {
                'video_url': video_url,
                'script': request.script_content,
                'target_duration': request.target_duration,
                'add_intro': True,
                'add_outro': True,
                'add_music': True,
                'add_subtitles': True
            }
            
            edited_result = await editor.edit_video(editing_request)
            
            if edited_result and 'edited_video_url' in edited_result:
                return edited_result['edited_video_url']
            else:
                return video_url  # Return original if editing fails
                
        except Exception as e:
            self.logger.error(f"Video editing failed: {str(e)}")
            return video_url
    
    async def _generate_thumbnail(self, request: VideoRequest) -> str:
        """Generate optimized thumbnail"""
        try:
            from t2i_sdxl_controlnet.generator import ImageGenerationEngine
            
            image_engine = ImageGenerationEngine()
            await image_engine.initialize()
            
            # Generate multiple thumbnail options
            thumbnail_prompts = [
                f"YouTube thumbnail for {request.topic}, bright colors, text overlay, professional",
                f"Eye-catching thumbnail about {request.topic}, high contrast, engaging",
                f"Professional YouTube thumbnail showing {request.topic}, clear and attractive"
            ]
            
            thumbnails = []
            for prompt in thumbnail_prompts:
                thumbnail = await image_engine.generate_image({
                    'prompt': prompt,
                    'width': 1280,
                    'height': 720,
                    'style': 'thumbnail'
                })
                
                if thumbnail and 'image_url' in thumbnail:
                    thumbnails.append(thumbnail['image_url'])
            
            # Save thumbnail options to database
            for thumbnail_url in thumbnails:
                await self._save_thumbnail_option(request.id, thumbnail_url)
            
            # Return the first thumbnail as default
            return thumbnails[0] if thumbnails else f"thumbnail_{request.id}.jpg"
            
        except Exception as e:
            self.logger.error(f"Thumbnail generation failed: {str(e)}")
            return f"thumbnail_{request.id}.jpg"
    
    async def _save_thumbnail_option(self, request_id: str, thumbnail_url: str):
        """Save thumbnail option to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO thumbnails (video_request_id, thumbnail_url, style_options)
        VALUES (?, ?, ?)
        ''', (request_id, thumbnail_url, json.dumps({})))
        
        conn.commit()
        conn.close()
    
    async def _schedule_video(self, request: VideoRequest):
        """Schedule video for publishing"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO publishing_schedule 
            (video_request_id, channel_id, scheduled_time, status)
            VALUES (?, ?, ?, ?)
            ''', (
                request.id,
                request.channel_id,
                request.scheduled_publish_time,
                'scheduled'
            ))
            
            conn.commit()
            conn.close()
            
            await self._update_request_status(request.id, VideoStatus.SCHEDULED)
            
        except Exception as e:
            self.logger.error(f"Failed to schedule video: {str(e)}")
    
    async def publish_video(self, request_id: str) -> bool:
        """Publish a ready video to YouTube"""
        try:
            request = self.video_requests.get(request_id)
            if not request:
                return False
            
            from youtube_integration.publisher import YouTubePublisher
            
            publisher = YouTubePublisher()
            await publisher.initialize()
            
            publish_request = {
                'channel_id': request.channel_id,
                'title': request.title,
                'description': request.description,
                'video_file': request.video_url,
                'thumbnail_file': request.thumbnail_url,
                'tags': request.keywords,
                'privacy': 'public'
            }
            
            result = await publisher.upload_video(publish_request)
            
            if result and result.get('success'):
                await self._update_request_status(request_id, VideoStatus.PUBLISHED)
                
                # Update publishing schedule
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                UPDATE publishing_schedule 
                SET published_time = ?, status = 'published', platform_response = ?
                WHERE video_request_id = ?
                ''', (
                    datetime.now().isoformat(),
                    json.dumps(result),
                    request_id
                ))
                conn.commit()
                conn.close()
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to publish video: {str(e)}")
            return False
    
    async def get_video_request(self, request_id: str) -> Optional[VideoRequest]:
        """Get video request by ID"""
        return self.video_requests.get(request_id)
    
    async def get_all_video_requests(self, channel_id: Optional[str] = None) -> List[VideoRequest]:
        """Get all video requests, optionally filtered by channel"""
        if channel_id:
            return [req for req in self.video_requests.values() if req.channel_id == channel_id]
        return list(self.video_requests.values())
    
    async def get_processing_status(self) -> Dict[str, Any]:
        """Get processing status overview"""
        status_counts = {}
        for status in VideoStatus:
            status_counts[status.value] = len([
                req for req in self.video_requests.values() 
                if req.status == status
            ])
        
        return {
            'total_requests': len(self.video_requests),
            'processing_queue_size': len(self.processing_queue),
            'status_breakdown': status_counts,
            'recent_completions': [
                req.to_dict() for req in sorted(
                    [req for req in self.video_requests.values() if req.status == VideoStatus.PUBLISHED],
                    key=lambda x: x.created_at,
                    reverse=True
                )[:5]
            ]
        }
    
    async def retry_failed_request(self, request_id: str) -> bool:
        """Retry a failed video request"""
        try:
            request = self.video_requests.get(request_id)
            if not request or request.status != VideoStatus.FAILED:
                return False
            
            # Reset status and add back to queue
            await self._update_request_status(request_id, VideoStatus.PENDING)
            self.processing_queue.append(request_id)
            
            # Start processing
            asyncio.create_task(self._process_video_request(request_id))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to retry request: {str(e)}")
            return False
    
    async def delete_video_request(self, request_id: str) -> bool:
        """Delete a video request"""
        try:
            if request_id not in self.video_requests:
                return False
            
            # Remove from database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM video_requests WHERE id = ?", (request_id,))
            cursor.execute("DELETE FROM content_history WHERE video_request_id = ?", (request_id,))
            cursor.execute("DELETE FROM thumbnails WHERE video_request_id = ?", (request_id,))
            cursor.execute("DELETE FROM publishing_schedule WHERE video_request_id = ?", (request_id,))
            
            conn.commit()
            conn.close()
            
            # Remove from memory
            del self.video_requests[request_id]
            
            # Remove from processing queue
            if request_id in self.processing_queue:
                self.processing_queue.remove(request_id)
            
            self.logger.info(f"Deleted video request: {request_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete video request: {str(e)}")
            return False

# Global instance
video_generation_manager = VideoGenerationManager()

async def initialize_video_generation_manager():
    """Initialize the global video generation manager"""
    await video_generation_manager.initialize()