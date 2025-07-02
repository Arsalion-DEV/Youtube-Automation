"""
AI-Powered Channel Management and Setup Wizard
Intelligent channel setup with country-specific SEO, branding, niche detection, and content strategy
"""

import os
import json
import sqlite3
import logging
import asyncio
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import random

from fastapi import HTTPException
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

logger = logging.getLogger(__name__)

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")

class ChannelNiche(Enum):
    TECH_REVIEWS = "tech_reviews"
    GAMING = "gaming"
    LIFESTYLE = "lifestyle"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    MUSIC = "music"
    FITNESS = "fitness"
    COOKING = "cooking"
    TRAVEL = "travel"
    BUSINESS = "business"
    NEWS = "news"
    COMEDY = "comedy"
    BEAUTY = "beauty"
    DIY = "diy"
    AUTOMOTIVE = "automotive"

class ContentType(Enum):
    SHORT_FORM = "short_form"  # YouTube Shorts
    LONG_FORM = "long_form"    # Standard videos
    LIVE_STREAM = "live_stream"
    TUTORIAL = "tutorial"
    REVIEW = "review"
    VLOG = "vlog"

@dataclass
class ChannelSetupConfig:
    channel_name: str
    niche: ChannelNiche
    target_country: str
    target_language: str
    content_style: str
    upload_frequency: str
    target_audience: str
    monetization_goals: List[str]
    budget_range: str

@dataclass
class SEOOptimization:
    keywords: List[str]
    trending_topics: List[str]
    optimal_upload_times: List[str]
    hashtag_suggestions: List[str]
    title_templates: List[str]
    description_templates: List[str]

@dataclass
class ChannelBranding:
    channel_art_url: str
    logo_url: str
    thumbnail_template: str
    color_palette: List[str]
    font_suggestions: List[str]
    brand_guidelines: str

@dataclass
class CompetitorAnalysis:
    top_competitors: List[Dict[str, Any]]
    content_gaps: List[str]
    trending_formats: List[str]
    optimal_video_length: Dict[str, int]
    engagement_insights: Dict[str, Any]

@dataclass
class ContentStrategy:
    content_calendar: List[Dict[str, Any]]
    content_pillars: List[str]
    series_ideas: List[Dict[str, Any]]
    collaboration_opportunities: List[str]
    monetization_timeline: Dict[str, str]

class CountryData:
    """Country-specific data for SEO optimization"""
    
    COUNTRY_CONFIGS = {
        "US": {
            "timezone": "America/New_York",
            "peak_hours": ["19:00", "20:00", "21:00"],
            "language": "en-US",
            "trending_topics": ["technology", "entertainment", "lifestyle"],
            "monetization_threshold": {"subscribers": 1000, "watch_hours": 4000}
        },
        "GB": {
            "timezone": "Europe/London", 
            "peak_hours": ["20:00", "21:00", "22:00"],
            "language": "en-GB",
            "trending_topics": ["comedy", "lifestyle", "education"],
            "monetization_threshold": {"subscribers": 1000, "watch_hours": 4000}
        },
        "CA": {
            "timezone": "America/Toronto",
            "peak_hours": ["19:00", "20:00", "21:00"],
            "language": "en-CA", 
            "trending_topics": ["outdoors", "technology", "comedy"],
            "monetization_threshold": {"subscribers": 1000, "watch_hours": 4000}
        },
        "AU": {
            "timezone": "Australia/Sydney",
            "peak_hours": ["19:00", "20:00", "21:00"],
            "language": "en-AU",
            "trending_topics": ["travel", "lifestyle", "outdoors"],
            "monetization_threshold": {"subscribers": 1000, "watch_hours": 4000}
        },
        "IN": {
            "timezone": "Asia/Kolkata",
            "peak_hours": ["20:00", "21:00", "22:00"],
            "language": "hi-IN",
            "trending_topics": ["bollywood", "technology", "education"],
            "monetization_threshold": {"subscribers": 1000, "watch_hours": 4000}
        },
        "DE": {
            "timezone": "Europe/Berlin",
            "peak_hours": ["20:00", "21:00", "22:00"],
            "language": "de-DE",
            "trending_topics": ["technology", "automotive", "education"],
            "monetization_threshold": {"subscribers": 1000, "watch_hours": 4000}
        }
    }
    
    @classmethod
    def get_country_config(cls, country_code: str) -> Dict[str, Any]:
        return cls.COUNTRY_CONFIGS.get(country_code.upper(), cls.COUNTRY_CONFIGS["US"])

