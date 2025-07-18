"""
TubeBuddy-Inspired Comment Management Module
Advanced comment moderation, analysis, and engagement tools
"""

import asyncio
import logging
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import uuid
import random

logger = logging.getLogger(__name__)

@dataclass
class Comment:
    """Comment structure"""
    comment_id: str
    video_id: str
    author_name: str
    author_channel_id: str
    text: str
    timestamp: datetime
    likes: int
    replies_count: int
    parent_comment_id: Optional[str] = None
    is_spam: Optional[bool] = None
    sentiment: Optional[str] = None  # positive, negative, neutral
    toxicity_score: Optional[float] = None
    moderation_status: str = 'approved'  # approved, pending, rejected, flagged

@dataclass
class CommentFilter:
    """Comment filtering criteria"""
    keywords: List[str] = None
    blocked_words: List[str] = None
    min_likes: int = 0
    max_likes: int = None
    sentiment: str = None  # positive, negative, neutral
    author_blacklist: List[str] = None
    author_whitelist: List[str] = None
    time_range: Tuple[datetime, datetime] = None
    has_replies: Optional[bool] = None

@dataclass
class ModerationRule:
    """Comment moderation rule"""
    rule_id: str
    name: str
    condition: str  # contains, starts_with, ends_with, regex, sentiment, toxicity
    value: str
    action: str  # auto_approve, auto_reject, flag_for_review, auto_reply
    auto_reply_text: str = ""
    is_active: bool = True

