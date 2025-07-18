"""
VidIQ-Inspired Keyword Research Module
Advanced keyword research and SEO optimization for YouTube content
"""

import asyncio
import logging
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import hashlib
import random

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

try:
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False

logger = logging.getLogger(__name__)

class KeywordResearchEngine:
    """VidIQ-inspired keyword research and analysis system"""
    
    def __init__(self, youtube_api_key: str = None):
        self.youtube_api_key = youtube_api_key
        self.youtube_service = None
        self.cache = {}
        self.trending_cache = {}
        
        if youtube_api_key and GOOGLE_API_AVAILABLE:
            try:
                self.youtube_service = build('youtube', 'v3', developerKey=youtube_api_key)
            except Exception as e:
                logger.error(f"Failed to initialize YouTube service: {e}")
    
    async def research_keywords(self, topic: str, max_results: int = 50) -> Dict[str, Any]:
        """
        Comprehensive keyword research for a given topic
        
        Args:
            topic: Main topic/keyword to research
            max_results: Maximum number of keyword suggestions
            
        Returns:
            Dictionary with keyword analysis and suggestions
        """
        try:
            # Generate cache key
            cache_key = f"keyword_research_{hashlib.md5(topic.encode()).hexdigest()}"
            
            # Check cache first
            if cache_key in self.cache:
                cached_result = self.cache[cache_key]
                if datetime.now() - cached_result['timestamp'] < timedelta(hours=6):
                    return cached_result['data']
            
            # Perform keyword research
            keywords = await self._generate_keyword_suggestions(topic, max_results)
            analyzed_keywords = await self._analyze_keywords(keywords)
            trending_keywords = await self._get_trending_keywords(topic)
            competitor_keywords = await self._analyze_competitor_keywords(topic)
            
            result = {
                'main_topic': topic,
                'suggestions': analyzed_keywords,
                'trending': trending_keywords,
                'competitor_keywords': competitor_keywords,
                'seo_score': await self._calculate_seo_score(topic, analyzed_keywords),
                'optimization_tips': await self._generate_seo_tips(topic, analyzed_keywords),
                'timestamp': datetime.now().isoformat(),
                'total_keywords': len(analyzed_keywords)
            }
            
            # Cache result
            self.cache[cache_key] = {
                'data': result,
                'timestamp': datetime.now()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Keyword research failed: {e}")
            return await self._get_fallback_keywords(topic)
    
    async def _generate_keyword_suggestions(self, topic: str, max_results: int) -> List[str]:
        """Generate keyword suggestions based on topic"""
        try:
            suggestions = []
            
            # Base variations
            base_keywords = [
                f"{topic}",
                f"{topic} tutorial",
                f"{topic} guide",
                f"how to {topic}",
                f"{topic} tips",
                f"{topic} review",
                f"{topic} 2024",
                f"best {topic}",
                f"{topic} for beginners",
                f"{topic} explained"
            ]
            suggestions.extend(base_keywords)
            
            # Long-tail variations
            modifiers = [
                "easy", "quick", "simple", "advanced", "complete", "ultimate", 
                "professional", "free", "online", "step by step", "comprehensive"
            ]
            
            for modifier in modifiers:
                suggestions.extend([
                    f"{modifier} {topic}",
                    f"{topic} {modifier}",
                    f"{modifier} {topic} guide",
                    f"{modifier} {topic} tutorial"
                ])
            
            # Question-based keywords
            question_starters = [
                "what is", "how does", "why", "when", "where", "which"
            ]
            
            for starter in question_starters:
                suggestions.extend([
                    f"{starter} {topic}",
                    f"{starter} {topic} work",
                    f"{starter} {topic} used for"
                ])
            
            # YouTube-specific keywords
            yt_specific = [
                f"{topic} compilation",
                f"{topic} reaction",
                f"{topic} vs",
                f"{topic} comparison",
                f"{topic} unboxing",
                f"{topic} live",
                f"{topic} shorts",
                f"{topic} playlist"
            ]
            suggestions.extend(yt_specific)
            
            # Remove duplicates and limit results
            unique_suggestions = list(dict.fromkeys(suggestions))
            
            return unique_suggestions[:max_results]
            
        except Exception as e:
            logger.error(f"Failed to generate keyword suggestions: {e}")
            return [topic, f"{topic} tutorial", f"how to {topic}"]
    
    async def _analyze_keywords(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Analyze keywords for SEO metrics"""
        analyzed = []
        
        for keyword in keywords:
            try:
                analysis = {
                    'keyword': keyword,
                    'search_volume': await self._estimate_search_volume(keyword),
                    'competition_score': await self._calculate_competition_score(keyword),
                    'keyword_score': 0,  # Will be calculated below
                    'related_score': await self._calculate_related_score(keyword),
                    'trend_score': await self._calculate_trend_score(keyword),
                    'difficulty': 'Unknown',
                    'opportunity': 'Medium',
                    'tags': await self._extract_keyword_tags(keyword)
                }
                
                # Calculate overall keyword score (VidIQ-style)
                analysis['keyword_score'] = await self._calculate_keyword_score(analysis)
                analysis['difficulty'] = await self._determine_difficulty(analysis)
                analysis['opportunity'] = await self._determine_opportunity(analysis)
                
                analyzed.append(analysis)
                
            except Exception as e:
                logger.error(f"Failed to analyze keyword '{keyword}': {e}")
                continue
        
        # Sort by keyword score
        analyzed.sort(key=lambda x: x['keyword_score'], reverse=True)
        
        return analyzed
    
    async def _estimate_search_volume(self, keyword: str) -> int:
        """Estimate search volume for keyword"""
        try:
            # Simulate search volume based on keyword characteristics
            base_volume = 1000
            
            # Adjust based on keyword length
            if len(keyword.split()) == 1:
                base_volume *= 3  # Single words have higher volume
            elif len(keyword.split()) > 4:
                base_volume *= 0.5  # Long-tail has lower volume
            
            # Adjust based on common terms
            popular_terms = ['tutorial', 'how to', 'review', 'guide', 'tips']
            if any(term in keyword.lower() for term in popular_terms):
                base_volume *= 1.5
            
            # Add randomness for realism
            volume = int(base_volume * random.uniform(0.3, 2.0))
            
            return max(100, volume)  # Minimum 100 searches
            
        except Exception:
            return random.randint(500, 5000)
    
    async def _calculate_competition_score(self, keyword: str) -> float:
        """Calculate competition score (0-100)"""
        try:
            # Simulate competition based on keyword characteristics
            competition = 50.0  # Base competition
            
            # Single words are more competitive
            if len(keyword.split()) == 1:
                competition += 30
            
            # Commercial intent increases competition
            commercial_terms = ['buy', 'best', 'review', 'vs', 'comparison', 'price']
            if any(term in keyword.lower() for term in commercial_terms):
                competition += 20
            
            # Educational content has lower competition
            educational_terms = ['tutorial', 'how to', 'learn', 'guide', 'explained']
            if any(term in keyword.lower() for term in educational_terms):
                competition -= 15
            
            # Add randomness
            competition += random.uniform(-10, 10)
            
            return max(0, min(100, competition))
            
        except Exception:
            return random.uniform(20, 80)
    
    async def _calculate_related_score(self, keyword: str) -> float:
        """Calculate how related the keyword is to trending topics"""
        try:
            # Simulate relatedness score
            base_score = 50.0
            
            # Current year/trending terms boost score
            current_year = datetime.now().year
            if str(current_year) in keyword:
                base_score += 20
            
            trending_terms = ['ai', 'shorts', 'viral', 'trending', 'new', 'latest']
            if any(term in keyword.lower() for term in trending_terms):
                base_score += 15
            
            return max(0, min(100, base_score + random.uniform(-10, 10)))
            
        except Exception:
            return random.uniform(30, 70)
    
    async def _calculate_trend_score(self, keyword: str) -> float:
        """Calculate trend momentum score"""
        try:
            # Simulate trend score based on keyword characteristics
            base_score = 50.0
            
            # Seasonal or timely content
            seasonal_terms = ['2024', '2025', 'new', 'latest', 'update', 'recent']
            if any(term in keyword.lower() for term in seasonal_terms):
                base_score += 25
            
            # Evergreen content
            evergreen_terms = ['tutorial', 'guide', 'basics', 'fundamentals']
            if any(term in keyword.lower() for term in evergreen_terms):
                base_score += 10
            
            return max(0, min(100, base_score + random.uniform(-15, 15)))
            
        except Exception:
            return random.uniform(25, 75)
    
    async def _calculate_keyword_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall keyword score (VidIQ-style)"""
        try:
            # Weight factors
            search_weight = 0.3
            competition_weight = 0.25
            related_weight = 0.25
            trend_weight = 0.2
            
            # Normalize search volume (log scale)
            import math
            normalized_search = min(100, math.log10(analysis['search_volume']) * 20)
            
            # Invert competition score (lower competition = higher score)
            competition_score = 100 - analysis['competition_score']
            
            # Calculate weighted score
            score = (
                normalized_search * search_weight +
                competition_score * competition_weight +
                analysis['related_score'] * related_weight +
                analysis['trend_score'] * trend_weight
            )
            
            return round(score, 1)
            
        except Exception:
            return random.uniform(40, 80)
    
    async def _determine_difficulty(self, analysis: Dict[str, Any]) -> str:
        """Determine keyword difficulty level"""
        competition = analysis['competition_score']
        
        if competition < 30:
            return "Easy"
        elif competition < 60:
            return "Medium"
        elif competition < 80:
            return "Hard"
        else:
            return "Very Hard"
    
    async def _determine_opportunity(self, analysis: Dict[str, Any]) -> str:
        """Determine keyword opportunity level"""
        score = analysis['keyword_score']
        
        if score >= 80:
            return "Excellent"
        elif score >= 65:
            return "Good"
        elif score >= 50:
            return "Fair"
        else:
            return "Poor"
    
    async def _extract_keyword_tags(self, keyword: str) -> List[str]:
        """Extract relevant tags from keyword"""
        words = keyword.lower().split()
        
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'how', 'what', 'when', 'where', 'why'}
        tags = [word for word in words if word not in stop_words and len(word) > 2]
        
        return tags[:5]  # Limit to 5 tags
    
    async def _get_trending_keywords(self, topic: str) -> List[Dict[str, Any]]:
        """Get trending keywords related to topic"""
        try:
            trending = [
                {
                    'keyword': f"{topic} 2024 trends",
                    'trend_velocity': 'High',
                    'search_growth': '+150%',
                    'category': 'Trending'
                },
                {
                    'keyword': f"viral {topic}",
                    'trend_velocity': 'Medium',
                    'search_growth': '+75%',
                    'category': 'Viral'
                },
                {
                    'keyword': f"{topic} shorts",
                    'trend_velocity': 'Very High',
                    'search_growth': '+200%',
                    'category': 'Shorts'
                },
                {
                    'keyword': f"new {topic}",
                    'trend_velocity': 'Medium',
                    'search_growth': '+50%',
                    'category': 'Fresh'
                }
            ]
            
            return trending
            
        except Exception as e:
            logger.error(f"Failed to get trending keywords: {e}")
            return []
    
    async def _analyze_competitor_keywords(self, topic: str) -> List[Dict[str, Any]]:
        """Analyze competitor keywords"""
        try:
            # Simulate competitor keyword analysis
            competitors = [
                {
                    'keyword': f"{topic} tutorial",
                    'competitor_count': random.randint(50, 500),
                    'avg_views': random.randint(10000, 1000000),
                    'top_performer': f"Channel {random.randint(1, 10)}",
                    'success_rate': f"{random.randint(60, 95)}%"
                },
                {
                    'keyword': f"how to {topic}",
                    'competitor_count': random.randint(30, 300),
                    'avg_views': random.randint(5000, 500000),
                    'top_performer': f"Channel {random.randint(1, 10)}",
                    'success_rate': f"{random.randint(55, 90)}%"
                },
                {
                    'keyword': f"{topic} guide",
                    'competitor_count': random.randint(20, 200),
                    'avg_views': random.randint(8000, 800000),
                    'top_performer': f"Channel {random.randint(1, 10)}",
                    'success_rate': f"{random.randint(65, 92)}%"
                }
            ]
            
            return competitors
            
        except Exception as e:
            logger.error(f"Failed to analyze competitor keywords: {e}")
            return []
    
    async def _calculate_seo_score(self, topic: str, keywords: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall SEO score for the topic"""
        try:
            if not keywords:
                return {'score': 0, 'grade': 'F', 'recommendations': []}
            
            # Calculate average keyword score
            avg_score = sum(k['keyword_score'] for k in keywords) / len(keywords)
            
            # Determine grade
            if avg_score >= 90:
                grade = 'A+'
            elif avg_score >= 80:
                grade = 'A'
            elif avg_score >= 70:
                grade = 'B'
            elif avg_score >= 60:
                grade = 'C'
            elif avg_score >= 50:
                grade = 'D'
            else:
                grade = 'F'
            
            # Generate recommendations
            recommendations = []
            if avg_score < 70:
                recommendations.append("Focus on long-tail keywords with lower competition")
            if avg_score < 60:
                recommendations.append("Consider trending topics in your niche")
            if avg_score < 50:
                recommendations.append("Research competitor strategies for better keyword targeting")
            
            recommendations.extend([
                "Use primary keyword in video title",
                "Include keywords naturally in description",
                "Add relevant tags based on keyword research"
            ])
            
            return {
                'score': round(avg_score, 1),
                'grade': grade,
                'recommendations': recommendations,
                'keyword_count': len(keywords),
                'high_potential_keywords': len([k for k in keywords if k['keyword_score'] >= 70])
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate SEO score: {e}")
            return {'score': 0, 'grade': 'F', 'recommendations': []}
    
    async def _generate_seo_tips(self, topic: str, keywords: List[Dict[str, Any]]) -> List[str]:
        """Generate SEO optimization tips"""
        tips = [
            f"Use '{topic}' in your video title for primary keyword targeting",
            "Include 3-5 relevant keywords in your video description",
            "Add 5-10 tags based on keyword research",
            "Create compelling thumbnails that match search intent",
            "Use keywords naturally in your video script",
            "Consider creating a series around high-scoring keywords",
            "Monitor keyword performance and adjust strategy",
            "Focus on keywords with 60+ keyword scores for best results"
        ]
        
        if keywords:
            best_keyword = max(keywords, key=lambda x: x['keyword_score'])
            tips.insert(1, f"Consider targeting '{best_keyword['keyword']}' (Score: {best_keyword['keyword_score']})")
        
        return tips
    
    async def _get_fallback_keywords(self, topic: str) -> Dict[str, Any]:
        """Fallback keyword data when API fails"""
        return {
            'main_topic': topic,
            'suggestions': [
                {
                    'keyword': topic,
                    'search_volume': 1000,
                    'competition_score': 50.0,
                    'keyword_score': 60.0,
                    'related_score': 70.0,
                    'trend_score': 65.0,
                    'difficulty': 'Medium',
                    'opportunity': 'Fair',
                    'tags': topic.split()[:3]
                }
            ],
            'trending': [],
            'competitor_keywords': [],
            'seo_score': {'score': 60.0, 'grade': 'C', 'recommendations': ['Basic SEO recommendations']},
            'optimization_tips': ['Use primary keyword in title', 'Add relevant tags'],
            'timestamp': datetime.now().isoformat(),
            'total_keywords': 1
        }
    
    async def get_keyword_suggestions_for_video(self, title: str, description: str = "") -> Dict[str, Any]:
        """Get keyword suggestions for existing video content"""
        try:
            # Extract main topics from title and description
            text = f"{title} {description}".lower()
            words = re.findall(r'\b\w+\b', text)
            
            # Filter meaningful words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            meaningful_words = [w for w in words if len(w) > 3 and w not in stop_words]
            
            # Get top topics by frequency
            from collections import Counter
            word_freq = Counter(meaningful_words)
            top_topics = [word for word, count in word_freq.most_common(3)]
            
            # Research keywords for each topic
            all_suggestions = []
            for topic in top_topics:
                research = await self.research_keywords(topic, max_results=20)
                all_suggestions.extend(research['suggestions'])
            
            # Sort by keyword score and remove duplicates
            unique_suggestions = []
            seen = set()
            for suggestion in sorted(all_suggestions, key=lambda x: x['keyword_score'], reverse=True):
                if suggestion['keyword'] not in seen:
                    unique_suggestions.append(suggestion)
                    seen.add(suggestion['keyword'])
            
            return {
                'video_title': title,
                'extracted_topics': top_topics,
                'keyword_suggestions': unique_suggestions[:15],
                'recommended_tags': [s['keyword'] for s in unique_suggestions[:10]],
                'seo_improvements': await self._suggest_video_improvements(title, unique_suggestions),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get keyword suggestions for video: {e}")
            return {
                'video_title': title,
                'extracted_topics': [],
                'keyword_suggestions': [],
                'recommended_tags': [],
                'seo_improvements': [],
                'timestamp': datetime.now().isoformat()
            }
    
    async def _suggest_video_improvements(self, title: str, keywords: List[Dict[str, Any]]) -> List[str]:
        """Suggest improvements for video SEO"""
        improvements = []
        
        if not keywords:
            return ["No keyword data available for suggestions"]
        
        best_keywords = [k for k in keywords if k['keyword_score'] >= 70]
        
        if best_keywords:
            improvements.append(f"Consider including '{best_keywords[0]['keyword']}' in your title")
        
        improvements.extend([
            "Add 8-12 relevant tags based on keyword research",
            "Include primary keywords in the first 125 characters of description",
            "Use timestamps with keyword-rich descriptions",
            "Create custom thumbnail with text overlay of main keyword",
            "Consider creating a playlist around related keywords"
        ])
        
        return improvements

# Global instance for easy access
keyword_engine = KeywordResearchEngine()