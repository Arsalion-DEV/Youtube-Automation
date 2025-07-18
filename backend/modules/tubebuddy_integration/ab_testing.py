"""
TubeBuddy-Inspired A/B Testing Module
Advanced A/B testing for YouTube thumbnails and titles
"""

import asyncio
import logging
import json
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import uuid
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class ABTestVariant:
    """A/B test variant structure"""
    id: str
    title: str
    thumbnail_url: str
    description: str
    tags: List[str]
    created_at: datetime
    
@dataclass
class ABTestResult:
    """A/B test result structure"""
    variant_id: str
    views: int
    clicks: int
    ctr: float  # Click-through rate
    watch_time: float
    engagement_rate: float
    conversion_rate: float

@dataclass 
class ABTest:
    """Complete A/B test structure"""
    test_id: str
    video_id: str
    test_name: str
    status: str  # 'running', 'completed', 'paused'
    variants: List[ABTestVariant]
    results: List[ABTestResult]
    winner_variant_id: str
    confidence_level: float
    start_date: datetime
    end_date: Optional[datetime]
    test_duration_hours: int

class ABTestingEngine:
    """TubeBuddy-inspired A/B testing system"""
    
    def __init__(self):
        self.active_tests = {}
        self.completed_tests = {}
        self.test_history = []
        
        # A/B testing configurations
        self.min_sample_size = 100  # Minimum views per variant
        self.confidence_threshold = 0.95  # 95% confidence level
        self.test_duration_hours = 24  # Default test duration
    
    async def create_ab_test(self, video_id: str, test_name: str, 
                           variants: List[Dict[str, Any]], 
                           test_duration_hours: int = 24) -> Dict[str, Any]:
        """
        Create a new A/B test for thumbnails and titles
        
        Args:
            video_id: YouTube video ID
            test_name: Human-readable test name
            variants: List of variant configurations
            test_duration_hours: How long to run the test
            
        Returns:
            Dictionary with test configuration and ID
        """
        try:
            test_id = str(uuid.uuid4())
            
            # Create variant objects
            test_variants = []
            for i, variant_data in enumerate(variants):
                variant = ABTestVariant(
                    id=f"{test_id}_variant_{i}",
                    title=variant_data.get('title', ''),
                    thumbnail_url=variant_data.get('thumbnail_url', ''),
                    description=variant_data.get('description', ''),
                    tags=variant_data.get('tags', []),
                    created_at=datetime.now()
                )
                test_variants.append(variant)
            
            # Create A/B test
            ab_test = ABTest(
                test_id=test_id,
                video_id=video_id,
                test_name=test_name,
                status='running',
                variants=test_variants,
                results=[],
                winner_variant_id='',
                confidence_level=0.0,
                start_date=datetime.now(),
                end_date=None,
                test_duration_hours=test_duration_hours
            )
            
            # Store test
            self.active_tests[test_id] = ab_test
            
            # Simulate initial traffic split
            await self._initialize_test_traffic(test_id)
            
            logger.info(f"Created A/B test {test_id} for video {video_id}")
            
            return {
                'test_id': test_id,
                'video_id': video_id,
                'test_name': test_name,
                'status': 'running',
                'variants_count': len(test_variants),
                'start_date': ab_test.start_date.isoformat(),
                'estimated_end_date': (ab_test.start_date + timedelta(hours=test_duration_hours)).isoformat(),
                'traffic_split': f"{100 // len(test_variants)}% per variant",
                'min_sample_size': self.min_sample_size,
                'confidence_threshold': f"{self.confidence_threshold * 100}%"
            }
            
        except Exception as e:
            logger.error(f"Failed to create A/B test: {e}")
            return {'error': 'Failed to create A/B test', 'details': str(e)}
    
    async def get_test_results(self, test_id: str) -> Dict[str, Any]:
        """Get current A/B test results and analysis"""
        try:
            ab_test = self.active_tests.get(test_id) or self.completed_tests.get(test_id)
            
            if not ab_test:
                return {'error': 'Test not found'}
            
            # Update results with latest data
            await self._update_test_results(test_id)
            
            # Calculate statistical significance
            significance = await self._calculate_statistical_significance(test_id)
            
            # Determine winner if test is complete
            winner = await self._determine_winner(test_id)
            
            # Format results
            results_data = []
            for variant in ab_test.variants:
                variant_result = next(
                    (r for r in ab_test.results if r.variant_id == variant.id), 
                    None
                )
                
                if variant_result:
                    results_data.append({
                        'variant_id': variant.id,
                        'title': variant.title,
                        'thumbnail_url': variant.thumbnail_url,
                        'views': variant_result.views,
                        'clicks': variant_result.clicks,
                        'ctr': variant_result.ctr,
                        'watch_time': variant_result.watch_time,
                        'engagement_rate': variant_result.engagement_rate,
                        'conversion_rate': variant_result.conversion_rate,
                        'is_winning': variant.id == winner.get('variant_id', '')
                    })
            
            return {
                'test_id': test_id,
                'test_name': ab_test.test_name,
                'status': ab_test.status,
                'variants': results_data,
                'winner': winner,
                'statistical_significance': significance,
                'confidence_level': ab_test.confidence_level,
                'start_date': ab_test.start_date.isoformat(),
                'end_date': ab_test.end_date.isoformat() if ab_test.end_date else None,
                'recommendations': await self._generate_test_recommendations(test_id),
                'next_steps': await self._suggest_next_steps(test_id)
            }
            
        except Exception as e:
            logger.error(f"Failed to get test results: {e}")
            return {'error': 'Failed to get test results', 'details': str(e)}
    
    async def stop_test(self, test_id: str, apply_winner: bool = True) -> Dict[str, Any]:
        """Stop A/B test and optionally apply winning variant"""
        try:
            if test_id not in self.active_tests:
                return {'error': 'Test not found or already stopped'}
            
            ab_test = self.active_tests[test_id]
            
            # Update final results
            await self._update_test_results(test_id)
            
            # Determine final winner
            winner = await self._determine_winner(test_id)
            
            # Update test status
            ab_test.status = 'completed'
            ab_test.end_date = datetime.now()
            ab_test.winner_variant_id = winner.get('variant_id', '')
            
            # Move to completed tests
            self.completed_tests[test_id] = ab_test
            del self.active_tests[test_id]
            
            # Add to history
            self.test_history.append({
                'test_id': test_id,
                'test_name': ab_test.test_name,
                'video_id': ab_test.video_id,
                'winner_variant_id': ab_test.winner_variant_id,
                'confidence_level': ab_test.confidence_level,
                'completed_date': ab_test.end_date.isoformat()
            })
            
            result = {
                'test_id': test_id,
                'status': 'completed',
                'winner': winner,
                'confidence_level': ab_test.confidence_level,
                'test_duration': str(ab_test.end_date - ab_test.start_date),
                'variants_tested': len(ab_test.variants),
                'total_views': sum(r.views for r in ab_test.results),
                'improvement': await self._calculate_improvement(test_id),
                'applied_winner': apply_winner
            }
            
            if apply_winner:
                # In a real implementation, this would update the video
                logger.info(f"Applied winning variant for test {test_id}")
                result['winner_applied'] = True
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to stop test: {e}")
            return {'error': 'Failed to stop test', 'details': str(e)}
    
    async def _initialize_test_traffic(self, test_id: str):
        """Initialize traffic split for A/B test"""
        try:
            ab_test = self.active_tests[test_id]
            
            # Initialize results for each variant
            for variant in ab_test.variants:
                result = ABTestResult(
                    variant_id=variant.id,
                    views=0,
                    clicks=0,
                    ctr=0.0,
                    watch_time=0.0,
                    engagement_rate=0.0,
                    conversion_rate=0.0
                )
                ab_test.results.append(result)
            
            logger.info(f"Initialized traffic split for test {test_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize test traffic: {e}")
    
    async def _update_test_results(self, test_id: str):
        """Update A/B test results with simulated data"""
        try:
            ab_test = self.active_tests.get(test_id) or self.completed_tests.get(test_id)
            if not ab_test:
                return
            
            # Simulate realistic A/B test data
            hours_running = (datetime.now() - ab_test.start_date).total_seconds() / 3600
            base_views_per_hour = random.randint(50, 200)
            
            for i, result in enumerate(ab_test.results):
                # Simulate views growth over time
                views_growth = int(base_views_per_hour * hours_running * random.uniform(0.8, 1.2))
                result.views = max(result.views, views_growth)
                
                # Simulate variant performance differences
                variant_modifier = 1.0
                if i == 0:  # First variant baseline
                    variant_modifier = 1.0
                elif i == 1:  # Second variant might perform better/worse
                    variant_modifier = random.uniform(0.9, 1.3)
                else:  # Additional variants
                    variant_modifier = random.uniform(0.85, 1.15)
                
                # Calculate CTR (click-through rate)
                base_ctr = random.uniform(0.02, 0.08) * variant_modifier
                result.ctr = round(base_ctr, 4)
                result.clicks = int(result.views * result.ctr)
                
                # Calculate watch time (average percentage of video watched)
                result.watch_time = round(random.uniform(0.4, 0.8) * variant_modifier, 2)
                
                # Calculate engagement rate
                result.engagement_rate = round(random.uniform(0.03, 0.12) * variant_modifier, 4)
                
                # Calculate conversion rate (subscribe, like, etc.)
                result.conversion_rate = round(random.uniform(0.01, 0.05) * variant_modifier, 4)
            
        except Exception as e:
            logger.error(f"Failed to update test results: {e}")
    
    async def _calculate_statistical_significance(self, test_id: str) -> Dict[str, Any]:
        """Calculate statistical significance of A/B test results"""
        try:
            ab_test = self.active_tests.get(test_id) or self.completed_tests.get(test_id)
            if not ab_test or len(ab_test.results) < 2:
                return {'significant': False, 'confidence': 0.0}
            
            # Simple statistical significance calculation
            # In a real implementation, this would use proper statistical tests
            
            results = sorted(ab_test.results, key=lambda x: x.ctr, reverse=True)
            best_result = results[0]
            second_best = results[1]
            
            # Check minimum sample size
            if best_result.views < self.min_sample_size:
                return {
                    'significant': False,
                    'confidence': 0.0,
                    'reason': f'Insufficient data (minimum {self.min_sample_size} views needed)',
                    'current_sample_size': best_result.views
                }
            
            # Calculate confidence level (simplified)
            ctr_difference = abs(best_result.ctr - second_best.ctr)
            relative_improvement = (ctr_difference / second_best.ctr) * 100 if second_best.ctr > 0 else 0
            
            # Simulate confidence calculation
            confidence = min(0.99, relative_improvement / 10 + random.uniform(0.6, 0.9))
            is_significant = confidence >= self.confidence_threshold
            
            ab_test.confidence_level = confidence
            
            return {
                'significant': is_significant,
                'confidence': round(confidence, 3),
                'relative_improvement': round(relative_improvement, 2),
                'ctr_difference': round(ctr_difference, 4),
                'sample_size': best_result.views,
                'threshold': self.confidence_threshold
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate statistical significance: {e}")
            return {'significant': False, 'confidence': 0.0, 'error': str(e)}
    
    async def _determine_winner(self, test_id: str) -> Dict[str, Any]:
        """Determine winning variant based on performance metrics"""
        try:
            ab_test = self.active_tests.get(test_id) or self.completed_tests.get(test_id)
            if not ab_test or not ab_test.results:
                return {}
            
            # Score each variant based on multiple metrics
            variant_scores = []
            
            for result in ab_test.results:
                variant = next(v for v in ab_test.variants if v.id == result.variant_id)
                
                # Weighted scoring system
                score = (
                    result.ctr * 40 +              # CTR weight: 40%
                    result.watch_time * 25 +       # Watch time weight: 25%
                    result.engagement_rate * 20 +  # Engagement weight: 20%
                    result.conversion_rate * 15    # Conversion weight: 15%
                )
                
                variant_scores.append({
                    'variant_id': result.variant_id,
                    'title': variant.title,
                    'score': score,
                    'ctr': result.ctr,
                    'views': result.views,
                    'watch_time': result.watch_time,
                    'engagement_rate': result.engagement_rate,
                    'conversion_rate': result.conversion_rate
                })
            
            # Sort by score
            variant_scores.sort(key=lambda x: x['score'], reverse=True)
            winner = variant_scores[0]
            
            return {
                'variant_id': winner['variant_id'],
                'title': winner['title'],
                'winning_score': round(winner['score'], 4),
                'winning_metrics': {
                    'ctr': winner['ctr'],
                    'watch_time': winner['watch_time'],
                    'engagement_rate': winner['engagement_rate'],
                    'conversion_rate': winner['conversion_rate']
                },
                'vs_runner_up': {
                    'score_difference': round(winner['score'] - variant_scores[1]['score'], 4) if len(variant_scores) > 1 else 0,
                    'ctr_improvement': round(((winner['ctr'] / variant_scores[1]['ctr']) - 1) * 100, 2) if len(variant_scores) > 1 and variant_scores[1]['ctr'] > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to determine winner: {e}")
            return {}
    
    async def _generate_test_recommendations(self, test_id: str) -> List[str]:
        """Generate recommendations based on test results"""
        try:
            ab_test = self.active_tests.get(test_id) or self.completed_tests.get(test_id)
            recommendations = []
            
            if not ab_test:
                return recommendations
            
            winner = await self._determine_winner(test_id)
            significance = await self._calculate_statistical_significance(test_id)
            
            # Generate specific recommendations
            if significance['significant']:
                recommendations.append(f"✅ Test is statistically significant with {significance['confidence']*100:.1f}% confidence")
                recommendations.append(f"🏆 Apply winning variant: {winner.get('title', 'Unknown')}")
            else:
                recommendations.append("⏳ Test needs more data to reach statistical significance")
                recommendations.append(f"📊 Current sample size: {significance.get('current_sample_size', 0)}, need minimum {self.min_sample_size}")
            
            # Performance-based recommendations
            best_ctr = max(r.ctr for r in ab_test.results) if ab_test.results else 0
            if best_ctr < 0.03:
                recommendations.append("🎯 All variants have low CTR - consider testing more compelling thumbnails")
            elif best_ctr > 0.08:
                recommendations.append("🚀 Excellent CTR performance - use similar thumbnail styles for future videos")
            
            # Engagement recommendations
            best_engagement = max(r.engagement_rate for r in ab_test.results) if ab_test.results else 0
            if best_engagement < 0.05:
                recommendations.append("💬 Low engagement - consider testing titles that encourage interaction")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return ["Unable to generate recommendations"]
    
    async def _suggest_next_steps(self, test_id: str) -> List[str]:
        """Suggest next steps after A/B test"""
        try:
            ab_test = self.active_tests.get(test_id) or self.completed_tests.get(test_id)
            next_steps = []
            
            if not ab_test:
                return next_steps
            
            if ab_test.status == 'running':
                hours_remaining = ab_test.test_duration_hours - (datetime.now() - ab_test.start_date).total_seconds() / 3600
                if hours_remaining > 0:
                    next_steps.append(f"⏰ Let test run for {hours_remaining:.1f} more hours")
                else:
                    next_steps.append("🛑 Test duration complete - review results and stop test")
            else:
                next_steps.append("📊 Analyze results and apply learnings to future videos")
                next_steps.append("🔄 Create new A/B test for next video with improved variants")
                next_steps.append("📝 Document winning patterns for thumbnail/title optimization")
            
            return next_steps
            
        except Exception as e:
            logger.error(f"Failed to suggest next steps: {e}")
            return ["Review test results"]
    
    async def _calculate_improvement(self, test_id: str) -> Dict[str, Any]:
        """Calculate improvement metrics from A/B test"""
        try:
            ab_test = self.completed_tests.get(test_id)
            if not ab_test or len(ab_test.results) < 2:
                return {}
            
            results = sorted(ab_test.results, key=lambda x: x.ctr, reverse=True)
            winner = results[0]
            baseline = results[-1]  # Worst performing as baseline
            
            improvements = {}
            
            if baseline.ctr > 0:
                improvements['ctr_improvement'] = round(((winner.ctr / baseline.ctr) - 1) * 100, 2)
            
            if baseline.watch_time > 0:
                improvements['watch_time_improvement'] = round(((winner.watch_time / baseline.watch_time) - 1) * 100, 2)
            
            if baseline.engagement_rate > 0:
                improvements['engagement_improvement'] = round(((winner.engagement_rate / baseline.engagement_rate) - 1) * 100, 2)
            
            return improvements
            
        except Exception as e:
            logger.error(f"Failed to calculate improvement: {e}")
            return {}
    
    async def get_test_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get A/B test history"""
        try:
            return self.test_history[-limit:] if self.test_history else []
        except Exception as e:
            logger.error(f"Failed to get test history: {e}")
            return []
    
    async def get_active_tests(self) -> List[Dict[str, Any]]:
        """Get all currently active A/B tests"""
        try:
            active = []
            for test_id, ab_test in self.active_tests.items():
                active.append({
                    'test_id': test_id,
                    'test_name': ab_test.test_name,
                    'video_id': ab_test.video_id,
                    'status': ab_test.status,
                    'variants_count': len(ab_test.variants),
                    'start_date': ab_test.start_date.isoformat(),
                    'hours_running': (datetime.now() - ab_test.start_date).total_seconds() / 3600
                })
            return active
        except Exception as e:
            logger.error(f"Failed to get active tests: {e}")
            return []

# Global instance
ab_testing_engine = ABTestingEngine()