class CommentManager:
    """TubeBuddy-inspired comment management system"""
    
    def __init__(self):
        self.comments_database = {}  # video_id -> list of comments
        self.moderation_rules = {}
        self.auto_replies = {}
        self.spam_patterns = []
        self.engagement_stats = {}
        
        # Initialize default moderation rules
        self._initialize_default_rules()
        self._initialize_spam_patterns()
    
    def _initialize_default_rules(self):
        """Initialize default moderation rules"""
        default_rules = [
            ModerationRule(
                rule_id="spam_filter",
                name="Spam Filter",
                condition="contains",
                value="buy now|click here|free money|make money fast",
                action="auto_reject"
            ),
            ModerationRule(
                rule_id="profanity_filter",
                name="Profanity Filter",
                condition="toxicity",
                value="0.7",  # High toxicity threshold
                action="flag_for_review"
            ),
            ModerationRule(
                rule_id="positive_feedback",
                name="Positive Feedback Auto-Reply",
                condition="sentiment",
                value="positive",
                action="auto_reply",
                auto_reply_text="Thank you for the positive feedback! 😊"
            )
        ]
        
        for rule in default_rules:
            self.moderation_rules[rule.rule_id] = rule
    
    def _initialize_spam_patterns(self):
        """Initialize spam detection patterns"""
        self.spam_patterns = [
            r'\b(?:buy|check out|click here|free|money|cash|earn|make \$)\b',
            r'\b(?:visit|subscribe to|follow me)\s+(?:my|our)\s+(?:channel|website|link)\b',
            r'(?:https?://|www\.)\S+',  # URLs in comments
            r'\b(?:first|early|notification squad)\b',  # Generic first comments
            r'\b(?:sub4sub|sub 4 sub|follow4follow)\b'
        ]
    
    async def analyze_comments(self, video_id: str, limit: int = 100) -> Dict[str, Any]:
        """
        Analyze comments for a video
        
        Args:
            video_id: YouTube video ID
            limit: Maximum number of comments to analyze
            
        Returns:
            Comment analysis results
        """
        try:
            # Simulate fetching comments
            comments = await self._fetch_comments(video_id, limit)
            
            # Analyze comments
            analysis = {
                'video_id': video_id,
                'total_comments': len(comments),
                'analysis_timestamp': datetime.now().isoformat(),
                'sentiment_breakdown': await self._analyze_sentiment(comments),
                'engagement_metrics': await self._calculate_engagement_metrics(comments),
                'spam_detection': await self._detect_spam_comments(comments),
                'toxicity_analysis': await self._analyze_toxicity(comments),
                'top_commenters': await self._get_top_commenters(comments),
                'keyword_analysis': await self._analyze_keywords(comments),
                'moderation_suggestions': await self._generate_moderation_suggestions(comments)
            }
            
            # Store analysis
            self.engagement_stats[video_id] = analysis
            
            return analysis
            
        except Exception as e:
            logger.error(f"Comment analysis failed: {e}")
            return {'error': 'Comment analysis failed', 'details': str(e)}
    
    async def moderate_comments(self, video_id: str, 
                              auto_moderate: bool = True,
                              custom_rules: List[ModerationRule] = None) -> Dict[str, Any]:
        """
        Moderate comments using predefined rules
        
        Args:
            video_id: Video ID to moderate
            auto_moderate: Whether to apply actions automatically
            custom_rules: Additional custom rules to apply
            
        Returns:
            Moderation results
        """
        try:
            # Get comments for video
            comments = await self._fetch_comments(video_id)
            
            # Combine default and custom rules
            rules_to_apply = list(self.moderation_rules.values())
            if custom_rules:
                rules_to_apply.extend(custom_rules)
            
            # Apply moderation rules
            moderation_results = {
                'video_id': video_id,
                'total_comments': len(comments),
                'moderated_comments': 0,
                'auto_approved': 0,
                'auto_rejected': 0,
                'flagged_for_review': 0,
                'auto_replied': 0,
                'actions': []
            }
            
            for comment in comments:
                actions = await self._apply_moderation_rules(comment, rules_to_apply, auto_moderate)
                
                for action in actions:
                    moderation_results['actions'].append({
                        'comment_id': comment.comment_id,
                        'author': comment.author_name,
                        'action': action['action'],
                        'rule': action['rule'],
                        'reason': action['reason']
                    })
                    
                    # Update counters
                    moderation_results['moderated_comments'] += 1
                    if action['action'] == 'auto_approve':
                        moderation_results['auto_approved'] += 1
                    elif action['action'] == 'auto_reject':
                        moderation_results['auto_rejected'] += 1
                    elif action['action'] == 'flag_for_review':
                        moderation_results['flagged_for_review'] += 1
                    elif action['action'] == 'auto_reply':
                        moderation_results['auto_replied'] += 1
            
            return moderation_results
            
        except Exception as e:
            logger.error(f"Comment moderation failed: {e}")
            return {'error': 'Comment moderation failed', 'details': str(e)}
    
    async def bulk_reply_comments(self, video_id: str, 
                                reply_template: str,
                                filter_criteria: CommentFilter = None) -> Dict[str, Any]:
        """
        Send bulk replies to comments
        
        Args:
            video_id: Video ID
            reply_template: Template for replies (can include placeholders)
            filter_criteria: Criteria to filter which comments to reply to
            
        Returns:
            Bulk reply results
        """
        try:
            # Get comments
            comments = await self._fetch_comments(video_id)
            
            # Apply filters
            if filter_criteria:
                comments = await self._filter_comments(comments, filter_criteria)
            
            # Send replies
            reply_results = {
                'video_id': video_id,
                'template_used': reply_template,
                'total_eligible_comments': len(comments),
                'successful_replies': 0,
                'failed_replies': 0,
                'replies': []
            }
            
            for comment in comments:
                try:
                    # Personalize reply template
                    personalized_reply = await self._personalize_reply(reply_template, comment)
                    
                    # Send reply (simulated)
                    success = await self._send_reply(comment.comment_id, personalized_reply)
                    
                    if success:
                        reply_results['successful_replies'] += 1
                        reply_results['replies'].append({
                            'comment_id': comment.comment_id,
                            'author': comment.author_name,
                            'reply_text': personalized_reply,
                            'status': 'sent'
                        })
                    else:
                        reply_results['failed_replies'] += 1
                        reply_results['replies'].append({
                            'comment_id': comment.comment_id,
                            'author': comment.author_name,
                            'status': 'failed'
                        })
                        
                except Exception as e:
                    reply_results['failed_replies'] += 1
                    logger.error(f"Failed to reply to comment {comment.comment_id}: {e}")
            
            return reply_results
            
        except Exception as e:
            logger.error(f"Bulk reply failed: {e}")
            return {'error': 'Bulk reply failed', 'details': str(e)}
    
    async def _fetch_comments(self, video_id: str, limit: int = 100) -> List[Comment]:
        """Simulate fetching comments from YouTube API"""
        try:
            # Generate simulated comments
            comments = []
            
            for i in range(min(limit, random.randint(20, 150))):
                comment = Comment(
                    comment_id=f"comment_{video_id}_{i}",
                    video_id=video_id,
                    author_name=f"User{random.randint(1, 1000)}",
                    author_channel_id=f"channel_{random.randint(1, 1000)}",
                    text=self._generate_sample_comment(),
                    timestamp=datetime.now() - timedelta(minutes=random.randint(1, 10080)),  # Last week
                    likes=random.randint(0, 50),
                    replies_count=random.randint(0, 5)
                )
                
                # Add sentiment and toxicity analysis
                comment.sentiment = await self._analyze_comment_sentiment(comment.text)
                comment.toxicity_score = await self._analyze_comment_toxicity(comment.text)
                comment.is_spam = await self._is_spam_comment(comment.text)
                
                comments.append(comment)
            
            # Store in database simulation
            self.comments_database[video_id] = comments
            
            return comments
            
        except Exception as e:
            logger.error(f"Failed to fetch comments: {e}")
            return []
    
    def _generate_sample_comment(self) -> str:
        """Generate realistic sample comments"""
        comment_templates = [
            "Great video! Really helpful content.",
            "Thanks for sharing this information!",
            "Could you make a tutorial about {topic}?",
            "First! Love your content ❤️",
            "This is exactly what I was looking for.",
            "Amazing explanation, very clear and easy to understand.",
            "Can you do a part 2 of this?",
            "Your videos always help me so much!",
            "Best tutorial I've seen on this topic.",
            "Subscribe to my channel for similar content!",  # Potential spam
            "Click here for free stuff: link.com",  # Spam
            "This video is terrible and waste of time.",  # Negative
            "You don't know what you're talking about.",  # Negative/toxic
            "Keep up the good work! 👍",
            "When will you upload the next video?",
            "This helped me pass my exam, thank you!",
            "Could you speak a bit slower next time?",
            "Love the editing in this video!",
            "Your channel has grown so much!",
            "This is my favorite YouTuber! ❤️"
        ]
        
        return random.choice(comment_templates)
    
    async def _analyze_sentiment(self, comments: List[Comment]) -> Dict[str, Any]:
        """Analyze overall sentiment of comments"""
        try:
            if not comments:
                return {'positive': 0, 'negative': 0, 'neutral': 0}
            
            sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
            
            for comment in comments:
                if comment.sentiment:
                    sentiment_counts[comment.sentiment] += 1
            
            total = len(comments)
            
            if total == 0:
                return {
                    'positive': 0,
                    'negative': 0,
                    'neutral': 0,
                    'total_analyzed': 0,
                    'dominant_sentiment': 'neutral'
                }
            
            return {
                'positive': round(sentiment_counts['positive'] / total * 100, 1),
                'negative': round(sentiment_counts['negative'] / total * 100, 1),
                'neutral': round(sentiment_counts['neutral'] / total * 100, 1),
                'total_analyzed': total,
                'dominant_sentiment': max(sentiment_counts, key=sentiment_counts.get)
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {'positive': 0, 'negative': 0, 'neutral': 0}
    
    async def _calculate_engagement_metrics(self, comments: List[Comment]) -> Dict[str, Any]:
        """Calculate engagement metrics"""
        try:
            if not comments:
                return {}
            
            total_likes = sum(comment.likes for comment in comments)
            total_replies = sum(comment.replies_count for comment in comments)
            avg_likes = total_likes / len(comments) if comments else 0
            avg_replies = total_replies / len(comments) if comments else 0
            
            # Calculate time-based metrics
            recent_comments = [c for c in comments if c.timestamp > datetime.now() - timedelta(hours=24)]
            
            return {
                'total_comments': len(comments),
                'total_likes': total_likes,
                'total_replies': total_replies,
                'average_likes_per_comment': round(avg_likes, 2),
                'average_replies_per_comment': round(avg_replies, 2),
                'comments_last_24h': len(recent_comments),
                'engagement_rate': round((total_likes + total_replies) / len(comments), 2),
                'most_liked_comment': max(comments, key=lambda x: x.likes).text if comments else None
            }
            
        except Exception as e:
            logger.error(f"Engagement metrics calculation failed: {e}")
            return {}
    
    async def _detect_spam_comments(self, comments: List[Comment]) -> Dict[str, Any]:
        """Detect spam comments"""
        try:
            spam_comments = [c for c in comments if c.is_spam]
            
            spam_patterns_found = {}
            for comment in spam_comments:
                for i, pattern in enumerate(self.spam_patterns):
                    if re.search(pattern, comment.text, re.IGNORECASE):
                        pattern_name = f"pattern_{i+1}"
                        spam_patterns_found[pattern_name] = spam_patterns_found.get(pattern_name, 0) + 1
            
            return {
                'total_spam_detected': len(spam_comments),
                'spam_percentage': round(len(spam_comments) / len(comments) * 100, 1) if comments else 0,
                'spam_patterns_found': spam_patterns_found,
                'spam_comments': [
                    {
                        'comment_id': c.comment_id,
                        'author': c.author_name,
                        'text': c.text[:100] + "..." if len(c.text) > 100 else c.text
                    }
                    for c in spam_comments[:5]  # Show first 5 spam comments
                ]
            }
            
        except Exception as e:
            logger.error(f"Spam detection failed: {e}")
            return {'total_spam_detected': 0, 'spam_percentage': 0}
    
    async def _analyze_toxicity(self, comments: List[Comment]) -> Dict[str, Any]:
        """Analyze comment toxicity"""
        try:
            if not comments:
                return {}
            
            toxicity_levels = {'low': 0, 'medium': 0, 'high': 0}
            
            for comment in comments:
                if comment.toxicity_score is not None:
                    if comment.toxicity_score < 0.3:
                        toxicity_levels['low'] += 1
                    elif comment.toxicity_score < 0.7:
                        toxicity_levels['medium'] += 1
                    else:
                        toxicity_levels['high'] += 1
            
            total = sum(toxicity_levels.values())
            
            return {
                'toxicity_distribution': {
                    'low': round(toxicity_levels['low'] / total * 100, 1) if total > 0 else 0,
                    'medium': round(toxicity_levels['medium'] / total * 100, 1) if total > 0 else 0,
                    'high': round(toxicity_levels['high'] / total * 100, 1) if total > 0 else 0
                },
                'high_toxicity_comments': len([c for c in comments if c.toxicity_score and c.toxicity_score > 0.7]),
                'average_toxicity_score': round(sum(c.toxicity_score for c in comments if c.toxicity_score) / len([c for c in comments if c.toxicity_score]), 3) if comments and len([c for c in comments if c.toxicity_score]) > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Toxicity analysis failed: {e}")
            return {}
    
    async def _get_top_commenters(self, comments: List[Comment]) -> List[Dict[str, Any]]:
        """Get top commenters by activity"""
        try:
            commenter_stats = {}
            
            for comment in comments:
                author = comment.author_name
                if author not in commenter_stats:
                    commenter_stats[author] = {
                        'comment_count': 0,
                        'total_likes': 0,
                        'avg_likes': 0,
                        'latest_comment': comment.timestamp
                    }
                
                commenter_stats[author]['comment_count'] += 1
                commenter_stats[author]['total_likes'] += comment.likes
                commenter_stats[author]['latest_comment'] = max(
                    commenter_stats[author]['latest_comment'],
                    comment.timestamp
                )
            
            # Calculate average likes
            for stats in commenter_stats.values():
                stats['avg_likes'] = round(stats['total_likes'] / stats['comment_count'], 1)
            
            # Sort by comment count
            top_commenters = sorted(
                commenter_stats.items(),
                key=lambda x: x[1]['comment_count'],
                reverse=True
            )[:10]
            
            return [
                {
                    'author_name': author,
                    'comment_count': stats['comment_count'],
                    'total_likes': stats['total_likes'],
                    'avg_likes_per_comment': stats['avg_likes'],
                    'latest_comment': stats['latest_comment'].isoformat()
                }
                for author, stats in top_commenters
            ]
            
        except Exception as e:
            logger.error(f"Top commenters analysis failed: {e}")
            return []
    
    async def _analyze_keywords(self, comments: List[Comment]) -> Dict[str, Any]:
        """Analyze keywords and topics in comments"""
        try:
            # Extract keywords from comments
            all_text = " ".join([c.text.lower() for c in comments])
            words = re.findall(r'\b\w{3,}\b', all_text)  # Words with 3+ characters
            
            # Count word frequency
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Remove common words
            stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use', 'this', 'that', 'with', 'have', 'from', 'they', 'know', 'want', 'been', 'good', 'much', 'some', 'time', 'very', 'when', 'come', 'here', 'just', 'like', 'long', 'make', 'many', 'over', 'such', 'take', 'than', 'them', 'well', 'were'}
            
            filtered_words = {k: v for k, v in word_freq.items() if k not in stop_words and v > 1}
            
            # Get top keywords
            top_keywords = sorted(filtered_words.items(), key=lambda x: x[1], reverse=True)[:20]
            
            return {
                'total_unique_words': len(word_freq),
                'top_keywords': [
                    {'keyword': word, 'frequency': count}
                    for word, count in top_keywords
                ],
                'keyword_insights': await self._generate_keyword_insights(top_keywords)
            }
            
        except Exception as e:
            logger.error(f"Keyword analysis failed: {e}")
            return {}
    
    async def _generate_keyword_insights(self, top_keywords: List[Tuple[str, int]]) -> List[str]:
        """Generate insights from keyword analysis"""
        insights = []
        
        try:
            if not top_keywords:
                return ["No significant keywords found"]
            
            most_frequent = top_keywords[0]
            insights.append(f"Most discussed topic: '{most_frequent[0]}' mentioned {most_frequent[1]} times")
            
            # Look for question words
            question_words = [kw for kw, count in top_keywords if kw in ['how', 'what', 'when', 'where', 'why', 'which']]
            if question_words:
                insights.append(f"Viewers are asking questions - consider creating FAQ content")
            
            # Look for positive/negative indicators
            positive_words = [kw for kw, count in top_keywords if kw in ['great', 'awesome', 'good', 'amazing', 'perfect', 'excellent']]
            if positive_words:
                insights.append("High positive sentiment - viewers are enjoying the content")
            
            negative_words = [kw for kw, count in top_keywords if kw in ['bad', 'terrible', 'worst', 'hate', 'stupid', 'boring']]
            if negative_words:
                insights.append("Some negative feedback detected - review content quality")
            
            return insights
            
        except Exception as e:
            logger.error(f"Keyword insights generation failed: {e}")
            return ["Unable to generate insights"]
    
    async def _generate_moderation_suggestions(self, comments: List[Comment]) -> List[str]:
        """Generate moderation suggestions"""
        suggestions = []
        
        try:
            spam_count = len([c for c in comments if c.is_spam])
            toxic_count = len([c for c in comments if c.toxicity_score and c.toxicity_score > 0.7])
            
            if spam_count > len(comments) * 0.1:  # More than 10% spam
                suggestions.append("🚨 High spam activity detected - consider stricter moderation rules")
            
            if toxic_count > len(comments) * 0.05:  # More than 5% toxic
                suggestions.append("⚠️ Elevated toxicity levels - enable automatic toxicity filtering")
            
            # Engagement suggestions
            positive_comments = len([c for c in comments if c.sentiment == 'positive'])
            if positive_comments > len(comments) * 0.7:  # More than 70% positive
                suggestions.append("😊 High positive engagement - consider pinning top positive comments")
            
            # Activity suggestions
            recent_activity = len([c for c in comments if c.timestamp > datetime.now() - timedelta(hours=2)])
            if recent_activity > 10:
                suggestions.append("🔥 High recent activity - monitor for trending conversations")
            
            return suggestions if suggestions else ["✅ Comment section looks healthy - no immediate action needed"]
            
        except Exception as e:
            logger.error(f"Moderation suggestions failed: {e}")
            return ["Unable to generate suggestions"]
    
    async def _apply_moderation_rules(self, comment: Comment, 
                                    rules: List[ModerationRule], 
                                    auto_moderate: bool) -> List[Dict[str, Any]]:
        """Apply moderation rules to a comment"""
        actions = []
        
        try:
            for rule in rules:
                if not rule.is_active:
                    continue
                
                should_trigger = False
                
                # Check rule conditions
                if rule.condition == 'contains':
                    should_trigger = any(keyword.lower() in comment.text.lower() 
                                       for keyword in rule.value.split('|'))
                elif rule.condition == 'sentiment':
                    should_trigger = comment.sentiment == rule.value
                elif rule.condition == 'toxicity':
                    threshold = float(rule.value)
                    should_trigger = comment.toxicity_score and comment.toxicity_score >= threshold
                elif rule.condition == 'regex':
                    should_trigger = bool(re.search(rule.value, comment.text, re.IGNORECASE))
                
                if should_trigger:
                    action = {
                        'action': rule.action,
                        'rule': rule.name,
                        'reason': f"Triggered by {rule.condition}: {rule.value}"
                    }
                    
                    if auto_moderate:
                        # Apply the action
                        if rule.action == 'auto_reply' and rule.auto_reply_text:
                            action['reply_text'] = rule.auto_reply_text
                        
                        # Update comment status
                        if rule.action == 'auto_reject':
                            comment.moderation_status = 'rejected'
                        elif rule.action == 'flag_for_review':
                            comment.moderation_status = 'flagged'
                        elif rule.action == 'auto_approve':
                            comment.moderation_status = 'approved'
                    
                    actions.append(action)
            
            return actions
            
        except Exception as e:
            logger.error(f"Rule application failed: {e}")
            return []
    
    async def _filter_comments(self, comments: List[Comment], 
                             filter_criteria: CommentFilter) -> List[Comment]:
        """Filter comments based on criteria"""
        try:
            filtered = comments
            
            if filter_criteria.keywords:
                filtered = [c for c in filtered if any(kw.lower() in c.text.lower() for kw in filter_criteria.keywords)]
            
            if filter_criteria.blocked_words:
                filtered = [c for c in filtered if not any(bw.lower() in c.text.lower() for bw in filter_criteria.blocked_words)]
            
            if filter_criteria.min_likes:
                filtered = [c for c in filtered if c.likes >= filter_criteria.min_likes]
            
            if filter_criteria.max_likes:
                filtered = [c for c in filtered if c.likes <= filter_criteria.max_likes]
            
            if filter_criteria.sentiment:
                filtered = [c for c in filtered if c.sentiment == filter_criteria.sentiment]
            
            if filter_criteria.author_blacklist:
                filtered = [c for c in filtered if c.author_name not in filter_criteria.author_blacklist]
            
            if filter_criteria.author_whitelist:
                filtered = [c for c in filtered if c.author_name in filter_criteria.author_whitelist]
            
            if filter_criteria.time_range:
                start_time, end_time = filter_criteria.time_range
                filtered = [c for c in filtered if start_time <= c.timestamp <= end_time]
            
            if filter_criteria.has_replies is not None:
                if filter_criteria.has_replies:
                    filtered = [c for c in filtered if c.replies_count > 0]
                else:
                    filtered = [c for c in filtered if c.replies_count == 0]
            
            return filtered
            
        except Exception as e:
            logger.error(f"Comment filtering failed: {e}")
            return comments
    
    async def _personalize_reply(self, template: str, comment: Comment) -> str:
        """Personalize reply template with comment data"""
        try:
            reply = template
            
            # Replace placeholders
            reply = reply.replace('{author}', comment.author_name)
            reply = reply.replace('{likes}', str(comment.likes))
            
            # Add timestamp if needed
            if '{time}' in reply:
                reply = reply.replace('{time}', comment.timestamp.strftime('%Y-%m-%d'))
            
            return reply
            
        except Exception as e:
            logger.error(f"Reply personalization failed: {e}")
            return template
    
    async def _send_reply(self, comment_id: str, reply_text: str) -> bool:
        """Simulate sending a reply to a comment"""
        try:
            # Simulate API delay
            await asyncio.sleep(0.1)
            
            # Simulate 95% success rate
            success = random.random() < 0.95
            
            if success:
                logger.info(f"Sent reply to comment {comment_id}: {reply_text}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send reply: {e}")
            return False
    
    async def _analyze_comment_sentiment(self, text: str) -> str:
        """Analyze sentiment of individual comment"""
        try:
            # Simple sentiment analysis based on keywords
            positive_words = ['great', 'awesome', 'amazing', 'love', 'excellent', 'fantastic', 'wonderful', 'perfect', 'good', 'best', 'helpful', 'thanks', 'thank you']
            negative_words = ['terrible', 'awful', 'hate', 'worst', 'bad', 'stupid', 'boring', 'waste', 'sucks', 'horrible']
            
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                return 'positive'
            elif negative_count > positive_count:
                return 'negative'
            else:
                return 'neutral'
                
        except Exception:
            return 'neutral'
    
    async def _analyze_comment_toxicity(self, text: str) -> float:
        """Analyze toxicity score of individual comment"""
        try:
            # Simple toxicity scoring based on problematic patterns
            toxic_patterns = [
                r'\b(?:stupid|idiot|moron|dumb|retard)\b',
                r'\b(?:hate|kill|die|death)\b',
                r'[A-Z]{3,}',  # ALL CAPS (mild indicator)
                r'!{3,}',  # Multiple exclamation marks
            ]
            
            score = 0.0
            text_lower = text.lower()
            
            for pattern in toxic_patterns:
                matches = len(re.findall(pattern, text_lower))
                score += matches * 0.2
            
            # Normalize to 0-1 range
            return min(1.0, score)
            
        except Exception:
            return 0.0
    
    async def _is_spam_comment(self, text: str) -> bool:
        """Check if comment is spam"""
        try:
            for pattern in self.spam_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return True
            return False
            
        except Exception:
            return False

# Global instance
comment_manager = CommentManager()