"""
Sophisticated Supporter Analytics
Advanced analytics and insights for patron/supporter management
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import math

logger = logging.getLogger(__name__)

@dataclass
class SupporterProfile:
    """Comprehensive supporter profile"""
    supporter_id: str
    name: str
    platform: str
    tier: str
    monthly_amount: float
    total_contribution: float
    join_date: datetime
    last_active: datetime
    engagement_score: float
    loyalty_score: float
    risk_score: float  # Risk of churning
    preferred_benefits: List[str] = field(default_factory=list)
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)
    content_preferences: Dict[str, float] = field(default_factory=dict)
    demographics: Dict[str, Any] = field(default_factory=dict)
    social_influence: float = 0.0  # Influence on other supporters

@dataclass
class SupporterSegment:
    """Supporter segment analysis"""
    name: str
    criteria: Dict[str, Any]
    supporters: List[str]
    total_revenue: float
    average_contribution: float
    retention_rate: float
    growth_rate: float
    churn_risk: float
    recommended_actions: List[str] = field(default_factory=list)

@dataclass
class RevenueAnalysis:
    """Revenue analysis and forecasting"""
    period: str
    total_revenue: float
    recurring_revenue: float
    one_time_revenue: float
    revenue_by_tier: Dict[str, float]
    revenue_by_platform: Dict[str, float]
    growth_rate: float
    churn_rate: float
    forecasted_revenue: Dict[str, float]
    risk_factors: List[str] = field(default_factory=list)

@dataclass
class SupporterInsight:
    """Actionable supporter insight"""
    insight_type: str
    title: str
    description: str
    impact_score: float
    action_items: List[str]
    affected_supporters: List[str]
    potential_revenue_impact: float

class SupporterAnalytics:
    """Advanced supporter analytics and insights"""
    
    def __init__(self):
        self.module_name = "supporter_analytics"
        
        # Data storage
        self.supporter_profiles: Dict[str, SupporterProfile] = {}
        self.supporter_segments: Dict[str, SupporterSegment] = {}
        self.revenue_history: List[RevenueAnalysis] = []
        self.insights: List[SupporterInsight] = []
        
        # Analytics settings
        self.analytics_settings = {
            "churn_prediction_window": 30,  # days
            "min_segment_size": 5,
            "loyalty_score_weights": {
                "tenure": 0.3,
                "consistency": 0.2,
                "tier_upgrades": 0.2,
                "engagement": 0.3
            },
            "risk_factors": {
                "payment_failures": 0.4,
                "declining_engagement": 0.3,
                "tier_downgrades": 0.3
            }
        }
        
        # Predefined segments
        self.segment_definitions = {
            "vip_supporters": {
                "criteria": {
                    "monthly_amount": {"min": 50},
                    "loyalty_score": {"min": 0.8}
                },
                "description": "High-value, loyal supporters"
            },
            "growing_supporters": {
                "criteria": {
                    "tier_upgrades": {"min": 1},
                    "tenure_days": {"min": 30}
                },
                "description": "Supporters who have upgraded their support"
            },
            "at_risk_supporters": {
                "criteria": {
                    "risk_score": {"min": 0.7},
                    "monthly_amount": {"min": 5}
                },
                "description": "Supporters at risk of churning"
            },
            "new_supporters": {
                "criteria": {
                    "tenure_days": {"max": 30}
                },
                "description": "Recently joined supporters"
            },
            "consistent_supporters": {
                "criteria": {
                    "payment_consistency": {"min": 0.9},
                    "tenure_days": {"min": 90}
                },
                "description": "Reliable, consistent supporters"
            },
            "high_engagement": {
                "criteria": {
                    "engagement_score": {"min": 0.7}
                },
                "description": "Highly engaged supporters"
            }
        }
        
        # Tier analysis templates
        self.tier_templates = {
            "bronze": {"min_amount": 5, "benefits": 3, "expected_retention": 0.7},
            "silver": {"min_amount": 15, "benefits": 5, "expected_retention": 0.8},
            "gold": {"min_amount": 30, "benefits": 7, "expected_retention": 0.85},
            "platinum": {"min_amount": 50, "benefits": 10, "expected_retention": 0.9},
            "diamond": {"min_amount": 100, "benefits": 15, "expected_retention": 0.95}
        }
    
    async def analyze_supporter_profile(
        self,
        supporter_data: Dict[str, Any],
        interaction_history: List[Dict[str, Any]] = None
    ) -> SupporterProfile:
        """Create comprehensive supporter profile"""
        try:
            supporter_id = supporter_data.get("id", "")
            
            # Calculate scores
            engagement_score = await self._calculate_engagement_score(supporter_data, interaction_history or [])
            loyalty_score = await self._calculate_loyalty_score(supporter_data)
            risk_score = await self._calculate_risk_score(supporter_data, interaction_history or [])
            
            # Analyze preferences
            content_preferences = await self._analyze_content_preferences(interaction_history or [])
            preferred_benefits = await self._identify_preferred_benefits(supporter_data, interaction_history or [])
            
            # Calculate social influence
            social_influence = await self._calculate_social_influence(supporter_data)
            
            profile = SupporterProfile(
                supporter_id=supporter_id,
                name=supporter_data.get("name", ""),
                platform=supporter_data.get("platform", ""),
                tier=supporter_data.get("tier", ""),
                monthly_amount=float(supporter_data.get("monthly_amount", 0)),
                total_contribution=float(supporter_data.get("total_contribution", 0)),
                join_date=self._parse_date(supporter_data.get("join_date")),
                last_active=self._parse_date(supporter_data.get("last_active")),
                engagement_score=engagement_score,
                loyalty_score=loyalty_score,
                risk_score=risk_score,
                preferred_benefits=preferred_benefits,
                interaction_history=interaction_history or [],
                content_preferences=content_preferences,
                demographics=supporter_data.get("demographics", {}),
                social_influence=social_influence
            )
            
            self.supporter_profiles[supporter_id] = profile
            return profile
            
        except Exception as e:
            logger.error(f"Error analyzing supporter profile: {str(e)}")
            raise
    
    async def _calculate_engagement_score(
        self,
        supporter_data: Dict[str, Any],
        interaction_history: List[Dict[str, Any]]
    ) -> float:
        """Calculate supporter engagement score"""
        try:
            score = 0.0
            
            # Comment activity
            comments_count = len([i for i in interaction_history if i.get("type") == "comment"])
            comment_score = min(comments_count / 10, 1.0) * 0.3
            
            # Message/DM activity
            messages_count = len([i for i in interaction_history if i.get("type") == "message"])
            message_score = min(messages_count / 5, 1.0) * 0.2
            
            # Community participation
            community_activity = supporter_data.get("community_posts_liked", 0)
            community_score = min(community_activity / 20, 1.0) * 0.2
            
            # Content consumption
            watch_time = supporter_data.get("total_watch_time", 0)
            watch_score = min(watch_time / 3600, 1.0) * 0.2  # 1 hour = max score
            
            # Special events participation
            events_attended = supporter_data.get("events_attended", 0)
            event_score = min(events_attended / 3, 1.0) * 0.1
            
            score = comment_score + message_score + community_score + watch_score + event_score
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating engagement score: {str(e)}")
            return 0.0
    
    async def _calculate_loyalty_score(self, supporter_data: Dict[str, Any]) -> float:
        """Calculate supporter loyalty score"""
        try:
            weights = self.analytics_settings["loyalty_score_weights"]
            
            # Tenure component
            join_date = self._parse_date(supporter_data.get("join_date"))
            if join_date:
                tenure_days = (datetime.utcnow() - join_date).days
                tenure_score = min(tenure_days / 365, 1.0)  # 1 year = max tenure score
            else:
                tenure_score = 0
            
            # Payment consistency
            payment_history = supporter_data.get("payment_history", [])
            if payment_history:
                successful_payments = len([p for p in payment_history if p.get("status") == "success"])
                consistency_score = successful_payments / len(payment_history)
            else:
                consistency_score = 0
            
            # Tier upgrades
            tier_upgrades = supporter_data.get("tier_upgrades", 0)
            upgrade_score = min(tier_upgrades / 3, 1.0)  # 3 upgrades = max score
            
            # Engagement score (already calculated)
            engagement_score = supporter_data.get("engagement_score", 0)
            
            loyalty_score = (
                tenure_score * weights["tenure"] +
                consistency_score * weights["consistency"] +
                upgrade_score * weights["tier_upgrades"] +
                engagement_score * weights["engagement"]
            )
            
            return min(loyalty_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating loyalty score: {str(e)}")
            return 0.0
    
    async def _calculate_risk_score(
        self,
        supporter_data: Dict[str, Any],
        interaction_history: List[Dict[str, Any]]
    ) -> float:
        """Calculate churn risk score"""
        try:
            risk_factors = self.analytics_settings["risk_factors"]
            risk_score = 0.0
            
            # Payment failures
            payment_history = supporter_data.get("payment_history", [])
            if payment_history:
                recent_payments = [p for p in payment_history if self._is_recent(p.get("date"), 90)]
                if recent_payments:
                    failed_payments = len([p for p in recent_payments if p.get("status") == "failed"])
                    payment_risk = failed_payments / len(recent_payments)
                    risk_score += payment_risk * risk_factors["payment_failures"]
            
            # Declining engagement
            recent_interactions = [i for i in interaction_history if self._is_recent(i.get("date"), 30)]
            previous_interactions = [i for i in interaction_history 
                                   if self._is_recent(i.get("date"), 60) and not self._is_recent(i.get("date"), 30)]
            
            if previous_interactions:
                recent_count = len(recent_interactions)
                previous_count = len(previous_interactions)
                
                if recent_count < previous_count * 0.5:  # 50% drop
                    risk_score += risk_factors["declining_engagement"]
            
            # Tier downgrades
            tier_downgrades = supporter_data.get("tier_downgrades", 0)
            if tier_downgrades > 0:
                risk_score += min(tier_downgrades / 2, 1.0) * risk_factors["tier_downgrades"]
            
            # Last activity
            last_active = self._parse_date(supporter_data.get("last_active"))
            if last_active:
                days_inactive = (datetime.utcnow() - last_active).days
                if days_inactive > 30:
                    inactivity_risk = min(days_inactive / 90, 1.0) * 0.3
                    risk_score += inactivity_risk
            
            return min(risk_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating risk score: {str(e)}")
            return 0.0
    
    async def _analyze_content_preferences(self, interaction_history: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze supporter's content preferences"""
        try:
            preferences = defaultdict(float)
            
            for interaction in interaction_history:
                content_type = interaction.get("content_type", "")
                engagement_level = interaction.get("engagement_level", 1.0)
                
                if content_type:
                    preferences[content_type] += engagement_level
            
            # Normalize scores
            if preferences:
                total_score = sum(preferences.values())
                preferences = {k: v / total_score for k, v in preferences.items()}
            
            return dict(preferences)
            
        except Exception as e:
            logger.error(f"Error analyzing content preferences: {str(e)}")
            return {}
    
    async def _identify_preferred_benefits(
        self,
        supporter_data: Dict[str, Any],
        interaction_history: List[Dict[str, Any]]
    ) -> List[str]:
        """Identify supporter's preferred benefits"""
        try:
            benefit_usage = Counter()
            
            # Analyze benefit usage from interaction history
            for interaction in interaction_history:
                benefit_used = interaction.get("benefit_used", "")
                if benefit_used:
                    benefit_usage[benefit_used] += 1
            
            # Also check from supporter data
            used_benefits = supporter_data.get("benefits_used", [])
            for benefit in used_benefits:
                benefit_usage[benefit] += 1
            
            # Return top 5 most used benefits
            preferred = [benefit for benefit, _ in benefit_usage.most_common(5)]
            return preferred
            
        except Exception as e:
            logger.error(f"Error identifying preferred benefits: {str(e)}")
            return []
    
    async def _calculate_social_influence(self, supporter_data: Dict[str, Any]) -> float:
        """Calculate supporter's social influence on others"""
        try:
            # Factors that contribute to social influence
            followers_count = supporter_data.get("social_followers", 0)
            referrals_made = supporter_data.get("referrals_made", 0)
            public_support = supporter_data.get("public_support_actions", 0)
            
            # Normalize and weight factors
            follower_score = min(followers_count / 10000, 1.0) * 0.4  # 10k followers = max
            referral_score = min(referrals_made / 5, 1.0) * 0.4      # 5 referrals = max
            public_score = min(public_support / 10, 1.0) * 0.2       # 10 actions = max
            
            influence_score = follower_score + referral_score + public_score
            return min(influence_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating social influence: {str(e)}")
            return 0.0
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime"""
        if not date_str:
            return None
        
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except:
            return None
    
    def _is_recent(self, date_str: Optional[str], days: int) -> bool:
        """Check if date is within recent days"""
        if not date_str:
            return False
        
        date = self._parse_date(date_str)
        if not date:
            return False
        
        return (datetime.utcnow() - date.replace(tzinfo=None)).days <= days
    
    async def segment_supporters(self, custom_segments: Dict[str, Any] = None) -> Dict[str, SupporterSegment]:
        """Segment supporters based on behavior and value"""
        try:
            # Combine default and custom segments
            segments_to_analyze = self.segment_definitions.copy()
            if custom_segments:
                segments_to_analyze.update(custom_segments)
            
            segments = {}
            
            for segment_name, segment_config in segments_to_analyze.items():
                criteria = segment_config["criteria"]
                matching_supporters = []
                
                # Find supporters matching criteria
                for supporter_id, profile in self.supporter_profiles.items():
                    if await self._supporter_matches_criteria(profile, criteria):
                        matching_supporters.append(supporter_id)
                
                if len(matching_supporters) >= self.analytics_settings["min_segment_size"]:
                    # Calculate segment metrics
                    segment_metrics = await self._calculate_segment_metrics(matching_supporters)
                    
                    segment = SupporterSegment(
                        name=segment_name,
                        criteria=criteria,
                        supporters=matching_supporters,
                        **segment_metrics
                    )
                    
                    segments[segment_name] = segment
                    self.supporter_segments[segment_name] = segment
            
            logger.info(f"Created {len(segments)} supporter segments")
            return segments
            
        except Exception as e:
            logger.error(f"Error segmenting supporters: {str(e)}")
            return {}
    
    async def _supporter_matches_criteria(self, profile: SupporterProfile, criteria: Dict[str, Any]) -> bool:
        """Check if supporter matches segment criteria"""
        try:
            for criterion, condition in criteria.items():
                # Get value from profile
                if criterion == "tenure_days":
                    if profile.join_date:
                        value = (datetime.utcnow() - profile.join_date.replace(tzinfo=None)).days
                    else:
                        value = 0
                elif criterion == "payment_consistency":
                    # This would be calculated from payment history
                    value = 0.8  # Placeholder
                elif criterion == "tier_upgrades":
                    # This would be calculated from upgrade history
                    value = 0  # Placeholder
                else:
                    value = getattr(profile, criterion, None)
                
                if value is None:
                    continue
                
                # Check condition
                if isinstance(condition, dict):
                    min_val = condition.get("min")
                    max_val = condition.get("max")
                    
                    if min_val is not None and value < min_val:
                        return False
                    if max_val is not None and value > max_val:
                        return False
                else:
                    if value != condition:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking supporter criteria: {str(e)}")
            return False
    
    async def _calculate_segment_metrics(self, supporter_ids: List[str]) -> Dict[str, Any]:
        """Calculate metrics for a supporter segment"""
        try:
            if not supporter_ids:
                return {
                    "total_revenue": 0,
                    "average_contribution": 0,
                    "retention_rate": 0,
                    "growth_rate": 0,
                    "churn_risk": 0
                }
            
            profiles = [self.supporter_profiles[sid] for sid in supporter_ids 
                       if sid in self.supporter_profiles]
            
            if not profiles:
                return {
                    "total_revenue": 0,
                    "average_contribution": 0,
                    "retention_rate": 0,
                    "growth_rate": 0,
                    "churn_risk": 0
                }
            
            # Calculate metrics
            total_revenue = sum(p.monthly_amount for p in profiles)
            average_contribution = total_revenue / len(profiles)
            
            # Retention rate (simplified)
            active_supporters = len([p for p in profiles if p.risk_score < 0.5])
            retention_rate = active_supporters / len(profiles)
            
            # Growth rate (placeholder - would calculate from historical data)
            growth_rate = 0.05
            
            # Average churn risk
            avg_churn_risk = sum(p.risk_score for p in profiles) / len(profiles)
            
            return {
                "total_revenue": total_revenue,
                "average_contribution": average_contribution,
                "retention_rate": retention_rate,
                "growth_rate": growth_rate,
                "churn_risk": avg_churn_risk
            }
            
        except Exception as e:
            logger.error(f"Error calculating segment metrics: {str(e)}")
            return {
                "total_revenue": 0,
                "average_contribution": 0,
                "retention_rate": 0,
                "growth_rate": 0,
                "churn_risk": 0
            }
    
    async def analyze_revenue_trends(
        self,
        period_months: int = 12
    ) -> RevenueAnalysis:
        """Analyze revenue trends and create forecasts"""
        try:
            # Calculate current period metrics
            current_date = datetime.utcnow()
            period_start = current_date - timedelta(days=period_months * 30)
            
            # Get active supporters
            active_supporters = [p for p in self.supporter_profiles.values() 
                               if p.last_active and p.last_active > period_start.replace(tzinfo=None)]
            
            # Calculate revenue metrics
            total_revenue = sum(p.monthly_amount for p in active_supporters)
            recurring_revenue = sum(p.monthly_amount for p in active_supporters if p.platform in ["patreon"])
            one_time_revenue = total_revenue - recurring_revenue
            
            # Revenue by tier
            revenue_by_tier = defaultdict(float)
            for supporter in active_supporters:
                revenue_by_tier[supporter.tier] += supporter.monthly_amount
            
            # Revenue by platform
            revenue_by_platform = defaultdict(float)
            for supporter in active_supporters:
                revenue_by_platform[supporter.platform] += supporter.monthly_amount
            
            # Calculate growth rate (simplified)
            growth_rate = 0.08  # Placeholder
            
            # Calculate churn rate
            at_risk_supporters = [p for p in active_supporters if p.risk_score > 0.7]
            churn_rate = len(at_risk_supporters) / max(len(active_supporters), 1)
            
            # Generate forecast
            forecasted_revenue = await self._forecast_revenue(
                total_revenue, growth_rate, churn_rate, period_months
            )
            
            # Identify risk factors
            risk_factors = await self._identify_revenue_risks(active_supporters)
            
            analysis = RevenueAnalysis(
                period=f"{period_months}_months",
                total_revenue=total_revenue,
                recurring_revenue=recurring_revenue,
                one_time_revenue=one_time_revenue,
                revenue_by_tier=dict(revenue_by_tier),
                revenue_by_platform=dict(revenue_by_platform),
                growth_rate=growth_rate,
                churn_rate=churn_rate,
                forecasted_revenue=forecasted_revenue,
                risk_factors=risk_factors
            )
            
            self.revenue_history.append(analysis)
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing revenue trends: {str(e)}")
            raise
    
    async def _forecast_revenue(
        self,
        current_revenue: float,
        growth_rate: float,
        churn_rate: float,
        periods: int
    ) -> Dict[str, float]:
        """Forecast revenue for future periods"""
        try:
            forecast = {}
            
            for month in range(1, min(periods, 12) + 1):
                # Apply growth and churn
                net_growth_rate = growth_rate - churn_rate
                forecasted = current_revenue * ((1 + net_growth_rate) ** month)
                
                forecast[f"month_{month}"] = round(forecasted, 2)
            
            return forecast
            
        except Exception as e:
            logger.error(f"Error forecasting revenue: {str(e)}")
            return {}
    
    async def _identify_revenue_risks(self, supporters: List[SupporterProfile]) -> List[str]:
        """Identify potential revenue risks"""
        try:
            risks = []
            
            # High churn risk
            high_risk_count = len([s for s in supporters if s.risk_score > 0.7])
            if high_risk_count > len(supporters) * 0.2:  # More than 20%
                risks.append(f"High churn risk: {high_risk_count} supporters at risk")
            
            # Tier concentration risk
            tier_distribution = Counter(s.tier for s in supporters)
            max_tier_percentage = max(tier_distribution.values()) / len(supporters)
            if max_tier_percentage > 0.6:  # More than 60% in one tier
                risks.append("Revenue concentration in single tier")
            
            # Platform concentration risk
            platform_distribution = Counter(s.platform for s in supporters)
            max_platform_percentage = max(platform_distribution.values()) / len(supporters)
            if max_platform_percentage > 0.8:  # More than 80% on one platform
                risks.append("Revenue concentration on single platform")
            
            # Low engagement risk
            low_engagement_count = len([s for s in supporters if s.engagement_score < 0.3])
            if low_engagement_count > len(supporters) * 0.3:  # More than 30%
                risks.append("High percentage of low-engagement supporters")
            
            return risks
            
        except Exception as e:
            logger.error(f"Error identifying revenue risks: {str(e)}")
            return []
    
    async def generate_supporter_insights(self) -> List[SupporterInsight]:
        """Generate actionable insights about supporters"""
        try:
            insights = []
            
            # Analyze churn risk
            high_risk_supporters = [
                p for p in self.supporter_profiles.values() 
                if p.risk_score > 0.7 and p.monthly_amount >= 10
            ]
            
            if high_risk_supporters:
                revenue_at_risk = sum(s.monthly_amount for s in high_risk_supporters)
                insight = SupporterInsight(
                    insight_type="churn_risk",
                    title="High-Value Supporters at Risk",
                    description=f"{len(high_risk_supporters)} high-value supporters are at risk of churning",
                    impact_score=0.8,
                    action_items=[
                        "Send personalized retention messages",
                        "Offer exclusive content or benefits",
                        "Schedule one-on-one check-ins"
                    ],
                    affected_supporters=[s.supporter_id for s in high_risk_supporters],
                    potential_revenue_impact=revenue_at_risk
                )
                insights.append(insight)
            
            # Analyze upgrade opportunities
            upgrade_candidates = [
                p for p in self.supporter_profiles.values()
                if p.loyalty_score > 0.7 and p.engagement_score > 0.6 and p.monthly_amount < 25
            ]
            
            if upgrade_candidates:
                potential_revenue = len(upgrade_candidates) * 10  # Assume $10 average upgrade
                insight = SupporterInsight(
                    insight_type="upgrade_opportunity",
                    title="Supporters Ready for Tier Upgrades",
                    description=f"{len(upgrade_candidates)} loyal supporters may be ready to upgrade",
                    impact_score=0.6,
                    action_items=[
                        "Present tier upgrade benefits",
                        "Offer limited-time upgrade incentives",
                        "Highlight exclusive higher-tier content"
                    ],
                    affected_supporters=[s.supporter_id for s in upgrade_candidates],
                    potential_revenue_impact=potential_revenue
                )
                insights.append(insight)
            
            # Analyze new supporter onboarding
            new_supporters = [
                p for p in self.supporter_profiles.values()
                if p.join_date and (datetime.utcnow() - p.join_date.replace(tzinfo=None)).days <= 30
            ]
            
            if new_supporters:
                low_engagement_new = [s for s in new_supporters if s.engagement_score < 0.4]
                if len(low_engagement_new) > len(new_supporters) * 0.4:  # More than 40%
                    insight = SupporterInsight(
                        insight_type="onboarding",
                        title="New Supporter Onboarding Needs Improvement",
                        description=f"{len(low_engagement_new)} of {len(new_supporters)} new supporters show low engagement",
                        impact_score=0.7,
                        action_items=[
                            "Improve onboarding sequence",
                            "Send welcome content package",
                            "Create new supporter community events"
                        ],
                        affected_supporters=[s.supporter_id for s in low_engagement_new],
                        potential_revenue_impact=0  # Retention focused
                    )
                    insights.append(insight)
            
            # Analyze benefit utilization
            all_supporters = list(self.supporter_profiles.values())
            if all_supporters:
                avg_benefits_used = sum(len(s.preferred_benefits) for s in all_supporters) / len(all_supporters)
                if avg_benefits_used < 2:  # Less than 2 benefits per supporter
                    insight = SupporterInsight(
                        insight_type="benefit_utilization",
                        title="Low Benefit Utilization",
                        description="Supporters are not fully utilizing available benefits",
                        impact_score=0.5,
                        action_items=[
                            "Educate supporters about available benefits",
                            "Simplify benefit access process",
                            "Send monthly benefit reminders"
                        ],
                        affected_supporters=[s.supporter_id for s in all_supporters],
                        potential_revenue_impact=0  # Satisfaction focused
                    )
                    insights.append(insight)
            
            self.insights.extend(insights)
            logger.info(f"Generated {len(insights)} supporter insights")
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating supporter insights: {str(e)}")
            return []
    
    async def get_supporter_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        try:
            total_supporters = len(self.supporter_profiles)
            
            if total_supporters == 0:
                return {"error": "No supporter data available"}
            
            # Summary metrics
            total_monthly_revenue = sum(s.monthly_amount for s in self.supporter_profiles.values())
            avg_contribution = total_monthly_revenue / total_supporters
            
            # Risk analysis
            high_risk_count = len([s for s in self.supporter_profiles.values() if s.risk_score > 0.7])
            churn_risk_percentage = (high_risk_count / total_supporters) * 100
            
            # Loyalty analysis
            high_loyalty_count = len([s for s in self.supporter_profiles.values() if s.loyalty_score > 0.7])
            loyalty_percentage = (high_loyalty_count / total_supporters) * 100
            
            # Tier distribution
            tier_distribution = Counter(s.tier for s in self.supporter_profiles.values())
            
            # Platform distribution
            platform_distribution = Counter(s.platform for s in self.supporter_profiles.values())
            
            # Recent trends
            recent_insights = self.insights[-5:] if self.insights else []
            
            # Top supporters by value
            top_supporters = sorted(
                self.supporter_profiles.values(),
                key=lambda x: x.monthly_amount,
                reverse=True
            )[:10]
            
            return {
                "summary": {
                    "total_supporters": total_supporters,
                    "monthly_revenue": total_monthly_revenue,
                    "average_contribution": avg_contribution,
                    "churn_risk_percentage": churn_risk_percentage,
                    "loyalty_percentage": loyalty_percentage
                },
                "distributions": {
                    "tiers": dict(tier_distribution),
                    "platforms": dict(platform_distribution)
                },
                "insights": [
                    {
                        "type": insight.insight_type,
                        "title": insight.title,
                        "description": insight.description,
                        "impact_score": insight.impact_score,
                        "action_items": insight.action_items
                    }
                    for insight in recent_insights
                ],
                "top_supporters": [
                    {
                        "name": s.name,
                        "tier": s.tier,
                        "monthly_amount": s.monthly_amount,
                        "loyalty_score": s.loyalty_score,
                        "risk_score": s.risk_score
                    }
                    for s in top_supporters
                ],
                "segments": {
                    name: {
                        "size": segment.total_revenue,
                        "average_contribution": segment.average_contribution,
                        "retention_rate": segment.retention_rate
                    }
                    for name, segment in self.supporter_segments.items()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {str(e)}")
            return {"error": str(e)}
    
    def export_supporter_data(self, include_personal_data: bool = False) -> Dict[str, Any]:
        """Export supporter analytics data"""
        try:
            export_data = {
                "summary_stats": {
                    "total_supporters": len(self.supporter_profiles),
                    "total_segments": len(self.supporter_segments),
                    "total_insights": len(self.insights)
                },
                "segments": {
                    name: {
                        "supporter_count": len(segment.supporters),
                        "total_revenue": segment.total_revenue,
                        "average_contribution": segment.average_contribution,
                        "retention_rate": segment.retention_rate,
                        "churn_risk": segment.churn_risk
                    }
                    for name, segment in self.supporter_segments.items()
                },
                "insights": [
                    {
                        "type": insight.insight_type,
                        "title": insight.title,
                        "impact_score": insight.impact_score,
                        "potential_revenue_impact": insight.potential_revenue_impact
                    }
                    for insight in self.insights
                ],
                "revenue_analysis": [
                    {
                        "period": analysis.period,
                        "total_revenue": analysis.total_revenue,
                        "growth_rate": analysis.growth_rate,
                        "churn_rate": analysis.churn_rate
                    }
                    for analysis in self.revenue_history
                ],
                "export_timestamp": datetime.utcnow().isoformat()
            }
            
            # Include personal data only if explicitly requested and authorized
            if include_personal_data:
                export_data["supporter_profiles"] = {
                    supporter_id: {
                        "name": profile.name,
                        "tier": profile.tier,
                        "monthly_amount": profile.monthly_amount,
                        "loyalty_score": profile.loyalty_score,
                        "risk_score": profile.risk_score,
                        "engagement_score": profile.engagement_score
                    }
                    for supporter_id, profile in self.supporter_profiles.items()
                }
            
            return export_data
            
        except Exception as e:
            logger.error(f"Error exporting supporter data: {str(e)}")
            return {"error": str(e)}