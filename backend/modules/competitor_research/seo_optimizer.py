"""
SEO Optimization Engine
Advanced SEO analysis and optimization system for YouTube content
"""

import asyncio
import logging
import json
import uuid
import re
import statistics
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from urllib.parse import urlparse

# Data analysis and ML
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import textstat
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Web scraping and APIs
import httpx
import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Internal modules
from modules.base import BaseModule
from database_extensions import DatabaseExtensions

logger = logging.getLogger(__name__)

class SEOOptimizationEngine(BaseModule):
    """Advanced SEO optimization and analysis system for YouTube"""
    
    def __init__(self):
        super().__init__()
        self.module_name = "seo_optimization"
        
        # SEO configuration
        self.seo_config = {
            "optimization_factors": {
                "title": {
                    "weight": 0.25,
                    "optimal_length": {"min": 30, "max": 60},
                    "keyword_density": {"min": 0.05, "max": 0.15}
                },
                "description": {
                    "weight": 0.20,
                    "optimal_length": {"min": 100, "max": 160},
                    "keyword_density": {"min": 0.03, "max": 0.08}
                },
                "tags": {
                    "weight": 0.15,
                    "optimal_count": {"min": 5, "max": 15},
                    "relevance_threshold": 0.7
                },
                "thumbnail": {
                    "weight": 0.15,
                    "factors": ["contrast", "text_readability", "face_presence", "color_psychology"]
                },
                "engagement": {
                    "weight": 0.25,
                    "metrics": ["ctr", "watch_time", "likes_ratio", "comments_ratio"]
                }
            },
            "youtube_seo_factors": {
                "primary": ["title_keywords", "description_keywords", "tags", "transcript"],
                "secondary": ["thumbnail_optimization", "upload_timing", "playlist_inclusion"],
                "engagement": ["ctr", "watch_time", "engagement_rate", "retention_rate"]
            },
            "keyword_analysis": {
                "difficulty_factors": ["search_volume", "competition", "trend", "seasonality"],
                "opportunity_scoring": ["low_competition", "high_volume", "trend_growth"],
                "long_tail_threshold": 3  # words
            }
        }
        
        # SEO best practices
        self.seo_best_practices = {
            "title_patterns": [
                "How to {keyword}",
                "{keyword} - Complete Guide",
                "Best {keyword} for {year}",
                "{number} {keyword} Tips",
                "{keyword} vs {alternative}"
            ],
            "description_templates": [
                "Learn {keyword} with this comprehensive guide...",
                "In this video, I'll show you {keyword}...",
                "Everything you need to know about {keyword}..."
            ],
            "tag_strategies": {
                "primary_tags": 3,      # Most important keywords
                "secondary_tags": 5,    # Related keywords
                "long_tail_tags": 4,    # Long-tail variations
                "trending_tags": 3      # Trending related topics
            }
        }
        
        # YouTube API and external services
        self.youtube_service = None
        self.keyword_research_apis = {}
        
        # Database extensions
        self.db_ext = None
        
        # Analysis tools
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.text_analyzer = textstat
        
        # SEO tracking data
        self.seo_cache = {}
        self.keyword_cache = {}
        self.competitor_seo_data = {}
    
    async def _setup_module(self):
        """Initialize the SEO optimization engine"""
        await super()._setup_module()
        
        try:
            # Initialize database extensions
            self.db_ext = DatabaseExtensions()
            
            # Initialize YouTube API
            youtube_api_key = self.config.get("youtube_api_key")
            if youtube_api_key:
                self.youtube_service = build("youtube", "v3", developerKey=youtube_api_key)
                logger.info("YouTube API initialized for SEO optimization")
            
            # Initialize keyword research APIs
            await self._initialize_keyword_apis()
            
            # Load existing SEO cache
            await self._load_seo_cache()
            
            logger.info("SEO Optimization Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize SEO Optimization Engine: {str(e)}")
            raise
    
    async def _initialize_keyword_apis(self):
        """Initialize keyword research and SEO APIs"""
        try:
            # Google Keyword Planner API
            # SEMrush API
            # Ahrefs API
            # TubeBuddy API
            # VidIQ API
            pass
            
        except Exception as e:
            logger.warning(f"Some keyword APIs unavailable: {str(e)}")
    
    async def analyze_seo_performance(
        self,
        video_id: Optional[str] = None,
        channel_id: Optional[str] = None,
        target_keywords: List[str] = None,
        analyze_competitors: bool = True,
        include_optimization_suggestions: bool = True,
        deep_analysis: bool = False
    ) -> Dict[str, Any]:
        """Comprehensive SEO performance analysis"""
        
        try:
            analysis_start = datetime.utcnow()
            seo_analysis_id = str(uuid.uuid4())
            
            logger.info(f"Starting SEO analysis for video: {video_id}, channel: {channel_id}")
            
            # Step 1: Collect content data
            content_data = await self._collect_content_data(video_id, channel_id)
            
            if not content_data:
                raise ValueError("No content data found for analysis")
            
            # Step 2: Analyze current SEO elements
            current_seo_analysis = await self._analyze_current_seo_elements(
                content_data, target_keywords
            )
            
            # Step 3: Keyword performance analysis
            keyword_analysis = await self._analyze_keyword_performance(
                content_data, target_keywords
            )
            
            # Step 4: Competitor SEO analysis (if enabled)
            competitor_analysis = {}
            if analyze_competitors:
                competitor_analysis = await self._analyze_competitor_seo(
                    target_keywords, content_data.get("niche", "")
                )
            
            # Step 5: Technical SEO analysis
            technical_seo_analysis = await self._analyze_technical_seo(
                content_data, deep_analysis
            )
            
            # Step 6: Content optimization analysis
            content_optimization_analysis = await self._analyze_content_optimization(
                content_data, target_keywords
            )
            
            # Step 7: Performance metrics analysis
            performance_analysis = await self._analyze_seo_performance_metrics(
                content_data, video_id
            )
            
            # Step 8: Generate optimization suggestions (if enabled)
            optimization_suggestions = {}
            if include_optimization_suggestions:
                optimization_suggestions = await self._generate_optimization_suggestions(
                    current_seo_analysis, keyword_analysis, competitor_analysis
                )
            
            # Step 9: Calculate overall SEO score
            overall_seo_score = self._calculate_overall_seo_score({
                "current_seo": current_seo_analysis,
                "keywords": keyword_analysis,
                "technical": technical_seo_analysis,
                "content": content_optimization_analysis,
                "performance": performance_analysis
            })
            
            # Step 10: Predict SEO impact of optimizations
            impact_predictions = await self._predict_optimization_impact(
                optimization_suggestions, current_seo_analysis
            )
            
            # Compile comprehensive SEO analysis report
            seo_analysis_report = {
                "analysis_id": seo_analysis_id,
                "video_id": video_id,
                "channel_id": channel_id,
                "analysis_date": analysis_start,
                "target_keywords": target_keywords or [],
                "overall_seo_score": overall_seo_score,
                "current_seo_analysis": current_seo_analysis,
                "keyword_analysis": keyword_analysis,
                "competitor_analysis": competitor_analysis,
                "technical_seo_analysis": technical_seo_analysis,
                "content_optimization_analysis": content_optimization_analysis,
                "performance_analysis": performance_analysis,
                "optimization_suggestions": optimization_suggestions,
                "impact_predictions": impact_predictions,
                "seo_insights": {
                    "key_strengths": await self._identify_seo_strengths(current_seo_analysis),
                    "critical_issues": await self._identify_critical_issues(current_seo_analysis),
                    "quick_wins": await self._identify_quick_wins(optimization_suggestions),
                    "long_term_opportunities": await self._identify_long_term_opportunities(
                        optimization_suggestions, competitor_analysis
                    )
                },
                "competitive_positioning": {
                    "keyword_rankings": keyword_analysis.get("current_rankings", {}),
                    "competitor_comparison": competitor_analysis.get("comparison", {}),
                    "market_opportunities": competitor_analysis.get("opportunities", [])
                },
                "action_plan": await self._create_seo_action_plan(
                    optimization_suggestions, impact_predictions
                ),
                "monitoring_recommendations": await self._generate_monitoring_recommendations(
                    target_keywords, video_id, channel_id
                ),
                "metadata": {
                    "analysis_time": (datetime.utcnow() - analysis_start).total_seconds(),
                    "analysis_depth": "deep" if deep_analysis else "standard",
                    "confidence_score": self._calculate_analysis_confidence(
                        content_data, len(target_keywords or [])
                    ),
                    "next_analysis_recommended": analysis_start + timedelta(weeks=2)
                }
            }
            
            # Save analysis to database
            await self._save_seo_analysis(seo_analysis_report)
            
            # Update SEO tracking
            await self._update_seo_tracking(
                video_id, channel_id, target_keywords, seo_analysis_report
            )
            
            await self.log_activity("seo_analysis_completed", {
                "video_id": video_id,
                "channel_id": channel_id,
                "overall_score": overall_seo_score,
                "analysis_time": seo_analysis_report["metadata"]["analysis_time"]
            })
            
            return seo_analysis_report
            
        except Exception as e:
            logger.error(f"SEO analysis failed: {str(e)}")
            raise
    
    async def _collect_content_data(
        self,
        video_id: Optional[str],
        channel_id: Optional[str]
    ) -> Dict[str, Any]:
        """Collect content data for SEO analysis"""
        
        content_data = {}
        
        try:
            if video_id and self.youtube_service:
                # Get video data
                video_response = self.youtube_service.videos().list(
                    part="snippet,statistics,contentDetails",
                    id=video_id
                ).execute()
                
                if video_response.get("items"):
                    video_info = video_response["items"][0]
                    content_data.update({
                        "video_id": video_id,
                        "title": video_info["snippet"].get("title", ""),
                        "description": video_info["snippet"].get("description", ""),
                        "tags": video_info["snippet"].get("tags", []),
                        "thumbnail_url": video_info["snippet"]["thumbnails"].get("maxres", {}).get("url", ""),
                        "published_at": video_info["snippet"].get("publishedAt"),
                        "statistics": video_info.get("statistics", {}),
                        "duration": video_info["contentDetails"].get("duration", ""),
                        "channel_id": video_info["snippet"].get("channelId", channel_id)
                    })
            
            if channel_id and self.youtube_service:
                # Get channel data
                channel_response = self.youtube_service.channels().list(
                    part="snippet,statistics,brandingSettings",
                    id=channel_id
                ).execute()
                
                if channel_response.get("items"):
                    channel_info = channel_response["items"][0]
                    content_data.update({
                        "channel_id": channel_id,
                        "channel_title": channel_info["snippet"].get("title", ""),
                        "channel_description": channel_info["snippet"].get("description", ""),
                        "channel_keywords": channel_info.get("brandingSettings", {}).get("channel", {}).get("keywords", ""),
                        "channel_statistics": channel_info.get("statistics", {})
                    })
            
            # Extract niche/category information
            if content_data.get("title") or content_data.get("channel_title"):
                content_data["niche"] = await self._detect_content_niche(content_data)
            
            return content_data
            
        except Exception as e:
            logger.error(f"Content data collection failed: {str(e)}")
            return content_data
    
    async def _analyze_current_seo_elements(
        self,
        content_data: Dict[str, Any],
        target_keywords: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Analyze current SEO elements of the content"""
        
        seo_analysis = {
            "title_analysis": {},
            "description_analysis": {},
            "tags_analysis": {},
            "thumbnail_analysis": {},
            "overall_element_scores": {}
        }
        
        try:
            title = content_data.get("title", "")
            description = content_data.get("description", "")
            tags = content_data.get("tags", [])
            
            # Title analysis
            seo_analysis["title_analysis"] = await self._analyze_title_seo(
                title, target_keywords
            )
            
            # Description analysis
            seo_analysis["description_analysis"] = await self._analyze_description_seo(
                description, target_keywords
            )
            
            # Tags analysis
            seo_analysis["tags_analysis"] = await self._analyze_tags_seo(
                tags, target_keywords
            )
            
            # Thumbnail analysis (if URL available)
            thumbnail_url = content_data.get("thumbnail_url")
            if thumbnail_url:
                seo_analysis["thumbnail_analysis"] = await self._analyze_thumbnail_seo(
                    thumbnail_url
                )
            
            # Calculate individual element scores
            title_score = seo_analysis["title_analysis"].get("seo_score", 0.5)
            description_score = seo_analysis["description_analysis"].get("seo_score", 0.5)
            tags_score = seo_analysis["tags_analysis"].get("seo_score", 0.5)
            thumbnail_score = seo_analysis["thumbnail_analysis"].get("seo_score", 0.5)
            
            seo_analysis["overall_element_scores"] = {
                "title_score": title_score,
                "description_score": description_score,
                "tags_score": tags_score,
                "thumbnail_score": thumbnail_score,
                "weighted_average": self._calculate_weighted_seo_score({
                    "title": title_score,
                    "description": description_score,
                    "tags": tags_score,
                    "thumbnail": thumbnail_score
                })
            }
            
            return seo_analysis
            
        except Exception as e:
            logger.error(f"SEO elements analysis failed: {str(e)}")
            return seo_analysis
    
    async def _analyze_title_seo(
        self,
        title: str,
        target_keywords: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Analyze title SEO optimization"""
        
        title_analysis = {
            "length": len(title),
            "word_count": len(title.split()),
            "character_count": len(title),
            "keyword_presence": {},
            "optimization_issues": [],
            "optimization_suggestions": [],
            "seo_score": 0.5
        }
        
        try:
            # Length analysis
            optimal_length = self.seo_config["optimization_factors"]["title"]["optimal_length"]
            if title_analysis["character_count"] < optimal_length["min"]:
                title_analysis["optimization_issues"].append("Title too short")
                title_analysis["optimization_suggestions"].append(
                    f"Increase title length to at least {optimal_length['min']} characters"
                )
            elif title_analysis["character_count"] > optimal_length["max"]:
                title_analysis["optimization_issues"].append("Title too long")
                title_analysis["optimization_suggestions"].append(
                    f"Reduce title length to maximum {optimal_length['max']} characters"
                )
            
            # Keyword analysis
            if target_keywords:
                keyword_analysis = {}
                title_lower = title.lower()
                
                for keyword in target_keywords:
                    keyword_lower = keyword.lower()
                    is_present = keyword_lower in title_lower
                    position = title_lower.find(keyword_lower) if is_present else -1
                    
                    keyword_analysis[keyword] = {
                        "present": is_present,
                        "position": position,
                        "early_placement": position < len(title) * 0.3 if position >= 0 else False
                    }
                
                title_analysis["keyword_presence"] = keyword_analysis
                
                # Check for missing primary keywords
                missing_keywords = [kw for kw, data in keyword_analysis.items() if not data["present"]]
                if missing_keywords:
                    title_analysis["optimization_suggestions"].append(
                        f"Include primary keywords: {', '.join(missing_keywords[:2])}"
                    )
            
            # Calculate title SEO score
            title_analysis["seo_score"] = self._calculate_title_seo_score(title_analysis)
            
            return title_analysis
            
        except Exception as e:
            logger.error(f"Title SEO analysis failed: {str(e)}")
            return title_analysis
    
    async def _analyze_description_seo(
        self,
        description: str,
        target_keywords: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Analyze description SEO optimization"""
        
        description_analysis = {
            "length": len(description),
            "word_count": len(description.split()),
            "sentence_count": len(description.split('.')),
            "keyword_density": {},
            "readability_score": 0.0,
            "sentiment": {},
            "optimization_issues": [],
            "optimization_suggestions": [],
            "seo_score": 0.5
        }
        
        try:
            # Length analysis
            optimal_length = self.seo_config["optimization_factors"]["description"]["optimal_length"]
            if description_analysis["length"] < optimal_length["min"]:
                description_analysis["optimization_issues"].append("Description too short")
                description_analysis["optimization_suggestions"].append(
                    f"Expand description to at least {optimal_length['min']} characters"
                )
            elif description_analysis["length"] > optimal_length["max"]:
                description_analysis["optimization_issues"].append("Description too long")
                description_analysis["optimization_suggestions"].append(
                    "Consider shortening description for better readability"
                )
            
            # Readability analysis
            if description:
                description_analysis["readability_score"] = textstat.flesch_reading_ease(description)
                
                if description_analysis["readability_score"] < 60:
                    description_analysis["optimization_suggestions"].append(
                        "Improve readability by using shorter sentences and simpler words"
                    )
            
            # Sentiment analysis
            if description:
                sentiment_scores = self.sentiment_analyzer.polarity_scores(description)
                description_analysis["sentiment"] = sentiment_scores
                
                if sentiment_scores["compound"] < 0.1:
                    description_analysis["optimization_suggestions"].append(
                        "Consider using more positive language in description"
                    )
            
            # Keyword analysis
            if target_keywords and description:
                keyword_density = {}
                description_lower = description.lower()
                word_count = len(description.split())
                
                for keyword in target_keywords:
                    keyword_count = description_lower.count(keyword.lower())
                    density = keyword_count / word_count if word_count > 0 else 0
                    
                    keyword_density[keyword] = {
                        "count": keyword_count,
                        "density": density,
                        "optimal": 0.03 <= density <= 0.08
                    }
                
                description_analysis["keyword_density"] = keyword_density
                
                # Check keyword optimization
                for keyword, data in keyword_density.items():
                    if data["count"] == 0:
                        description_analysis["optimization_suggestions"].append(
                            f"Include keyword '{keyword}' in description"
                        )
                    elif data["density"] < 0.03:
                        description_analysis["optimization_suggestions"].append(
                            f"Increase usage of keyword '{keyword}' in description"
                        )
                    elif data["density"] > 0.08:
                        description_analysis["optimization_suggestions"].append(
                            f"Reduce keyword stuffing for '{keyword}' in description"
                        )
            
            # Calculate description SEO score
            description_analysis["seo_score"] = self._calculate_description_seo_score(description_analysis)
            
            return description_analysis
            
        except Exception as e:
            logger.error(f"Description SEO analysis failed: {str(e)}")
            return description_analysis
    
    async def _analyze_tags_seo(
        self,
        tags: List[str],
        target_keywords: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Analyze tags SEO optimization"""
        
        tags_analysis = {
            "tag_count": len(tags),
            "target_keyword_coverage": {},
            "tag_types": {},
            "optimization_issues": [],
            "optimization_suggestions": [],
            "seo_score": 0.5
        }
        
        try:
            # Tag count analysis
            optimal_count = self.seo_config["optimization_factors"]["tags"]["optimal_count"]
            if tags_analysis["tag_count"] < optimal_count["min"]:
                tags_analysis["optimization_issues"].append("Too few tags")
                tags_analysis["optimization_suggestions"].append(
                    f"Add more tags (recommended: {optimal_count['min']}-{optimal_count['max']})"
                )
            elif tags_analysis["tag_count"] > optimal_count["max"]:
                tags_analysis["optimization_issues"].append("Too many tags")
                tags_analysis["optimization_suggestions"].append(
                    f"Reduce to {optimal_count['max']} most relevant tags"
                )
            
            # Target keyword coverage
            if target_keywords:
                coverage = {}
                tags_lower = [tag.lower() for tag in tags]
                
                for keyword in target_keywords:
                    keyword_lower = keyword.lower()
                    is_covered = any(keyword_lower in tag or tag in keyword_lower for tag in tags_lower)
                    coverage[keyword] = is_covered
                
                tags_analysis["target_keyword_coverage"] = coverage
                
                # Check for missing keyword coverage
                missing_coverage = [kw for kw, covered in coverage.items() if not covered]
                if missing_coverage:
                    tags_analysis["optimization_suggestions"].append(
                        f"Add tags for keywords: {', '.join(missing_coverage[:3])}"
                    )
            
            # Analyze tag types
            if tags:
                tag_types = {
                    "short_tail": len([tag for tag in tags if len(tag.split()) <= 2]),
                    "long_tail": len([tag for tag in tags if len(tag.split()) > 2]),
                    "branded": len([tag for tag in tags if any(brand in tag.lower() for brand in ["brand", "company"])]),
                    "generic": len([tag for tag in tags if tag.lower() in ["video", "content", "youtube"]])
                }
                tags_analysis["tag_types"] = tag_types
                
                if tag_types["generic"] > 2:
                    tags_analysis["optimization_suggestions"].append(
                        "Replace generic tags with more specific, relevant tags"
                    )
            
            # Calculate tags SEO score
            tags_analysis["seo_score"] = self._calculate_tags_seo_score(tags_analysis)
            
            return tags_analysis
            
        except Exception as e:
            logger.error(f"Tags SEO analysis failed: {str(e)}")
            return tags_analysis
    
    async def _analyze_keyword_performance(
        self,
        content_data: Dict[str, Any],
        target_keywords: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Analyze keyword performance and opportunities"""
        
        keyword_analysis = {
            "current_rankings": {},
            "keyword_difficulty": {},
            "search_volume_data": {},
            "trend_analysis": {},
            "opportunity_score": {},
            "suggested_keywords": []
        }
        
        try:
            if not target_keywords:
                return keyword_analysis
            
            # Analyze each target keyword
            for keyword in target_keywords:
                # Get keyword metrics (placeholder - would use real APIs)
                keyword_metrics = await self._get_keyword_metrics(keyword)
                
                keyword_analysis["search_volume_data"][keyword] = keyword_metrics.get("search_volume", 0)
                keyword_analysis["keyword_difficulty"][keyword] = keyword_metrics.get("difficulty", 0.5)
                keyword_analysis["trend_analysis"][keyword] = keyword_metrics.get("trend", "stable")
                
                # Calculate opportunity score
                opportunity = self._calculate_keyword_opportunity_score(keyword_metrics)
                keyword_analysis["opportunity_score"][keyword] = opportunity
            
            # Suggest additional keywords
            title = content_data.get("title", "")
            description = content_data.get("description", "")
            suggested_keywords = await self._suggest_related_keywords(
                title + " " + description, target_keywords
            )
            keyword_analysis["suggested_keywords"] = suggested_keywords
            
            return keyword_analysis
            
        except Exception as e:
            logger.error(f"Keyword performance analysis failed: {str(e)}")
            return keyword_analysis
    
    # Helper methods for SEO analysis
    
    def _calculate_weighted_seo_score(self, element_scores: Dict[str, float]) -> float:
        """Calculate weighted SEO score across elements"""
        weights = {
            "title": 0.25,
            "description": 0.20,
            "tags": 0.15,
            "thumbnail": 0.15,
            "engagement": 0.25
        }
        
        weighted_score = sum(
            element_scores.get(element, 0.5) * weight
            for element, weight in weights.items()
        )
        
        return round(weighted_score, 3)
    
    def _calculate_title_seo_score(self, title_analysis: Dict[str, Any]) -> float:
        """Calculate title SEO score"""
        score = 0.5  # Base score
        
        # Length score
        length = title_analysis["character_count"]
        optimal_range = self.seo_config["optimization_factors"]["title"]["optimal_length"]
        if optimal_range["min"] <= length <= optimal_range["max"]:
            score += 0.2
        
        # Keyword presence score
        keyword_presence = title_analysis.get("keyword_presence", {})
        if keyword_presence:
            keywords_present = sum(1 for data in keyword_presence.values() if data["present"])
            keyword_score = keywords_present / len(keyword_presence)
            score += keyword_score * 0.3
        
        return min(score, 1.0)
    
    def _calculate_description_seo_score(self, description_analysis: Dict[str, Any]) -> float:
        """Calculate description SEO score"""
        score = 0.5  # Base score
        
        # Length score
        length = description_analysis["length"]
        optimal_range = self.seo_config["optimization_factors"]["description"]["optimal_length"]
        if optimal_range["min"] <= length <= optimal_range["max"]:
            score += 0.2
        
        # Readability score
        readability = description_analysis.get("readability_score", 50)
        if readability >= 60:  # Good readability
            score += 0.15
        
        # Keyword density score
        keyword_density = description_analysis.get("keyword_density", {})
        if keyword_density:
            optimal_densities = sum(1 for data in keyword_density.values() if data["optimal"])
            density_score = optimal_densities / len(keyword_density)
            score += density_score * 0.15
        
        return min(score, 1.0)
    
    def _calculate_tags_seo_score(self, tags_analysis: Dict[str, Any]) -> float:
        """Calculate tags SEO score"""
        score = 0.5  # Base score
        
        # Tag count score
        tag_count = tags_analysis["tag_count"]
        optimal_range = self.seo_config["optimization_factors"]["tags"]["optimal_count"]
        if optimal_range["min"] <= tag_count <= optimal_range["max"]:
            score += 0.3
        
        # Keyword coverage score
        coverage = tags_analysis.get("target_keyword_coverage", {})
        if coverage:
            covered_keywords = sum(1 for covered in coverage.values() if covered)
            coverage_score = covered_keywords / len(coverage)
            score += coverage_score * 0.2
        
        return min(score, 1.0)
    
    def _calculate_overall_seo_score(self, analysis_components: Dict[str, Any]) -> float:
        """Calculate overall SEO score"""
        current_seo = analysis_components.get("current_seo", {})
        element_scores = current_seo.get("overall_element_scores", {})
        
        return element_scores.get("weighted_average", 0.5)
    
    def _calculate_keyword_opportunity_score(self, keyword_metrics: Dict[str, Any]) -> float:
        """Calculate keyword opportunity score"""
        search_volume = keyword_metrics.get("search_volume", 0)
        difficulty = keyword_metrics.get("difficulty", 0.5)
        trend = keyword_metrics.get("trend", "stable")
        
        # Normalize search volume (assuming max 100k)
        volume_score = min(search_volume / 100000, 1.0)
        
        # Lower difficulty = higher opportunity
        difficulty_score = 1.0 - difficulty
        
        # Trend score
        trend_score = 0.8 if trend == "rising" else 0.5 if trend == "stable" else 0.2
        
        opportunity_score = (volume_score * 0.4 + difficulty_score * 0.4 + trend_score * 0.2)
        
        return round(opportunity_score, 3)
    
    # Placeholder methods for comprehensive SEO analysis
    # These would be implemented with actual APIs and analysis logic
    
    async def _detect_content_niche(self, content_data: Dict[str, Any]) -> str:
        """Detect content niche from title and description"""
        return "technology"  # Placeholder
    
    async def _analyze_thumbnail_seo(self, thumbnail_url: str) -> Dict[str, Any]:
        """Analyze thumbnail SEO factors"""
        return {"seo_score": 0.7, "factors": ["good_contrast", "readable_text"]}
    
    async def _analyze_competitor_seo(self, keywords: List[str], niche: str) -> Dict[str, Any]:
        """Analyze competitor SEO strategies"""
        return {"comparison": {}, "opportunities": []}
    
    async def _analyze_technical_seo(self, content_data: Dict, deep_analysis: bool) -> Dict[str, Any]:
        """Analyze technical SEO factors"""
        return {"technical_score": 0.8, "issues": []}
    
    async def _analyze_content_optimization(self, content_data: Dict, keywords: List) -> Dict[str, Any]:
        """Analyze content optimization opportunities"""
        return {"optimization_score": 0.6, "suggestions": []}
    
    async def _analyze_seo_performance_metrics(self, content_data: Dict, video_id: str) -> Dict[str, Any]:
        """Analyze SEO performance metrics"""
        return {"ctr": 0.05, "impressions": 10000, "avg_position": 25}
    
    async def _generate_optimization_suggestions(self, current_seo: Dict, keywords: Dict, competitors: Dict) -> Dict[str, Any]:
        """Generate comprehensive optimization suggestions"""
        return {
            "title_suggestions": ["Optimize title with primary keyword"],
            "description_suggestions": ["Add more keywords to description"],
            "tags_suggestions": ["Include long-tail keyword tags"],
            "thumbnail_suggestions": ["Improve thumbnail contrast"]
        }
    
    async def _predict_optimization_impact(self, suggestions: Dict, current_seo: Dict) -> Dict[str, Any]:
        """Predict impact of SEO optimizations"""
        return {"estimated_traffic_increase": "15-25%", "ranking_improvement": "5-10 positions"}
    
    async def _get_keyword_metrics(self, keyword: str) -> Dict[str, Any]:
        """Get keyword metrics from APIs"""
        return {"search_volume": 5000, "difficulty": 0.6, "trend": "rising"}
    
    async def _suggest_related_keywords(self, content_text: str, target_keywords: List[str]) -> List[Dict[str, Any]]:
        """Suggest related keywords"""
        return [{"keyword": "related keyword", "relevance": 0.8, "search_volume": 3000}]
    
    async def _identify_seo_strengths(self, seo_analysis: Dict) -> List[str]:
        return ["Good title optimization", "Appropriate tag usage"]
    
    async def _identify_critical_issues(self, seo_analysis: Dict) -> List[str]:
        return ["Missing meta description", "No target keywords in title"]
    
    async def _identify_quick_wins(self, suggestions: Dict) -> List[Dict[str, Any]]:
        return [{"suggestion": "Add primary keyword to title", "impact": "high", "effort": "low"}]
    
    async def _identify_long_term_opportunities(self, suggestions: Dict, competitors: Dict) -> List[Dict[str, Any]]:
        return [{"opportunity": "Target long-tail keywords", "potential": "high"}]
    
    async def _create_seo_action_plan(self, suggestions: Dict, predictions: Dict) -> Dict[str, Any]:
        return {"immediate_actions": [], "weekly_actions": [], "monthly_actions": []}
    
    async def _generate_monitoring_recommendations(self, keywords: List, video_id: str, channel_id: str) -> List[str]:
        return ["Monitor keyword rankings weekly", "Track CTR improvements"]
    
    def _calculate_analysis_confidence(self, content_data: Dict, keyword_count: int) -> float:
        """Calculate confidence level of SEO analysis"""
        base_confidence = 0.7
        
        # Adjust based on available data
        data_completeness = 0.0
        if content_data.get("title"):
            data_completeness += 0.25
        if content_data.get("description"):
            data_completeness += 0.25
        if content_data.get("tags"):
            data_completeness += 0.25
        if keyword_count > 0:
            data_completeness += 0.25
        
        return min(base_confidence * data_completeness, 1.0)
    
    async def _save_seo_analysis(self, analysis_report: Dict[str, Any]):
        """Save SEO analysis to database"""
        try:
            import aiosqlite
            
            async with aiosqlite.connect(self.db_ext.db_path) as db:
                for keyword in analysis_report.get("target_keywords", []):
                    await db.execute("""
                        INSERT OR REPLACE INTO seo_performance_tracking (
                            id, video_id, channel_id, target_keyword, optimization_score,
                            title_optimization_score, description_optimization_score,
                            tags_optimization_score, optimization_suggestions,
                            last_updated
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        str(uuid.uuid4()),
                        analysis_report.get("video_id"),
                        analysis_report.get("channel_id"),
                        keyword,
                        analysis_report.get("overall_seo_score", 0.5),
                        analysis_report.get("current_seo_analysis", {}).get("overall_element_scores", {}).get("title_score", 0.5),
                        analysis_report.get("current_seo_analysis", {}).get("overall_element_scores", {}).get("description_score", 0.5),
                        analysis_report.get("current_seo_analysis", {}).get("overall_element_scores", {}).get("tags_score", 0.5),
                        json.dumps(analysis_report.get("optimization_suggestions", {})),
                        datetime.utcnow()
                    ))
                await db.commit()
                
        except Exception as e:
            logger.error(f"Failed to save SEO analysis: {str(e)}")
    
    async def _update_seo_tracking(self, video_id: str, channel_id: str, keywords: List, analysis: Dict):
        """Update SEO tracking data"""
        if video_id:
            self.seo_cache[video_id] = analysis
        if keywords:
            for keyword in keywords:
                self.keyword_cache[keyword] = analysis.get("keyword_analysis", {}).get(keyword, {})
    
    async def _load_seo_cache(self):
        """Load existing SEO cache"""
        self.seo_cache = {}
        self.keyword_cache = {}
        self.competitor_seo_data = {}