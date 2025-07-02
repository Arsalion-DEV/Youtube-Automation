"""
Social Blade API Integration Module
Provides comprehensive YouTube channel statistics, growth tracking, and analytics
"""

import asyncio
import aiohttp
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import time
import random

logger = logging.getLogger(__name__)

@dataclass
class ChannelStats:
    channel_id: str
    channel_name: str
    subscriber_count: int
    total_views: int
    video_count: int
    avg_views_per_video: int
    subscriber_rank: int
    view_rank: int
    country_rank: int
    category_rank: int
    grade: str
    
    def to_dict(self):
        return asdict(self)

@dataclass
class GrowthMetrics:
    daily_subscribers: int
    daily_views: int
    weekly_growth: float
    monthly_growth: float
    projected_30_day: int
    growth_trend: str
    
    def to_dict(self):
        return asdict(self)

@dataclass
class SocialBladeReport:
    channel_stats: ChannelStats
    growth_metrics: GrowthMetrics
    historical_data: List[Dict[str, Any]]
    predictions: Dict[str, Any]
    recommendations: List[str]
    
    def to_dict(self):
        return {
            'channel_stats': self.channel_stats.to_dict(),
            'growth_metrics': self.growth_metrics.to_dict(),
            'historical_data': self.historical_data,
            'predictions': self.predictions,
            'recommendations': self.recommendations
        }

