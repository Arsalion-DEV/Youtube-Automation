"""
Social Blade-Inspired Growth Tracking Module
Comprehensive channel growth tracking, analytics, and prediction system
"""

import asyncio
import logging
import json
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import uuid
import math

logger = logging.getLogger(__name__)

@dataclass
class ChannelMetrics:
    """Channel metrics at a specific point in time"""
    timestamp: datetime
    subscribers: int
    total_views: int
    video_count: int
    average_views: float
    estimated_earnings: float
    engagement_rate: float
    upload_frequency: float  # videos per week

@dataclass
class GrowthTrend:
    """Growth trend analysis"""
    period: str  # daily, weekly, monthly, yearly
    subscriber_growth: int
    subscriber_growth_rate: float
    view_growth: int
    view_growth_rate: float
    video_growth: int
    engagement_change: float
    growth_velocity: str  # accelerating, stable, declining

@dataclass
class ChannelRanking:
    """Channel ranking information"""
    global_rank: int
    country_rank: int
    category_rank: int
    grade: str  # A++, A+, A, B+, B, C+, C, D, F
    growth_grade: str
    subscriber_rank: int
    view_rank: int

class GrowthTracker:
    """Social Blade-inspired growth tracking system"""
    
    def __init__(self):
        self.channel_data = {}  # channel_id -> historical data
        self.growth_predictions = {}
        self.ranking_data = {}
        self.milestones = {}
        
        # Growth rate thresholds
        self.growth_thresholds = {
            'explosive': 0.5,    # 50%+ growth
            'rapid': 0.2,        # 20%+ growth
            'steady': 0.05,      # 5%+ growth
            'slow': 0.01,        # 1%+ growth
            'stagnant': 0.0,     # No growth
            'declining': -0.01   # Negative growth
        }
    
    async def track_channel_growth(self, channel_id: str, 
                                 timeframe: str = '30d') -> Dict[str, Any]:
        """
        Track comprehensive channel growth metrics
        
        Args:
            channel_id: YouTube channel ID
            timeframe: Analysis timeframe (7d, 30d, 90d, 1y)
            
        Returns:
            Complete growth analysis
        """
        try:
            # Get or create channel data
            if channel_id not in self.channel_data:
                await self._initialize_channel_data(channel_id)
            
            # Calculate timeframe
            days = self._parse_timeframe(timeframe)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get historical data for period
            historical_data = await self._get_historical_data(channel_id, start_date, end_date)
            
            # Calculate growth metrics
            growth_analysis = {
                'channel_id': channel_id,
                'analysis_period': timeframe,
                'analysis_date': end_date.isoformat(),
                'current_metrics': await self._get_current_metrics(channel_id),
                'growth_trends': await self._calculate_growth_trends(historical_data),
                'predictions': await self._generate_growth_predictions(channel_id, historical_data),
                'milestones': await self._track_milestones(channel_id, historical_data),
                'performance_analysis': await self._analyze_performance(historical_data),
                'recommendations': await self._generate_growth_recommendations(channel_id, historical_data),
                'ranking': await self._get_channel_ranking(channel_id)
            }
            
            return growth_analysis
            
        except Exception as e:
            logger.error(f"Growth tracking failed: {e}")
            return {'error': 'Growth tracking failed', 'details': str(e)}
    
    async def compare_channels(self, channel_ids: List[str], 
                             metric: str = 'subscribers') -> Dict[str, Any]:
        """
        Compare multiple channels across various metrics
        
        Args:
            channel_ids: List of channel IDs to compare
            metric: Primary metric for comparison
            
        Returns:
            Channel comparison analysis
        """
        try:
            comparison_data = []
            
            for channel_id in channel_ids:
                # Get current metrics
                metrics = await self._get_current_metrics(channel_id)
                growth_data = await self.track_channel_growth(channel_id, '30d')
                
                comparison_data.append({
                    'channel_id': channel_id,
                    'current_metrics': metrics,
                    'growth_30d': growth_data.get('growth_trends', {}),
                    'ranking': growth_data.get('ranking', {}),
                    'performance_score': await self._calculate_performance_score(metrics, growth_data)
                })
            
            # Sort by primary metric
            comparison_data.sort(
                key=lambda x: x['current_metrics'].get(metric, 0), 
                reverse=True
            )
            
            # Calculate relative performance
            best_performer = comparison_data[0] if comparison_data else None
            
            for i, data in enumerate(comparison_data):
                data['rank'] = i + 1
                data['relative_performance'] = await self._calculate_relative_performance(
                    data, best_performer, metric
                )
            
            return {
                'comparison_metric': metric,
                'channels_compared': len(channel_ids),
                'analysis_date': datetime.now().isoformat(),
                'rankings': comparison_data,
                'leader': best_performer,
                'growth_champion': await self._find_growth_champion(comparison_data),
                'insights': await self._generate_comparison_insights(comparison_data, metric)
            }
            
        except Exception as e:
            logger.error(f"Channel comparison failed: {e}")
            return {'error': 'Channel comparison failed', 'details': str(e)}
    
    async def predict_future_growth(self, channel_id: str, 
                                  prediction_days: int = 90) -> Dict[str, Any]:
        """
        Predict future channel growth using trend analysis
        
        Args:
            channel_id: Channel to analyze
            prediction_days: Number of days to predict ahead
            
        Returns:
            Growth predictions and scenarios
        """
        try:
            # Get historical data
            historical_data = await self._get_historical_data(
                channel_id, 
                datetime.now() - timedelta(days=180),  # Use 6 months of history
                datetime.now()
            )
            
            if len(historical_data) < 30:  # Need at least 30 data points
                return {'error': 'Insufficient historical data for prediction'}
            
            # Calculate growth patterns
            growth_patterns = await self._analyze_growth_patterns(historical_data)
            
            # Generate multiple scenarios
            predictions = {
                'channel_id': channel_id,
                'prediction_period': f"{prediction_days} days",
                'prediction_date': datetime.now().isoformat(),
                'current_metrics': historical_data[-1] if historical_data else None,
                'scenarios': {
                    'conservative': await self._predict_conservative_growth(historical_data, prediction_days),
                    'realistic': await self._predict_realistic_growth(historical_data, prediction_days),
                    'optimistic': await self._predict_optimistic_growth(historical_data, prediction_days)
                },
                'growth_patterns': growth_patterns,
                'confidence_factors': await self._calculate_prediction_confidence(historical_data),
                'milestone_predictions': await self._predict_milestones(channel_id, historical_data, prediction_days),
                'growth_factors': await self._identify_growth_factors(historical_data),
                'recommendations': await self._generate_prediction_recommendations(growth_patterns)
            }
            
            return predictions
            
        except Exception as e:
            logger.error(f"Growth prediction failed: {e}")
            return {'error': 'Growth prediction failed', 'details': str(e)}
    
    async def _initialize_channel_data(self, channel_id: str):
        """Initialize channel data with simulated historical metrics"""
        try:
            # Generate 180 days of historical data
            historical_data = []
            base_date = datetime.now() - timedelta(days=180)
            
            # Starting metrics (simulate realistic channel)
            base_subscribers = random.randint(1000, 100000)
            base_views = random.randint(base_subscribers * 10, base_subscribers * 500)
            base_videos = random.randint(50, 500)
            
            for day in range(180):
                date = base_date + timedelta(days=day)
                
                # Simulate growth patterns with some randomness
                growth_factor = 1 + random.uniform(-0.02, 0.05)  # -2% to +5% daily variance
                
                # Apply seasonal patterns
                seasonal_factor = 1 + 0.1 * math.sin(2 * math.pi * day / 365)  # Yearly pattern
                
                subscribers = int(base_subscribers * (growth_factor ** day) * seasonal_factor)
                views = int(base_views * (growth_factor ** day) * seasonal_factor * random.uniform(0.8, 1.5))
                videos = base_videos + random.randint(0, 2) if day % 7 == 0 else base_videos  # New videos weekly
                
                metrics = ChannelMetrics(
                    timestamp=date,
                    subscribers=subscribers,
                    total_views=views,
                    video_count=videos,
                    average_views=views / videos if videos > 0 else 0,
                    estimated_earnings=views * random.uniform(0.001, 0.005),  # $1-5 per 1000 views
                    engagement_rate=random.uniform(0.02, 0.08),  # 2-8% engagement
                    upload_frequency=videos / (day + 1) * 7 if day > 0 else 0  # Videos per week
                )
                
                historical_data.append(metrics)
                base_videos = videos  # Update base for next iteration
            
            self.channel_data[channel_id] = historical_data
            
        except Exception as e:
            logger.error(f"Failed to initialize channel data: {e}")
    
    def _parse_timeframe(self, timeframe: str) -> int:
        """Parse timeframe string to days"""
        timeframe_map = {
            '7d': 7,
            '30d': 30,
            '90d': 90,
            '1y': 365,
            '6m': 180
        }
        return timeframe_map.get(timeframe, 30)
    
    async def _get_historical_data(self, channel_id: str, 
                                 start_date: datetime, 
                                 end_date: datetime) -> List[ChannelMetrics]:
        """Get historical data for specified period"""
        try:
            if channel_id not in self.channel_data:
                await self._initialize_channel_data(channel_id)
            
            all_data = self.channel_data[channel_id]
            
            # Filter data by date range
            filtered_data = [
                metrics for metrics in all_data
                if start_date <= metrics.timestamp <= end_date
            ]
            
            return filtered_data
            
        except Exception as e:
            logger.error(f"Failed to get historical data: {e}")
            return []
    
    async def _get_current_metrics(self, channel_id: str) -> Dict[str, Any]:
        """Get current channel metrics"""
        try:
            if channel_id not in self.channel_data:
                await self._initialize_channel_data(channel_id)
            
            latest_metrics = self.channel_data[channel_id][-1]
            
            return {
                'subscribers': latest_metrics.subscribers,
                'total_views': latest_metrics.total_views,
                'video_count': latest_metrics.video_count,
                'average_views': round(latest_metrics.average_views, 0),
                'estimated_monthly_earnings': round(latest_metrics.estimated_earnings * 30, 2),
                'engagement_rate': round(latest_metrics.engagement_rate, 4),
                'upload_frequency': round(latest_metrics.upload_frequency, 2),
                'last_updated': latest_metrics.timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get current metrics: {e}")
            return {}
    
    async def _calculate_growth_trends(self, historical_data: List[ChannelMetrics]) -> Dict[str, Any]:
        """Calculate growth trends for various timeframes"""
        try:
            if len(historical_data) < 2:
                return {}
            
            latest = historical_data[-1]
            
            trends = {}
            
            # Calculate trends for different periods
            periods = [
                ('daily', 1),
                ('weekly', 7),
                ('monthly', 30)
            ]
            
            for period_name, days in periods:
                if len(historical_data) > days:
                    past_data = historical_data[-(days+1)]
                    
                    subscriber_growth = latest.subscribers - past_data.subscribers
                    subscriber_growth_rate = (subscriber_growth / past_data.subscribers) * 100 if past_data.subscribers > 0 else 0
                    
                    view_growth = latest.total_views - past_data.total_views
                    view_growth_rate = (view_growth / past_data.total_views) * 100 if past_data.total_views > 0 else 0
                    
                    video_growth = latest.video_count - past_data.video_count
                    
                    engagement_change = latest.engagement_rate - past_data.engagement_rate
                    
                    # Determine growth velocity
                    growth_velocity = self._determine_growth_velocity(subscriber_growth_rate)
                    
                    trends[period_name] = GrowthTrend(
                        period=period_name,
                        subscriber_growth=subscriber_growth,
                        subscriber_growth_rate=round(subscriber_growth_rate, 2),
                        view_growth=view_growth,
                        view_growth_rate=round(view_growth_rate, 2),
                        video_growth=video_growth,
                        engagement_change=round(engagement_change, 4),
                        growth_velocity=growth_velocity
                    )
            
            return {period: asdict(trend) for period, trend in trends.items()}
            
        except Exception as e:
            logger.error(f"Growth trends calculation failed: {e}")
            return {}
    
    def _determine_growth_velocity(self, growth_rate: float) -> str:
        """Determine growth velocity category"""
        growth_rate_decimal = growth_rate / 100
        
        if growth_rate_decimal >= self.growth_thresholds['explosive']:
            return 'explosive'
        elif growth_rate_decimal >= self.growth_thresholds['rapid']:
            return 'rapid'
        elif growth_rate_decimal >= self.growth_thresholds['steady']:
            return 'steady'
        elif growth_rate_decimal >= self.growth_thresholds['slow']:
            return 'slow'
        elif growth_rate_decimal >= self.growth_thresholds['stagnant']:
            return 'stagnant'
        else:
            return 'declining'
    
    async def _generate_growth_predictions(self, channel_id: str, 
                                         historical_data: List[ChannelMetrics]) -> Dict[str, Any]:
        """Generate growth predictions"""
        try:
            if len(historical_data) < 10:
                return {'error': 'Insufficient data for predictions'}
            
            # Calculate growth rates for the last 30 days
            recent_data = historical_data[-30:]
            
            avg_daily_subscriber_growth = (recent_data[-1].subscribers - recent_data[0].subscribers) / 30
            avg_daily_view_growth = (recent_data[-1].total_views - recent_data[0].total_views) / 30
            
            # Predict next 30 days
            predictions = {
                'next_30_days': {
                    'predicted_subscribers': recent_data[-1].subscribers + int(avg_daily_subscriber_growth * 30),
                    'predicted_views': recent_data[-1].total_views + int(avg_daily_view_growth * 30),
                    'confidence': 'medium'
                },
                'next_90_days': {
                    'predicted_subscribers': recent_data[-1].subscribers + int(avg_daily_subscriber_growth * 90),
                    'predicted_views': recent_data[-1].total_views + int(avg_daily_view_growth * 90),
                    'confidence': 'low'
                },
                'growth_trajectory': self._determine_growth_velocity(
                    (avg_daily_subscriber_growth / recent_data[0].subscribers) * 100 * 30
                )
            }
            
            return predictions
            
        except Exception as e:
            logger.error(f"Growth prediction failed: {e}")
            return {}
    
    async def _track_milestones(self, channel_id: str, 
                              historical_data: List[ChannelMetrics]) -> Dict[str, Any]:
        """Track milestone achievements and predict future milestones"""
        try:
            if not historical_data:
                return {}
            
            current_subs = historical_data[-1].subscribers
            current_views = historical_data[-1].total_views
            
            # Define milestone thresholds
            subscriber_milestones = [1000, 10000, 50000, 100000, 500000, 1000000]
            view_milestones = [100000, 1000000, 10000000, 100000000]
            
            # Find achieved milestones
            achieved_sub_milestones = [m for m in subscriber_milestones if current_subs >= m]
            achieved_view_milestones = [m for m in view_milestones if current_views >= m]
            
            # Find next milestones
            next_sub_milestone = next((m for m in subscriber_milestones if m > current_subs), None)
            next_view_milestone = next((m for m in view_milestones if m > current_views), None)
            
            # Calculate progress to next milestones
            sub_progress = 0
            view_progress = 0
            
            if next_sub_milestone:
                prev_sub_milestone = max([m for m in subscriber_milestones if m <= current_subs] or [0])
                sub_progress = (current_subs - prev_sub_milestone) / (next_sub_milestone - prev_sub_milestone) * 100
            
            if next_view_milestone:
                prev_view_milestone = max([m for m in view_milestones if m <= current_views] or [0])
                view_progress = (current_views - prev_view_milestone) / (next_view_milestone - prev_view_milestone) * 100
            
            return {
                'achieved_subscriber_milestones': achieved_sub_milestones,
                'achieved_view_milestones': achieved_view_milestones,
                'next_subscriber_milestone': next_sub_milestone,
                'next_view_milestone': next_view_milestone,
                'subscriber_milestone_progress': round(sub_progress, 1),
                'view_milestone_progress': round(view_progress, 1),
                'subscribers_to_next_milestone': next_sub_milestone - current_subs if next_sub_milestone else 0,
                'views_to_next_milestone': next_view_milestone - current_views if next_view_milestone else 0
            }
            
        except Exception as e:
            logger.error(f"Milestone tracking failed: {e}")
            return {}
    
    async def _analyze_performance(self, historical_data: List[ChannelMetrics]) -> Dict[str, Any]:
        """Analyze channel performance patterns"""
        try:
            if len(historical_data) < 7:
                return {}
            
            # Calculate various performance metrics
            subscriber_velocities = []
            view_velocities = []
            engagement_rates = []
            
            for i in range(1, len(historical_data)):
                prev = historical_data[i-1]
                curr = historical_data[i]
                
                sub_velocity = curr.subscribers - prev.subscribers
                view_velocity = curr.total_views - prev.total_views
                
                subscriber_velocities.append(sub_velocity)
                view_velocities.append(view_velocity)
                engagement_rates.append(curr.engagement_rate)
            
            # Calculate performance statistics
            avg_daily_sub_growth = sum(subscriber_velocities) / len(subscriber_velocities)
            avg_daily_view_growth = sum(view_velocities) / len(view_velocities)
            avg_engagement = sum(engagement_rates) / len(engagement_rates)
            
            # Find best and worst performing days
            best_sub_day = max(subscriber_velocities) if subscriber_velocities else 0
            worst_sub_day = min(subscriber_velocities) if subscriber_velocities else 0
            
            # Calculate consistency score (lower variance = more consistent)
            import statistics
            sub_variance = statistics.variance(subscriber_velocities) if len(subscriber_velocities) > 1 else 0
            consistency_score = max(0, 100 - (sub_variance / avg_daily_sub_growth * 100)) if avg_daily_sub_growth > 0 else 50
            
            return {
                'average_daily_subscriber_growth': round(avg_daily_sub_growth, 2),
                'average_daily_view_growth': round(avg_daily_view_growth, 2),
                'average_engagement_rate': round(avg_engagement, 4),
                'best_single_day_growth': best_sub_day,
                'worst_single_day_growth': worst_sub_day,
                'growth_consistency_score': round(consistency_score, 1),
                'performance_grade': await self._calculate_performance_grade(historical_data),
                'trending_direction': await self._calculate_trending_direction(subscriber_velocities)
            }
            
        except Exception as e:
            logger.error(f"Performance analysis failed: {e}")
            return {}
    
    async def _calculate_performance_grade(self, historical_data: List[ChannelMetrics]) -> str:
        """Calculate overall performance grade"""
        try:
            if len(historical_data) < 30:
                return 'N/A'
            
            recent_30 = historical_data[-30:]
            growth_rate = (recent_30[-1].subscribers - recent_30[0].subscribers) / recent_30[0].subscribers * 100
            
            if growth_rate >= 50:
                return 'A++'
            elif growth_rate >= 25:
                return 'A+'
            elif growth_rate >= 15:
                return 'A'
            elif growth_rate >= 10:
                return 'B+'
            elif growth_rate >= 5:
                return 'B'
            elif growth_rate >= 2:
                return 'C+'
            elif growth_rate >= 0:
                return 'C'
            elif growth_rate >= -5:
                return 'D'
            else:
                return 'F'
                
        except Exception:
            return 'N/A'
    
    async def _calculate_trending_direction(self, velocities: List[float]) -> str:
        """Calculate if growth is trending up, down, or stable"""
        try:
            if len(velocities) < 7:
                return 'stable'
            
            recent_week = velocities[-7:]
            previous_week = velocities[-14:-7] if len(velocities) >= 14 else velocities[:-7]
            
            recent_avg = sum(recent_week) / len(recent_week)
            previous_avg = sum(previous_week) / len(previous_week)
            
            change = recent_avg - previous_avg
            change_percentage = (change / previous_avg * 100) if previous_avg != 0 else 0
            
            if change_percentage > 10:
                return 'accelerating'
            elif change_percentage < -10:
                return 'declining'
            else:
                return 'stable'
                
        except Exception:
            return 'stable'
    
    async def _generate_growth_recommendations(self, channel_id: str, 
                                             historical_data: List[ChannelMetrics]) -> List[str]:
        """Generate growth recommendations based on performance"""
        recommendations = []
        
        try:
            if not historical_data:
                return ["No data available for recommendations"]
            
            current = historical_data[-1]
            
            # Analyze recent performance
            if len(historical_data) >= 30:
                recent_growth = (current.subscribers - historical_data[-30].subscribers) / 30
                
                if recent_growth < 1:
                    recommendations.append("📈 Focus on increasing upload frequency to boost growth")
                    recommendations.append("🎯 Analyze top-performing videos and create similar content")
                
                if current.engagement_rate < 0.03:
                    recommendations.append("💬 Improve engagement by asking questions and encouraging comments")
                    recommendations.append("👍 Add clear call-to-actions for likes and subscriptions")
                
                if current.upload_frequency < 1:
                    recommendations.append("⏰ Maintain consistent upload schedule (at least weekly)")
                
                if current.average_views < current.subscribers * 0.1:
                    recommendations.append("🔍 Optimize video titles and thumbnails for better click-through rates")
                    recommendations.append("📊 Use YouTube Analytics to understand audience retention")
            
            # General recommendations
            recommendations.extend([
                "🎨 A/B test thumbnails to improve click-through rates",
                "📝 Optimize video descriptions with relevant keywords",
                "🔗 Collaborate with other creators in your niche",
                "📱 Optimize content for mobile viewing",
                "⏰ Post at optimal times for your audience"
            ])
            
            return recommendations[:8]  # Limit to top 8
            
        except Exception as e:
            logger.error(f"Recommendations generation failed: {e}")
            return ["Unable to generate recommendations"]
    
    async def _get_channel_ranking(self, channel_id: str) -> Dict[str, Any]:
        """Get channel ranking information (simulated)"""
        try:
            current_metrics = await self._get_current_metrics(channel_id)
            subscribers = current_metrics.get('subscribers', 0)
            
            # Simulate ranking based on subscriber count
            if subscribers >= 1000000:
                global_rank = random.randint(1, 1000)
                grade = random.choice(['A++', 'A+', 'A'])
            elif subscribers >= 100000:
                global_rank = random.randint(1000, 10000)
                grade = random.choice(['A', 'B+', 'B'])
            elif subscribers >= 10000:
                global_rank = random.randint(10000, 100000)
                grade = random.choice(['B', 'C+', 'C'])
            else:
                global_rank = random.randint(100000, 1000000)
                grade = random.choice(['C', 'D', 'F'])
            
            return {
                'global_rank': global_rank,
                'country_rank': global_rank // 10,  # Approximate country rank
                'category_rank': global_rank // 50,  # Approximate category rank
                'grade': grade,
                'growth_grade': await self._calculate_performance_grade(self.channel_data.get(channel_id, [])),
                'subscriber_rank': global_rank,
                'view_rank': global_rank + random.randint(-500, 500)
            }
            
        except Exception as e:
            logger.error(f"Ranking calculation failed: {e}")
            return {}
    
    async def _calculate_performance_score(self, metrics: Dict[str, Any], 
                                         growth_data: Dict[str, Any]) -> float:
        """Calculate overall performance score"""
        try:
            # Weight different factors
            subscriber_score = min(100, math.log10(max(1, metrics.get('subscribers', 1))) * 15)
            engagement_score = metrics.get('engagement_rate', 0) * 1000
            growth_score = growth_data.get('growth_trends', {}).get('monthly', {}).get('subscriber_growth_rate', 0)
            
            total_score = (subscriber_score * 0.4 + engagement_score * 0.3 + growth_score * 0.3)
            
            return round(total_score, 2)
            
        except Exception:
            return 0.0
    
    async def _calculate_relative_performance(self, channel_data: Dict[str, Any], 
                                            best_performer: Dict[str, Any], 
                                            metric: str) -> Dict[str, Any]:
        """Calculate relative performance compared to best performer"""
        try:
            if not best_performer:
                return {}
            
            current_value = channel_data['current_metrics'].get(metric, 0)
            best_value = best_performer['current_metrics'].get(metric, 1)
            
            relative_percentage = (current_value / best_value * 100) if best_value > 0 else 0
            gap = best_value - current_value
            
            return {
                'relative_percentage': round(relative_percentage, 1),
                'gap_to_leader': gap,
                'performance_vs_leader': 'leading' if current_value >= best_value else 'following'
            }
            
        except Exception:
            return {}
    
    async def _find_growth_champion(self, comparison_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find the channel with the highest growth rate"""
        try:
            if not comparison_data:
                return {}
            
            # Sort by monthly growth rate
            sorted_by_growth = sorted(
                comparison_data,
                key=lambda x: x.get('growth_30d', {}).get('monthly', {}).get('subscriber_growth_rate', 0),
                reverse=True
            )
            
            growth_champion = sorted_by_growth[0]
            
            return {
                'channel_id': growth_champion['channel_id'],
                'growth_rate': growth_champion.get('growth_30d', {}).get('monthly', {}).get('subscriber_growth_rate', 0),
                'growth_velocity': growth_champion.get('growth_30d', {}).get('monthly', {}).get('growth_velocity', 'unknown')
            }
            
        except Exception:
            return {}
    
    async def _generate_comparison_insights(self, comparison_data: List[Dict[str, Any]], 
                                          metric: str) -> List[str]:
        """Generate insights from channel comparison"""
        insights = []
        
        try:
            if len(comparison_data) < 2:
                return ["Need at least 2 channels for meaningful comparison"]
            
            leader = comparison_data[0]
            last_place = comparison_data[-1]
            
            # Performance gap insight
            leader_value = leader['current_metrics'].get(metric, 0)
            last_value = last_place['current_metrics'].get(metric, 0)
            
            if leader_value > 0:
                gap_multiplier = leader_value / last_value if last_value > 0 else float('inf')
                insights.append(f"📊 Performance gap: Leader has {gap_multiplier:.1f}x more {metric}")
            
            # Growth insights
            fastest_grower = await self._find_growth_champion(comparison_data)
            if fastest_grower:
                insights.append(f"🚀 Fastest growing: {fastest_grower['channel_id']} with {fastest_grower['growth_rate']}% monthly growth")
            
            # Average performance
            avg_metric = sum(c['current_metrics'].get(metric, 0) for c in comparison_data) / len(comparison_data)
            insights.append(f"📈 Average {metric}: {avg_metric:,.0f}")
            
            # Performance distribution
            above_avg = len([c for c in comparison_data if c['current_metrics'].get(metric, 0) > avg_metric])
            insights.append(f"⚖️ {above_avg}/{len(comparison_data)} channels perform above average")
            
            return insights
            
        except Exception as e:
            logger.error(f"Comparison insights failed: {e}")
            return ["Unable to generate insights"]

# Global instance
growth_tracker = GrowthTracker()