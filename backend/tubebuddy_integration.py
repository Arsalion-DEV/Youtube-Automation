"""
TubeBuddy API Integration Module
Provides YouTube optimization tools, best upload times, tag suggestions, and channel management
"""

import asyncio
import aiohttp
import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import time
import random
import re
from collections import Counter

logger = logging.getLogger(__name__)

@dataclass
class UploadTimeAnalysis:
    best_times: List[Dict[str, Any]]
    audience_activity: Dict[str, int]
    timezone_recommendations: List[str]
    day_of_week_analysis: Dict[str, float]
    
    def to_dict(self):
        return asdict(self)

@dataclass
class TagSuggestion:
    tag: str
    relevance_score: float
    search_volume: int
    competition: str
    suggested_reason: str
    
    def to_dict(self):
        return asdict(self)

@dataclass
class ThumbnailAnalysis:
    current_score: int
    recommendations: List[str]
    color_analysis: Dict[str, Any]
    text_analysis: Dict[str, Any]
    best_practices: List[str]
    
    def to_dict(self):
        return asdict(self)

@dataclass
class ContentOptimization:
    seo_score: int
    title_optimization: Dict[str, Any]
    description_optimization: Dict[str, Any]
    tag_optimization: Dict[str, Any]
    engagement_predictions: Dict[str, Any]
    
    def to_dict(self):
        return asdict(self)

