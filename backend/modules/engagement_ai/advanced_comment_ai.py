"""
Advanced Comment AI
Context-aware replies with per-channel customization and language optimization
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import re

import httpx

logger = logging.getLogger(__name__)

@dataclass
class ChannelContext:
    """Channel-specific context for replies"""
    channel_id: str
    channel_name: str
    niche: str  # gaming, tech, education, etc.
    tone: str  # friendly, professional, casual, etc.
    language: str
    custom_responses: Dict[str, List[str]] = field(default_factory=dict)
    banned_words: List[str] = field(default_factory=list)
    auto_reply_rate: float = 0.3
    subscriber_count: int = 0
    recent_videos: List[str] = field(default_factory=list)
    
@dataclass
class CommentContext:
    """Context for individual comment analysis"""
    comment_id: str
    user_id: str
    user_name: str
    comment_text: str
    timestamp: datetime
    video_id: str
    video_title: str
    sentiment: str
    intent: str
    language: str
    user_history: Dict[str, Any] = field(default_factory=dict)
    thread_context: List[str] = field(default_factory=list)
    
@dataclass
class ReplyTemplate:
    """Smart reply template with context variables"""
    template: str
    contexts: List[str]  # When to use this template
    variables: List[str]  # Available variables
    languages: List[str]  # Supported languages
    sentiment_filter: Optional[str] = None
    min_subscriber_count: int = 0

class AdvancedCommentAI:
    """Advanced AI-powered comment management with context awareness"""
    
    def __init__(self):
        self.module_name = "advanced_comment_ai"
        
        # Channel contexts
        self.channel_contexts: Dict[str, ChannelContext] = {}
        
        # Advanced reply templates
        self.context_templates: Dict[str, List[ReplyTemplate]] = {
            "gaming": [
                ReplyTemplate(
                    template="That was an epic {action}! {user_name}, what's your favorite strategy for {game_element}? Drop your tips below! 🎮",
                    contexts=["gameplay_discussion", "strategy_question"],
                    variables=["action", "user_name", "game_element"],
                    languages=["en", "es", "fr"]
                ),
                ReplyTemplate(
                    template="GG {user_name}! That boss fight was intense! Have you tried the secret technique I showed in my last video? 🔥",
                    contexts=["boss_fight", "difficulty_discussion"],
                    variables=["user_name"],
                    languages=["en"],
                    sentiment_filter="positive"
                )
            ],
            "tech": [
                ReplyTemplate(
                    template="Great question, {user_name}! The {tech_topic} you mentioned is actually covered in detail in my {related_video}. I'll pin the timestamp! 💡",
                    contexts=["technical_question", "how_to_request"],
                    variables=["user_name", "tech_topic", "related_video"],
                    languages=["en", "de"]
                ),
                ReplyTemplate(
                    template="Thanks for catching that, {user_name}! You're absolutely right about {technical_detail}. I'll update the description with the correction! 🛠️",
                    contexts=["error_correction", "technical_feedback"],
                    variables=["user_name", "technical_detail"],
                    languages=["en"]
                )
            ],
            "education": [
                ReplyTemplate(
                    template="Excellent insight, {user_name}! Your understanding of {concept} is spot on. For others who want to dive deeper, check out {resource_link}! 📚",
                    contexts=["concept_discussion", "learning_question"],
                    variables=["user_name", "concept", "resource_link"],
                    languages=["en", "es", "fr", "pt"]
                ),
                ReplyTemplate(
                    template="{user_name}, that's a common misconception about {topic}! The key difference is {explanation}. Hope that helps clarify! ✨",
                    contexts=["misconception_correction", "clarification_needed"],
                    variables=["user_name", "topic", "explanation"],
                    languages=["en"]
                )
            ]
        }
        
        # Language-specific responses
        self.language_templates = {
            "en": {
                "greeting": ["Hey {user_name}! Welcome to the community! 👋", "Hi {user_name}! Thanks for watching! 😊"],
                "thanks": ["Thank you so much, {user_name}! ❤️", "Really appreciate that, {user_name}! 🙏"],
                "question": ["Great question, {user_name}! 🤔", "That's a thoughtful question, {user_name}! 💭"]
            },
            "es": {
                "greeting": ["¡Hola {user_name}! ¡Bienvenido a la comunidad! 👋", "¡Hola {user_name}! ¡Gracias por ver! 😊"],
                "thanks": ["¡Muchas gracias, {user_name}! ❤️", "¡Realmente aprecio eso, {user_name}! 🙏"],
                "question": ["¡Excelente pregunta, {user_name}! 🤔", "¡Esa es una pregunta reflexiva, {user_name}! 💭"]
            },
            "fr": {
                "greeting": ["Salut {user_name}! Bienvenue dans la communauté! 👋", "Salut {user_name}! Merci de regarder! 😊"],
                "thanks": ["Merci beaucoup, {user_name}! ❤️", "J'apprécie vraiment ça, {user_name}! 🙏"],
                "question": ["Excellente question, {user_name}! 🤔", "C'est une question réfléchie, {user_name}! 💭"]
            },
            "de": {
                "greeting": ["Hallo {user_name}! Willkommen in der Community! 👋", "Hallo {user_name}! Danke fürs Zuschauen! 😊"],
                "thanks": ["Vielen Dank, {user_name}! ❤️", "Das schätze ich wirklich, {user_name}! 🙏"],
                "question": ["Großartige Frage, {user_name}! 🤔", "Das ist eine durchdachte Frage, {user_name}! 💭"]
            },
            "pt": {
                "greeting": ["Olá {user_name}! Bem-vindo à comunidade! 👋", "Oi {user_name}! Obrigado por assistir! 😊"],
                "thanks": ["Muito obrigado, {user_name}! ❤️", "Realmente aprecio isso, {user_name}! 🙏"],
                "question": ["Excelente pergunta, {user_name}! 🤔", "Essa é uma pergunta bem pensada, {user_name}! 💭"]
            }
        }
        
        # Context analysis patterns
        self.context_patterns = {
            "gaming": {
                "keywords": ["game", "play", "level", "boss", "strategy", "gameplay", "character", "weapon", "score"],
                "intent_patterns": {
                    "strategy_question": r"how.*(?:beat|win|strategy|tips)",
                    "difficulty_discussion": r"(?:hard|difficult|easy|tough|boss)",
                    "gameplay_discussion": r"(?:favorite|best|worst|love|hate).*(?:game|level|character)"
                }
            },
            "tech": {
                "keywords": ["code", "programming", "software", "hardware", "tutorial", "guide", "setup", "install"],
                "intent_patterns": {
                    "technical_question": r"how.*(?:do|setup|install|configure)",
                    "error_discussion": r"(?:error|bug|issue|problem|wrong)",
                    "how_to_request": r"(?:can you|could you).*(?:show|tutorial|guide)"
                }
            },
            "education": {
                "keywords": ["learn", "understand", "explain", "concept", "theory", "example", "study", "knowledge"],
                "intent_patterns": {
                    "concept_discussion": r"(?:understand|explain|concept|theory)",
                    "learning_question": r"(?:how.*learn|what.*mean|why.*important)",
                    "clarification_needed": r"(?:confused|don't understand|unclear|what.*difference)"
                }
            }
        }
        
        # AI API configurations
        self.ai_apis = {
            "openai": {
                "url": "https://api.openai.com/v1/chat/completions",
                "model": "gpt-3.5-turbo",
                "api_key_env": "OPENAI_API_KEY"
            },
            "anthropic": {
                "url": "https://api.anthropic.com/v1/messages",
                "model": "claude-3-sonnet-20240229",
                "api_key_env": "ANTHROPIC_API_KEY"
            },
            "together": {
                "url": "https://api.together.xyz/v1/chat/completions",
                "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
                "api_key_env": "TOGETHER_API_KEY"
            }
        }
    
    async def setup_channel_context(self, channel_id: str, channel_config: Dict[str, Any]) -> bool:
        """Setup context for a specific channel"""
        try:
            context = ChannelContext(
                channel_id=channel_id,
                channel_name=channel_config.get("name", ""),
                niche=channel_config.get("niche", "general"),
                tone=channel_config.get("tone", "friendly"),
                language=channel_config.get("language", "en"),
                custom_responses=channel_config.get("custom_responses", {}),
                banned_words=channel_config.get("banned_words", []),
                auto_reply_rate=channel_config.get("auto_reply_rate", 0.3),
                subscriber_count=channel_config.get("subscriber_count", 0),
                recent_videos=channel_config.get("recent_videos", [])
            )
            
            self.channel_contexts[channel_id] = context
            logger.info(f"Setup context for channel {channel_id} ({context.niche}, {context.language})")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up channel context: {str(e)}")
            return False
    
    async def analyze_comment_context(
        self,
        comment_data: Dict[str, Any],
        channel_id: str,
        video_context: Dict[str, Any] = None
    ) -> CommentContext:
        """Analyze comment with full context"""
        try:
            # Extract basic comment info
            comment_text = comment_data.get("text", "")
            user_name = comment_data.get("user", "")
            user_id = comment_data.get("user_id", "")
            
            # Get channel context
            channel_context = self.channel_contexts.get(channel_id)
            if not channel_context:
                # Create default context
                await self.setup_channel_context(channel_id, {"language": "en", "niche": "general"})
                channel_context = self.channel_contexts[channel_id]
            
            # Analyze sentiment and intent
            sentiment = await self._analyze_sentiment_advanced(comment_text, channel_context)
            intent = await self._analyze_intent_advanced(comment_text, channel_context)
            
            # Detect language
            language = await self._detect_language_advanced(comment_text)
            
            # Get user history (if available)
            user_history = await self._get_user_history(user_id, channel_id)
            
            # Get thread context
            thread_context = await self._get_thread_context(comment_data.get("parent_id"))
            
            return CommentContext(
                comment_id=comment_data.get("id", ""),
                user_id=user_id,
                user_name=user_name,
                comment_text=comment_text,
                timestamp=datetime.utcnow(),
                video_id=video_context.get("video_id", "") if video_context else "",
                video_title=video_context.get("title", "") if video_context else "",
                sentiment=sentiment,
                intent=intent,
                language=language,
                user_history=user_history,
                thread_context=thread_context
            )
            
        except Exception as e:
            logger.error(f"Error analyzing comment context: {str(e)}")
            # Return basic context
            return CommentContext(
                comment_id=comment_data.get("id", ""),
                user_id=comment_data.get("user_id", ""),
                user_name=comment_data.get("user", ""),
                comment_text=comment_data.get("text", ""),
                timestamp=datetime.utcnow(),
                video_id="",
                video_title="",
                sentiment="neutral",
                intent="general",
                language="en"
            )
    
    async def generate_context_aware_reply(
        self,
        comment_context: CommentContext,
        channel_id: str
    ) -> Optional[str]:
        """Generate context-aware reply"""
        try:
            channel_context = self.channel_contexts.get(channel_id)
            if not channel_context:
                return None
            
            # Try AI generation first
            ai_reply = await self._generate_ai_contextual_reply(comment_context, channel_context)
            if ai_reply:
                return ai_reply
            
            # Fallback to template-based reply
            template_reply = await self._generate_template_contextual_reply(comment_context, channel_context)
            return template_reply
            
        except Exception as e:
            logger.error(f"Error generating context-aware reply: {str(e)}")
            return None
    
    async def _analyze_sentiment_advanced(self, text: str, channel_context: ChannelContext) -> str:
        """Advanced sentiment analysis with channel context"""
        try:
            text_lower = text.lower()
            
            # Channel-specific sentiment indicators
            if channel_context.niche == "gaming":
                positive_indicators = ["gg", "epic", "awesome", "clutch", "poggers", "nice play"]
                negative_indicators = ["noob", "trash", "bad", "terrible", "worst"]
            elif channel_context.niche == "tech":
                positive_indicators = ["helpful", "clear", "works", "solved", "perfect"]
                negative_indicators = ["confusing", "broken", "error", "doesn't work", "buggy"]
            else:
                positive_indicators = ["great", "love", "amazing", "awesome", "perfect"]
                negative_indicators = ["hate", "bad", "terrible", "awful", "worst"]
            
            # Score sentiment
            positive_score = sum(1 for indicator in positive_indicators if indicator in text_lower)
            negative_score = sum(1 for indicator in negative_indicators if indicator in text_lower)
            
            if positive_score > negative_score:
                return "positive"
            elif negative_score > positive_score:
                return "negative"
            else:
                return "neutral"
                
        except Exception as e:
            logger.error(f"Error in advanced sentiment analysis: {str(e)}")
            return "neutral"
    
    async def _analyze_intent_advanced(self, text: str, channel_context: ChannelContext) -> str:
        """Advanced intent analysis with niche-specific patterns"""
        try:
            text_lower = text.lower()
            niche = channel_context.niche
            
            if niche in self.context_patterns:
                patterns = self.context_patterns[niche]["intent_patterns"]
                
                for intent, pattern in patterns.items():
                    if re.search(pattern, text_lower):
                        return intent
            
            # General intent detection
            if "?" in text or any(word in text_lower for word in ["how", "what", "why", "when", "where"]):
                return "question"
            elif any(word in text_lower for word in ["thank", "thanks", "appreciate"]):
                return "appreciation"
            elif any(word in text_lower for word in ["love", "awesome", "great", "amazing"]):
                return "praise"
            elif any(word in text_lower for word in ["wrong", "error", "mistake", "fix"]):
                return "correction"
            else:
                return "general"
                
        except Exception as e:
            logger.error(f"Error in advanced intent analysis: {str(e)}")
            return "general"
    
    async def _detect_language_advanced(self, text: str) -> str:
        """Advanced language detection"""
        try:
            # Simple heuristic-based detection
            text_lower = text.lower()
            
            # Spanish indicators
            spanish_words = ["que", "como", "donde", "cuando", "porque", "gracias", "hola", "muy", "esta", "con"]
            if sum(1 for word in spanish_words if word in text_lower) >= 2:
                return "es"
            
            # French indicators
            french_words = ["que", "comme", "avec", "pour", "dans", "est", "merci", "bonjour", "très", "vous"]
            if sum(1 for word in french_words if word in text_lower) >= 2:
                return "fr"
            
            # German indicators
            german_words = ["und", "der", "die", "das", "ist", "mit", "für", "wie", "was", "danke"]
            if sum(1 for word in german_words if word in text_lower) >= 2:
                return "de"
            
            # Portuguese indicators
            portuguese_words = ["que", "como", "com", "para", "muito", "obrigado", "olá", "está", "tem", "por"]
            if sum(1 for word in portuguese_words if word in text_lower) >= 2:
                return "pt"
            
            # Default to English
            return "en"
            
        except Exception as e:
            logger.error(f"Error in language detection: {str(e)}")
            return "en"
    
    async def _get_user_history(self, user_id: str, channel_id: str) -> Dict[str, Any]:
        """Get user interaction history"""
        try:
            # This would fetch from database in real implementation
            return {
                "previous_comments": 0,
                "is_regular": False,
                "last_interaction": None,
                "sentiment_history": [],
                "topics_discussed": []
            }
        except Exception as e:
            logger.error(f"Error getting user history: {str(e)}")
            return {}
    
    async def _get_thread_context(self, parent_id: Optional[str]) -> List[str]:
        """Get context from comment thread"""
        try:
            if not parent_id:
                return []
            
            # This would fetch thread context in real implementation
            return []
            
        except Exception as e:
            logger.error(f"Error getting thread context: {str(e)}")
            return []
    
    async def _generate_ai_contextual_reply(
        self,
        comment_context: CommentContext,
        channel_context: ChannelContext
    ) -> Optional[str]:
        """Generate AI reply with full context"""
        try:
            # Build comprehensive prompt
            prompt = f"""
