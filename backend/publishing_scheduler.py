"""
Intelligent Publishing Scheduler
Handles optimal timing algorithms, queue management, and automated scheduling
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional, Tuple
import pytz
from dataclasses import dataclass
import schedule
import threading
import time

from social_media_manager import SocialMediaManager, SocialPlatform, PublishingJob

logger = logging.getLogger(__name__)

@dataclass
class OptimalTimingData:
    """Data structure for optimal posting times"""
    platform: SocialPlatform
    timezone: str
    weekday_times: Dict[str, List[str]]  # {'monday': ['09:00', '17:00'], ...}
    weekend_times: Dict[str, List[str]]  # {'saturday': ['10:00', '14:00'], ...}
    engagement_factors: Dict[str, float]  # Engagement multipliers by time
    audience_demographics: Dict[str, Any]

class PublishingScheduler:
    """Intelligent publishing scheduler with optimal timing algorithms"""
    
    def __init__(self, social_manager: SocialMediaManager):
        self.social_manager = social_manager
        self.is_running = False
        self.scheduler_thread = None
        self.pending_jobs = []
        
        # Platform-specific optimal timing data
        self.optimal_timings = self._initialize_optimal_timings()
        
    def _initialize_optimal_timings(self) -> Dict[SocialPlatform, OptimalTimingData]:
        """Initialize platform-specific optimal posting times based on research"""
        return {
            SocialPlatform.FACEBOOK: OptimalTimingData(
                platform=SocialPlatform.FACEBOOK,
                timezone="UTC",
                weekday_times={
                    'monday': ['09:00', '15:00'],
                    'tuesday': ['09:00', '15:00'],
                    'wednesday': ['09:00', '15:00', '19:00'],
                    'thursday': ['09:00', '15:00'],
                    'friday': ['09:00', '13:00', '15:00']
                },
                weekend_times={
                    'saturday': ['10:00', '14:00'],
                    'sunday': ['12:00', '14:00']
                },
                engagement_factors={
                    '09:00': 1.2, '13:00': 1.1, '15:00': 1.3, '19:00': 1.4
                },
                audience_demographics={
                    'peak_age_group': '25-54',
                    'active_hours': '09:00-22:00',
                    'best_content_types': ['video', 'image', 'link']
                }
            ),
            
            SocialPlatform.TWITTER: OptimalTimingData(
                platform=SocialPlatform.TWITTER,
                timezone="UTC",
                weekday_times={
                    'monday': ['08:00', '12:00', '17:00'],
                    'tuesday': ['08:00', '12:00', '17:00'],
                    'wednesday': ['08:00', '12:00', '17:00', '19:00'],
                    'thursday': ['08:00', '12:00', '17:00'],
                    'friday': ['08:00', '12:00', '17:00']
                },
                weekend_times={
                    'saturday': ['09:00', '12:00'],
                    'sunday': ['12:00', '15:00']
                },
                engagement_factors={
                    '08:00': 1.1, '12:00': 1.3, '17:00': 1.4, '19:00': 1.2
                },
                audience_demographics={
                    'peak_age_group': '18-49',
                    'active_hours': '07:00-21:00',
                    'best_content_types': ['video', 'image', 'text']
                }
            ),
            
            SocialPlatform.INSTAGRAM: OptimalTimingData(
                platform=SocialPlatform.INSTAGRAM,
                timezone="UTC",
                weekday_times={
                    'monday': ['11:00', '14:00', '17:00'],
                    'tuesday': ['11:00', '14:00', '17:00'],
                    'wednesday': ['11:00', '14:00', '17:00'],
                    'thursday': ['11:00', '14:00', '17:00'],
                    'friday': ['11:00', '14:00', '17:00']
                },
                weekend_times={
                    'saturday': ['10:00', '11:00', '14:00'],
                    'sunday': ['10:00', '11:00', '14:00']
                },
                engagement_factors={
                    '11:00': 1.3, '14:00': 1.2, '17:00': 1.4
                },
                audience_demographics={
                    'peak_age_group': '18-34',
                    'active_hours': '08:00-20:00',
                    'best_content_types': ['video', 'story', 'reel']
                }
            ),
            
            SocialPlatform.TIKTOK: OptimalTimingData(
                platform=SocialPlatform.TIKTOK,
                timezone="UTC",
                weekday_times={
                    'monday': ['06:00', '10:00', '19:00'],
                    'tuesday': ['06:00', '10:00', '19:00'],
                    'wednesday': ['06:00', '10:00', '19:00'],
                    'thursday': ['06:00', '10:00', '19:00'],
                    'friday': ['06:00', '10:00', '19:00']
                },
                weekend_times={
                    'saturday': ['07:00', '09:00', '11:00'],
                    'sunday': ['07:00', '09:00', '11:00']
                },
                engagement_factors={
                    '06:00': 1.2, '10:00': 1.1, '19:00': 1.5
                },
                audience_demographics={
                    'peak_age_group': '16-24',
                    'active_hours': '06:00-22:00',
                    'best_content_types': ['video', 'trend']
                }
            ),
            
            SocialPlatform.LINKEDIN: OptimalTimingData(
                platform=SocialPlatform.LINKEDIN,
                timezone="UTC",
                weekday_times={
                    'monday': ['08:00', '12:00', '17:00'],
                    'tuesday': ['08:00', '10:00', '12:00'],
                    'wednesday': ['08:00', '10:00', '12:00'],
                    'thursday': ['08:00', '10:00', '12:00'],
                    'friday': ['08:00', '12:00']
                },
                weekend_times={
                    'saturday': [],  # Professional network, minimal weekend activity
                    'sunday': []
                },
                engagement_factors={
                    '08:00': 1.3, '10:00': 1.2, '12:00': 1.4, '17:00': 1.1
                },
                audience_demographics={
                    'peak_age_group': '25-54',
                    'active_hours': '08:00-18:00',
                    'best_content_types': ['professional_video', 'article', 'update']
                }
            )
        }

    def get_optimal_posting_time(
        self, 
        platform: SocialPlatform, 
        user_timezone: str = "UTC",
        target_date: Optional[datetime] = None
    ) -> Tuple[datetime, float]:
        """
        Calculate optimal posting time for a platform
        Returns: (optimal_datetime, engagement_score)
        """
        if target_date is None:
            target_date = datetime.now(timezone.utc)
        
        # Convert to user timezone
        user_tz = pytz.timezone(user_timezone)
        local_date = target_date.astimezone(user_tz)
        
        # Get platform timing data
        timing_data = self.optimal_timings.get(platform)
        if not timing_data:
            # Default to 12:00 if no data available
            optimal_time = local_date.replace(hour=12, minute=0, second=0, microsecond=0)
            return optimal_time.astimezone(timezone.utc), 1.0
        
        # Determine if it's a weekend
        is_weekend = local_date.weekday() >= 5
        weekday_name = local_date.strftime('%A').lower()
        
        # Get available times for the day
        if is_weekend:
            available_times = timing_data.weekend_times.get(weekday_name, ['12:00'])
        else:
            available_times = timing_data.weekday_times.get(weekday_name, ['12:00'])
        
        if not available_times:
            available_times = ['12:00']
        
        # Find the time with highest engagement factor
        best_time = '12:00'
        best_score = 1.0
        
        for time_str in available_times:
            engagement_score = timing_data.engagement_factors.get(time_str, 1.0)
            if engagement_score > best_score:
                best_time = time_str
                best_score = engagement_score
        
        # Parse time and create datetime
        hour, minute = map(int, best_time.split(':'))
        optimal_datetime = local_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Convert back to UTC
        return optimal_datetime.astimezone(timezone.utc), best_score

    def schedule_optimal_posting(
        self,
        user_id: int,
        video_path: str,
        title: str,
        description: str,
        platforms: List[SocialPlatform],
        tags: List[str] = None,
        user_timezone: str = "UTC",
        days_ahead: int = 1
    ) -> Dict[str, Any]:
        """
        Schedule posts at optimal times for each platform
        """
        scheduled_posts = []
        
        for platform in platforms:
            # Calculate optimal time
            target_date = datetime.now(timezone.utc) + timedelta(days=days_ahead)
            optimal_time, engagement_score = self.get_optimal_posting_time(
                platform, user_timezone, target_date
            )
            
            # Create individual publishing job for this platform
            job_data = {
                "user_id": user_id,
                "video_path": video_path,
                "title": title,
                "description": description,
                "platforms": [platform],
                "tags": tags or [],
                "scheduled_time": optimal_time,
                "engagement_score": engagement_score
            }
            
            scheduled_posts.append({
                "platform": platform.value,
                "scheduled_time": optimal_time.isoformat(),
                "engagement_score": engagement_score,
                "local_time": optimal_time.astimezone(pytz.timezone(user_timezone)).isoformat()
            })
            
            # Add to pending jobs
            self.pending_jobs.append(job_data)
        
        return {
            "success": True,
            "scheduled_posts": scheduled_posts,
            "total_posts": len(scheduled_posts),
            "message": "Posts scheduled at optimal times"
        }

    def bulk_schedule_content(
        self,
        user_id: int,
        content_calendar: List[Dict[str, Any]],
        user_timezone: str = "UTC"
    ) -> Dict[str, Any]:
        """
        Schedule multiple pieces of content across platforms
        """
        scheduled_content = []
        
        for content_item in content_calendar:
            video_path = content_item.get("video_path")
            title = content_item.get("title")
            description = content_item.get("description")
            platforms = [SocialPlatform(p) for p in content_item.get("platforms", [])]
            tags = content_item.get("tags", [])
            target_date = content_item.get("target_date")
            
            if target_date:
                target_datetime = datetime.fromisoformat(target_date)
            else:
                target_datetime = datetime.now(timezone.utc) + timedelta(days=1)
            
            # Schedule for each platform
            for platform in platforms:
                optimal_time, engagement_score = self.get_optimal_posting_time(
                    platform, user_timezone, target_datetime
                )
                
                job_data = {
                    "user_id": user_id,
                    "video_path": video_path,
                    "title": title,
                    "description": description,
                    "platforms": [platform],
                    "tags": tags,
                    "scheduled_time": optimal_time,
                    "engagement_score": engagement_score
                }
                
                self.pending_jobs.append(job_data)
                
                scheduled_content.append({
                    "content_id": content_item.get("id"),
                    "platform": platform.value,
                    "scheduled_time": optimal_time.isoformat(),
                    "engagement_score": engagement_score
                })
        
        return {
            "success": True,
            "scheduled_content": scheduled_content,
            "total_scheduled": len(scheduled_content)
        }

    def get_content_calendar_suggestions(
        self,
        platforms: List[SocialPlatform],
        user_timezone: str = "UTC",
        days_ahead: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Generate content calendar suggestions with optimal posting times
        """
        suggestions = []
        start_date = datetime.now(timezone.utc)
        
        for day in range(days_ahead):
            current_date = start_date + timedelta(days=day)
            daily_suggestions = {}
            
            for platform in platforms:
                optimal_time, engagement_score = self.get_optimal_posting_time(
                    platform, user_timezone, current_date
                )
                
                timing_data = self.optimal_timings.get(platform)
                audience_info = timing_data.audience_demographics if timing_data else {}
                
                daily_suggestions[platform.value] = {
                    "optimal_time": optimal_time.isoformat(),
                    "local_time": optimal_time.astimezone(pytz.timezone(user_timezone)).isoformat(),
                    "engagement_score": engagement_score,
                    "recommended_content_types": audience_info.get("best_content_types", []),
                    "target_audience": audience_info.get("peak_age_group", "All ages")
                }
            
            suggestions.append({
                "date": current_date.date().isoformat(),
                "weekday": current_date.strftime("%A"),
                "platforms": daily_suggestions
            })
        
        return suggestions

    def analyze_posting_performance(
        self,
        user_id: int,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze past posting performance to optimize future scheduling
        """
        import sqlite3
        
        conn = sqlite3.connect(self.social_manager.db_path)
        cursor = conn.cursor()
        
        try:
            # Get publishing history
            start_date = datetime.now() - timedelta(days=days_back)
            
            cursor.execute('''
                SELECT platforms, platform_results, created_at, completed_at
                FROM publishing_jobs
                WHERE user_id = ? AND created_at >= ? AND status = 'completed'
            ''', (user_id, start_date.isoformat()))
            
            jobs = cursor.fetchall()
            
            # Analyze performance by platform and time
            platform_performance = {}
            time_performance = {}
            
            for job in jobs:
                platforms = json.loads(job[0])
                platform_results = json.loads(job[1]) if job[1] else {}
                created_at = datetime.fromisoformat(job[2])
                
                hour = created_at.hour
                weekday = created_at.strftime("%A").lower()
                
                for platform in platforms:
                    if platform not in platform_performance:
                        platform_performance[platform] = {
                            "total_posts": 0,
                            "successful_posts": 0,
                            "avg_engagement": 0,
                            "best_times": [],
                            "best_days": []
                        }
                    
                    platform_performance[platform]["total_posts"] += 1
                    
                    if platform in platform_results and platform_results[platform].get("success"):
                        platform_performance[platform]["successful_posts"] += 1
                        
                        # Track successful posting times
                        time_key = f"{weekday}_{hour:02d}"
                        if time_key not in time_performance:
                            time_performance[time_key] = {"count": 0, "success_rate": 0}
                        time_performance[time_key]["count"] += 1
            
            # Calculate success rates and recommendations
            for platform in platform_performance:
                total = platform_performance[platform]["total_posts"]
                successful = platform_performance[platform]["successful_posts"]
                platform_performance[platform]["success_rate"] = (successful / total * 100) if total > 0 else 0
            
            # Find best performing times
            best_times = sorted(
                time_performance.items(),
                key=lambda x: x[1]["count"],
                reverse=True
            )[:5]
            
            return {
                "analysis_period_days": days_back,
                "platform_performance": platform_performance,
                "best_posting_times": [
                    {
                        "time_slot": time_key,
                        "post_count": data["count"],
                        "weekday": time_key.split("_")[0],
                        "hour": int(time_key.split("_")[1])
                    }
                    for time_key, data in best_times
                ],
                "recommendations": self._generate_recommendations(platform_performance, best_times)
            }
            
        finally:
            conn.close()

    def _generate_recommendations(
        self,
        platform_performance: Dict[str, Any],
        best_times: List[Tuple[str, Dict]]
    ) -> List[str]:
        """Generate recommendations based on performance analysis"""
        recommendations = []
        
        # Platform-specific recommendations
        for platform, stats in platform_performance.items():
            success_rate = stats["success_rate"]
            
            if success_rate < 50:
                recommendations.append(
                    f"Consider reviewing your {platform} content strategy - success rate is {success_rate:.1f}%"
                )
            elif success_rate > 80:
                recommendations.append(
                    f"Great {platform} performance! Consider increasing posting frequency"
                )
        
        # Timing recommendations
        if best_times:
            best_day = best_times[0][0].split("_")[0]
            best_hour = int(best_times[0][0].split("_")[1])
            recommendations.append(
                f"Your most active posting time is {best_day}s at {best_hour:02d}:00"
            )
        
        return recommendations

    def start_scheduler(self):
        """Start the background scheduler"""
        if self.is_running:
            return
        
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        logger.info("Publishing scheduler started")

    def stop_scheduler(self):
        """Stop the background scheduler"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        
        logger.info("Publishing scheduler stopped")

    def _run_scheduler(self):
        """Main scheduler loop"""
        while self.is_running:
            try:
                self._process_pending_jobs()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Scheduler error: {str(e)}")

    async def _process_pending_jobs(self):
        """Process jobs that are ready to be published"""
        now = datetime.now(timezone.utc)
        ready_jobs = []
        
        for job_data in self.pending_jobs[:]:
            scheduled_time = job_data["scheduled_time"]
            
            if scheduled_time <= now:
                ready_jobs.append(job_data)
                self.pending_jobs.remove(job_data)
        
        # Process ready jobs
        for job_data in ready_jobs:
            try:
                await self.social_manager.create_publishing_job(
                    user_id=job_data["user_id"],
                    video_path=job_data["video_path"],
                    title=job_data["title"],
                    description=job_data["description"],
                    platforms=job_data["platforms"],
                    tags=job_data["tags"],
                    scheduled_time=None  # Execute immediately
                )
                
                logger.info(f"Processed scheduled job for platforms: {[p.value for p in job_data['platforms']]}")
                
            except Exception as e:
                logger.error(f"Error processing scheduled job: {str(e)}")

    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get current scheduler status"""
        return {
            "is_running": self.is_running,
            "pending_jobs": len(self.pending_jobs),
            "next_job": min([job["scheduled_time"] for job in self.pending_jobs], default=None),
            "supported_platforms": [platform.value for platform in self.optimal_timings.keys()]
        }

# Global scheduler instance
scheduler_instance = None

def get_scheduler() -> PublishingScheduler:
    """Get the global scheduler instance"""
    global scheduler_instance
    if scheduler_instance is None:
        from social_media_manager import SocialMediaManager
        social_manager = SocialMediaManager()
        scheduler_instance = PublishingScheduler(social_manager)
        scheduler_instance.start_scheduler()
    
    return scheduler_instance