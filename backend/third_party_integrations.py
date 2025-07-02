"""
Third-Party Integrations Manager
Coordinates VidIQ, Social Blade, and TubeBuddy integrations for comprehensive YouTube analytics
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from vidiq_integration import VidIQIntegration, initialize_vidiq
from socialblade_integration import SocialBladeIntegration, initialize_socialblade
from tubebuddy_integration import TubeBuddyIntegration, initialize_tubebuddy

logger = logging.getLogger(__name__)

class ThirdPartyIntegrationsManager:
    """Comprehensive manager for all third-party YouTube analytics integrations"""
    
    def __init__(self):
        self.vidiq: Optional[VidIQIntegration] = None
        self.socialblade: Optional[SocialBladeIntegration] = None
        self.tubebuddy: Optional[TubeBuddyIntegration] = None
        self.initialized = False
        
    async def initialize(self, api_keys: Dict[str, str] = None):
        """Initialize all integrations with their respective API keys"""
        try:
            api_keys = api_keys or {}
            
            # Initialize VidIQ
            self.vidiq = await initialize_vidiq(api_keys.get('vidiq_api_key'))
            logger.info("VidIQ integration initialized")
            
            # Initialize Social Blade
            self.socialblade = await initialize_socialblade(api_keys.get('socialblade_api_key'))
            logger.info("Social Blade integration initialized")
            
            # Initialize TubeBuddy
            self.tubebuddy = await initialize_tubebuddy(api_keys.get('tubebuddy_api_key'))
            logger.info("TubeBuddy integration initialized")
            
            self.initialized = True
            logger.info("All third-party integrations initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize integrations: {str(e)}")
            raise
    
    async def cleanup(self):
        """Cleanup all integration resources"""
        try:
            if self.vidiq:
                await self.vidiq.cleanup()
            if self.socialblade:
                await self.socialblade.cleanup()
            if self.tubebuddy:
                await self.tubebuddy.cleanup()
            
            self.initialized = False
            logger.info("All integrations cleaned up")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    async def comprehensive_channel_analysis(self, channel_id: str) -> Dict[str, Any]:
        """Perform comprehensive analysis using all integrated services"""
        if not self.initialized:
            raise RuntimeError("Integrations not initialized")
        
        try:
            # Run all analyses in parallel for efficiency
            tasks = [
                self._get_vidiq_analysis(channel_id),
                self._get_socialblade_analysis(channel_id),
                self._get_tubebuddy_analysis(channel_id)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine results
            comprehensive_report = {
                "channel_id": channel_id,
                "analysis_timestamp": datetime.now().isoformat(),
                "vidiq_analysis": results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])},
                "socialblade_analysis": results[1] if not isinstance(results[1], Exception) else {"error": str(results[1])},
                "tubebuddy_analysis": results[2] if not isinstance(results[2], Exception) else {"error": str(results[2])},
                "combined_insights": await self._generate_combined_insights(results, channel_id)
            }
            
            return comprehensive_report
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {str(e)}")
            raise
    
    async def _get_vidiq_analysis(self, channel_id: str) -> Dict[str, Any]:
        """Get VidIQ analysis"""
        try:
            growth_insights = await self.vidiq.get_channel_growth_insights(channel_id)
            trending_topics = await self.vidiq.get_trending_topics()
            
            return {
                "service": "VidIQ",
                "growth_insights": growth_insights,
                "trending_topics": trending_topics[:5],  # Top 5 topics
                "status": "success"
            }
        except Exception as e:
            logger.error(f"VidIQ analysis error: {str(e)}")
            return {"service": "VidIQ", "status": "error", "error": str(e)}
    
    async def _get_socialblade_analysis(self, channel_id: str) -> Dict[str, Any]:
        """Get Social Blade analysis"""
        try:
            channel_stats = await self.socialblade.get_channel_stats(channel_id)
            growth_metrics = await self.socialblade.get_growth_metrics(channel_id)
            
            return {
                "service": "Social Blade",
                "channel_stats": channel_stats.to_dict(),
                "growth_metrics": growth_metrics.to_dict(),
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Social Blade analysis error: {str(e)}")
            return {"service": "Social Blade", "status": "error", "error": str(e)}
    
    async def _get_tubebuddy_analysis(self, channel_id: str) -> Dict[str, Any]:
        """Get TubeBuddy analysis"""
        try:
            upload_time_analysis = await self.tubebuddy.get_best_upload_time(channel_id)
            channel_health = await self.tubebuddy.get_channel_health_score(channel_id)
            
            return {
                "service": "TubeBuddy",
                "upload_optimization": upload_time_analysis.to_dict(),
                "channel_health": channel_health,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"TubeBuddy analysis error: {str(e)}")
            return {"service": "TubeBuddy", "status": "error", "error": str(e)}
    
    async def _generate_combined_insights(self, results: List[Any], channel_id: str) -> Dict[str, Any]:
        """Generate combined insights from all services"""
        try:
            insights = {
                "overall_health_score": 0,
                "top_recommendations": [],
                "growth_potential": "unknown",
                "optimization_priority": [],
                "competitive_position": "unknown",
                "content_strategy_suggestions": []
            }
            
            valid_results = [r for r in results if not isinstance(r, Exception) and r.get("status") == "success"]
            
            if not valid_results:
                return {"error": "No valid results from any service"}
            
            # Calculate overall health score
            health_scores = []
            for result in valid_results:
                if "channel_health" in result and "overall_score" in result["channel_health"]:
                    health_scores.append(result["channel_health"]["overall_score"])
            
            if health_scores:
                insights["overall_health_score"] = sum(health_scores) / len(health_scores)
            
            # Combine recommendations
            all_recommendations = []
            for result in valid_results:
                if "growth_insights" in result and "content_recommendations" in result["growth_insights"]:
                    all_recommendations.extend(result["growth_insights"]["content_recommendations"])
                if "channel_health" in result and "recommendations" in result["channel_health"]:
                    all_recommendations.extend(result["channel_health"]["recommendations"])
            
            # Get unique recommendations
            insights["top_recommendations"] = list(set(all_recommendations))[:10]
            
            # Determine growth potential
            growth_rates = []
            for result in valid_results:
                if "growth_metrics" in result:
                    monthly_growth = result["growth_metrics"].get("monthly_growth", 0)
                    if isinstance(monthly_growth, (int, float)):
                        growth_rates.append(monthly_growth)
            
            if growth_rates:
                avg_growth = sum(growth_rates) / len(growth_rates)
                if avg_growth > 10:
                    insights["growth_potential"] = "high"
                elif avg_growth > 5:
                    insights["growth_potential"] = "medium"
                else:
                    insights["growth_potential"] = "low"
            
            # Generate content strategy suggestions
            insights["content_strategy_suggestions"] = [
                "Focus on trending topics identified by VidIQ",
                "Optimize upload times based on TubeBuddy analysis",
                "Monitor competitor performance through Social Blade",
                "Improve video SEO using combined keyword insights",
                "Maintain consistent upload schedule for better growth"
            ]
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating combined insights: {str(e)}")
            return {"error": str(e)}
    
    async def keyword_research_suite(self, topic: str, channel_id: str) -> Dict[str, Any]:
        """Comprehensive keyword research using all services"""
        if not self.initialized:
            raise RuntimeError("Integrations not initialized")
        
        try:
            # Get keyword data from VidIQ
            vidiq_keywords = await self.vidiq.get_keyword_suggestions(channel_id, topic)
            
            # Get trending content from Social Blade
            trending_content = await self.socialblade.get_trending_content(topic)
            
            # Get tag suggestions from TubeBuddy
            tubebuddy_tags = await self.tubebuddy.get_tag_suggestions(topic)
            
            # Combine and analyze
            keyword_suite = {
                "topic": topic,
                "analysis_timestamp": datetime.now().isoformat(),
                "vidiq_keywords": [k.to_dict() for k in vidiq_keywords],
                "trending_content": trending_content,
                "tubebuddy_tags": [t.to_dict() for t in tubebuddy_tags],
                "combined_recommendations": await self._combine_keyword_insights(vidiq_keywords, trending_content, tubebuddy_tags)
            }
            
            return keyword_suite
            
        except Exception as e:
            logger.error(f"Error in keyword research suite: {str(e)}")
            raise
    
    async def _combine_keyword_insights(self, vidiq_keywords, trending_content, tubebuddy_tags) -> Dict[str, Any]:
        """Combine keyword insights from all sources"""
        try:
            # Extract all keywords
            all_keywords = set()
            
            # From VidIQ
            for keyword in vidiq_keywords:
                all_keywords.add(keyword.keyword.lower())
                all_keywords.update([k.lower() for k in keyword.related_keywords])
            
            # From TubeBuddy
            for tag in tubebuddy_tags:
                all_keywords.add(tag.tag.lower())
            
            # From trending content
            for content in trending_content:
                if "title" in content:
                    words = content["title"].lower().split()
                    all_keywords.update(words)
            
            # Filter and rank keywords
            keyword_scores = {}
            for keyword in all_keywords:
                if len(keyword) > 2:  # Filter out short words
                    score = 0
                    
                    # Score based on presence in multiple sources
                    if any(keyword in k.keyword.lower() for k in vidiq_keywords):
                        score += 3
                    if any(keyword in t.tag.lower() for t in tubebuddy_tags):
                        score += 2
                    if any(keyword in c.get("title", "").lower() for c in trending_content):
                        score += 1
                    
                    keyword_scores[keyword] = score
            
            # Get top keywords
            top_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)[:20]
            
            recommendations = {
                "high_priority_keywords": [k for k, s in top_keywords if s >= 3][:10],
                "medium_priority_keywords": [k for k, s in top_keywords if s == 2][:10],
                "long_tail_opportunities": [k for k in all_keywords if len(k.split()) > 2][:10],
                "content_ideas": [
                    f"How to {keyword}" for keyword, _ in top_keywords[:5]
                ] + [
                    f"Best {keyword} tips" for keyword, _ in top_keywords[5:10]
                ]
            }
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error combining keyword insights: {str(e)}")
            return {}
    
    async def competitor_intelligence(self, channel_id: str, competitor_channels: List[str]) -> Dict[str, Any]:
        """Comprehensive competitor analysis using all services"""
        if not self.initialized:
            raise RuntimeError("Integrations not initialized")
        
        try:
            # Get competitor analysis from VidIQ
            vidiq_competitors = await self.vidiq.get_competitor_analysis(channel_id, "general")
            
            # Get competitive analysis from Social Blade
            sb_analysis = await self.socialblade.get_competitive_analysis(channel_id, competitor_channels)
            
            # Combine analyses
            intelligence_report = {
                "channel_id": channel_id,
                "competitors_analyzed": competitor_channels,
                "analysis_timestamp": datetime.now().isoformat(),
                "vidiq_competitor_data": [c.to_dict() for c in vidiq_competitors],
                "socialblade_comparison": sb_analysis,
                "strategic_insights": await self._generate_strategic_insights(vidiq_competitors, sb_analysis)
            }
            
            return intelligence_report
            
        except Exception as e:
            logger.error(f"Error in competitor intelligence: {str(e)}")
            raise
    
    async def _generate_strategic_insights(self, vidiq_data, sb_data) -> Dict[str, Any]:
        """Generate strategic insights from competitor data"""
        try:
            insights = {
                "market_position": "unknown",
                "content_gaps": [],
                "growth_opportunities": [],
                "competitive_advantages": [],
                "strategic_recommendations": []
            }
            
            # Analyze market position from Social Blade data
            if "performance_comparison" in sb_data:
                perf = sb_data["performance_comparison"]
                above_avg_metrics = sum(1 for metric in perf.values() if metric.get("performance") == "above")
                total_metrics = len(perf)
                
                if above_avg_metrics / total_metrics > 0.6:
                    insights["market_position"] = "strong"
                elif above_avg_metrics / total_metrics > 0.4:
                    insights["market_position"] = "competitive"
                else:
                    insights["market_position"] = "emerging"
            
            # Identify content gaps from VidIQ data
            if vidiq_data:
                competitor_topics = set()
                for competitor in vidiq_data:
                    if "content_strategy" in competitor.to_dict():
                        topics = competitor.to_dict()["content_strategy"].get("primary_topics", [])
                        competitor_topics.update(topics)
                
                insights["content_gaps"] = list(competitor_topics)[:5]
            
            # Generate strategic recommendations
            insights["strategic_recommendations"] = [
                "Monitor competitor upload schedules and adjust timing",
                "Analyze top-performing competitor content for format insights",
                "Identify underserved topics in your niche",
                "Collaborate with similar-sized channels for mutual growth",
                "Differentiate content style while following successful patterns"
            ]
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating strategic insights: {str(e)}")
            return {}
    
    async def video_optimization_suite(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive video optimization using all services"""
        if not self.initialized:
            raise RuntimeError("Integrations not initialized")
        
        try:
            video_id = video_data.get('id', '')
            
            # Run optimizations in parallel
            tasks = [
                self.vidiq.optimize_video_metadata(video_data),
                self.tubebuddy.optimize_content(video_data),
                self.tubebuddy.analyze_thumbnail(video_data.get('thumbnail_url'), video_data.get('title', ''))
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            optimization_suite = {
                "video_id": video_id,
                "optimization_timestamp": datetime.now().isoformat(),
                "vidiq_optimization": results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])},
                "tubebuddy_optimization": results[1].to_dict() if not isinstance(results[1], Exception) else {"error": str(results[1])},
                "thumbnail_analysis": results[2].to_dict() if not isinstance(results[2], Exception) else {"error": str(results[2])},
                "combined_recommendations": await self._combine_optimization_insights(results)
            }
            
            return optimization_suite
            
        except Exception as e:
            logger.error(f"Error in video optimization suite: {str(e)}")
            raise
    
    async def _combine_optimization_insights(self, results: List[Any]) -> Dict[str, Any]:
        """Combine optimization insights from all services"""
        try:
            combined = {
                "priority_actions": [],
                "seo_improvements": [],
                "engagement_boosters": [],
                "technical_optimizations": []
            }
            
            # Extract insights from VidIQ optimization
            if len(results) > 0 and not isinstance(results[0], Exception):
                vidiq_result = results[0]
                if "seo_improvements" in vidiq_result:
                    combined["seo_improvements"].extend(vidiq_result["seo_improvements"])
                if "keyword_suggestions" in vidiq_result:
                    combined["priority_actions"].append("Implement suggested keywords in title and description")
            
            # Extract insights from TubeBuddy optimization
            if len(results) > 1 and not isinstance(results[1], Exception):
                tb_result = results[1]
                if "title_optimization" in tb_result:
                    suggestions = tb_result["title_optimization"].get("suggestions", [])
                    combined["seo_improvements"].extend(suggestions)
                if "seo_score" in tb_result and tb_result["seo_score"] < 70:
                    combined["priority_actions"].append("Improve overall SEO score")
            
            # Extract insights from thumbnail analysis
            if len(results) > 2 and not isinstance(results[2], Exception):
                thumb_result = results[2]
                if "recommendations" in thumb_result:
                    combined["engagement_boosters"].extend(thumb_result["recommendations"])
                if "current_score" in thumb_result and thumb_result["current_score"] < 80:
                    combined["priority_actions"].append("Optimize thumbnail for better click-through rate")
            
            # Add general technical optimizations
            combined["technical_optimizations"] = [
                "Ensure video quality is 1080p or higher",
                "Add closed captions for accessibility",
                "Include end screens and cards",
                "Optimize video file size for faster loading",
                "Use consistent branding elements"
            ]
            
            return combined
            
        except Exception as e:
            logger.error(f"Error combining optimization insights: {str(e)}")
            return {}
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get status of all integrations"""
        return {
            "initialized": self.initialized,
            "services": {
                "vidiq": {
                    "available": self.vidiq is not None,
                    "status": "active" if self.vidiq else "inactive"
                },
                "socialblade": {
                    "available": self.socialblade is not None,
                    "status": "active" if self.socialblade else "inactive"
                },
                "tubebuddy": {
                    "available": self.tubebuddy is not None,
                    "status": "active" if self.tubebuddy else "inactive"
                }
            },
            "last_check": datetime.now().isoformat()
        }

# Global instance
integrations_manager = ThirdPartyIntegrationsManager()

async def initialize_integrations_manager(api_keys: Dict[str, str] = None):
    """Initialize the global integrations manager"""
    await integrations_manager.initialize(api_keys)

async def cleanup_integrations_manager():
    """Cleanup the global integrations manager"""
    await integrations_manager.cleanup()