Generate a personalized reply to this YouTube comment with the following context:

Channel Info:
- Niche: {channel_context.niche}
- Tone: {channel_context.tone}
- Language: {channel_context.language}
- Subscriber Count: {channel_context.subscriber_count:,}

Comment Details:
- User: {comment_context.user_name}
- Text: "{comment_context.comment_text}"
- Sentiment: {comment_context.sentiment}
- Intent: {comment_context.intent}
- Language: {comment_context.language}
- Video: {comment_context.video_title}

Context Guidelines:
- Match the channel's {channel_context.tone} tone
- Respond in {comment_context.language}
- Consider this is a {channel_context.niche} channel
- Address the {comment_context.intent} intent appropriately
- Keep response under 100 words
- Include relevant emojis
- Be authentic and engaging
- Reference the video or channel content when relevant

Reply:"""

            # Try different AI APIs
            for api_name, api_config in self.ai_apis.items():
                api_key = os.getenv(api_config["api_key_env"])
                if api_key:
                    reply = await self._call_contextual_ai_api(prompt, api_config, api_key)
                    if reply:
                        # Post-process reply
                        processed_reply = await self._post_process_reply(reply, comment_context, channel_context)
                        return processed_reply
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating AI contextual reply: {str(e)}")
            return None
    
    async def _call_contextual_ai_api(self, prompt: str, api_config: Dict[str, Any], api_key: str) -> Optional[str]:
        """Call AI API with context-aware prompt"""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            if "anthropic" in api_config["url"]:
                payload = {
                    "model": api_config["model"],
                    "max_tokens": 150,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                }
            else:
                payload = {
                    "model": api_config["model"],
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful YouTube creator responding to comments. Be friendly, authentic, and engaging."
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
                    
                    if "anthropic" in api_config["url"]:
                        return data["content"][0]["text"]
                    else:
                        return data["choices"][0]["message"]["content"]
                else:
                    logger.warning(f"AI API error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"AI API call failed: {str(e)}")
            return None
    
    async def _generate_template_contextual_reply(
        self,
        comment_context: CommentContext,
        channel_context: ChannelContext
    ) -> str:
        """Generate template-based contextual reply"""
        try:
            niche = channel_context.niche
            language = comment_context.language
            intent = comment_context.intent
            
            # Try niche-specific templates first
            if niche in self.context_templates:
                for template in self.context_templates[niche]:
                    if (intent in template.contexts and 
                        language in template.languages and
                        (not template.sentiment_filter or template.sentiment_filter == comment_context.sentiment)):
                        
                        # Fill template variables
                        reply = template.template.format(
                            user_name=comment_context.user_name,
                            action="move",  # Default values
                            game_element="level",
                            tech_topic="setup",
                            related_video="previous tutorial",
                            technical_detail="configuration",
                            concept="principle",
                            resource_link="description",
                            topic="subject",
                            explanation="the main difference"
                        )
                        return reply
            
            # Fallback to language-specific templates
            if language in self.language_templates:
                lang_templates = self.language_templates[language]
                
                if intent == "question" and "question" in lang_templates:
                    template = lang_templates["question"][0]
                elif comment_context.sentiment == "positive" and "thanks" in lang_templates:
                    template = lang_templates["thanks"][0]
                else:
                    template = lang_templates["greeting"][0]
                
                return template.format(user_name=comment_context.user_name)
            
            # Final fallback
            return f"Thanks for your comment, {comment_context.user_name}! 😊"
            
        except Exception as e:
            logger.error(f"Error generating template contextual reply: {str(e)}")
            return f"Thanks for your comment, {comment_context.user_name}! 😊"
    
    async def _post_process_reply(
        self,
        reply: str,
        comment_context: CommentContext,
        channel_context: ChannelContext
    ) -> str:
        """Post-process generated reply"""
        try:
            # Remove quotes if present
            reply = reply.strip().strip('"').strip("'")
            
            # Ensure proper length
            if len(reply) > 280:  # YouTube comment limit
                reply = reply[:277] + "..."
            
            # Add channel-specific elements
            if channel_context.niche == "gaming" and "🎮" not in reply:
                reply += " 🎮"
            elif channel_context.niche == "tech" and "💡" not in reply:
                reply += " 💡"
            elif channel_context.niche == "education" and "📚" not in reply:
                reply += " 📚"
            
            # Filter banned words
            for banned_word in channel_context.banned_words:
                reply = reply.replace(banned_word, "*" * len(banned_word))
            
            return reply
            
        except Exception as e:
            logger.error(f"Error post-processing reply: {str(e)}")
            return reply
    
    async def get_reply_suggestions(
        self,
        comment_context: CommentContext,
        channel_id: str,
        count: int = 3
    ) -> List[str]:
        """Get multiple reply suggestions"""
        try:
            suggestions = []
            
            for i in range(count):
                suggestion = await self.generate_context_aware_reply(comment_context, channel_id)
                if suggestion and suggestion not in suggestions:
                    suggestions.append(suggestion)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting reply suggestions: {str(e)}")
            return []
    
    async def analyze_conversation_flow(
        self,
        comments: List[Dict[str, Any]],
        channel_id: str
    ) -> Dict[str, Any]:
        """Analyze conversation flow for better replies"""
        try:
            analysis = {
                "dominant_sentiment": "neutral",
                "main_topics": [],
                "conversation_tone": "neutral",
                "engagement_level": "medium",
                "trending_questions": [],
                "user_retention": []
            }
            
            if not comments:
                return analysis
            
            # Analyze sentiments
            sentiments = []
            topics = []
            
            for comment in comments:
                context = await self.analyze_comment_context(comment, channel_id)
                sentiments.append(context.sentiment)
                
                # Extract topics (simplified)
                words = context.comment_text.lower().split()
                topics.extend([word for word in words if len(word) > 4])
            
            # Determine dominant sentiment
            sentiment_counts = {s: sentiments.count(s) for s in set(sentiments)}
            analysis["dominant_sentiment"] = max(sentiment_counts, key=sentiment_counts.get)
            
            # Find main topics
            from collections import Counter
            topic_counts = Counter(topics)
            analysis["main_topics"] = [topic for topic, count in topic_counts.most_common(5)]
            
            # Calculate engagement level
            total_comments = len(comments)
            if total_comments > 50:
                analysis["engagement_level"] = "high"
            elif total_comments > 20:
                analysis["engagement_level"] = "medium"
            else:
                analysis["engagement_level"] = "low"
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing conversation flow: {str(e)}")
            return {"error": str(e)}
    
    def get_channel_contexts(self) -> Dict[str, Dict[str, Any]]:
        """Get all channel contexts"""
        return {
            channel_id: {
                "channel_name": context.channel_name,
                "niche": context.niche,
                "tone": context.tone,
                "language": context.language,
                "auto_reply_rate": context.auto_reply_rate,
                "subscriber_count": context.subscriber_count
            }
            for channel_id, context in self.channel_contexts.items()
        }
    
    def update_channel_context(self, channel_id: str, updates: Dict[str, Any]) -> bool:
        """Update channel context"""
        try:
            if channel_id in self.channel_contexts:
                context = self.channel_contexts[channel_id]
                
                for key, value in updates.items():
                    if hasattr(context, key):
                        setattr(context, key, value)
                
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error updating channel context: {str(e)}")
            return False