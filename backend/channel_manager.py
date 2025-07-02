"""
Multi-Channel Management System for YouTube Automation Platform
Supports multiple YouTube channels with independent Gmail accounts and API management
"""

import sqlite3
import json
import uuid
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class ChannelStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    SUSPENDED = "suspended"
    PENDING_SETUP = "pending_setup"

class APIProviderType(Enum):
    GOOGLE_YOUTUBE = "google_youtube"
    GOOGLE_VERTEX = "google_vertex"
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    SOCIAL_BLADE = "social_blade"
    VIDIQ = "vidiq"
    TUBEBUDDY = "tubebuddy"

@dataclass
class APIConfiguration:
    provider: APIProviderType
    api_key: str
    secret_key: Optional[str] = None
    oauth_credentials: Optional[Dict] = None
    monthly_limit: int = 1000
    current_usage: int = 0
    reset_date: str = ""
    is_active: bool = True
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**data)

@dataclass
class ChannelConfiguration:
    channel_id: str
    channel_name: str
    gmail_account: str
    gmail_app_password: str
    status: ChannelStatus = ChannelStatus.PENDING_SETUP
    api_configurations: Dict[str, APIConfiguration] = None
    created_at: str = ""
    updated_at: str = ""
    settings: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.api_configurations is None:
            self.api_configurations = {}
        if self.settings is None:
            self.settings = {}
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self):
        data = asdict(self)
        # Convert APIConfiguration objects to dict
        data['api_configurations'] = {
            k: v.to_dict() if isinstance(v, APIConfiguration) else v
            for k, v in self.api_configurations.items()
        }
        return data
    
    @classmethod
    def from_dict(cls, data: Dict):
        # Convert dict back to APIConfiguration objects
        if 'api_configurations' in data:
            api_configs = {}
            for k, v in data['api_configurations'].items():
                if isinstance(v, dict):
                    api_configs[k] = APIConfiguration.from_dict(v)
                else:
                    api_configs[k] = v
            data['api_configurations'] = api_configs
        
        # Convert status if it's a string
        if isinstance(data.get('status'), str):
            data['status'] = ChannelStatus(data['status'])
            
        return cls(**data)