class TubeBuddyIntegration:
    """Enhanced TubeBuddy-like functionality for YouTube optimization"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.session = None
        self.rate_limit_delay = 1.0
        self.last_request_time = 0
        
        # Optimization databases
        self.high_performing_keywords = [
            "tutorial", "how to", "guide", "tips", "review", "2024", "best",
            "ultimate", "complete", "beginner", "advanced", "step by step",
            "quick", "easy", "amazing", "incredible", "must know"
        ]
        
        self.trending_tags = [
            "viral", "trending", "popular", "new", "latest", "update",
            "news", "reaction", "first time", "challenge", "vs", "comparison"
        ]
        
    async def initialize(self):
        """Initialize the TubeBuddy integration"""
        self.session = aiohttp.ClientSession()
        logger.info("TubeBuddy integration initialized")
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
    
    async def _rate_limit_check(self):
        """Ensure we respect rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
    
    async def get_best_upload_time(self, channel_id: str) -> UploadTimeAnalysis:
        """Analyze and recommend best upload times for the channel"""
        try:
            if not self.session:
                await self.initialize()
            
            await self._rate_limit_check()
            
            # Get channel analytics data
            audience_data = await self._get_audience_analytics(channel_id)
            
            # Analyze optimal upload times
            analysis = await self._analyze_upload_times(audience_data)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error getting best upload time: {str(e)}")
            raise
    
    async def _get_audience_analytics(self, channel_id: str) -> Dict[str, Any]:
        """Get audience analytics for the channel"""
        # Mock audience data (in production, use YouTube Analytics API)
        return {
            "timezone_distribution": {
                "America/New_York": 35,
                "America/Los_Angeles": 25,
                "Europe/London": 20,
                "Asia/Tokyo": 10,
                "Australia/Sydney": 10
            },
            "hourly_activity": {
                str(hour): random.randint(10, 100) for hour in range(24)
            },
            "daily_activity": {
                "Monday": random.randint(60, 90),
                "Tuesday": random.randint(70, 95),
                "Wednesday": random.randint(65, 88),
                "Thursday": random.randint(75, 98),
                "Friday": random.randint(60, 85),
                "Saturday": random.randint(80, 95),
                "Sunday": random.randint(70, 90)
            },
            "device_breakdown": {
                "mobile": 65,
                "desktop": 30,
                "tv": 5
            }
        }
    
    async def _analyze_upload_times(self, audience_data: Dict[str, Any]) -> UploadTimeAnalysis:
        """Analyze optimal upload times based on audience data"""
        hourly_activity = audience_data.get("hourly_activity", {})
        daily_activity = audience_data.get("daily_activity", {})
        timezone_dist = audience_data.get("timezone_distribution", {})
        
        # Find peak hours
        peak_hours = sorted(hourly_activity.items(), key=lambda x: int(x[1]), reverse=True)[:3]
        
        # Generate best upload times
        best_times = []
        for hour, activity in peak_hours:
            for day, day_score in daily_activity.items():
                if day_score > 80:  # High activity days
                    best_times.append({
                        "day": day,
                        "time": f"{hour}:00",
                        "timezone": "EST",  # Primary timezone
                        "expected_reach": int(activity) * day_score // 100,
                        "confidence": "high" if day_score > 90 else "medium"
                    })
        
        # Sort by expected reach
        best_times = sorted(best_times, key=lambda x: x["expected_reach"], reverse=True)[:5]
        
        # Timezone recommendations
        timezone_recs = [
            f"Primary: {max(timezone_dist.items(), key=lambda x: x[1])[0]}",
            "Consider scheduling for multiple timezones",
            "Peak hours: 2-4 PM and 7-9 PM in primary timezone"
        ]
        
        return UploadTimeAnalysis(
            best_times=best_times,
            audience_activity=hourly_activity,
            timezone_recommendations=timezone_recs,
            day_of_week_analysis=daily_activity
        )
    
    async def get_tag_suggestions(self, video_title: str, description: str = "") -> List[TagSuggestion]:
        """Generate optimized tag suggestions for video"""
        try:
            await self._rate_limit_check()
            
            # Analyze title and description for keywords
            content_keywords = self._extract_keywords(video_title + " " + description)
            
            # Generate tag suggestions
            suggestions = await self._generate_tag_suggestions(content_keywords, video_title)
            
            return suggestions[:15]  # Return top 15 suggestions
            
        except Exception as e:
            logger.error(f"Error getting tag suggestions: {str(e)}")
            return []
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Clean and tokenize text
        text = re.sub(r'[^\w\s]', '', text.lower())
        words = text.split()
        
        # Filter out common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'among', 'is', 'are',
            'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can'
        }
        
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Get most frequent keywords
        keyword_freq = Counter(keywords)
        return [word for word, freq in keyword_freq.most_common(10)]
    
    async def _generate_tag_suggestions(self, content_keywords: List[str], title: str) -> List[TagSuggestion]:
        """Generate tag suggestions based on content analysis"""
        suggestions = []
        
        # Add content-based tags
        for keyword in content_keywords:
            suggestions.append(TagSuggestion(
                tag=keyword,
                relevance_score=0.9,
                search_volume=random.randint(1000, 50000),
                competition="medium",
                suggested_reason="Extracted from content"
            ))
        
        # Add high-performing keyword variations
        for keyword in content_keywords[:3]:  # Top 3 keywords
            for hp_keyword in self.high_performing_keywords[:5]:
                combined_tag = f"{keyword} {hp_keyword}"
                suggestions.append(TagSuggestion(
                    tag=combined_tag,
                    relevance_score=0.7,
                    search_volume=random.randint(500, 25000),
                    competition="low",
                    suggested_reason="High-performing keyword combination"
                ))
        
        # Add trending tags if relevant
        for trending in self.trending_tags[:3]:
            if len(suggestions) < 15:
                suggestions.append(TagSuggestion(
                    tag=trending,
                    relevance_score=0.6,
                    search_volume=random.randint(10000, 100000),
                    competition="high",
                    suggested_reason="Currently trending"
                ))
        
        # Add long-tail variations
        if content_keywords:
            main_keyword = content_keywords[0]
            long_tail_variations = [
                f"how to {main_keyword}",
                f"{main_keyword} tutorial",
                f"best {main_keyword}",
                f"{main_keyword} guide",
                f"{main_keyword} tips"
            ]
            
            for variation in long_tail_variations:
                if len(suggestions) < 15:
                    suggestions.append(TagSuggestion(
                        tag=variation,
                        relevance_score=0.8,
                        search_volume=random.randint(2000, 15000),
                        competition="low",
                        suggested_reason="Long-tail keyword variation"
                    ))
        
        # Sort by relevance score
        suggestions.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return suggestions
    
    async def analyze_thumbnail(self, thumbnail_url: str = None, video_title: str = "") -> ThumbnailAnalysis:
        """Analyze thumbnail effectiveness and provide recommendations"""
        try:
            await self._rate_limit_check()
            
            # Mock thumbnail analysis (in production, use image analysis APIs)
            analysis = await self._perform_thumbnail_analysis(thumbnail_url, video_title)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing thumbnail: {str(e)}")
            raise
    
    async def _perform_thumbnail_analysis(self, thumbnail_url: str, video_title: str) -> ThumbnailAnalysis:
        """Perform detailed thumbnail analysis"""
        # Mock analysis (in production, use computer vision APIs)
        current_score = random.randint(60, 95)
        
        recommendations = []
        if current_score < 80:
            recommendations.extend([
                "Use brighter, more contrasting colors",
                "Add clear, readable text overlay",
                "Include human faces for better click-through rates",
                "Ensure thumbnail is clear at small sizes"
            ])
        
        if current_score < 70:
            recommendations.extend([
                "Simplify the composition",
                "Use bold, sans-serif fonts",
                "Increase contrast between elements",
                "Follow the rule of thirds"
            ])
        
        color_analysis = {
            "dominant_colors": ["#FF6B35", "#004E98", "#FFFFFF"],
            "color_harmony": "complementary",
            "readability_score": random.randint(70, 95),
            "brand_consistency": random.randint(60, 90)
        }
        
        text_analysis = {
            "text_present": random.choice([True, False]),
            "text_readability": random.randint(60, 95),
            "font_size_score": random.randint(70, 90),
            "text_positioning": "good" if random.random() > 0.3 else "needs improvement"
        }
        
        best_practices = [
            "Use high contrast colors",
            "Keep text large and readable",
            "Show faces when possible",
            "Test thumbnail at different sizes",
            "Use consistent branding elements",
            "Avoid cluttered compositions",
            "Consider mobile viewing experience"
        ]
        
        return ThumbnailAnalysis(
            current_score=current_score,
            recommendations=recommendations,
            color_analysis=color_analysis,
            text_analysis=text_analysis,
            best_practices=best_practices
        )
    
    async def optimize_content(self, video_data: Dict[str, Any]) -> ContentOptimization:
        """Provide comprehensive content optimization recommendations"""
        try:
            await self._rate_limit_check()
            
            title = video_data.get('title', '')
            description = video_data.get('description', '')
            tags = video_data.get('tags', [])
            
            # Analyze each component
            title_opt = await self._optimize_title(title)
            desc_opt = await self._optimize_description(description)
            tag_opt = await self._optimize_tags(tags, title)
            
            # Calculate overall SEO score
            seo_score = self._calculate_seo_score(title_opt, desc_opt, tag_opt)
            
            # Generate engagement predictions
            engagement_pred = await self._predict_engagement(video_data)
            
            return ContentOptimization(
                seo_score=seo_score,
                title_optimization=title_opt,
                description_optimization=desc_opt,
                tag_optimization=tag_opt,
                engagement_predictions=engagement_pred
            )
            
        except Exception as e:
            logger.error(f"Error optimizing content: {str(e)}")
            raise
    
    async def _optimize_title(self, title: str) -> Dict[str, Any]:
        """Optimize video title"""
        analysis = {
            "current_title": title,
            "length_score": 0,
            "keyword_score": 0,
            "emotional_score": 0,
            "suggestions": [],
            "optimized_versions": []
        }
        
        # Length analysis
        if 30 <= len(title) <= 60:
            analysis["length_score"] = 100
        elif len(title) < 30:
            analysis["length_score"] = 70
            analysis["suggestions"].append("Consider making title longer for better SEO")
        else:
            analysis["length_score"] = 60
            analysis["suggestions"].append("Consider shortening title for better visibility")
        
        # Keyword analysis
        has_power_words = any(word in title.lower() for word in self.high_performing_keywords)
        analysis["keyword_score"] = 90 if has_power_words else 50
        
        if not has_power_words:
            analysis["suggestions"].append("Add power words like 'how to', 'best', or 'ultimate'")
        
        # Emotional analysis
        emotional_words = ["amazing", "incredible", "shocking", "unbelievable", "secret", "revealed"]
        has_emotion = any(word in title.lower() for word in emotional_words)
        analysis["emotional_score"] = 80 if has_emotion else 60
        
        # Generate optimized versions
        if title:
            words = title.split()
            analysis["optimized_versions"] = [
                f"How to {title}",
                f"Ultimate {title} Guide",
                f"Best {title} Tips",
                f"{title} - Complete Tutorial",
                f"Amazing {title} Secrets"
            ]
        
        return analysis
    
    async def _optimize_description(self, description: str) -> Dict[str, Any]:
        """Optimize video description"""
        analysis = {
            "current_description": description,
            "length_score": 0,
            "structure_score": 0,
            "keyword_density": 0,
            "suggestions": [],
            "template": ""
        }
        
        # Length analysis
        if len(description) >= 125:
            analysis["length_score"] = 100
        elif len(description) >= 50:
            analysis["length_score"] = 70
        else:
            analysis["length_score"] = 40
            analysis["suggestions"].append("Add more detail to description (aim for 125+ characters)")
        
        # Structure analysis
        has_links = "http" in description
        has_timestamps = any(re.search(r'\d+:\d+', line) for line in description.split('\n'))
        has_cta = any(word in description.lower() for word in ["subscribe", "like", "comment", "share"])
        
        structure_elements = [has_links, has_timestamps, has_cta]
        analysis["structure_score"] = (sum(structure_elements) / len(structure_elements)) * 100
        
        if not has_cta:
            analysis["suggestions"].append("Add call-to-action (subscribe, like, comment)")
        if not has_links:
            analysis["suggestions"].append("Add relevant links (social media, website)")
        
        # Keyword density
        words = description.lower().split()
        if words:
            word_freq = Counter(words)
            most_common = word_freq.most_common(1)[0] if word_freq else ("", 0)
            analysis["keyword_density"] = (most_common[1] / len(words)) * 100
        
        # Provide template
        analysis["template"] = """
📝 In this video, we cover [main topic]
⏰ Timestamps:
0:00 Introduction
2:30 Main content
8:45 Conclusion

🔗 Useful links:
- Website: [your website]
- Social media: [your social]

💬 Let me know your thoughts in the comments!
👍 Don't forget to like and subscribe for more content!

#hashtag1 #hashtag2 #hashtag3
"""
        
        return analysis
    
    async def _optimize_tags(self, tags: List[str], title: str) -> Dict[str, Any]:
        """Optimize video tags"""
        analysis = {
            "current_tags": tags,
            "count_score": 0,
            "relevance_score": 0,
            "diversity_score": 0,
            "suggestions": [],
            "recommended_tags": []
        }
        
        # Count analysis
        tag_count = len(tags)
        if 8 <= tag_count <= 15:
            analysis["count_score"] = 100
        elif 5 <= tag_count < 8:
            analysis["count_score"] = 80
        elif tag_count > 15:
            analysis["count_score"] = 70
        else:
            analysis["count_score"] = 50
        
        if tag_count < 8:
            analysis["suggestions"].append("Add more tags (aim for 8-15 tags)")
        elif tag_count > 15:
            analysis["suggestions"].append("Consider reducing tags for better focus")
        
        # Relevance analysis (check if tags relate to title)
        title_words = set(title.lower().split())
        relevant_tags = sum(1 for tag in tags if any(word in tag.lower() for word in title_words))
        analysis["relevance_score"] = (relevant_tags / max(len(tags), 1)) * 100
        
        # Diversity analysis (mix of specific and broad tags)
        specific_tags = [tag for tag in tags if len(tag.split()) > 1]
        broad_tags = [tag for tag in tags if len(tag.split()) == 1]
        
        if specific_tags and broad_tags:
            analysis["diversity_score"] = 100
        elif specific_tags or broad_tags:
            analysis["diversity_score"] = 70
        else:
            analysis["diversity_score"] = 50
        
        # Generate recommended tags
        suggested_tags = await self.get_tag_suggestions(title)
        analysis["recommended_tags"] = [tag.tag for tag in suggested_tags[:10]]
        
        return analysis
    
    def _calculate_seo_score(self, title_opt: Dict, desc_opt: Dict, tag_opt: Dict) -> int:
        """Calculate overall SEO score"""
        title_weight = 0.4
        desc_weight = 0.3
        tag_weight = 0.3
        
        title_score = (title_opt["length_score"] + title_opt["keyword_score"] + title_opt["emotional_score"]) / 3
        desc_score = (desc_opt["length_score"] + desc_opt["structure_score"]) / 2
        tag_score = (tag_opt["count_score"] + tag_opt["relevance_score"] + tag_opt["diversity_score"]) / 3
        
        overall_score = (title_score * title_weight) + (desc_score * desc_weight) + (tag_score * tag_weight)
        
        return int(overall_score)
    
    async def _predict_engagement(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict engagement based on optimization factors"""
        title = video_data.get('title', '')
        description = video_data.get('description', '')
        tags = video_data.get('tags', [])
        
        # Mock engagement prediction (in production, use ML models)
        base_score = random.randint(60, 85)
        
        # Boost for good optimization
        if len(title) >= 30:
            base_score += 5
        if len(description) >= 125:
            base_score += 5
        if len(tags) >= 8:
            base_score += 5
        
        predictions = {
            "estimated_ctr": f"{base_score/10:.1f}%",
            "estimated_engagement_rate": f"{(base_score-20)/10:.1f}%",
            "predicted_reach": f"{base_score * 100}-{base_score * 150}",
            "confidence_level": "high" if base_score > 80 else "medium",
            "factors": [
                "Title optimization",
                "Description completeness",
                "Tag relevance",
                "Content quality indicators"
            ]
        }
        
        return predictions
    
    async def get_channel_health_score(self, channel_id: str) -> Dict[str, Any]:
        """Get overall channel health and optimization score"""
        try:
            await self._rate_limit_check()
            
            # Mock channel health analysis
            health_data = await self._analyze_channel_health(channel_id)
            
            return health_data
            
        except Exception as e:
            logger.error(f"Error getting channel health score: {str(e)}")
            return {}
    
    async def _analyze_channel_health(self, channel_id: str) -> Dict[str, Any]:
        """Analyze overall channel health"""
        # Mock health analysis
        scores = {
            "content_optimization": random.randint(60, 95),
            "upload_consistency": random.randint(70, 90),
            "audience_engagement": random.randint(65, 88),
            "seo_optimization": random.randint(55, 85),
            "thumbnail_quality": random.randint(70, 92),
            "metadata_completeness": random.randint(60, 90)
        }
        
        overall_score = sum(scores.values()) / len(scores)
        
        # Generate recommendations based on scores
        recommendations = []
        for category, score in scores.items():
            if score < 70:
                recommendations.append(f"Improve {category.replace('_', ' ')}")
        
        return {
            "overall_score": int(overall_score),
            "category_scores": scores,
            "grade": self._get_grade(overall_score),
            "recommendations": recommendations,
            "strengths": [cat for cat, score in scores.items() if score >= 85],
            "improvement_priority": sorted(scores.items(), key=lambda x: x[1])[:3]
        }
    
    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return "A+"
        elif score >= 85:
            return "A"
        elif score >= 80:
            return "B+"
        elif score >= 75:
            return "B"
        elif score >= 70:
            return "C+"
        elif score >= 65:
            return "C"
        else:
            return "D"
    
    async def bulk_optimize_videos(self, video_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize multiple videos in bulk"""
        try:
            optimized_videos = []
            
            for video_data in video_list:
                video_id = video_data.get('id', '')
                optimization = await self.optimize_content(video_data)
                
                optimized_videos.append({
                    "video_id": video_id,
                    "original_data": video_data,
                    "optimization": optimization.to_dict(),
                    "priority": "high" if optimization.seo_score < 70 else "medium"
                })
                
                # Rate limiting for bulk operations
                await asyncio.sleep(0.5)
            
            return optimized_videos
            
        except Exception as e:
            logger.error(f"Error in bulk optimization: {str(e)}")
            return []

# Helper functions for TubeBuddy integration
async def initialize_tubebuddy(api_key: str = None) -> TubeBuddyIntegration:
    """Initialize TubeBuddy integration"""
    tb = TubeBuddyIntegration(api_key)
    await tb.initialize()
    return tb