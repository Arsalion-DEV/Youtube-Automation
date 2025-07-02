"""
Community Scheduler
Automated post scheduling with optimal timing and audience analysis
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from enum import Enum
import pytz

logger = logging.getLogger(__name__)

class PostType(Enum):
    """Types of community posts"""
    POLL = "poll"
    IMAGE = "image"
    TEXT = "text"
    VIDEO = "video"
    UPDATE = "update"
    QUESTION = "question"
    ANNOUNCEMENT = "announcement"
    BEHIND_SCENES = "behind_scenes"

@dataclass
class ScheduledPost:
    """Scheduled community post"""
    id: str
    channel_id: str
    post_type: PostType
    content: str
    scheduled_time: datetime
    optimal_time: bool = False
    audience_score: float = 0.0
    hashtags: List[str] = field(default_factory=list)
    media_path: Optional[str] = None
    poll_options: List[str] = field(default_factory=list)
    target_demographics: List[str] = field(default_factory=list)
    expected_engagement: float = 0.0
    status: str = "scheduled"  # scheduled, posted, failed
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class AudienceInsight:
    """Audience behavior insights"""
    channel_id: str
    timezone: str
    peak_hours: List[int]  # Hours of day (0-23)
    peak_days: List[str]  # Days of week
    demographic_data: Dict[str, Any]
    engagement_patterns: Dict[str, Any]
    optimal_posting_frequency: float
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class PostTemplate:
    """Community post template"""
    name: str
    post_type: PostType
    content_template: str
    variables: List[str]
    optimal_times: List[str]  # Time ranges like "18:00-20:00"
    target_demographics: List[str]
    engagement_multiplier: float = 1.0
    seasonal_adjust: bool = False

class CommunityScheduler:
    """Advanced community post scheduling with optimal timing"""
    
    def __init__(self):
        self.module_name = "community_scheduler"
        
        # Scheduled posts storage
        self.scheduled_posts: Dict[str, ScheduledPost] = {}
        self.audience_insights: Dict[str, AudienceInsight] = {}
        
        # Post templates
        self.post_templates: Dict[str, PostTemplate] = {}
        self._setup_default_templates()
        
        # Scheduling settings
        self.scheduling_settings = {
            "auto_optimize_timing": True,
            "respect_timezone": True,
            "avoid_overposting": True,
            "max_daily_posts": 3,
            "min_post_interval": 4,  # hours
            "engagement_threshold": 0.05,  # 5% engagement rate target
            "seasonal_adjustment": True
        }
        
        # Global optimal times (general guidelines)
        self.global_optimal_times = {
            "weekday": {
                "morning": (8, 10),    # 8 AM - 10 AM
                "lunch": (12, 14),     # 12 PM - 2 PM
                "evening": (18, 21)    # 6 PM - 9 PM
            },
            "weekend": {
                "morning": (9, 12),    # 9 AM - 12 PM
                "afternoon": (14, 17), # 2 PM - 5 PM
                "evening": (19, 22)    # 7 PM - 10 PM
            }
        }
        
        # Audience demographic patterns
        self.demographic_patterns = {
            "gaming": {
                "primary_age": "18-34",
                "peak_days": ["Friday", "Saturday", "Sunday"],
                "peak_hours": [16, 17, 18, 19, 20, 21, 22],
                "timezone_distribution": {"PST": 0.4, "EST": 0.3, "GMT": 0.2, "Other": 0.1}
            },
            "tech": {
                "primary_age": "25-44",
                "peak_days": ["Tuesday", "Wednesday", "Thursday"],
                "peak_hours": [9, 10, 11, 14, 15, 16, 17, 18],
                "timezone_distribution": {"PST": 0.35, "EST": 0.25, "GMT": 0.25, "Other": 0.15}
            },
            "education": {
                "primary_age": "18-54",
                "peak_days": ["Monday", "Tuesday", "Wednesday", "Thursday"],
                "peak_hours": [10, 11, 14, 15, 16, 17, 19, 20],
                "timezone_distribution": {"EST": 0.3, "PST": 0.25, "GMT": 0.2, "Other": 0.25}
            },
            "lifestyle": {
                "primary_age": "25-54",
                "peak_days": ["Wednesday", "Thursday", "Friday", "Saturday"],
                "peak_hours": [11, 12, 13, 17, 18, 19, 20, 21],
                "timezone_distribution": {"EST": 0.35, "PST": 0.25, "GMT": 0.15, "Other": 0.25}
            }
        }
        
        # Seasonal adjustments
        self.seasonal_adjustments = {
            "spring": {"engagement_boost": 1.1, "optimal_shift": 0},
            "summer": {"engagement_boost": 0.9, "optimal_shift": 1},  # Post 1 hour later
            "fall": {"engagement_boost": 1.2, "optimal_shift": -1},   # Post 1 hour earlier
            "winter": {"engagement_boost": 1.15, "optimal_shift": 0}
        }
    
    def _setup_default_templates(self):
        """Setup default post templates"""
        
        # Weekly updates
        self.post_templates["weekly_update"] = PostTemplate(
            name="Weekly Update",
            post_type=PostType.UPDATE,
            content_template="Hey everyone! 🌟 This week has been amazing! {weekly_highlights} What's been the highlight of your week? Drop it in the comments! {hashtags}",
            variables=["weekly_highlights", "hashtags"],
            optimal_times=["Sunday 18:00-20:00"],
            target_demographics=["all"],
            engagement_multiplier=1.2
        )
        
        # Behind the scenes
        self.post_templates["behind_scenes"] = PostTemplate(
            name="Behind the Scenes",
            post_type=PostType.BEHIND_SCENES,
            content_template="Taking you behind the scenes! 🎬 {behind_scenes_content} Love showing you how the magic happens! What would you like to see more of? {hashtags}",
            variables=["behind_scenes_content", "hashtags"],
            optimal_times=["Wednesday 16:00-18:00", "Saturday 14:00-16:00"],
            target_demographics=["engaged_followers"],
            engagement_multiplier=1.4
        )
        
        # Q&A prompts
        self.post_templates["qa_prompt"] = PostTemplate(
            name="Q&A Prompt",
            post_type=PostType.QUESTION,
            content_template="Q&A Time! 🤔 {question_prompt} I'll answer the best questions in my next video! {hashtags}",
            variables=["question_prompt", "hashtags"],
            optimal_times=["Tuesday 19:00-21:00", "Thursday 19:00-21:00"],
            target_demographics=["active_commenters"],
            engagement_multiplier=1.3
        )
        
        # Polls
        self.post_templates["content_poll"] = PostTemplate(
            name="Content Poll",
            post_type=PostType.POLL,
            content_template="Help me decide! 🗳️ {poll_question} Your vote matters! {hashtags}",
            variables=["poll_question", "hashtags"],
            optimal_times=["Monday 17:00-19:00", "Friday 16:00-18:00"],
            target_demographics=["all"],
            engagement_multiplier=1.5
        )
        
        # Milestone celebrations
        self.post_templates["milestone"] = PostTemplate(
            name="Milestone Celebration",
            post_type=PostType.ANNOUNCEMENT,
            content_template="🎉 WE DID IT! {milestone_achievement} Thank you all for being part of this incredible journey! {celebration_message} {hashtags}",
            variables=["milestone_achievement", "celebration_message", "hashtags"],
            optimal_times=["Any peak time"],
            target_demographics=["all"],
            engagement_multiplier=2.0
        )
    
    async def analyze_audience_patterns(self, channel_id: str, analytics_data: Dict[str, Any]) -> AudienceInsight:
        """Analyze audience behavior patterns"""
        try:
            # Extract timezone information
            timezone_data = analytics_data.get("demographics", {}).get("geography", {})
            primary_timezone = self._determine_primary_timezone(timezone_data)
            
            # Analyze engagement patterns
            engagement_data = analytics_data.get("engagement", {})
            peak_hours = self._calculate_peak_hours(engagement_data)
            peak_days = self._calculate_peak_days(engagement_data)
            
            # Get demographic insights
            demographic_data = analytics_data.get("demographics", {})
            
            # Calculate optimal posting frequency
            optimal_frequency = self._calculate_optimal_frequency(engagement_data)
            
            insight = AudienceInsight(
                channel_id=channel_id,
                timezone=primary_timezone,
                peak_hours=peak_hours,
                peak_days=peak_days,
                demographic_data=demographic_data,
                engagement_patterns=engagement_data,
                optimal_posting_frequency=optimal_frequency
            )
            
            self.audience_insights[channel_id] = insight
            logger.info(f"Updated audience insights for channel {channel_id}")
            
            return insight
            
        except Exception as e:
            logger.error(f"Error analyzing audience patterns: {str(e)}")
            # Return default insight
            return AudienceInsight(
                channel_id=channel_id,
                timezone="UTC",
                peak_hours=[18, 19, 20],
                peak_days=["Friday", "Saturday", "Sunday"],
                demographic_data={},
                engagement_patterns={},
                optimal_posting_frequency=2.0
            )
    
    def _determine_primary_timezone(self, timezone_data: Dict[str, Any]) -> str:
        """Determine primary timezone of audience"""
        try:
            if not timezone_data:
                return "UTC"
            
            # Find timezone with highest percentage
            max_percentage = 0
            primary_timezone = "UTC"
            
            for timezone, percentage in timezone_data.items():
                if percentage > max_percentage:
                    max_percentage = percentage
                    primary_timezone = timezone
            
            return primary_timezone
            
        except Exception:
            return "UTC"
    
    def _calculate_peak_hours(self, engagement_data: Dict[str, Any]) -> List[int]:
        """Calculate peak engagement hours"""
        try:
            hourly_data = engagement_data.get("hourly", {})
            if not hourly_data:
                return [18, 19, 20]  # Default evening hours
            
            # Sort hours by engagement and take top 3-5
            sorted_hours = sorted(hourly_data.items(), key=lambda x: x[1], reverse=True)
            peak_hours = [int(hour) for hour, _ in sorted_hours[:5]]
            
            return sorted(peak_hours)
            
        except Exception:
            return [18, 19, 20]
    
    def _calculate_peak_days(self, engagement_data: Dict[str, Any]) -> List[str]:
        """Calculate peak engagement days"""
        try:
            daily_data = engagement_data.get("daily", {})
            if not daily_data:
                return ["Friday", "Saturday", "Sunday"]
            
            # Sort days by engagement
            sorted_days = sorted(daily_data.items(), key=lambda x: x[1], reverse=True)
            peak_days = [day for day, _ in sorted_days[:3]]
            
            return peak_days
            
        except Exception:
            return ["Friday", "Saturday", "Sunday"]
    
    def _calculate_optimal_frequency(self, engagement_data: Dict[str, Any]) -> float:
        """Calculate optimal posting frequency per week"""
        try:
            avg_engagement = engagement_data.get("average_engagement_rate", 0.05)
            
            # More engagement = can post more frequently
            if avg_engagement > 0.1:  # 10%+
                return 5.0  # 5 posts per week
            elif avg_engagement > 0.07:  # 7%+
                return 4.0  # 4 posts per week
            elif avg_engagement > 0.05:  # 5%+
                return 3.0  # 3 posts per week
            else:
                return 2.0  # 2 posts per week
                
        except Exception:
            return 2.0
    
    async def schedule_post(
        self,
        channel_id: str,
        post_type: PostType,
        content: str,
        scheduled_time: Optional[datetime] = None,
        auto_optimize: bool = True,
        **kwargs
    ) -> str:
        """Schedule a community post"""
        try:
            post_id = f"post_{channel_id}_{datetime.utcnow().timestamp()}"
            
            # Auto-optimize timing if requested
            if auto_optimize and scheduled_time is None:
                optimal_time = await self._find_optimal_time(channel_id, post_type)
                scheduled_time = optimal_time
                optimal_time_flag = True
            elif scheduled_time is None:
                # Default to next good time
                scheduled_time = datetime.utcnow() + timedelta(hours=1)
                optimal_time_flag = False
            else:
                optimal_time_flag = False
            
            # Calculate audience score
            audience_score = await self._calculate_audience_score(channel_id, scheduled_time, post_type)
            
            # Calculate expected engagement
            expected_engagement = await self._predict_engagement(channel_id, post_type, scheduled_time, content)
            
            # Create scheduled post
            scheduled_post = ScheduledPost(
                id=post_id,
                channel_id=channel_id,
                post_type=post_type,
                content=content,
                scheduled_time=scheduled_time,
                optimal_time=optimal_time_flag,
                audience_score=audience_score,
                hashtags=kwargs.get("hashtags", []),
                media_path=kwargs.get("media_path"),
                poll_options=kwargs.get("poll_options", []),
                target_demographics=kwargs.get("target_demographics", []),
                expected_engagement=expected_engagement
            )
            
            self.scheduled_posts[post_id] = scheduled_post
            
            logger.info(f"Scheduled post {post_id} for {scheduled_time}")
            return post_id
            
        except Exception as e:
            logger.error(f"Error scheduling post: {str(e)}")
            raise
    
    async def _find_optimal_time(self, channel_id: str, post_type: PostType) -> datetime:
        """Find optimal time for posting"""
        try:
            # Get audience insights
            insight = self.audience_insights.get(channel_id)
            if not insight:
                # Use default timing
                return self._get_default_optimal_time(post_type)
            
            # Get timezone
            try:
                tz = pytz.timezone(insight.timezone)
            except:
                tz = pytz.UTC
            
            # Find next optimal time based on patterns
            now = datetime.now(tz)
            current_day = now.strftime("%A")
            current_hour = now.hour
            
            # Check if we should post today
            if current_day in insight.peak_days:
                # Find next peak hour today
                future_peak_hours = [h for h in insight.peak_hours if h > current_hour]
                if future_peak_hours:
                    optimal_hour = min(future_peak_hours)
                    optimal_time = now.replace(hour=optimal_hour, minute=0, second=0, microsecond=0)
                    
                    # Check if this time conflicts with recent posts
                    if not await self._has_recent_posts(channel_id, optimal_time):
                        return optimal_time.astimezone(pytz.UTC)
            
            # Look for next peak day
            for i in range(1, 8):  # Look up to 7 days ahead
                future_date = now + timedelta(days=i)
                future_day = future_date.strftime("%A")
                
                if future_day in insight.peak_days:
                    optimal_hour = insight.peak_hours[0] if insight.peak_hours else 18
                    optimal_time = future_date.replace(hour=optimal_hour, minute=0, second=0, microsecond=0)
                    
                    # Apply seasonal adjustments
                    if self.scheduling_settings["seasonal_adjustment"]:
                        optimal_time = self._apply_seasonal_adjustment(optimal_time)
                    
                    return optimal_time.astimezone(pytz.UTC)
            
            # Fallback to default
            return self._get_default_optimal_time(post_type)
            
        except Exception as e:
            logger.error(f"Error finding optimal time: {str(e)}")
            return self._get_default_optimal_time(post_type)
    
    def _get_default_optimal_time(self, post_type: PostType) -> datetime:
        """Get default optimal time based on post type"""
        now = datetime.utcnow()
        
        # Different post types have different optimal times
        if post_type == PostType.POLL:
            # Polls work well on Monday or Friday evening
            days_until_friday = (4 - now.weekday()) % 7
            optimal_date = now + timedelta(days=days_until_friday)
            return optimal_date.replace(hour=18, minute=0, second=0, microsecond=0)
        
        elif post_type == PostType.BEHIND_SCENES:
            # Behind scenes work well mid-week
            days_until_wednesday = (2 - now.weekday()) % 7
            optimal_date = now + timedelta(days=days_until_wednesday)
            return optimal_date.replace(hour=16, minute=0, second=0, microsecond=0)
        
        elif post_type == PostType.UPDATE:
            # Updates work well on Sunday evening
            days_until_sunday = (6 - now.weekday()) % 7
            optimal_date = now + timedelta(days=days_until_sunday)
            return optimal_date.replace(hour=19, minute=0, second=0, microsecond=0)
        
        else:
            # Default to next good time (usually evening)
            if now.hour < 18:
                return now.replace(hour=18, minute=0, second=0, microsecond=0)
            else:
                return (now + timedelta(days=1)).replace(hour=18, minute=0, second=0, microsecond=0)
    
    async def _has_recent_posts(self, channel_id: str, target_time: datetime) -> bool:
        """Check if there are recent posts that would conflict"""
        try:
            min_interval_hours = self.scheduling_settings["min_post_interval"]
            
            for post in self.scheduled_posts.values():
                if (post.channel_id == channel_id and 
                    post.status == "scheduled" and
                    abs((post.scheduled_time - target_time).total_seconds()) < min_interval_hours * 3600):
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _apply_seasonal_adjustment(self, optimal_time: datetime) -> datetime:
        """Apply seasonal adjustments to timing"""
        try:
            # Determine season
            month = optimal_time.month
            if month in [3, 4, 5]:
                season = "spring"
            elif month in [6, 7, 8]:
                season = "summer"
            elif month in [9, 10, 11]:
                season = "fall"
            else:
                season = "winter"
            
            # Apply adjustment
            adjustment = self.seasonal_adjustments.get(season, {})
            hour_shift = adjustment.get("optimal_shift", 0)
            
            if hour_shift != 0:
                optimal_time += timedelta(hours=hour_shift)
            
            return optimal_time
            
        except Exception:
            return optimal_time
    
    async def _calculate_audience_score(self, channel_id: str, scheduled_time: datetime, post_type: PostType) -> float:
        """Calculate audience score for the scheduled time"""
        try:
            insight = self.audience_insights.get(channel_id)
            if not insight:
                return 0.5  # Neutral score
            
            score = 0.0
            
            # Day of week score
            day_name = scheduled_time.strftime("%A")
            if day_name in insight.peak_days:
                score += 0.4
            
            # Hour of day score
            hour = scheduled_time.hour
            if hour in insight.peak_hours:
                score += 0.4
            
            # Post type bonus
            type_multipliers = {
                PostType.POLL: 1.2,
                PostType.BEHIND_SCENES: 1.1,
                PostType.ANNOUNCEMENT: 1.3,
                PostType.QUESTION: 1.1,
                PostType.UPDATE: 1.0
            }
            multiplier = type_multipliers.get(post_type, 1.0)
            score *= multiplier
            
            return min(1.0, score)  # Cap at 1.0
            
        except Exception:
            return 0.5
    
    async def _predict_engagement(self, channel_id: str, post_type: PostType, scheduled_time: datetime, content: str) -> float:
        """Predict engagement rate for the post"""
        try:
            insight = self.audience_insights.get(channel_id)
            base_engagement = 0.05  # 5% default
            
            if insight:
                base_engagement = insight.engagement_patterns.get("average_engagement_rate", 0.05)
            
            # Adjust based on post type
            type_multipliers = {
                PostType.POLL: 1.5,
                PostType.QUESTION: 1.3,
                PostType.BEHIND_SCENES: 1.2,
                PostType.ANNOUNCEMENT: 1.4,
                PostType.UPDATE: 1.0,
                PostType.TEXT: 0.9
            }
            
            multiplier = type_multipliers.get(post_type, 1.0)
            
            # Adjust based on content length and quality
            content_length = len(content)
            if 100 <= content_length <= 300:  # Optimal length
                length_multiplier = 1.1
            elif content_length < 50:  # Too short
                length_multiplier = 0.9
            elif content_length > 500:  # Too long
                length_multiplier = 0.8
            else:
                length_multiplier = 1.0
            
            # Adjust based on timing quality
            audience_score = await self._calculate_audience_score(channel_id, scheduled_time, post_type)
            timing_multiplier = 0.7 + (audience_score * 0.6)  # 0.7 to 1.3 range
            
            predicted_engagement = base_engagement * multiplier * length_multiplier * timing_multiplier
            
            return min(0.25, predicted_engagement)  # Cap at reasonable maximum
            
        except Exception as e:
            logger.error(f"Error predicting engagement: {str(e)}")
            return 0.05
    
    async def generate_post_from_template(
        self,
        template_name: str,
        variables: Dict[str, str],
        channel_id: str
    ) -> Dict[str, Any]:
        """Generate post content from template"""
        try:
            if template_name not in self.post_templates:
                raise ValueError(f"Template {template_name} not found")
            
            template = self.post_templates[template_name]
            
            # Format content
            content = template.content_template
            for var, value in variables.items():
                content = content.replace(f"{{{var}}}", value)
            
            # Auto-schedule the post
            post_id = await self.schedule_post(
                channel_id=channel_id,
                post_type=template.post_type,
                content=content,
                auto_optimize=True,
                target_demographics=template.target_demographics
            )
            
            return {
                "post_id": post_id,
                "content": content,
                "post_type": template.post_type.value,
                "template_used": template_name
            }
            
        except Exception as e:
            logger.error(f"Error generating post from template: {str(e)}")
            raise
    
    async def bulk_schedule_weekly_content(self, channel_id: str, content_plan: Dict[str, Any]) -> List[str]:
        """Bulk schedule a week's worth of content"""
        try:
            scheduled_post_ids = []
            
            # Get optimal frequency for this channel
            insight = self.audience_insights.get(channel_id)
            weekly_posts = int(insight.optimal_posting_frequency) if insight else 3
            
            # Schedule posts throughout the week
            for i in range(weekly_posts):
                # Determine post type based on day
                post_types = [PostType.UPDATE, PostType.BEHIND_SCENES, PostType.QUESTION, PostType.POLL]
                post_type = post_types[i % len(post_types)]
                
                # Generate content
                content = self._generate_weekly_content(post_type, content_plan, i)
                
                # Schedule with auto-optimization
                post_id = await self.schedule_post(
                    channel_id=channel_id,
                    post_type=post_type,
                    content=content,
                    auto_optimize=True
                )
                
                scheduled_post_ids.append(post_id)
            
            logger.info(f"Bulk scheduled {len(scheduled_post_ids)} posts for channel {channel_id}")
            return scheduled_post_ids
            
        except Exception as e:
            logger.error(f"Error bulk scheduling weekly content: {str(e)}")
            return []
    
    def _generate_weekly_content(self, post_type: PostType, content_plan: Dict[str, Any], index: int) -> str:
        """Generate content for weekly schedule"""
        try:
            if post_type == PostType.UPDATE:
                return f"Weekly update! 🌟 {content_plan.get('weekly_highlights', 'This week has been amazing!')} What's been the highlight of your week? #WeeklyUpdate #Community"
            
            elif post_type == PostType.BEHIND_SCENES:
                return f"Behind the scenes peek! 🎬 {content_plan.get('behind_scenes', 'Working on something exciting!')} Love showing you the process! #BehindTheScenes #Creating"
            
            elif post_type == PostType.QUESTION:
                questions = content_plan.get('questions', [
                    "What topic should I cover next?",
                    "What's your biggest challenge right now?",
                    "What would you like to see more of?"
                ])
                question = questions[index % len(questions)]
                return f"Q&A time! 🤔 {question} Drop your answers below and I'll feature the best ones! #QA #Community"
            
            elif post_type == PostType.POLL:
                polls = content_plan.get('polls', [
                    "What type of content do you prefer?",
                    "Which topic interests you most?",
                    "What should be my next big project?"
                ])
                poll = polls[index % len(polls)]
                return f"Help me decide! 🗳️ {poll} Your vote matters! #Poll #YourChoice"
            
            else:
                return f"Thanks for being part of this amazing community! 💙 {content_plan.get('general_message', 'Your support means everything!')} #Community #ThankYou"
                
        except Exception:
            return "Thanks for being part of this amazing community! 💙 #Community"
    
    async def get_scheduled_posts(self, channel_id: str, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Get scheduled posts for a channel"""
        try:
            end_date = datetime.utcnow() + timedelta(days=days_ahead)
            
            channel_posts = [
                {
                    "id": post.id,
                    "post_type": post.post_type.value,
                    "content": post.content,
                    "scheduled_time": post.scheduled_time.isoformat(),
                    "optimal_time": post.optimal_time,
                    "audience_score": post.audience_score,
                    "expected_engagement": post.expected_engagement,
                    "status": post.status
                }
                for post in self.scheduled_posts.values()
                if (post.channel_id == channel_id and 
                    post.scheduled_time <= end_date and
                    post.status == "scheduled")
            ]
            
            # Sort by scheduled time
            return sorted(channel_posts, key=lambda x: x["scheduled_time"])
            
        except Exception as e:
            logger.error(f"Error getting scheduled posts: {str(e)}")
            return []
    
    async def optimize_existing_schedule(self, channel_id: str) -> int:
        """Optimize existing scheduled posts"""
        try:
            optimized_count = 0
            
            channel_posts = [
                post for post in self.scheduled_posts.values()
                if post.channel_id == channel_id and post.status == "scheduled"
            ]
            
            for post in channel_posts:
                # Find new optimal time
                new_optimal_time = await self._find_optimal_time(channel_id, post.post_type)
                
                # Check if new time is significantly better
                old_score = await self._calculate_audience_score(channel_id, post.scheduled_time, post.post_type)
                new_score = await self._calculate_audience_score(channel_id, new_optimal_time, post.post_type)
                
                if new_score > old_score + 0.1:  # Significant improvement
                    post.scheduled_time = new_optimal_time
                    post.optimal_time = True
                    post.audience_score = new_score
                    optimized_count += 1
            
            logger.info(f"Optimized {optimized_count} posts for channel {channel_id}")
            return optimized_count
            
        except Exception as e:
            logger.error(f"Error optimizing schedule: {str(e)}")
            return 0
    
    def get_scheduling_analytics(self, channel_id: str) -> Dict[str, Any]:
        """Get scheduling analytics for a channel"""
        try:
            channel_posts = [
                post for post in self.scheduled_posts.values()
                if post.channel_id == channel_id
            ]
            
            if not channel_posts:
                return {"error": "No posts found for channel"}
            
            # Calculate metrics
            total_posts = len(channel_posts)
            optimal_posts = len([p for p in channel_posts if p.optimal_time])
            avg_audience_score = sum(p.audience_score for p in channel_posts) / total_posts
            avg_expected_engagement = sum(p.expected_engagement for p in channel_posts) / total_posts
            
            # Post type distribution
            post_type_dist = {}
            for post in channel_posts:
                post_type = post.post_type.value
                post_type_dist[post_type] = post_type_dist.get(post_type, 0) + 1
            
            return {
                "total_posts": total_posts,
                "optimal_posts": optimal_posts,
                "optimization_rate": optimal_posts / total_posts if total_posts > 0 else 0,
                "average_audience_score": avg_audience_score,
                "average_expected_engagement": avg_expected_engagement,
                "post_type_distribution": post_type_dist,
                "scheduling_efficiency": avg_audience_score * 100
            }
            
        except Exception as e:
            logger.error(f"Error getting scheduling analytics: {str(e)}")
            return {"error": str(e)}
    
    def get_post_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get available post templates"""
        return {
            name: {
                "name": template.name,
                "post_type": template.post_type.value,
                "content_template": template.content_template,
                "variables": template.variables,
                "optimal_times": template.optimal_times,
                "engagement_multiplier": template.engagement_multiplier
            }
            for name, template in self.post_templates.items()
        }
    
    def update_scheduling_settings(self, settings: Dict[str, Any]) -> bool:
        """Update scheduling settings"""
        try:
            self.scheduling_settings.update(settings)
            return True
        except Exception as e:
            logger.error(f"Error updating scheduling settings: {str(e)}")
            return False