class ChannelManager:
    """Comprehensive Multi-Channel Management System"""
    
    def __init__(self, database_path: str = "youtube_automation.db"):
        self.db_path = database_path
        self.channels: Dict[str, ChannelConfiguration] = {}
        self.api_rate_limits: Dict[str, Dict[str, int]] = {}
        self.logger = logging.getLogger(f"{__name__}.ChannelManager")
        
    async def initialize(self):
        """Initialize the channel management system"""
        try:
            await self._create_database_tables()
            await self._load_channels()
            await self._setup_api_monitoring()
            self.logger.info("Channel Manager initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Channel Manager: {str(e)}")
            raise

    async def _create_database_tables(self):
        """Create necessary database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Channels table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS channels (
            channel_id TEXT PRIMARY KEY,
            channel_name TEXT NOT NULL,
            gmail_account TEXT NOT NULL UNIQUE,
            gmail_app_password TEXT NOT NULL,
            status TEXT DEFAULT 'pending_setup',
            api_configurations TEXT DEFAULT '{}',
            settings TEXT DEFAULT '{}',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # API Usage Tracking table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id TEXT,
            api_provider TEXT,
            usage_count INTEGER DEFAULT 0,
            usage_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (channel_id) REFERENCES channels (channel_id)
        )
        ''')
        
        # Channel Analytics table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS channel_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id TEXT,
            metric_name TEXT,
            metric_value REAL,
            metric_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (channel_id) REFERENCES channels (channel_id)
        )
        ''')
        
        # Video Queue table for channel-specific content
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS video_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id TEXT,
            video_title TEXT,
            video_description TEXT,
            video_tags TEXT,
            video_status TEXT DEFAULT 'pending',
            scheduled_time TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (channel_id) REFERENCES channels (channel_id)
        )
        ''')
        
        conn.commit()
        conn.close()
        
    async def _load_channels(self):
        """Load existing channels from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM channels")
        rows = cursor.fetchall()
        
        for row in rows:
            channel_data = {
                'channel_id': row[0],
                'channel_name': row[1], 
                'gmail_account': row[2],
                'gmail_app_password': row[3],
                'status': ChannelStatus(row[4]),
                'api_configurations': json.loads(row[5]),
                'settings': json.loads(row[6]),
                'created_at': row[7],
                'updated_at': row[8]
            }
            
            # Convert API configurations
            api_configs = {}
            for provider, config in channel_data['api_configurations'].items():
                api_configs[provider] = APIConfiguration.from_dict(config)
            channel_data['api_configurations'] = api_configs
            
            channel = ChannelConfiguration.from_dict(channel_data)
            self.channels[channel.channel_id] = channel
            
        conn.close()
        self.logger.info(f"Loaded {len(self.channels)} channels")

    async def _setup_api_monitoring(self):
        """Setup API usage monitoring and rate limiting"""
        for channel in self.channels.values():
            for provider, config in channel.api_configurations.items():
                if config.reset_date:
                    reset_date = datetime.fromisoformat(config.reset_date)
                    if datetime.now() > reset_date:
                        # Reset monthly usage
                        await self._reset_api_usage(channel.channel_id, provider)

    async def add_channel(self, channel_name: str, gmail_account: str, gmail_app_password: str) -> str:
        """Add a new channel to the system"""
        try:
            # Generate unique channel ID
            channel_id = str(uuid.uuid4())
            
            # Verify Gmail account is unique
            if any(ch.gmail_account == gmail_account for ch in self.channels.values()):
                raise ValueError(f"Gmail account {gmail_account} is already in use")
            
            # Create channel configuration
            channel = ChannelConfiguration(
                channel_id=channel_id,
                channel_name=channel_name,
                gmail_account=gmail_account,
                gmail_app_password=gmail_app_password,
                status=ChannelStatus.PENDING_SETUP
            )
            
            # Save to database
            await self._save_channel(channel)
            
            # Add to memory
            self.channels[channel_id] = channel
            
            self.logger.info(f"Added new channel: {channel_name} ({channel_id})")
            return channel_id
            
        except Exception as e:
            self.logger.error(f"Failed to add channel {channel_name}: {str(e)}")
            raise

    async def _save_channel(self, channel: ChannelConfiguration):
        """Save channel to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert API configurations to JSON
        api_configs_json = json.dumps({
            k: v.to_dict() for k, v in channel.api_configurations.items()
        })
        
        cursor.execute('''
        INSERT OR REPLACE INTO channels 
        (channel_id, channel_name, gmail_account, gmail_app_password, status, 
         api_configurations, settings, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            channel.channel_id,
            channel.channel_name,
            channel.gmail_account,
            channel.gmail_app_password,
            channel.status.value,
            api_configs_json,
            json.dumps(channel.settings),
            channel.created_at,
            channel.updated_at
        ))
        
        conn.commit()
        conn.close()

    async def remove_channel(self, channel_id: str) -> bool:
        """Remove a channel from the system"""
        try:
            if channel_id not in self.channels:
                return False
            
            # Remove from database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM channels WHERE channel_id = ?", (channel_id,))
            cursor.execute("DELETE FROM api_usage WHERE channel_id = ?", (channel_id,))
            cursor.execute("DELETE FROM channel_analytics WHERE channel_id = ?", (channel_id,))
            cursor.execute("DELETE FROM video_queue WHERE channel_id = ?", (channel_id,))
            
            conn.commit()
            conn.close()
            
            # Remove from memory
            del self.channels[channel_id]
            
            self.logger.info(f"Removed channel: {channel_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove channel {channel_id}: {str(e)}")
            return False

    async def update_channel_api_config(self, channel_id: str, provider: APIProviderType, 
                                      api_key: str, secret_key: Optional[str] = None,
                                      oauth_credentials: Optional[Dict] = None,
                                      monthly_limit: int = 1000) -> bool:
        """Update API configuration for a specific channel"""
        try:
            if channel_id not in self.channels:
                raise ValueError(f"Channel {channel_id} not found")
            
            channel = self.channels[channel_id]
            
            # Create or update API configuration
            api_config = APIConfiguration(
                provider=provider,
                api_key=api_key,
                secret_key=secret_key,
                oauth_credentials=oauth_credentials,
                monthly_limit=monthly_limit,
                reset_date=(datetime.now() + timedelta(days=30)).isoformat()
            )
            
            channel.api_configurations[provider.value] = api_config
            channel.updated_at = datetime.now().isoformat()
            
            # Save to database
            await self._save_channel(channel)
            
            self.logger.info(f"Updated API config for channel {channel_id}, provider {provider.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update API config for {channel_id}: {str(e)}")
            return False

    async def get_channel(self, channel_id: str) -> Optional[ChannelConfiguration]:
        """Get channel configuration by ID"""
        return self.channels.get(channel_id)

    async def get_all_channels(self) -> List[ChannelConfiguration]:
        """Get all channels"""
        return list(self.channels.values())

    async def get_channels_by_status(self, status: ChannelStatus) -> List[ChannelConfiguration]:
        """Get channels by status"""
        return [ch for ch in self.channels.values() if ch.status == status]

    async def update_channel_status(self, channel_id: str, status: ChannelStatus) -> bool:
        """Update channel status"""
        try:
            if channel_id not in self.channels:
                return False
            
            self.channels[channel_id].status = status
            self.channels[channel_id].updated_at = datetime.now().isoformat()
            
            await self._save_channel(self.channels[channel_id])
            
            self.logger.info(f"Updated channel {channel_id} status to {status.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update status for {channel_id}: {str(e)}")
            return False

    async def check_api_limit(self, channel_id: str, provider: APIProviderType) -> Dict[str, Any]:
        """Check API usage and limits for a channel"""
        try:
            if channel_id not in self.channels:
                raise ValueError(f"Channel {channel_id} not found")
            
            channel = self.channels[channel_id]
            
            if provider.value not in channel.api_configurations:
                return {
                    'available': False,
                    'reason': 'API configuration not found',
                    'usage': 0,
                    'limit': 0,
                    'remaining': 0
                }
            
            api_config = channel.api_configurations[provider.value]
            
            # Check if we need to reset monthly usage
            if api_config.reset_date:
                reset_date = datetime.fromisoformat(api_config.reset_date)
                if datetime.now() > reset_date:
                    await self._reset_api_usage(channel_id, provider.value)
                    api_config.reset_date = (datetime.now() + timedelta(days=30)).isoformat()
                    await self._save_channel(channel)
            
            remaining = api_config.monthly_limit - api_config.current_usage
            
            return {
                'available': remaining > 0 and api_config.is_active,
                'usage': api_config.current_usage,
                'limit': api_config.monthly_limit,
                'remaining': remaining,
                'reset_date': api_config.reset_date
            }
            
        except Exception as e:
            self.logger.error(f"Failed to check API limit for {channel_id}: {str(e)}")
            return {'available': False, 'reason': str(e)}

    async def increment_api_usage(self, channel_id: str, provider: APIProviderType, 
                                usage_count: int = 1) -> bool:
        """Increment API usage for a channel"""
        try:
            if channel_id not in self.channels:
                return False
            
            channel = self.channels[channel_id]
            
            if provider.value in channel.api_configurations:
                api_config = channel.api_configurations[provider.value]
                api_config.current_usage += usage_count
                
                # Log usage to database
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                INSERT INTO api_usage (channel_id, api_provider, usage_count)
                VALUES (?, ?, ?)
                ''', (channel_id, provider.value, usage_count))
                conn.commit()
                conn.close()
                
                await self._save_channel(channel)
                
                self.logger.info(f"Incremented API usage for {channel_id}, {provider.value}: +{usage_count}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to increment API usage for {channel_id}: {str(e)}")
            return False

    async def _reset_api_usage(self, channel_id: str, provider: str):
        """Reset monthly API usage for a channel"""
        if channel_id in self.channels:
            channel = self.channels[channel_id]
            if provider in channel.api_configurations:
                channel.api_configurations[provider].current_usage = 0
                self.logger.info(f"Reset API usage for {channel_id}, {provider}")

    async def get_channel_analytics(self, channel_id: str, 
                                  metric_name: Optional[str] = None,
                                  days: int = 30) -> List[Dict]:
        """Get analytics data for a channel"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            if metric_name:
                cursor.execute('''
                SELECT metric_name, metric_value, metric_date
                FROM channel_analytics
                WHERE channel_id = ? AND metric_name = ? AND metric_date >= ?
                ORDER BY metric_date DESC
                ''', (channel_id, metric_name, start_date))
            else:
                cursor.execute('''
                SELECT metric_name, metric_value, metric_date
                FROM channel_analytics
                WHERE channel_id = ? AND metric_date >= ?
                ORDER BY metric_date DESC
                ''', (channel_id, start_date))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'metric_name': row[0],
                    'metric_value': row[1],
                    'metric_date': row[2]
                }
                for row in rows
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to get analytics for {channel_id}: {str(e)}")
            return []

    async def add_video_to_queue(self, channel_id: str, video_title: str,
                               video_description: str, video_tags: List[str],
                               scheduled_time: Optional[str] = None) -> bool:
        """Add video to channel's content queue"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO video_queue 
            (channel_id, video_title, video_description, video_tags, scheduled_time)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                channel_id,
                video_title,
                video_description,
                json.dumps(video_tags),
                scheduled_time
            ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Added video to queue for channel {channel_id}: {video_title}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add video to queue for {channel_id}: {str(e)}")
            return False

    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        try:
            active_channels = len([ch for ch in self.channels.values() if ch.status == ChannelStatus.ACTIVE])
            total_channels = len(self.channels)
            
            # Calculate total API usage across all channels
            total_api_usage = {}
            for channel in self.channels.values():
                for provider, config in channel.api_configurations.items():
                    if provider not in total_api_usage:
                        total_api_usage[provider] = 0
                    total_api_usage[provider] += config.current_usage
            
            return {
                'total_channels': total_channels,
                'active_channels': active_channels,
                'paused_channels': len([ch for ch in self.channels.values() if ch.status == ChannelStatus.PAUSED]),
                'pending_channels': len([ch for ch in self.channels.values() if ch.status == ChannelStatus.PENDING_SETUP]),
                'api_usage': total_api_usage,
                'system_healthy': active_channels > 0,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system status: {str(e)}")
            return {'system_healthy': False, 'error': str(e)}

# Global instance
channel_manager = ChannelManager()

async def initialize_channel_manager():
    """Initialize the global channel manager"""
    await channel_manager.initialize()

# Third-party Integration Classes
class VidIQIntegration:
    """VidIQ API Integration for channel analytics and optimization"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.vidiq.com/v1"
        
    async def get_keyword_suggestions(self, channel_id: str, topic: str) -> List[Dict]:
        """Get keyword suggestions from VidIQ"""
        # Implementation would connect to VidIQ API
        return []
        
    async def get_competitor_analysis(self, channel_id: str, competitor_channel: str) -> Dict:
        """Get competitor analysis from VidIQ"""
        # Implementation would connect to VidIQ API
        return {}

class SocialBladeIntegration:
    """Social Blade API Integration for channel statistics"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.socialblade.com"
        
    async def get_channel_stats(self, channel_id: str) -> Dict:
        """Get channel statistics from Social Blade"""
        # Implementation would connect to Social Blade API
        return {}
        
    async def get_trending_content(self, niche: str) -> List[Dict]:
        """Get trending content in a niche"""
        # Implementation would connect to Social Blade API
        return []

class TubeBuddyIntegration:
    """TubeBuddy-like functionality for channel optimization"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    async def get_best_upload_time(self, channel_id: str) -> Dict:
        """Get optimal upload time for channel"""
        # Implementation would analyze channel data
        return {}
        
    async def get_tag_suggestions(self, video_title: str) -> List[str]:
        """Get tag suggestions for video"""
        # Implementation would analyze video content
        return []