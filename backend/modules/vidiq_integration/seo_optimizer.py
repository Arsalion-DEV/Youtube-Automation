"""
VidIQ-Inspired SEO Optimization Module
Comprehensive SEO optimization tools for YouTube content
"""

import asyncio
import logging
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import hashlib
import random
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SEOAnalysis:
    """SEO analysis result structure"""
    title_score: float
    description_score: float
    tags_score: float
    overall_score: float
    grade: str
    recommendations: List[str]
    optimization_opportunities: List[str]

class SEOOptimizer:
    """VidIQ-inspired SEO optimization engine"""
    
    def __init__(self):
        self.best_practices = {
            'title_length': {'min': 30, 'max': 60, 'optimal': 50},
            'description_length': {'min': 200, 'max': 5000, 'optimal': 1000},
            'tags_count': {'min': 5, 'max': 15, 'optimal': 10},
            'keyword_density': {'min': 0.5, 'max': 3.0, 'optimal': 1.5}
        }
    
    async def analyze_video_seo(self, title: str, description: str, tags: List[str], 
                               target_keywords: List[str] = None) -> SEOAnalysis:
        """
        Comprehensive SEO analysis for video content
        
        Args:
            title: Video title
            description: Video description
            tags: List of video tags
            target_keywords: Primary keywords to optimize for
            
        Returns:
            SEOAnalysis object with scores and recommendations
        """
        try:
            # Analyze each component
            title_analysis = await self._analyze_title(title, target_keywords)
            description_analysis = await self._analyze_description(description, target_keywords)
            tags_analysis = await self._analyze_tags(tags, target_keywords)
            
            # Calculate overall score
            overall_score = (
                title_analysis['score'] * 0.4 +
                description_analysis['score'] * 0.35 +
                tags_analysis['score'] * 0.25
            )
            
            # Determine grade
            grade = self._calculate_grade(overall_score)
            
            # Generate comprehensive recommendations
            recommendations = []
            recommendations.extend(title_analysis['recommendations'])
            recommendations.extend(description_analysis['recommendations'])
            recommendations.extend(tags_analysis['recommendations'])
            
            # Generate optimization opportunities
            opportunities = await self._identify_opportunities(
                title, description, tags, target_keywords, overall_score
            )
            
            return SEOAnalysis(
                title_score=title_analysis['score'],
                description_score=description_analysis['score'],
                tags_score=tags_analysis['score'],
                overall_score=round(overall_score, 1),
                grade=grade,
                recommendations=recommendations,
                optimization_opportunities=opportunities
            )
            
        except Exception as e:
            logger.error(f"SEO analysis failed: {e}")
            return SEOAnalysis(0, 0, 0, 0, 'F', ['Analysis failed'], [])
    
    async def _analyze_title(self, title: str, target_keywords: List[str] = None) -> Dict[str, Any]:
        """Analyze title SEO optimization"""
        try:
            score = 0
            recommendations = []
            max_score = 100
            
            # Length analysis (25 points)
            length_score = self._score_length(
                len(title), 
                self.best_practices['title_length']
            )
            score += length_score * 0.25
            
            if len(title) < 30:
                recommendations.append("Title is too short - aim for 30-60 characters")
            elif len(title) > 60:
                recommendations.append("Title is too long - keep under 60 characters for better visibility")
            
            # Keyword optimization (30 points)
            keyword_score = 0
            if target_keywords:
                keyword_score = self._analyze_keyword_placement(title, target_keywords, 'title')
                score += keyword_score * 0.30
                
                primary_keyword = target_keywords[0] if target_keywords else ""
                if primary_keyword.lower() not in title.lower():
                    recommendations.append(f"Include primary keyword '{primary_keyword}' in title")
                elif not title.lower().startswith(primary_keyword.lower()[:10]):
                    recommendations.append("Consider placing primary keyword at the beginning of title")
            else:
                score += 15  # Neutral score if no keywords provided
            
            # Engagement factors (25 points)
            engagement_score = self._analyze_title_engagement(title)
            score += engagement_score * 0.25
            
            if engagement_score < 60:
                recommendations.append("Add power words or emotional triggers to increase engagement")
            
            # Technical optimization (20 points)
            technical_score = self._analyze_title_technical(title)
            score += technical_score * 0.20
            
            if technical_score < 70:
                recommendations.append("Avoid excessive capitalization and special characters")
            
            return {
                'score': min(100, score),
                'recommendations': recommendations,
                'details': {
                    'length_score': length_score,
                    'keyword_score': keyword_score,
                    'engagement_score': engagement_score,
                    'technical_score': technical_score
                }
            }
            
        except Exception as e:
            logger.error(f"Title analysis failed: {e}")
            return {'score': 0, 'recommendations': ['Title analysis failed']}
    
    async def _analyze_description(self, description: str, target_keywords: List[str] = None) -> Dict[str, Any]:
        """Analyze description SEO optimization"""
        try:
            score = 0
            recommendations = []
            
            # Length analysis (20 points)
            length_score = self._score_length(
                len(description), 
                self.best_practices['description_length']
            )
            score += length_score * 0.20
            
            if len(description) < 200:
                recommendations.append("Description is too short - aim for at least 200 characters")
            elif len(description) > 5000:
                recommendations.append("Description is very long - consider condensing key information")
            
            # Keyword optimization (35 points)
            keyword_score = 0
            if target_keywords:
                keyword_score = self._analyze_keyword_placement(description, target_keywords, 'description')
                score += keyword_score * 0.35
                
                # Check first 125 characters for keywords
                first_125 = description[:125].lower()
                if target_keywords and target_keywords[0].lower() not in first_125:
                    recommendations.append("Include primary keyword in first 125 characters of description")
            else:
                score += 17.5  # Neutral score
            
            # Structure analysis (25 points)
            structure_score = self._analyze_description_structure(description)
            score += structure_score * 0.25
            
            if structure_score < 70:
                recommendations.append("Improve description structure with paragraphs and bullet points")
            
            # Call-to-action analysis (20 points)
            cta_score = self._analyze_call_to_action(description)
            score += cta_score * 0.20
            
            if cta_score < 60:
                recommendations.append("Add clear call-to-action (like, subscribe, comment)")
            
            return {
                'score': min(100, score),
                'recommendations': recommendations,
                'details': {
                    'length_score': length_score,
                    'keyword_score': keyword_score,
                    'structure_score': structure_score,
                    'cta_score': cta_score
                }
            }
            
        except Exception as e:
            logger.error(f"Description analysis failed: {e}")
            return {'score': 0, 'recommendations': ['Description analysis failed']}
    
    async def _analyze_tags(self, tags: List[str], target_keywords: List[str] = None) -> Dict[str, Any]:
        """Analyze tags SEO optimization"""
        try:
            score = 0
            recommendations = []
            
            # Count analysis (25 points)
            tag_count = len(tags)
            count_score = self._score_count(tag_count, self.best_practices['tags_count'])
            score += count_score * 0.25
            
            if tag_count < 5:
                recommendations.append("Add more tags - aim for 8-12 relevant tags")
            elif tag_count > 15:
                recommendations.append("Too many tags - focus on 8-12 most relevant ones")
            
            # Relevance analysis (40 points)
            relevance_score = self._analyze_tag_relevance(tags, target_keywords)
            score += relevance_score * 0.40
            
            if relevance_score < 70:
                recommendations.append("Ensure all tags are relevant to your content")
            
            # Keyword coverage (35 points)
            keyword_coverage = 0
            if target_keywords:
                keyword_coverage = self._analyze_keyword_coverage_in_tags(tags, target_keywords)
                score += keyword_coverage * 0.35
                
                missing_keywords = [kw for kw in target_keywords if not any(kw.lower() in tag.lower() for tag in tags)]
                if missing_keywords:
                    recommendations.append(f"Add tags for missing keywords: {', '.join(missing_keywords[:3])}")
            else:
                score += 17.5  # Neutral score
            
            return {
                'score': min(100, score),
                'recommendations': recommendations,
                'details': {
                    'count_score': count_score,
                    'relevance_score': relevance_score,
                    'keyword_coverage': keyword_coverage,
                    'tag_count': tag_count
                }
            }
            
        except Exception as e:
            logger.error(f"Tags analysis failed: {e}")
            return {'score': 0, 'recommendations': ['Tags analysis failed']}
    
    def _score_length(self, actual: int, optimal: Dict[str, int]) -> float:
        """Score based on optimal length range"""
        if optimal['min'] <= actual <= optimal['max']:
            # Within acceptable range
            if actual == optimal['optimal']:
                return 100
            # Calculate distance from optimal
            distance = abs(actual - optimal['optimal'])
            max_distance = max(optimal['optimal'] - optimal['min'], optimal['max'] - optimal['optimal'])
            return max(60, 100 - (distance / max_distance) * 40)
        elif actual < optimal['min']:
            # Too short
            return max(20, (actual / optimal['min']) * 60)
        else:
            # Too long
            excess = actual - optimal['max']
            penalty = min(50, excess / optimal['max'] * 100)
            return max(10, 60 - penalty)
    
    def _score_count(self, actual: int, optimal: Dict[str, int]) -> float:
        """Score based on optimal count range"""
        return self._score_length(actual, optimal)
    
    def _analyze_keyword_placement(self, text: str, keywords: List[str], context: str) -> float:
        """Analyze keyword placement and density"""
        try:
            if not keywords:
                return 50  # Neutral score
            
            text_lower = text.lower()
            total_score = 0
            
            for i, keyword in enumerate(keywords):
                keyword_lower = keyword.lower()
                
                # Check if keyword exists
                if keyword_lower in text_lower:
                    keyword_score = 30  # Base score for presence
                    
                    # Bonus for primary keyword (first in list)
                    if i == 0:
                        # Check placement for primary keyword
                        if context == 'title' and text_lower.startswith(keyword_lower):
                            keyword_score += 20  # Beginning of title
                        elif context == 'description' and text_lower[:125].find(keyword_lower) != -1:
                            keyword_score += 15  # First 125 chars of description
                        
                        # Check keyword density
                        word_count = len(text.split())
                        keyword_count = text_lower.count(keyword_lower)
                        if word_count > 0:
                            density = (keyword_count / word_count) * 100
                            if 0.5 <= density <= 3.0:
                                keyword_score += 10  # Good density
                            elif density > 3.0:
                                keyword_score -= 5   # Over-optimization penalty
                    else:
                        keyword_score += 10  # Secondary keyword bonus
                    
                    # Weight by keyword importance (primary gets more weight)
                    weight = 1.0 if i == 0 else 0.5
                    total_score += keyword_score * weight
            
            # Normalize score based on number of keywords
            if keywords:
                max_possible = len(keywords) * 50  # Approximate max score
                normalized_score = min(100, (total_score / max_possible) * 100)
                return normalized_score
            
            return 0
            
        except Exception as e:
            logger.error(f"Keyword placement analysis failed: {e}")
            return 0
    
    def _analyze_title_engagement(self, title: str) -> float:
        """Analyze title for engagement factors"""
        try:
            score = 50  # Base score
            
            # Power words
            power_words = [
                'ultimate', 'best', 'complete', 'amazing', 'incredible', 'secret',
                'proven', 'essential', 'perfect', 'exclusive', 'advanced', 'simple',
                'quick', 'easy', 'powerful', 'effective', 'professional', 'expert'
            ]
            
            title_lower = title.lower()
            power_word_count = sum(1 for word in power_words if word in title_lower)
            score += min(20, power_word_count * 5)
            
            # Numbers (people love numbered lists)
            if re.search(r'\d+', title):
                score += 15
            
            # Question format
            if title.strip().endswith('?'):
                score += 10
            
            # Action words
            action_words = ['how to', 'learn', 'master', 'discover', 'create', 'build', 'make']
            if any(word in title_lower for word in action_words):
                score += 10
            
            # Current year (indicates fresh content)
            current_year = str(datetime.now().year)
            if current_year in title:
                score += 5
            
            return min(100, score)
            
        except Exception:
            return 50
    
    def _analyze_title_technical(self, title: str) -> float:
        """Analyze technical aspects of title"""
        try:
            score = 80  # Start with good score
            
            # Check for excessive capitalization
            if sum(1 for c in title if c.isupper()) / len(title) > 0.5:
                score -= 20
            
            # Check for excessive special characters
            special_chars = sum(1 for c in title if not c.isalnum() and c != ' ')
            if special_chars > 5:
                score -= 15
            
            # Check for clickbait indicators (too many caps/exclamation marks)
            if title.count('!') > 2:
                score -= 10
            
            # Check for emojis (can be good but not excessive)
            emoji_count = sum(1 for c in title if ord(c) > 127)
            if emoji_count > 3:
                score -= 10
            
            return max(0, score)
            
        except Exception:
            return 70
    
    def _analyze_description_structure(self, description: str) -> float:
        """Analyze description structure and formatting"""
        try:
            score = 50  # Base score
            
            # Check for paragraphs (line breaks)
            paragraph_count = description.count('\n\n') + 1
            if paragraph_count > 1:
                score += 20
            
            # Check for bullet points or lists
            if any(marker in description for marker in ['•', '-', '*', '1.', '2.']):
                score += 15
            
            # Check for timestamps
            if re.search(r'\d+:\d+', description):
                score += 10
            
            # Check for links (social media, website)
            if 'http' in description or 'www.' in description:
                score += 10
            
            # Check for hashtags
            if '#' in description:
                score += 5
            
            return min(100, score)
            
        except Exception:
            return 50
    
    def _analyze_call_to_action(self, description: str) -> float:
        """Analyze call-to-action elements"""
        try:
            score = 0
            description_lower = description.lower()
            
            # Common CTAs
            cta_phrases = [
                'like', 'subscribe', 'comment', 'share', 'follow',
                'click', 'watch', 'check out', 'download', 'visit'
            ]
            
            cta_count = sum(1 for phrase in cta_phrases if phrase in description_lower)
            score += min(60, cta_count * 15)
            
            # Specific YouTube CTAs
            youtube_ctas = ['like this video', 'subscribe for more', 'hit the bell', 'notification bell']
            if any(cta in description_lower for cta in youtube_ctas):
                score += 25
            
            # Social media mentions
            social_platforms = ['instagram', 'twitter', 'facebook', 'tiktok', 'discord']
            if any(platform in description_lower for platform in social_platforms):
                score += 15
            
            return min(100, score)
            
        except Exception:
            return 30
    
    def _analyze_tag_relevance(self, tags: List[str], target_keywords: List[str] = None) -> float:
        """Analyze tag relevance and quality"""
        try:
            if not tags:
                return 0
            
            score = 60  # Base score
            
            # Check tag length distribution
            avg_length = sum(len(tag) for tag in tags) / len(tags)
            if 5 <= avg_length <= 20:  # Good tag length range
                score += 20
            
            # Check for single vs multi-word tags (mix is good)
            single_word = sum(1 for tag in tags if len(tag.split()) == 1)
            multi_word = len(tags) - single_word
            
            if 0.3 <= (single_word / len(tags)) <= 0.7:  # Good mix
                score += 15
            
            # Check for duplicate or very similar tags
            unique_tags = set(tag.lower() for tag in tags)
            if len(unique_tags) == len(tags):
                score += 5
            else:
                score -= 10  # Penalty for duplicates
            
            return min(100, score)
            
        except Exception:
            return 50
    
    def _analyze_keyword_coverage_in_tags(self, tags: List[str], keywords: List[str]) -> float:
        """Analyze how well tags cover target keywords"""
        try:
            if not keywords or not tags:
                return 50
            
            tags_lower = [tag.lower() for tag in tags]
            covered_keywords = 0
            
            for keyword in keywords:
                keyword_lower = keyword.lower()
                # Check if keyword is covered by any tag
                if any(keyword_lower in tag or tag in keyword_lower for tag in tags_lower):
                    covered_keywords += 1
            
            coverage_percentage = (covered_keywords / len(keywords)) * 100
            return min(100, coverage_percentage)
            
        except Exception:
            return 0
    
    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade from score"""
        if score >= 95:
            return 'A+'
        elif score >= 90:
            return 'A'
        elif score >= 85:
            return 'A-'
        elif score >= 80:
            return 'B+'
        elif score >= 75:
            return 'B'
        elif score >= 70:
            return 'B-'
        elif score >= 65:
            return 'C+'
        elif score >= 60:
            return 'C'
        elif score >= 55:
            return 'C-'
        elif score >= 50:
            return 'D'
        else:
            return 'F'
    
    async def _identify_opportunities(self, title: str, description: str, tags: List[str], 
                                    keywords: List[str], current_score: float) -> List[str]:
        """Identify specific optimization opportunities"""
        opportunities = []
        
        try:
            # Low-hanging fruit based on current score
            if current_score < 60:
                opportunities.append("Focus on basic SEO optimization - title, description, and tags")
            
            # Title opportunities
            if len(title) < 30:
                opportunities.append("Expand title to 30-60 characters for better keyword coverage")
            
            if keywords and keywords[0].lower() not in title.lower():
                opportunities.append(f"Include primary keyword '{keywords[0]}' in title")
            
            # Description opportunities
            if len(description) < 200:
                opportunities.append("Expand description to at least 200 characters")
            
            if 'subscribe' not in description.lower():
                opportunities.append("Add call-to-action to subscribe in description")
            
            # Tags opportunities
            if len(tags) < 8:
                opportunities.append("Add more relevant tags (aim for 8-12)")
            
            if keywords:
                missing_keyword_tags = [kw for kw in keywords if not any(kw.lower() in tag.lower() for tag in tags)]
                if missing_keyword_tags:
                    opportunities.append(f"Create tags for keywords: {', '.join(missing_keyword_tags[:2])}")
            
            # Advanced opportunities
            if current_score >= 70:
                opportunities.append("Consider A/B testing different titles and thumbnails")
                opportunities.append("Analyze competitor content for additional keyword opportunities")
                opportunities.append("Create timestamps in description for better user experience")
            
            return opportunities[:6]  # Limit to top 6 opportunities
            
        except Exception as e:
            logger.error(f"Failed to identify opportunities: {e}")
            return ["Review and optimize basic SEO elements"]
    
    async def generate_optimized_title(self, original_title: str, keywords: List[str], 
                                     target_length: int = 50) -> List[str]:
        """Generate optimized title variations"""
        try:
            variations = []
            
            if not keywords:
                return [original_title]
            
            primary_keyword = keywords[0]
            
            # Variation 1: Keyword first
            variations.append(f"{primary_keyword}: {original_title}"[:target_length])
            
            # Variation 2: How-to format
            variations.append(f"How to {primary_keyword} - {original_title}"[:target_length])
            
            # Variation 3: Number-based
            variations.append(f"Top 5 {primary_keyword} Tips - {original_title}"[:target_length])
            
            # Variation 4: Year-specific
            current_year = datetime.now().year
            variations.append(f"{primary_keyword} {current_year} - {original_title}"[:target_length])
            
            # Variation 5: Question format
            variations.append(f"What is {primary_keyword}? {original_title}"[:target_length])
            
            # Clean up and remove duplicates
            clean_variations = []
            for var in variations:
                if len(var) >= 20 and var not in clean_variations:
                    clean_variations.append(var.strip())
            
            return clean_variations[:5]
            
        except Exception as e:
            logger.error(f"Failed to generate optimized titles: {e}")
            return [original_title]
    
    async def generate_optimized_description(self, original_description: str, 
                                           keywords: List[str], title: str) -> str:
        """Generate optimized description"""
        try:
            # Start with primary keyword in first 125 characters
            primary_keyword = keywords[0] if keywords else ""
            
            optimized = f"In this video, we cover {primary_keyword} "
            
            # Add original description
            if len(original_description) > 0:
                optimized += f"and {original_description.lower()}"
            else:
                optimized += f"with comprehensive tips and strategies."
            
            # Add paragraph breaks
            optimized += "\n\n"
            
            # Add timestamps section
            optimized += "📍 Timestamps:\n"
            optimized += "0:00 Introduction\n"
            optimized += "1:30 Main Content\n"
            optimized += "8:45 Conclusion\n\n"
            
            # Add keywords section
            if keywords:
                optimized += "🎯 Key Topics Covered:\n"
                for keyword in keywords[:5]:
                    optimized += f"• {keyword}\n"
                optimized += "\n"
            
            # Add call to action
            optimized += "👍 If you found this helpful, please like and subscribe for more content!\n"
            optimized += "💬 Leave a comment below with your thoughts or questions.\n\n"
            
            # Add hashtags
            if keywords:
                optimized += "Tags: "
                hashtags = [f"#{kw.replace(' ', '')}" for kw in keywords[:3]]
                optimized += " ".join(hashtags)
            
            return optimized
            
        except Exception as e:
            logger.error(f"Failed to generate optimized description: {e}")
            return original_description
    
    async def suggest_tags(self, title: str, description: str, keywords: List[str] = None) -> List[str]:
        """Suggest optimal tags for the video"""
        try:
            suggested_tags = []
            
            # Add primary keywords as tags
            if keywords:
                suggested_tags.extend(keywords[:3])
            
            # Extract key terms from title
            title_words = re.findall(r'\b\w+\b', title.lower())
            meaningful_title_words = [w for w in title_words if len(w) > 3]
            suggested_tags.extend(meaningful_title_words[:3])
            
            # Extract key terms from description
            description_words = re.findall(r'\b\w+\b', description.lower())
            word_freq = {}
            for word in description_words:
                if len(word) > 3:
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Get most frequent words
            top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            suggested_tags.extend([word for word, freq in top_words[:3]])
            
            # Add category-based tags
            category_tags = [
                "tutorial", "guide", "tips", "how to", "explained", 
                "review", "comparison", "beginner", "advanced"
            ]
            
            for tag in category_tags:
                if tag in title.lower() or tag in description.lower():
                    suggested_tags.append(tag)
            
            # Clean and deduplicate
            clean_tags = []
            seen = set()
            
            for tag in suggested_tags:
                tag_clean = tag.strip().lower()
                if tag_clean not in seen and len(tag_clean) > 2:
                    clean_tags.append(tag.strip().title())
                    seen.add(tag_clean)
            
            return clean_tags[:12]  # Limit to 12 tags
            
        except Exception as e:
            logger.error(f"Failed to suggest tags: {e}")
            return ["video", "tutorial", "guide"]

# Global instance
seo_optimizer = SEOOptimizer()