class AIChannelWizard:
    """AI-powered channel setup and management wizard"""
    
    def __init__(self, db_path: str = "../youtube_automation.db"):
        self.db_path = db_path
        self.init_tables()
    
    def init_tables(self):
        """Initialize AI wizard tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Channel wizard configurations
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS channel_wizard_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    channel_id TEXT NOT NULL,
                    setup_config TEXT NOT NULL,
                    seo_optimization TEXT,
                    branding_data TEXT,
                    competitor_analysis TEXT,
                    content_strategy TEXT,
                    setup_stage TEXT DEFAULT 'initial',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE(user_id, channel_id)
                )
            ''')
            
            # AI-generated content ideas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_content_ideas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    content_type TEXT,
                    keywords TEXT,
                    estimated_performance TEXT,
                    creation_date DATE,
                    status TEXT DEFAULT 'suggested',
                    ai_confidence REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Competitor tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS competitor_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id TEXT NOT NULL,
                    competitor_channel_id TEXT NOT NULL,
                    competitor_name TEXT,
                    subscriber_count INTEGER,
                    avg_views INTEGER,
                    upload_frequency TEXT,
                    content_analysis TEXT,
                    last_analyzed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # SEO keyword tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS seo_keywords (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id TEXT NOT NULL,
                    keyword TEXT NOT NULL,
                    search_volume INTEGER,
                    competition_level TEXT,
                    country_code TEXT,
                    trend_data TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            logger.info("AI wizard tables initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing AI wizard tables: {str(e)}")
            raise
        finally:
            conn.close()
    
    async def analyze_channel_niche(self, channel_description: str, sample_videos: List[str]) -> ChannelNiche:
        """AI-powered niche detection based on channel description and videos"""
        try:
            # Combine description and video titles for analysis
            content_text = f"{channel_description} {' '.join(sample_videos)}"
            
            # Use keyword matching and AI analysis
            niche_keywords = {
                ChannelNiche.TECH_REVIEWS: ["tech", "review", "gadget", "smartphone", "laptop", "technology"],
                ChannelNiche.GAMING: ["gaming", "game", "gameplay", "stream", "esports", "gamer"],
                ChannelNiche.LIFESTYLE: ["lifestyle", "vlog", "daily", "routine", "life", "personal"],
                ChannelNiche.EDUCATION: ["education", "tutorial", "learn", "teach", "course", "lesson"],
                ChannelNiche.ENTERTAINMENT: ["entertainment", "funny", "comedy", "show", "entertainment"],
                ChannelNiche.MUSIC: ["music", "song", "cover", "instrumental", "band", "musician"],
                ChannelNiche.FITNESS: ["fitness", "workout", "exercise", "health", "gym", "training"],
                ChannelNiche.COOKING: ["cooking", "recipe", "food", "kitchen", "chef", "cuisine"],
                ChannelNiche.TRAVEL: ["travel", "trip", "destination", "adventure", "explore", "journey"],
                ChannelNiche.BUSINESS: ["business", "entrepreneur", "startup", "finance", "marketing"],
            }
            
            # Score each niche based on keyword presence
            niche_scores = {}
            content_lower = content_text.lower()
            
            for niche, keywords in niche_keywords.items():
                score = sum(1 for keyword in keywords if keyword in content_lower)
                niche_scores[niche] = score
            
            # Return the niche with highest score
            if niche_scores:
                detected_niche = max(niche_scores, key=niche_scores.get)
                if niche_scores[detected_niche] > 0:
                    return detected_niche
            
            # Default fallback
            return ChannelNiche.ENTERTAINMENT
            
        except Exception as e:
            logger.error(f"Error analyzing channel niche: {str(e)}")
            return ChannelNiche.ENTERTAINMENT
    
    async def generate_country_specific_seo(self, niche: ChannelNiche, country: str, target_language: str) -> SEOOptimization:
        """Generate country-specific SEO optimization"""
        try:
            country_config = CountryData.get_country_config(country)
            
            # Base keywords by niche
            base_keywords = {
                ChannelNiche.TECH_REVIEWS: ["tech review", "gadget unboxing", "smartphone test", "laptop review"],
                ChannelNiche.GAMING: ["gaming", "gameplay", "game review", "gaming news"],
                ChannelNiche.LIFESTYLE: ["lifestyle", "daily vlog", "life tips", "personal development"],
                ChannelNiche.EDUCATION: ["tutorial", "how to", "educational", "learning"],
                ChannelNiche.ENTERTAINMENT: ["entertainment", "funny videos", "comedy", "viral"],
                ChannelNiche.MUSIC: ["music", "songs", "cover", "musical"],
                ChannelNiche.FITNESS: ["fitness", "workout", "exercise", "health tips"],
                ChannelNiche.COOKING: ["cooking", "recipes", "food", "kitchen tips"],
                ChannelNiche.TRAVEL: ["travel", "destination", "travel guide", "adventure"],
                ChannelNiche.BUSINESS: ["business", "entrepreneurship", "marketing", "finance"],
            }
            
            keywords = base_keywords.get(niche, ["general content"])
            
            # Add country-specific trending topics
            trending_topics = country_config.get("trending_topics", [])
            
            # Generate title templates
            title_templates = [
                "The Ultimate Guide to {topic} in {year}",
                "Top 10 {topic} Tips for Beginners",
                "{topic} Review: Is It Worth It?",
                "How to Master {topic} in 30 Days",
                "The Secret to {topic} Success",
            ]
            
            # Generate description templates
            description_templates = [
                "In this video, we explore {topic}. Don't forget to subscribe for more content!",
                "Today I'm sharing my thoughts on {topic}. What do you think? Let me know in the comments!",
                "Complete guide to {topic}. Links and resources in the description below.",
            ]
            
            return SEOOptimization(
                keywords=keywords,
                trending_topics=trending_topics,
                optimal_upload_times=country_config.get("peak_hours", ["19:00", "20:00"]),
                hashtag_suggestions=[f"#{kw.replace(' ', '')}" for kw in keywords[:5]],
                title_templates=title_templates,
                description_templates=description_templates
            )
            
        except Exception as e:
            logger.error(f"Error generating SEO optimization: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to generate SEO optimization")
    
    async def generate_channel_branding(self, channel_name: str, niche: ChannelNiche, color_preferences: List[str] = None) -> ChannelBranding:
        """Generate automated channel branding elements"""
        try:
            # Color palettes by niche
            niche_colors = {
                ChannelNiche.TECH_REVIEWS: ["#007acc", "#ff6b6b", "#4ecdc4", "#45b7d1"],
                ChannelNiche.GAMING: ["#ff4757", "#5352ed", "#3742fa", "#2ed573"],
                ChannelNiche.LIFESTYLE: ["#fd79a8", "#fdcb6e", "#e17055", "#00b894"],
                ChannelNiche.EDUCATION: ["#0984e3", "#6c5ce7", "#00b894", "#fd79a8"],
                ChannelNiche.ENTERTAINMENT: ["#fd79a8", "#fdcb6e", "#ff7675", "#74b9ff"],
                ChannelNiche.MUSIC: ["#a29bfe", "#fd79a8", "#fdcb6e", "#55a3ff"],
                ChannelNiche.FITNESS: ["#00b894", "#00cec9", "#55a3ff", "#fd79a8"],
                ChannelNiche.COOKING: ["#e17055", "#fdcb6e", "#fd79a8", "#00b894"],
                ChannelNiche.TRAVEL: ["#74b9ff", "#0984e3", "#00b894", "#fdcb6e"],
                ChannelNiche.BUSINESS: ["#2d3436", "#636e72", "#0984e3", "#00b894"],
            }
            
            color_palette = color_preferences or niche_colors.get(niche, ["#007acc", "#ff6b6b", "#4ecdc4"])
            
            # Font suggestions by niche
            font_suggestions = {
                ChannelNiche.TECH_REVIEWS: ["Roboto", "Open Sans", "Montserrat"],
                ChannelNiche.GAMING: ["Orbitron", "Exo", "Rajdhani"],
                ChannelNiche.LIFESTYLE: ["Poppins", "Nunito", "Comfortaa"],
                ChannelNiche.EDUCATION: ["Lato", "Source Sans Pro", "Merriweather"],
                ChannelNiche.ENTERTAINMENT: ["Fredoka One", "Quicksand", "Cabin"],
                ChannelNiche.MUSIC: ["Oswald", "Dancing Script", "Playfair Display"],
                ChannelNiche.FITNESS: ["Bebas Neue", "Oswald", "Fjalla One"],
                ChannelNiche.COOKING: ["Crimson Text", "Libre Baskerville", "Playfair Display"],
                ChannelNiche.TRAVEL: ["Pacifico", "Kaushan Script", "Amatic SC"],
                ChannelNiche.BUSINESS: ["Inter", "Roboto", "Lato"],
            }
            
            fonts = font_suggestions.get(niche, ["Roboto", "Open Sans"])
            
            # Generate brand guidelines
            brand_guidelines = f"""
            Channel Branding Guidelines for {channel_name}:
            
            Primary Colors: {', '.join(color_palette[:2])}
            Accent Colors: {', '.join(color_palette[2:4]) if len(color_palette) > 2 else 'N/A'}
            
            Typography:
            - Headers: {fonts[0]}
            - Body: {fonts[1] if len(fonts) > 1 else fonts[0]}
            
            Style: Modern, {niche.value.replace('_', ' ').title()}
            Tone: Professional yet approachable
            """
            
            return ChannelBranding(
                channel_art_url=f"/api/generate-channel-art/{channel_name}",
                logo_url=f"/api/generate-logo/{channel_name}",
                thumbnail_template="modern_gradient",
                color_palette=color_palette,
                font_suggestions=fonts,
                brand_guidelines=brand_guidelines
            )
            
        except Exception as e:
            logger.error(f"Error generating channel branding: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to generate channel branding")
    
    async def analyze_competitors(self, niche: ChannelNiche, country: str, credentials: Optional[Credentials] = None) -> CompetitorAnalysis:
        """Analyze competitors in the same niche"""
        try:
            # Simulated competitor analysis (in production, use YouTube Data API)
            niche_competitors = {
                ChannelNiche.TECH_REVIEWS: [
                    {"name": "TechCrunch", "subscribers": "1.5M", "avg_views": "100K", "upload_frequency": "daily"},
                    {"name": "The Verge", "subscribers": "2.8M", "avg_views": "200K", "upload_frequency": "3x/week"},
                    {"name": "Marques Brownlee", "subscribers": "17M", "avg_views": "2M", "upload_frequency": "2x/week"}
                ],
                ChannelNiche.GAMING: [
                    {"name": "PewDiePie", "subscribers": "111M", "avg_views": "3M", "upload_frequency": "daily"},
                    {"name": "Markiplier", "subscribers": "34M", "avg_views": "1.5M", "upload_frequency": "daily"},
                    {"name": "Jacksepticeye", "subscribers": "28M", "avg_views": "1M", "upload_frequency": "daily"}
                ],
                ChannelNiche.LIFESTYLE: [
                    {"name": "Emma Chamberlain", "subscribers": "12M", "avg_views": "2M", "upload_frequency": "weekly"},
                    {"name": "James Charles", "subscribers": "24M", "avg_views": "5M", "upload_frequency": "2x/week"},
                    {"name": "Tana Mongeau", "subscribers": "5.4M", "avg_views": "1M", "upload_frequency": "weekly"}
                ]
            }
            
            competitors = niche_competitors.get(niche, [])
            
            # Analyze content gaps
            content_gaps = [
                "Under 10-minute tutorials",
                "Mobile-first content",
                "Interactive Q&A sessions",
                "Behind-the-scenes content",
                "Collaboration videos"
            ]
            
            # Trending formats
            trending_formats = [
                "YouTube Shorts (under 60 seconds)",
                "Long-form tutorials (20+ minutes)",
                "Live streaming",
                "Series/episodic content",
                "Reaction videos"
            ]
            
            # Optimal video lengths by content type
            optimal_lengths = {
                "tutorial": 600,  # 10 minutes
                "review": 480,    # 8 minutes
                "vlog": 720,      # 12 minutes
                "short": 45,      # 45 seconds
                "live": 3600      # 1 hour
            }
            
            engagement_insights = {
                "best_posting_time": "8:00 PM local time",
                "optimal_frequency": "3-4 videos per week",
                "high_engagement_topics": ["trending news", "tutorials", "reviews"],
                "audience_demographics": {"age": "18-34", "interests": ["technology", "entertainment"]}
            }
            
            return CompetitorAnalysis(
                top_competitors=competitors,
                content_gaps=content_gaps,
                trending_formats=trending_formats,
                optimal_video_length=optimal_lengths,
                engagement_insights=engagement_insights
            )
            
        except Exception as e:
            logger.error(f"Error analyzing competitors: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to analyze competitors")
    
    async def generate_content_strategy(self, setup_config: ChannelSetupConfig, seo_data: SEOOptimization, competitor_data: CompetitorAnalysis) -> ContentStrategy:
        """Generate 30-day content strategy with AI recommendations"""
        try:
            # Content pillars based on niche
            niche_pillars = {
                ChannelNiche.TECH_REVIEWS: ["Product Reviews", "Tech News", "Tutorials", "Comparisons"],
                ChannelNiche.GAMING: ["Gameplay", "Reviews", "Tips & Tricks", "News"],
                ChannelNiche.LIFESTYLE: ["Daily Vlogs", "Tips & Advice", "Product Reviews", "Q&A"],
                ChannelNiche.EDUCATION: ["Tutorials", "Explanations", "Case Studies", "Q&A"],
                ChannelNiche.ENTERTAINMENT: ["Comedy Skits", "Reactions", "Challenges", "Collaborations"]
            }
            
            content_pillars = niche_pillars.get(setup_config.niche, ["General Content", "Reviews", "Tips", "Entertainment"])
            
            # Generate 30-day content calendar
            content_calendar = []
            base_date = datetime.now().date()
            
            # Upload frequency mapping
            frequency_map = {
                "daily": 1,
                "3x_week": 2,  # Every 2-3 days
                "weekly": 7,
                "bi_weekly": 14
            }
            
            interval = frequency_map.get(setup_config.upload_frequency, 7)
            
            for i in range(0, 30, interval):
                publish_date = base_date + timedelta(days=i)
                pillar = content_pillars[i % len(content_pillars)]
                
                # Generate content idea based on pillar and keywords
                keyword = seo_data.keywords[i % len(seo_data.keywords)]
                
                content_calendar.append({
                    "date": publish_date.isoformat(),
                    "title": f"{pillar}: {keyword.title()} Guide",
                    "content_pillar": pillar,
                    "keywords": [keyword],
                    "estimated_length": competitor_data.optimal_video_length.get("tutorial", 600),
                    "content_type": "tutorial" if "tutorial" in pillar.lower() else "educational",
                    "priority": "high" if i < 7 else "medium"
                })
            
            # Series ideas
            series_ideas = [
                {
                    "title": f"{setup_config.niche.value.replace('_', ' ').title()} Basics",
                    "description": "Beginner-friendly series covering fundamentals",
                    "episodes": 5,
                    "frequency": "weekly"
                },
                {
                    "title": "Weekly Roundup",
                    "description": "Weekly news and updates in your niche",
                    "episodes": 12,
                    "frequency": "weekly"
                }
            ]
            
            # Collaboration opportunities
            collaborations = [
                "Guest expert interviews",
                "Joint reviews with other creators",
                "Podcast appearances",
                "Cross-promotion with complementary channels"
            ]
            
            # Monetization timeline
            monetization_timeline = {
                "Month 1": "Focus on content quality and consistency",
                "Month 2-3": "Build audience and engagement",
                "Month 4-6": "Apply for YouTube Partner Program",
                "Month 6+": "Explore brand partnerships and sponsorships"
            }
            
            return ContentStrategy(
                content_calendar=content_calendar,
                content_pillars=content_pillars,
                series_ideas=series_ideas,
                collaboration_opportunities=collaborations,
                monetization_timeline=monetization_timeline
            )
            
        except Exception as e:
            logger.error(f"Error generating content strategy: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to generate content strategy")
    
    async def run_complete_channel_wizard(self, user_id: int, channel_config: ChannelSetupConfig, oauth_credentials: Optional[Dict] = None) -> Dict[str, Any]:
        """Run the complete AI-powered channel setup wizard"""
        try:
            logger.info(f"Starting AI channel wizard for user {user_id}")
            
            # Step 1: Analyze niche (if not provided)
            if not hasattr(channel_config, 'niche') or not channel_config.niche:
                channel_config.niche = await self.analyze_channel_niche(
                    channel_config.channel_name, 
                    []  # Would use existing videos if available
                )
            
            # Step 2: Generate country-specific SEO
            seo_optimization = await self.generate_country_specific_seo(
                channel_config.niche,
                channel_config.target_country,
                channel_config.target_language
            )
            
            # Step 3: Generate channel branding
            branding = await self.generate_channel_branding(
                channel_config.channel_name,
                channel_config.niche
            )
            
            # Step 4: Analyze competitors
            competitor_analysis = await self.analyze_competitors(
                channel_config.niche,
                channel_config.target_country
            )
            
            # Step 5: Generate content strategy
            content_strategy = await self.generate_content_strategy(
                channel_config,
                seo_optimization,
                competitor_analysis
            )
            
            # Step 6: Save to database
            wizard_result = {
                "setup_config": asdict(channel_config),
                "seo_optimization": asdict(seo_optimization),
                "branding": asdict(branding),
                "competitor_analysis": asdict(competitor_analysis),
                "content_strategy": asdict(content_strategy),
                "wizard_version": "1.0",
                "completion_date": datetime.now().isoformat()
            }
            
            await self.save_wizard_result(user_id, channel_config.channel_name, wizard_result)
            
            logger.info(f"AI channel wizard completed for user {user_id}")
            return wizard_result
            
        except Exception as e:
            logger.error(f"Error running channel wizard: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Channel wizard failed: {str(e)}")
    
    async def save_wizard_result(self, user_id: int, channel_id: str, wizard_data: Dict[str, Any]):
        """Save wizard results to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO channel_wizard_configs 
                (user_id, channel_id, setup_config, seo_optimization, branding_data, 
                 competitor_analysis, content_strategy, setup_stage, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                channel_id,
                json.dumps(wizard_data["setup_config"]),
                json.dumps(wizard_data["seo_optimization"]),
                json.dumps(wizard_data["branding"]),
                json.dumps(wizard_data["competitor_analysis"]),
                json.dumps(wizard_data["content_strategy"]),
                "completed",
                datetime.now().isoformat()
            ))
            
            conn.commit()
            logger.info(f"Wizard results saved for user {user_id}, channel {channel_id}")
            
        except Exception as e:
            logger.error(f"Error saving wizard result: {str(e)}")
            raise
        finally:
            conn.close()
    
    async def get_wizard_result(self, user_id: int, channel_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve wizard results from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT setup_config, seo_optimization, branding_data, 
                       competitor_analysis, content_strategy, setup_stage, updated_at
                FROM channel_wizard_configs 
                WHERE user_id = ? AND channel_id = ?
            """, (user_id, channel_id))
            
            result = cursor.fetchone()
            if result:
                return {
                    "setup_config": json.loads(result[0]),
                    "seo_optimization": json.loads(result[1]) if result[1] else None,
                    "branding": json.loads(result[2]) if result[2] else None,
                    "competitor_analysis": json.loads(result[3]) if result[3] else None,
                    "content_strategy": json.loads(result[4]) if result[4] else None,
                    "setup_stage": result[5],
                    "updated_at": result[6]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving wizard result: {str(e)}")
            return None
        finally:
            conn.close()

# Global instance
ai_wizard = AIChannelWizard()