class SocialBladeIntegration:
    """Enhanced Social Blade-like functionality with comprehensive analytics"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.socialblade_url = "https://api.socialblade.com"
        self.session = None
        self.rate_limit_delay = 1.5
        self.last_request_time = 0
        
    async def initialize(self):
        """Initialize the Social Blade integration"""
        self.session = aiohttp.ClientSession()
        logger.info("Social Blade integration initialized")
    
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
    
    async def get_channel_stats(self, channel_id: str) -> ChannelStats:
        """Get comprehensive channel statistics"""
        try:
            if not self.session:
                await self.initialize()
            
            await self._rate_limit_check()
            
            # Get channel data from YouTube API
            channel_data = await self._get_youtube_channel_data(channel_id)
            
            if not channel_data:
                raise ValueError(f"Channel {channel_id} not found")
            
            # Calculate additional metrics
            stats = await self._calculate_channel_stats(channel_data)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting channel stats: {str(e)}")
            raise
    
    async def _get_youtube_channel_data(self, channel_id: str) -> Dict[str, Any]:
        """Get channel data from YouTube API"""
        if not self.api_key:
            # Return mock data for demo
            return self._generate_mock_channel_data(channel_id)
        
        url = f"{self.base_url}/channels"
        params = {
            'part': 'snippet,statistics,brandingSettings',
            'id': channel_id,
            'key': self.api_key
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                if data['items']:
                    return data['items'][0]
            return {}
    
    def _generate_mock_channel_data(self, channel_id: str) -> Dict[str, Any]:
        """Generate mock channel data for demo purposes"""
        return {
            'snippet': {
                'title': f'Channel {channel_id}',
                'description': 'Sample channel description',
                'publishedAt': '2020-01-01T00:00:00Z',
                'country': 'US'
            },
            'statistics': {
                'subscriberCount': str(random.randint(10000, 1000000)),
                'viewCount': str(random.randint(1000000, 100000000)),
                'videoCount': str(random.randint(100, 2000))
            }
        }
    
    async def _calculate_channel_stats(self, channel_data: Dict[str, Any]) -> ChannelStats:
        """Calculate comprehensive channel statistics"""
        snippet = channel_data.get('snippet', {})
        stats = channel_data.get('statistics', {})
        
        subscriber_count = int(stats.get('subscriberCount', 0))
        total_views = int(stats.get('viewCount', 0))
        video_count = int(stats.get('videoCount', 0))
        
        avg_views = total_views // video_count if video_count > 0 else 0
        
        # Calculate ranks (mock data for demo)
        subscriber_rank = await self._calculate_rank(subscriber_count, 'subscribers')
        view_rank = await self._calculate_rank(total_views, 'views')
        
        # Calculate grade based on performance metrics
        grade = self._calculate_grade(subscriber_count, avg_views, video_count)
        
        return ChannelStats(
            channel_id=channel_data.get('id', ''),
            channel_name=snippet.get('title', ''),
            subscriber_count=subscriber_count,
            total_views=total_views,
            video_count=video_count,
            avg_views_per_video=avg_views,
            subscriber_rank=subscriber_rank,
            view_rank=view_rank,
            country_rank=random.randint(1, 10000),
            category_rank=random.randint(1, 1000),
            grade=grade
        )
    
    async def _calculate_rank(self, value: int, metric_type: str) -> int:
        """Calculate rank based on value and metric type"""
        # Mock ranking calculation
        if metric_type == 'subscribers':
            if value > 1000000:
                return random.randint(1, 1000)
            elif value > 100000:
                return random.randint(1000, 10000)
            else:
                return random.randint(10000, 100000)
        else:  # views
            if value > 100000000:
                return random.randint(1, 500)
            elif value > 10000000:
                return random.randint(500, 5000)
            else:
                return random.randint(5000, 50000)
    
    def _calculate_grade(self, subscribers: int, avg_views: int, video_count: int) -> str:
        """Calculate channel grade based on performance"""
        score = 0
        
        # Subscriber score (0-40 points)
        if subscribers > 1000000:
            score += 40
        elif subscribers > 100000:
            score += 30
        elif subscribers > 10000:
            score += 20
        elif subscribers > 1000:
            score += 10
        
        # Average views score (0-40 points)
        view_ratio = avg_views / subscribers if subscribers > 0 else 0
        if view_ratio > 0.1:  # 10% view rate
            score += 40
        elif view_ratio > 0.05:  # 5% view rate
            score += 30
        elif view_ratio > 0.02:  # 2% view rate
            score += 20
        elif view_ratio > 0.01:  # 1% view rate
            score += 10
        
        # Content volume score (0-20 points)
        if video_count > 500:
            score += 20
        elif video_count > 100:
            score += 15
        elif video_count > 50:
            score += 10
        elif video_count > 10:
            score += 5
        
        # Convert score to grade
        if score >= 80:
            return 'A+'
        elif score >= 70:
            return 'A'
        elif score >= 60:
            return 'B+'
        elif score >= 50:
            return 'B'
        elif score >= 40:
            return 'C+'
        elif score >= 30:
            return 'C'
        else:
            return 'D'
    
    async def get_growth_metrics(self, channel_id: str) -> GrowthMetrics:
        """Get detailed growth metrics for channel"""
        try:
            await self._rate_limit_check()
            
            # Get historical data (mock for demo)
            historical_data = await self._get_historical_data(channel_id)
            
            # Calculate growth metrics
            metrics = self._calculate_growth_metrics(historical_data)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting growth metrics: {str(e)}")
            raise
    
    async def _get_historical_data(self, channel_id: str) -> List[Dict[str, Any]]:
        """Get historical channel data"""
        # Mock historical data for demo
        historical_data = []
        base_date = datetime.now() - timedelta(days=30)
        
        for i in range(30):
            date = base_date + timedelta(days=i)
            historical_data.append({
                'date': date.isoformat(),
                'subscribers': 100000 + (i * random.randint(50, 500)),
                'views': 1000000 + (i * random.randint(5000, 50000)),
                'videos': 100 + (i // 3)  # New video every 3 days
            })
        
        return historical_data
    
    def _calculate_growth_metrics(self, historical_data: List[Dict[str, Any]]) -> GrowthMetrics:
        """Calculate growth metrics from historical data"""
        if len(historical_data) < 2:
            return GrowthMetrics(0, 0, 0.0, 0.0, 0, "stable")
        
        latest = historical_data[-1]
        previous = historical_data[-2]
        week_ago = historical_data[-8] if len(historical_data) >= 8 else historical_data[0]
        month_ago = historical_data[0]
        
        # Daily growth
        daily_subs = latest['subscribers'] - previous['subscribers']
        daily_views = latest['views'] - previous['views']
        
        # Weekly growth
        weekly_subs_growth = ((latest['subscribers'] - week_ago['subscribers']) / week_ago['subscribers']) * 100
        
        # Monthly growth
        monthly_subs_growth = ((latest['subscribers'] - month_ago['subscribers']) / month_ago['subscribers']) * 100
        
        # Projected 30-day growth
        avg_daily_growth = daily_subs
        projected_30_day = latest['subscribers'] + (avg_daily_growth * 30)
        
        # Growth trend
        if daily_subs > 0:
            trend = "growing"
        elif daily_subs < 0:
            trend = "declining"
        else:
            trend = "stable"
        
        return GrowthMetrics(
            daily_subscribers=daily_subs,
            daily_views=daily_views,
            weekly_growth=round(weekly_subs_growth, 2),
            monthly_growth=round(monthly_subs_growth, 2),
            projected_30_day=projected_30_day,
            growth_trend=trend
        )
    
    async def get_trending_content(self, niche: str, region: str = "US") -> List[Dict[str, Any]]:
        """Get trending content in a specific niche"""
        try:
            await self._rate_limit_check()
            
            # Generate trending content based on niche
            trending_content = await self._generate_trending_content(niche, region)
            
            return trending_content
            
        except Exception as e:
            logger.error(f"Error getting trending content: {str(e)}")
            return []
    
    async def _generate_trending_content(self, niche: str, region: str) -> List[Dict[str, Any]]:
        """Generate trending content for niche"""
        content_types = {
            "tech": [
                "Latest smartphone reviews",
                "AI and machine learning tutorials",
                "Coding bootcamp videos",
                "Tech news and updates",
                "Product unboxing videos"
            ],
            "gaming": [
                "New game releases",
                "Gaming tutorials and guides",
                "Live streaming highlights",
                "Game reviews and ratings",
                "Esports tournament coverage"
            ],
            "lifestyle": [
                "Morning routine videos",
                "Fitness and workout content",
                "Cooking and recipe videos",
                "Home organization tips",
                "Travel vlogs and guides"
            ],
            "education": [
                "Online course reviews",
                "Study tips and techniques",
                "Career advice videos",
                "Skill development tutorials",
                "Educational documentary content"
            ]
        }
        
        niche_content = content_types.get(niche, content_types["tech"])
        
        trending_list = []
        for i, content in enumerate(niche_content):
            trending_list.append({
                "rank": i + 1,
                "title": content,
                "engagement_score": random.randint(70, 100),
                "view_velocity": f"+{random.randint(10, 50)}% in 24h",
                "creator_count": random.randint(50, 500),
                "avg_views": random.randint(10000, 1000000),
                "trend_duration": f"{random.randint(3, 14)} days",
                "recommendation": self._get_content_recommendation(content)
            })
        
        return trending_list
    
    def _get_content_recommendation(self, content: str) -> str:
        """Get recommendation for content type"""
        recommendations = {
            "reviews": "Focus on detailed analysis and honest opinions",
            "tutorials": "Break down complex topics into simple steps",
            "unboxing": "Show clear visuals and first impressions",
            "news": "Be timely and provide unique perspective",
            "vlogs": "Share personal stories and authentic moments"
        }
        
        for key, recommendation in recommendations.items():
            if key in content.lower():
                return recommendation
        
        return "Create engaging content that provides value to your audience"
    
    async def get_competitive_analysis(self, channel_id: str, competitors: List[str]) -> Dict[str, Any]:
        """Perform competitive analysis against other channels"""
        try:
            await self._rate_limit_check()
            
            # Get stats for main channel
            main_channel_stats = await self.get_channel_stats(channel_id)
            
            # Get stats for competitors
            competitor_stats = []
            for competitor in competitors:
                try:
                    stats = await self.get_channel_stats(competitor)
                    competitor_stats.append(stats)
                except Exception as e:
                    logger.warning(f"Could not get stats for competitor {competitor}: {str(e)}")
            
            # Perform comparison analysis
            analysis = self._analyze_competition(main_channel_stats, competitor_stats)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error performing competitive analysis: {str(e)}")
            return {}
    
    def _analyze_competition(self, main_channel: ChannelStats, competitors: List[ChannelStats]) -> Dict[str, Any]:
        """Analyze channel performance against competitors"""
        if not competitors:
            return {"error": "No competitor data available"}
        
        # Calculate averages for competitors
        avg_subscribers = sum(c.subscriber_count for c in competitors) / len(competitors)
        avg_views = sum(c.total_views for c in competitors) / len(competitors)
        avg_videos = sum(c.video_count for c in competitors) / len(competitors)
        avg_views_per_video = sum(c.avg_views_per_video for c in competitors) / len(competitors)
        
        # Performance comparison
        analysis = {
            "performance_comparison": {
                "subscribers": {
                    "your_channel": main_channel.subscriber_count,
                    "competitor_average": int(avg_subscribers),
                    "performance": "above" if main_channel.subscriber_count > avg_subscribers else "below",
                    "difference": abs(main_channel.subscriber_count - avg_subscribers)
                },
                "total_views": {
                    "your_channel": main_channel.total_views,
                    "competitor_average": int(avg_views),
                    "performance": "above" if main_channel.total_views > avg_views else "below",
                    "difference": abs(main_channel.total_views - avg_views)
                },
                "avg_views_per_video": {
                    "your_channel": main_channel.avg_views_per_video,
                    "competitor_average": int(avg_views_per_video),
                    "performance": "above" if main_channel.avg_views_per_video > avg_views_per_video else "below",
                    "difference": abs(main_channel.avg_views_per_video - avg_views_per_video)
                }
            },
            "ranking": {
                "subscriber_rank": sorted([c.subscriber_count for c in competitors] + [main_channel.subscriber_count], reverse=True).index(main_channel.subscriber_count) + 1,
                "view_rank": sorted([c.total_views for c in competitors] + [main_channel.total_views], reverse=True).index(main_channel.total_views) + 1
            },
            "opportunities": self._identify_opportunities(main_channel, competitors),
            "strengths": self._identify_strengths(main_channel, competitors),
            "recommendations": self._get_competitive_recommendations(main_channel, competitors)
        }
        
        return analysis
    
    def _identify_opportunities(self, main_channel: ChannelStats, competitors: List[ChannelStats]) -> List[str]:
        """Identify growth opportunities"""
        opportunities = []
        
        avg_videos = sum(c.video_count for c in competitors) / len(competitors)
        if main_channel.video_count < avg_videos:
            opportunities.append("Increase content production frequency")
        
        avg_views_per_video = sum(c.avg_views_per_video for c in competitors) / len(competitors)
        if main_channel.avg_views_per_video < avg_views_per_video:
            opportunities.append("Improve video optimization and promotion")
        
        best_competitor = max(competitors, key=lambda x: x.subscriber_count)
        if main_channel.subscriber_count < best_competitor.subscriber_count * 0.5:
            opportunities.append("Significant growth potential in subscriber acquisition")
        
        return opportunities
    
    def _identify_strengths(self, main_channel: ChannelStats, competitors: List[ChannelStats]) -> List[str]:
        """Identify channel strengths"""
        strengths = []
        
        avg_subscribers = sum(c.subscriber_count for c in competitors) / len(competitors)
        if main_channel.subscriber_count > avg_subscribers:
            strengths.append("Above-average subscriber base")
        
        avg_views_per_video = sum(c.avg_views_per_video for c in competitors) / len(competitors)
        if main_channel.avg_views_per_video > avg_views_per_video:
            strengths.append("Strong video performance and engagement")
        
        if main_channel.grade in ['A+', 'A']:
            strengths.append("Excellent overall channel performance")
        
        return strengths
    
    def _get_competitive_recommendations(self, main_channel: ChannelStats, competitors: List[ChannelStats]) -> List[str]:
        """Get recommendations based on competitive analysis"""
        recommendations = []
        
        best_competitor = max(competitors, key=lambda x: x.subscriber_count)
        
        if main_channel.video_count < best_competitor.video_count:
            recommendations.append("Increase upload frequency to match top competitors")
        
        if main_channel.avg_views_per_video < best_competitor.avg_views_per_video:
            recommendations.append("Analyze top competitor content strategies and apply insights")
        
        recommendations.extend([
            "Monitor competitor posting schedules and content themes",
            "Identify content gaps that competitors aren't addressing",
            "Collaborate with similar-sized channels in your niche",
            "Study successful competitor video formats and adapt to your style"
        ])
        
        return recommendations
    
    async def generate_full_report(self, channel_id: str) -> SocialBladeReport:
        """Generate comprehensive Social Blade-style report"""
        try:
            # Get all data components
            channel_stats = await self.get_channel_stats(channel_id)
            growth_metrics = await self.get_growth_metrics(channel_id)
            historical_data = await self._get_historical_data(channel_id)
            
            # Generate predictions
            predictions = self._generate_predictions(growth_metrics, historical_data)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(channel_stats, growth_metrics)
            
            return SocialBladeReport(
                channel_stats=channel_stats,
                growth_metrics=growth_metrics,
                historical_data=historical_data,
                predictions=predictions,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error generating full report: {str(e)}")
            raise
    
    def _generate_predictions(self, growth_metrics: GrowthMetrics, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate growth predictions"""
        current_subs = historical_data[-1]['subscribers'] if historical_data else 0
        
        return {
            "30_day_projection": growth_metrics.projected_30_day,
            "90_day_projection": current_subs + (growth_metrics.daily_subscribers * 90),
            "1_year_projection": current_subs + (growth_metrics.daily_subscribers * 365),
            "milestone_predictions": {
                "next_10k": self._calculate_milestone_date(current_subs, growth_metrics.daily_subscribers, 10000),
                "next_100k": self._calculate_milestone_date(current_subs, growth_metrics.daily_subscribers, 100000),
                "next_1m": self._calculate_milestone_date(current_subs, growth_metrics.daily_subscribers, 1000000)
            }
        }
    
    def _calculate_milestone_date(self, current: int, daily_growth: int, milestone: int) -> str:
        """Calculate when a milestone will be reached"""
        if daily_growth <= 0:
            return "Not projected with current growth rate"
        
        remaining = milestone - current
        if remaining <= 0:
            return "Milestone already achieved"
        
        days_to_milestone = remaining / daily_growth
        target_date = datetime.now() + timedelta(days=days_to_milestone)
        
        return target_date.strftime("%Y-%m-%d")
    
    def _generate_recommendations(self, channel_stats: ChannelStats, growth_metrics: GrowthMetrics) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if growth_metrics.daily_subscribers < 10:
            recommendations.append("Focus on subscriber acquisition strategies")
        
        if channel_stats.avg_views_per_video < channel_stats.subscriber_count * 0.1:
            recommendations.append("Improve video thumbnails and titles for better click-through rates")
        
        if growth_metrics.growth_trend == "declining":
            recommendations.append("Analyze recent content performance and adjust strategy")
        
        if channel_stats.grade in ['C', 'D']:
            recommendations.append("Consider content audit and optimization")
        
        recommendations.extend([
            "Maintain consistent upload schedule",
            "Engage with your audience through comments and community posts",
            "Collaborate with other creators in your niche",
            "Optimize video SEO with relevant keywords and tags"
        ])
        
        return recommendations

# Helper functions for Social Blade integration
async def initialize_socialblade(api_key: str = None) -> SocialBladeIntegration:
    """Initialize Social Blade integration"""
    sb = SocialBladeIntegration(api_key)
    await sb.initialize()
    return sb