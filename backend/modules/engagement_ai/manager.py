"""
Engagement AI Manager
Handles automated comment replies, community posts, and audience interaction
"""

import asyncio
import logging
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import re
import random

# Sentiment analysis
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

# YouTube API
try:
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False

import httpx

from ..base import BaseModule

logger = logging.getLogger(__name__)

class EngagementManager(BaseModule):
    """AI-powered engagement and community management"""
    
    def __init__(self):
        super().__init__()
        self.module_name = "engagement_ai"
        
        # YouTube API
        self.youtube_service = None
        self.youtube_api_key = os.getenv("YOUTUBE_API_KEY")
        
        # AI APIs for response generation
        self.ai_api_endpoints = {
            "together": {
                "url": "https://api.together.xyz/v1/chat/completions",
                "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
                "api_key_env": "TOGETHER_API_KEY"
            },
            "openai": {
                "url": "https://api.openai.com/v1/chat/completions",
                "model": "gpt-3.5-turbo",
                "api_key_env": "OPENAI_API_KEY"
            }
        }
        
        # Reply templates and patterns
        self.reply_templates = {
            "positive": [
                "Thank you so much for watching! {custom}",
                "Really appreciate your support! {custom}",
                "Glad you enjoyed the video! {custom}",
                "Thanks for the positive feedback! {custom}",
                "Your support means everything! {custom}"
            ],
            "question": [
                "Great question! {custom}",
                "Thanks for asking! {custom}",
                "That's an excellent point! {custom}",
                "Let me address that: {custom}",
                "Good question! {custom}"
            ],
            "negative": [
                "Thanks for the feedback. {custom}",
                "I appreciate your perspective. {custom}",
                "Thank you for sharing your thoughts. {custom}",
                "I understand your concern. {custom}",
                "Thanks for letting me know. {custom}"
            ],
            "neutral": [
                "Thanks for watching! {custom}",
                "Appreciate your comment! {custom}",
                "Thank you for engaging! {custom}",
                "Thanks for being part of the community! {custom}",
                "Appreciate you taking the time to comment! {custom}"
            ]
        }
        
        # Community post templates
        self.community_post_templates = {
            "update": [
                "Hey everyone! Just wanted to share a quick update: {content}",
                "Community update: {content}",
                "Quick update for you all: {content}",
                "Thought you'd like to know: {content}"
            ],
            "question": [
                "I'd love to hear your thoughts: {content}",
                "What do you think about this: {content}",
                "Question for the community: {content}",
                "Your opinion matters - {content}"
            ],
            "behind_scenes": [
                "Behind the scenes: {content}",
                "Here's what's happening behind the camera: {content}",
                "Sneak peek: {content}",
                "Exclusive look: {content}"
            ],
            "appreciation": [
                "Just wanted to say thank you: {content}",
                "Feeling grateful: {content}",
                "Appreciation post: {content}",
                "Thank you all: {content}"
            ]
        }
        
        # Sentiment keywords
        self.sentiment_keywords = {
            "positive": ["great", "awesome", "amazing", "love", "fantastic", "excellent", "perfect", "wonderful", "best", "incredible"],
            "negative": ["bad", "terrible", "awful", "hate", "worst", "horrible", "stupid", "boring", "waste", "disappointing"],
            "question": ["?", "how", "what", "why", "when", "where", "which", "can you", "could you", "would you", "do you"]
        }
        
        # Language support
        self.supported_languages = {
            "en": "english",
            "es": "spanish",
            "fr": "french",
            "de": "german",
            "it": "italian",
            "pt": "portuguese",
            "ru": "russian",
            "ja": "japanese",
            "ko": "korean",
            "zh": "chinese"
        }
    
    async def _setup_module(self):
        """Initialize engagement manager"""
        await super()._setup_module()
        
        try:
            # Initialize YouTube API
            if self.youtube_api_key and YOUTUBE_API_AVAILABLE:
                self.youtube_service = build("youtube", "v3", developerKey=self.youtube_api_key)
                self.logger.info("YouTube API initialized")
            else:
                self.logger.warning("YouTube API not available - comment features limited")
            
            if not TEXTBLOB_AVAILABLE:
                self.logger.warning("TextBlob not available - sentiment analysis limited")
            
            self.logger.info("Engagement AI Manager initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize engagement manager: {str(e)}")
            raise
    
    async def process_comments(
        self,
        video_id: str,
        channel_id: str,
        language: str = "en",
        max_comments: int = 50
    ) -> Dict[str, Any]:
        """Process and reply to comments on a video"""
        
        try:
            if not self.youtube_service:
                self.logger.warning("YouTube API not available")
                return {"processed": 0, "replied": 0, "errors": 0}
            
            self.logger.info(f"Processing comments for video: {video_id}")
            
            # Fetch comments
            comments = await self._fetch_video_comments(video_id, max_comments)
            
            processed_count = 0
            replied_count = 0
            error_count = 0
            
            for comment in comments:
                try:
                    # Analyze comment
                    analysis = await self._analyze_comment(comment, language)
                    
                    # Decide if reply is needed
                    should_reply = await self._should_reply_to_comment(comment, analysis)
                    
                    if should_reply:
                        # Generate reply
                        reply = await self._generate_comment_reply(comment, analysis, language)
                        
                        if reply:
                            # Post reply (in a real implementation)
                            # await self._post_comment_reply(comment["id"], reply)
                            replied_count += 1
                            self.logger.info(f"Generated reply for comment: {comment['snippet']['textDisplay'][:50]}...")
                    
                    processed_count += 1
                    
                except Exception as e:
                    self.logger.error(f"Error processing comment: {str(e)}")
                    error_count += 1
            
            await self.log_activity("comments_processed", {
                "video_id": video_id,
                "processed": processed_count,
                "replied": replied_count,
                "errors": error_count
            })
            
            return {
                "processed": processed_count,
                "replied": replied_count,
                "errors": error_count,
                "comments": comments[:10]  # Return sample for review
            }
            
        except Exception as e:
            self.logger.error(f"Comment processing failed: {str(e)}")
            raise
    
    async def _fetch_video_comments(self, video_id: str, max_comments: int) -> List[Dict[str, Any]]:
        """Fetch comments from a YouTube video"""
        
        try:
            if not self.youtube_service:
                return []
            
            comments = []
            next_page_token = None
            
            while len(comments) < max_comments:
                request = self.youtube_service.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=min(100, max_comments - len(comments)),
                    order="time",
                    pageToken=next_page_token
                )
                
                response = request.execute()
                
                for item in response.get("items", []):
                    comments.append(item)
                
                next_page_token = response.get("nextPageToken")
                if not next_page_token:
                    break
            
            self.logger.info(f"Fetched {len(comments)} comments for video {video_id}")
            return comments
            
        except Exception as e:
            self.logger.error(f"Failed to fetch comments: {str(e)}")
            return []
    
    async def _analyze_comment(self, comment: Dict[str, Any], language: str) -> Dict[str, Any]:
        """Analyze comment sentiment and intent"""
        
        try:
            text = comment["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            
            # Basic sentiment analysis
            sentiment = await self._analyze_sentiment(text)
            
            # Intent detection
            intent = await self._detect_intent(text)
            
            # Language detection (if different from expected)
            detected_language = await self._detect_language(text)
            
            return {
                "text": text,
                "sentiment": sentiment,
                "intent": intent,
                "language": detected_language,
                "author": comment["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"],
                "published_at": comment["snippet"]["topLevelComment"]["snippet"]["publishedAt"],
                "like_count": comment["snippet"]["topLevelComment"]["snippet"]["likeCount"]
            }
            
        except Exception as e:
            self.logger.error(f"Comment analysis failed: {str(e)}")
            return {
                "text": "",
                "sentiment": "neutral",
                "intent": "unknown",
                "language": language,
                "author": "Unknown",
                "published_at": "",
                "like_count": 0
            }
    
    async def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text"""
        
        try:
            # Use TextBlob if available
            if TEXTBLOB_AVAILABLE:
                blob = TextBlob(text)
                polarity = blob.sentiment.polarity
                
                if polarity > 0.1:
                    return "positive"
                elif polarity < -0.1:
                    return "negative"
                else:
                    return "neutral"
            
            # Fallback: keyword-based sentiment
            text_lower = text.lower()
            
            positive_score = sum(1 for word in self.sentiment_keywords["positive"] if word in text_lower)
            negative_score = sum(1 for word in self.sentiment_keywords["negative"] if word in text_lower)
            
            if positive_score > negative_score:
                return "positive"
            elif negative_score > positive_score:
                return "negative"
            else:
                return "neutral"
                
        except Exception as e:
            self.logger.error(f"Sentiment analysis failed: {str(e)}")
            return "neutral"
    
    async def _detect_intent(self, text: str) -> str:
        """Detect intent of comment"""
        
        try:
            text_lower = text.lower()
            
            # Check for question
            if any(keyword in text_lower for keyword in self.sentiment_keywords["question"]):
                return "question"
            
            # Check for praise
            if any(keyword in text_lower for keyword in self.sentiment_keywords["positive"][:5]):
                return "praise"
            
            # Check for complaint
            if any(keyword in text_lower for keyword in self.sentiment_keywords["negative"][:5]):
                return "complaint"
            
            # Check for feedback/suggestion
            if any(phrase in text_lower for phrase in ["suggest", "recommend", "should", "could", "feedback"]):
                return "feedback"
            
            return "general"
            
        except Exception as e:
            self.logger.error(f"Intent detection failed: {str(e)}")
            return "general"
    
    async def _detect_language(self, text: str) -> str:
        """Detect language of text"""
        
        try:
            if TEXTBLOB_AVAILABLE:
                blob = TextBlob(text)
                detected = blob.detect_language()
                return detected if detected in self.supported_languages else "en"
            
            # Fallback: assume English
            return "en"
            
        except Exception:
            return "en"
    
    async def _should_reply_to_comment(self, comment: Dict[str, Any], analysis: Dict[str, Any]) -> bool:
        """Determine if a comment should receive a reply"""
        
        try:
            # Reply criteria
            sentiment = analysis["sentiment"]
            intent = analysis["intent"]
            like_count = analysis.get("like_count", 0)
            
            # Always reply to questions
            if intent == "question":
                return True
            
            # Reply to popular comments
            if like_count >= 5:
                return True
            
            # Reply to complaints to address concerns
            if intent == "complaint":
                return True
            
            # Sometimes reply to positive comments
            if sentiment == "positive" and random.random() < 0.3:  # 30% chance
                return True
            
            # Sometimes reply to feedback
            if intent == "feedback" and random.random() < 0.5:  # 50% chance
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Reply decision failed: {str(e)}")
            return False
    
    async def _generate_comment_reply(
        self,
        comment: Dict[str, Any],
        analysis: Dict[str, Any],
        language: str
    ) -> Optional[str]:
        """Generate AI reply to comment"""
        
        try:
            # Try AI generation first
            ai_reply = await self._generate_ai_reply(comment, analysis, language)
            if ai_reply:
                return ai_reply
            
            # Fallback to templates
            return await self._generate_template_reply(analysis)
            
        except Exception as e:
            self.logger.error(f"Reply generation failed: {str(e)}")
            return None
    
    async def _generate_ai_reply(
        self,
        comment: Dict[str, Any],
        analysis: Dict[str, Any],
        language: str
    ) -> Optional[str]:
        """Generate AI-powered reply"""
        
        try:
            # Build prompt for AI
            prompt = f"""
Generate a friendly, engaging reply to this YouTube comment:

Comment: "{analysis['text']}"
Sentiment: {analysis['sentiment']}
Intent: {analysis['intent']}
Language: {language}

Reply guidelines:
- Be friendly and authentic
- Keep it under 100 words
- Match the language of the comment
- Be helpful if it's a question
- Be appreciative if it's positive feedback
- Be professional if it's criticism
- Include a call to action if appropriate (like/subscribe/check other videos)

Reply:"""

            # Try different AI APIs
            for api_name, api_config in self.ai_api_endpoints.items():
                api_key = os.getenv(api_config["api_key_env"])
                if api_key:
                    reply = await self._call_ai_api(prompt, api_config, api_key)
                    if reply:
                        return reply.strip()
            
            return None
            
        except Exception as e:
            self.logger.error(f"AI reply generation failed: {str(e)}")
            return None
    
    async def _call_ai_api(self, prompt: str, api_config: Dict[str, Any], api_key: str) -> Optional[str]:
        """Call AI API for text generation"""
        
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": api_config["model"],
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful and friendly YouTube creator responding to comments on your videos."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 150,
                "temperature": 0.7
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    api_config["url"],
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    self.logger.warning(f"AI API error: {response.status_code}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"AI API call failed: {str(e)}")
            return None
    
    async def _generate_template_reply(self, analysis: Dict[str, Any]) -> str:
        """Generate template-based reply"""
        
        try:
            sentiment = analysis["sentiment"]
            intent = analysis["intent"]
            
            # Choose template category
            if intent == "question":
                category = "question"
            elif sentiment == "positive":
                category = "positive"
            elif sentiment == "negative":
                category = "negative"
            else:
                category = "neutral"
            
            # Select random template
            templates = self.reply_templates.get(category, self.reply_templates["neutral"])
            template = random.choice(templates)
            
            # Generate custom content based on intent
            custom_content = ""
            if intent == "question":
                custom_content = "I'll consider making a detailed video about this topic!"
            elif sentiment == "positive":
                custom_content = "Don't forget to subscribe for more content like this!"
            elif intent == "feedback":
                custom_content = "Your feedback helps me improve my content."
            else:
                custom_content = "Let me know what you'd like to see next!"
            
            return template.format(custom=custom_content)
            
        except Exception as e:
            self.logger.error(f"Template reply generation failed: {str(e)}")
            return "Thanks for your comment!"
    
    async def create_community_post(
        self,
        channel_id: str,
        post_type: str,
        content: str,
        image_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a community post"""
        
        try:
            # Generate post content
            post_content = await self._generate_community_post(post_type, content)
            
            # In a real implementation, this would post to YouTube
            # For now, we'll return the generated content
            
            post_data = {
                "channel_id": channel_id,
                "type": post_type,
                "content": post_content,
                "image_path": image_path,
                "created_at": datetime.utcnow().isoformat(),
                "status": "generated"  # Would be "posted" in real implementation
            }
            
            await self.log_activity("community_post_created", {
                "channel_id": channel_id,
                "type": post_type,
                "content_length": len(post_content)
            })
            
            return post_data
            
        except Exception as e:
            self.logger.error(f"Community post creation failed: {str(e)}")
            raise
    
    async def _generate_community_post(self, post_type: str, content: str) -> str:
        """Generate community post content"""
        
        try:
            # Choose template
            templates = self.community_post_templates.get(post_type, self.community_post_templates["update"])
            template = random.choice(templates)
            
            # Format content
            post_content = template.format(content=content)
            
            # Add hashtags based on type
            hashtags = []
            if post_type == "update":
                hashtags = ["#Update", "#Community"]
            elif post_type == "question":
                hashtags = ["#Question", "#YourThoughts"]
            elif post_type == "behind_scenes":
                hashtags = ["#BehindTheScenes", "#Exclusive"]
            elif post_type == "appreciation":
                hashtags = ["#ThankYou", "#Grateful"]
            
            if hashtags:
                post_content += f"\n\n{' '.join(hashtags)}"
            
            return post_content
            
        except Exception as e:
            self.logger.error(f"Community post generation failed: {str(e)}")
            return content
    
    async def generate_engagement_insights(self, channel_id: str, days: int = 30) -> Dict[str, Any]:
        """Generate engagement insights and recommendations"""
        
        try:
            # This would analyze real engagement data in a full implementation
            # For now, we'll return sample insights
            
            insights = {
                "period_days": days,
                "total_comments": 1250,
                "reply_rate": 0.35,
                "average_sentiment": "positive",
                "top_topics": [
                    {"topic": "Tutorial requests", "count": 45},
                    {"topic": "Positive feedback", "count": 38},
                    {"topic": "Technical questions", "count": 32},
                    {"topic": "Feature suggestions", "count": 28}
                ],
                "peak_engagement_hours": ["18:00-20:00", "12:00-14:00"],
                "recommended_actions": [
                    "Increase reply rate to questions (currently 60%, target 80%)",
                    "Create tutorial videos based on frequent requests",
                    "Schedule community posts during peak hours",
                    "Address technical questions in FAQ video"
                ],
                "sentiment_breakdown": {
                    "positive": 0.65,
                    "neutral": 0.25,
                    "negative": 0.10
                }
            }
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Engagement insights generation failed: {str(e)}")
            return {}
    
    def get_supported_languages(self) -> List[str]:
        """Get supported languages for engagement"""
        return list(self.supported_languages.keys())
    
    def get_reply_templates(self) -> Dict[str, List[str]]:
        """Get available reply templates"""
        return self.reply_templates
    
    def get_engagement_stats(self) -> Dict[str, Any]:
        """Get engagement manager statistics"""
        stats = super().get_status()
        stats.update({
            "youtube_api_available": self.youtube_service is not None,
            "sentiment_analysis_available": TEXTBLOB_AVAILABLE,
            "supported_languages": len(self.supported_languages),
            "reply_templates": sum(len(templates) for templates in self.reply_templates.values()),
            "community_post_types": len(self.community_post_templates)
        })
        return stats