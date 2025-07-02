# Niche Intelligence & Competitor Research API Reference

## Overview

Complete API reference for the new enterprise features including niche intelligence, competitor research, trend detection, content gap analysis, and SEO optimization.

## Base URL
```
https://your-platform-domain.com/api/v1
```

## Authentication
All API requests require authentication. Include your API key in the request headers:
```http
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

---

## 🧠 Niche Intelligence API

### Analyze Niche
Perform comprehensive niche analysis with market research, competitor analysis, and growth prediction.

**Endpoint:** `POST /niche/analyze`

**Request Body:**
```json
{
  "niche_name": "AI Tutorials",
  "category": "technology",
  "target_audience": "developers",
  "analyze_competitors": true,
  "analyze_trends": true,
  "analyze_keywords": true,
  "deep_analysis": false
}
```

**Response:**
```json
{
  "id": "niche_12345",
  "niche_name": "AI Tutorials",
  "category": "technology",
  "growth_rate": 0.85,
  "competition_level": "medium",
  "monetization_potential": 0.75,
  "market_size_estimate": 2500000,
  "avg_views_per_video": 15000,
  "avg_engagement_rate": 0.045,
  "top_performing_formats": [
    {
      "format": "tutorial",
      "avg_engagement": 0.055,
      "video_count": 1250
    }
  ],
  "content_gaps": [
    {
      "gap_type": "topic",
      "topic_area": "AI ethics",
      "opportunity_score": 0.85,
      "difficulty_level": "medium"
    }
  ],
  "trending_topics": [
    {
      "topic": "GPT applications",
      "trending_score": 0.92,
      "viral_potential": 0.78
    }
  ],
  "recommended_strategy": {
    "focus_areas": ["beginner tutorials", "practical applications"],
    "content_frequency": "3 videos per week",
    "optimal_length": "10-15 minutes"
  },
  "confidence_score": 0.87,
  "last_analyzed": "2024-01-15T10:30:00Z"
}
```

### Get Niche Information
Retrieve existing niche analysis data.

**Endpoint:** `GET /niche/{niche_id}`

**Response:**
```json
{
  "id": "niche_12345",
  "niche_name": "AI Tutorials",
  "category": "technology",
  "growth_rate": 0.85,
  "competition_level": "medium",
  "last_analyzed": "2024-01-15T10:30:00Z",
  "analysis_components": {
    "market_analysis": { /* ... */ },
    "competition_analysis": { /* ... */ },
    "trend_analysis": { /* ... */ }
  }
}
```

### Update Niche Settings
Update niche analysis parameters and trigger re-analysis.

**Endpoint:** `PUT /niche/{niche_id}`

**Request Body:**
```json
{
  "target_audience": "beginners",
  "content_strategy": {
    "focus_on_trends": true,
    "content_frequency": "daily"
  },
  "analyze_competitors": true,
  "analyze_trends": true
}
```

### Get Niche Insights
Get strategic insights and recommendations for a niche.

**Endpoint:** `GET /niche/{niche_id}/insights`

**Response:**
```json
{
  "niche_id": "niche_12345",
  "market_opportunity": "high",
  "key_insights": [
    "Strong growth potential in beginner content",
    "Underserved audience in practical applications"
  ],
  "strategic_recommendations": [
    {
      "category": "content_strategy",
      "recommendation": "Focus on beginner-friendly tutorials",
      "priority": "high",
      "expected_impact": "high"
    }
  ],
  "action_plan": {
    "immediate_actions": [
      "Create beginner tutorial series",
      "Optimize existing content for SEO"
    ],
    "short_term_actions": [
      "Build community engagement",
      "Collaborate with other creators"
    ]
  }
}
```

---

## 🔍 Competitor Research API

### Analyze Competitors
Perform comprehensive competitor analysis including performance benchmarking and strategic positioning.

**Endpoint:** `POST /competitors/analyze`

**Request Body:**
```json
{
  "niche_id": "niche_12345",
  "competitor_channels": [
    "UCChannelID1",
    "UCChannelID2",
    "UCChannelID3"
  ],
  "analysis_depth": "standard",
  "include_video_analysis": true,
  "include_audience_analysis": true,
  "include_content_gaps": true,
  "video_sample_size": 25
}
```

**Response:**
```json
{
  "analysis_id": "comp_analysis_67890",
  "niche_id": "niche_12345",
  "competitors": [
    {
      "id": "comp_12345",
      "competitor_channel_id": "UCChannelID1",
      "competitor_name": "AI Academy",
      "subscriber_count": 125000,
      "video_count": 245,
      "avg_views_per_video": 8500,
      "avg_engagement_rate": 0.042,
      "upload_frequency": 2.5,
      "content_quality_score": 0.78,
      "brand_strength_score": 0.65,
      "strengths": [
        "Consistent upload schedule",
        "High production quality",
        "Strong community engagement"
      ],
      "weaknesses": [
        "Limited content variety",
        "Slow adaptation to trends"
      ],
      "opportunities": [
        "Expand to advanced topics",
        "Cross-platform content"
      ],
      "threats": [
        "New competitors entering",
        "Platform algorithm changes"
      ],
      "competitive_advantage": "Strong brand recognition and community",
      "last_analyzed": "2024-01-15T10:30:00Z"
    }
  ],
  "market_position": {
    "market_leaders": ["UCChannelID1"],
    "challengers": ["UCChannelID2"],
    "followers": ["UCChannelID3"],
    "competitive_intensity": "medium"
  },
  "opportunity_matrix": [
    {
      "opportunity": "Advanced AI tutorials",
      "difficulty": "medium",
      "potential_impact": "high",
      "market_gap": true
    }
  ],
  "strategic_recommendations": [
    {
      "recommendation": "Focus on advanced content gap",
      "priority": "high",
      "timeline": "1-2 months"
    }
  ]
}
```

### Get Competitor Data
Retrieve stored competitor analysis data.

**Endpoint:** `GET /competitors/{niche_id}`

**Query Parameters:**
- `include_profiles` (boolean) - Include detailed competitor profiles
- `include_performance` (boolean) - Include performance metrics
- `limit` (integer) - Limit number of competitors returned

**Response:**
```json
{
  "niche_id": "niche_12345",
  "competitors": [
    {
      "competitor_channel_id": "UCChannelID1",
      "competitor_name": "AI Academy",
      "subscriber_count": 125000,
      "performance_summary": {
        "avg_views": 8500,
        "engagement_rate": 0.042,
        "growth_rate": 0.15
      },
      "last_analyzed": "2024-01-15T10:30:00Z"
    }
  ],
  "competitive_landscape": {
    "total_competitors": 25,
    "market_concentration": 0.35,
    "avg_subscriber_count": 75000
  }
}
```

### Set Up Competitor Monitoring
Configure automated competitor monitoring with specified frequency.

**Endpoint:** `POST /competitors/monitor`

**Request Body:**
```json
{
  "niche_id": "niche_12345",
  "competitor_channels": [
    "UCChannelID1",
    "UCChannelID2"
  ],
  "monitoring_frequency": "daily",
  "track_metrics": [
    "subscriber_count",
    "video_count",
    "engagement_rate",
    "upload_frequency"
  ],
  "alert_thresholds": {
    "subscriber_growth": 0.1,
    "engagement_drop": -0.2
  }
}
```

**Response:**
```json
{
  "monitoring_id": "monitor_12345",
  "niche_id": "niche_12345",
  "competitors_monitored": 2,
  "monitoring_frequency": "daily",
  "next_update": "2024-01-16T10:30:00Z",
  "monitoring_tasks": [
    {
      "task_id": "task_67890",
      "task_type": "competitor_monitoring"
    }
  ]
}
```

### Get Content Gaps
Identify content gaps based on competitor analysis.

**Endpoint:** `GET /competitors/{niche_id}/gaps`

**Query Parameters:**
- `gap_types` (array) - Types of gaps to analyze
- `min_opportunity_score` (float) - Minimum opportunity score threshold

**Response:**
```json
{
  "niche_id": "niche_12345",
  "content_gaps": [
    {
      "gap_type": "topic",
      "topic_area": "AI ethics and bias",
      "opportunity_score": 0.85,
      "demand_level": "high",
      "supply_level": "low",
      "suggested_content_types": [
        "educational video",
        "case study analysis"
      ],
      "priority_level": 5
    }
  ],
  "implementation_roadmap": {
    "quick_wins": [
      {
        "gap": "Basic AI concepts",
        "effort": "low",
        "impact": "medium"
      }
    ],
    "strategic_opportunities": [
      {
        "gap": "Advanced neural networks",
        "effort": "high",
        "impact": "high"
      }
    ]
  }
}
```

---

## 📈 Trend Detection API

### Detect Trends
Analyze trending topics and emerging opportunities in a niche.

**Endpoint:** `POST /trends/detect`

**Request Body:**
```json
{
  "niche_id": "niche_12345",
  "keywords": ["artificial intelligence", "machine learning"],
  "geographic_scope": "global",
  "time_range": "7d",
  "trend_categories": ["technology", "education"],
  "min_trending_score": 0.6,
  "include_predictions": true
}
```

**Response:**
```json
{
  "detection_timestamp": "2024-01-15T10:30:00Z",
  "trends": [
    {
      "id": "trend_12345",
      "topic_name": "ChatGPT alternatives",
      "trending_score": 0.89,
      "search_volume": 45000,
      "viral_potential": 0.76,
      "trending_duration": "rising",
      "related_keywords": [
        "open source AI",
        "ChatGPT competitors",
        "AI alternatives"
      ],
      "content_opportunities": [
        {
          "angle": "comparison",
          "difficulty": "medium",
          "potential_views": 25000
        }
      ],
      "optimal_timing": {
        "urgency": "high",
        "best_posting_window": "next 48 hours"
      },
      "difficulty_level": "medium",
      "monetization_potential": 0.78,
      "predicted_longevity": "2-3 weeks"
    }
  ],
  "trend_categories": {
    "technology": 8,
    "education": 5,
    "business": 3
  },
  "content_calendar_suggestions": [
    {
      "week": 1,
      "trending_topics": ["ChatGPT alternatives"],
      "content_type": "comparison video"
    }
  ]
}
```

### Get Niche Trends
Retrieve trending topics specific to a niche.

**Endpoint:** `GET /trends/{niche_id}`

**Query Parameters:**
- `time_range` (string) - Time range for trends (1d, 7d, 30d)
- `min_score` (float) - Minimum trending score
- `limit` (integer) - Maximum number of trends

**Response:**
```json
{
  "niche_id": "niche_12345",
  "trends": [
    {
      "topic_name": "AI image generation",
      "trending_score": 0.92,
      "search_volume": 67000,
      "trend_direction": "rising"
    }
  ],
  "trend_insights": {
    "hot_topics": 5,
    "emerging_topics": 3,
    "declining_topics": 1
  }
}
```

### Get Content Opportunities
Get content opportunities based on trend analysis.

**Endpoint:** `GET /trends/opportunities`

**Query Parameters:**
- `niche_id` (string) - Niche ID filter
- `urgency_level` (string) - Urgency filter (immediate, short_term, planned)
- `content_types` (array) - Content type filters

**Response:**
```json
{
  "opportunities": [
    {
      "trend_id": "trend_12345",
      "opportunity_type": "content_creation",
      "suggested_title": "Why ChatGPT Alternatives Are Taking Over",
      "content_angle": "trending_analysis",
      "trending_score": 0.89,
      "urgency_level": "immediate",
      "estimated_views": 35000,
      "difficulty": "medium",
      "optimal_timing": "next 24 hours"
    }
  ],
  "timing_recommendations": {
    "immediate_opportunities": 3,
    "short_term_opportunities": 7,
    "planned_opportunities": 12
  }
}
```

### Predict Trends
Get AI-powered trend predictions and evolution forecasts.

**Endpoint:** `POST /trends/predict`

**Request Body:**
```json
{
  "niche_id": "niche_12345",
  "prediction_timeframe": "30d",
  "trend_factors": [
    "search_volume",
    "social_mentions",
    "competitor_activity"
  ]
}
```

**Response:**
```json
{
  "predictions": [
    {
      "topic": "AI regulation",
      "current_score": 0.65,
      "predicted_score_7d": 0.78,
      "predicted_score_30d": 0.85,
      "confidence": 0.82,
      "factors": [
        "increasing news coverage",
        "government announcements",
        "industry discussions"
      ]
    }
  ],
  "market_evolution": {
    "emerging_niches": ["AI safety", "ethical AI"],
    "declining_topics": ["basic ML tutorials"],
    "stable_areas": ["Python programming"]
  }
}
```

---

## 🔧 SEO Optimization API

### Analyze SEO Performance
Comprehensive SEO analysis for videos or channels.

**Endpoint:** `POST /seo/analyze`

**Request Body:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "channel_id": "UCChannelID1",
  "target_keywords": [
    "AI tutorial",
    "machine learning guide",
    "deep learning basics"
  ],
  "analyze_competitors": true,
  "include_optimization_suggestions": true,
  "deep_analysis": false
}
```

**Response:**
```json
{
  "analysis_id": "seo_analysis_12345",
  "video_id": "dQw4w9WgXcQ",
  "channel_id": "UCChannelID1",
  "overall_seo_score": 0.72,
  "title_optimization": {
    "current_score": 0.65,
    "optimization_suggestions": [
      "Include primary keyword in first 30 characters",
      "Add emotional trigger words"
    ],
    "impact_level": "high",
    "difficulty": "low",
    "estimated_improvement": 0.15
  },
  "description_optimization": {
    "current_score": 0.58,
    "optimization_suggestions": [
      "Add keyword-rich first paragraph",
      "Include relevant hashtags",
      "Add call-to-action"
    ],
    "impact_level": "medium",
    "difficulty": "low",
    "estimated_improvement": 0.12
  },
  "tags_optimization": {
    "current_score": 0.75,
    "optimization_suggestions": [
      "Add long-tail keyword variations",
      "Include trending related terms"
    ],
    "impact_level": "medium",
    "difficulty": "low",
    "estimated_improvement": 0.08
  },
  "competitor_comparison": {
    "ranking_vs_competitors": {
      "better_than": 3,
      "worse_than": 7,
      "position": "middle_tier"
    },
    "optimization_gaps": [
      "Competitors use more long-tail keywords",
      "Missing trending topic integration"
    ]
  },
  "keyword_rankings": [
    {
      "keyword": "AI tutorial",
      "current_position": 15,
      "search_volume": 8000,
      "difficulty": 0.65
    }
  ],
  "estimated_traffic_increase": {
    "percentage": "15-25%",
    "additional_views": "2000-3500 per month"
  }
}
```

### Get Optimization Suggestions
Get specific optimization recommendations for content.

**Endpoint:** `POST /seo/optimize`

**Request Body:**
```json
{
  "content_type": "video",
  "current_title": "Learn AI in 10 Minutes",
  "current_description": "Basic AI tutorial for beginners...",
  "current_tags": ["ai", "tutorial", "beginners"],
  "target_keywords": ["AI tutorial", "machine learning"],
  "optimization_level": "comprehensive"
}
```

**Response:**
```json
{
  "optimized_content": {
    "title_suggestions": [
      "Complete AI Tutorial for Beginners - Machine Learning in 10 Minutes",
      "AI Tutorial 2024: Learn Machine Learning Basics in 10 Minutes"
    ],
    "description_suggestions": [
      "🤖 Learn AI and machine learning fundamentals in just 10 minutes! This comprehensive AI tutorial covers...\n\n⏰ Timestamps:\n0:00 Introduction to AI\n2:30 Machine Learning Basics\n...\n\n🔗 Related Videos:\n[Links to related content]\n\n#AI #MachineLearning #Tutorial"
    ],
    "tag_suggestions": [
      "AI tutorial",
      "machine learning guide",
      "artificial intelligence basics",
      "AI for beginners",
      "deep learning introduction",
      "ML tutorial 2024",
      "AI explained simply",
      "machine learning course"
    ]
  },
  "optimization_impact": {
    "seo_score_improvement": 0.23,
    "estimated_ranking_boost": "5-8 positions",
    "traffic_increase_projection": "20-35%"
  },
  "implementation_priority": [
    {
      "element": "title",
      "priority": "high",
      "effort": "low",
      "impact": "high"
    },
    {
      "element": "tags",
      "priority": "medium",
      "effort": "low",
      "impact": "medium"
    }
  ]
}
```

### Track SEO Performance
Monitor SEO performance over time for videos.

**Endpoint:** `GET /seo/track/{video_id}`

**Query Parameters:**
- `date_range` (string) - Date range for tracking (7d, 30d, 90d)
- `keywords` (array) - Specific keywords to track

**Response:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "tracking_period": "30d",
  "seo_metrics": {
    "overall_score_trend": [
      {"date": "2024-01-01", "score": 0.65},
      {"date": "2024-01-15", "score": 0.72},
      {"date": "2024-01-30", "score": 0.78}
    ],
    "keyword_rankings": {
      "AI tutorial": {
        "current_position": 12,
        "previous_position": 18,
        "trend": "improving"
      }
    },
    "traffic_metrics": {
      "impressions": 15000,
      "clicks": 750,
      "ctr": 0.05,
      "avg_position": 15.2
    }
  },
  "performance_insights": [
    "SEO score improved by 20% over 30 days",
    "Keyword 'AI tutorial' moved up 6 positions",
    "CTR increased by 15% following optimization"
  ]
}
```

### Keyword Research
Research keywords for content optimization.

**Endpoint:** `POST /seo/keywords/research`

**Request Body:**
```json
{
  "niche_id": "niche_12345",
  "seed_keywords": [
    "AI tutorial",
    "machine learning",
    "deep learning"
  ],
  "include_long_tail": true,
  "competition_analysis": true,
  "youtube_specific": true,
  "difficulty_threshold": 0.7,
  "min_search_volume": 500
}
```

**Response:**
```json
{
  "keywords": [
    {
      "keyword": "AI tutorial for beginners",
      "search_volume": 12000,
      "competition_level": "medium",
      "difficulty_score": 0.55,
      "relevance_score": 0.92,
      "trend_direction": "rising",
      "youtube_specific_volume": 8000,
      "video_competition_count": 2500,
      "content_gaps": [
        "Beginner-friendly explanations",
        "Practical examples"
      ],
      "suggested_title_formats": [
        "AI Tutorial for Complete Beginners - {Year}",
        "Learn AI in {Time} - Beginner's Guide"
      ],
      "conversion_potential": 0.78
    }
  ],
  "keyword_clusters": [
    {
      "cluster_name": "Beginner AI Tutorials",
      "keywords": [
        "AI tutorial for beginners",
        "AI basics explained",
        "intro to artificial intelligence"
      ],
      "cluster_difficulty": 0.58
    }
  ],
  "content_strategy_suggestions": [
    {
      "strategy": "Target beginner-level keywords first",
      "reasoning": "Lower competition, higher conversion rates"
    }
  ]
}
```

---

## 📊 Content Gap Analysis API

### Analyze Content Gaps
Identify content opportunities and gaps in the market.

**Endpoint:** `POST /content-gaps/analyze`

**Request Body:**
```json
{
  "niche_id": "niche_12345",
  "competitor_channels": [
    "UCChannelID1",
    "UCChannelID2"
  ],
  "content_types": ["tutorial", "review", "news"],
  "analysis_depth": "comprehensive",
  "include_trending_gaps": true,
  "include_seasonal_gaps": true,
  "min_opportunity_score": 0.6
}
```

**Response:**
```json
{
  "analysis_id": "gap_analysis_12345",
  "niche_id": "niche_12345",
  "content_gaps": [
    {
      "id": "gap_67890",
      "gap_type": "topic",
      "topic_area": "AI ethics and bias detection",
      "opportunity_score": 0.88,
      "demand_level": "high",
      "supply_level": "low",
      "competition_gap": 0.75,
      "audience_need_score": 0.92,
      "suggested_content_types": [
        "educational deep-dive",
        "case study analysis",
        "interview format"
      ],
      "recommended_approach": {
        "content_angle": "practical ethics in AI development",
        "target_length": "15-20 minutes",
        "difficulty_level": "intermediate"
      },
      "success_probability": 0.78,
      "effort_required": "medium",
      "potential_impact": "high",
      "timeline_to_fill": "2-3 weeks",
      "action_items": [
        "Research current AI ethics frameworks",
        "Interview industry experts",
        "Create practical examples"
      ],
      "priority_level": 5
    }
  ],
  "opportunity_matrix": {
    "high_impact_low_effort": [
      "Basic AI terminology explained"
    ],
    "high_impact_high_effort": [
      "Complete AI ethics course"
    ],
    "quick_wins": [
      "AI news roundup format",
      "Tool comparison videos"
    ]
  },
  "implementation_roadmap": {
    "week_1": [
      "Create AI ethics introduction video"
    ],
    "week_2": [
      "Develop bias detection tutorial"
    ],
    "month_1": [
      "Launch AI ethics series"
    ]
  }
}
```

---

## 📋 Market Research API

### Conduct Market Research
Comprehensive market research for a niche.

**Endpoint:** `POST /market-research/conduct`

**Request Body:**
```json
{
  "niche_id": "niche_12345",
  "research_scope": "comprehensive",
  "geographic_focus": ["US", "EU", "Asia"],
  "demographic_segments": ["millennials", "gen_z"],
  "competitor_benchmark": true,
  "trend_analysis_period": "12m"
}
```

**Response:**
```json
{
  "research_id": "research_12345",
  "niche_id": "niche_12345",
  "market_size_data": {
    "total_addressable_market": 5000000,
    "serviceable_addressable_market": 1500000,
    "serviceable_obtainable_market": 150000,
    "growth_rate": 0.25,
    "market_maturity": "growth_stage"
  },
  "audience_demographics": {
    "primary_age_group": "25-34",
    "gender_distribution": {"male": 60, "female": 35, "other": 5},
    "education_level": "university_educated",
    "income_bracket": "middle_to_high",
    "geographic_distribution": {
      "US": 35,
      "EU": 30,
      "Asia": 25,
      "Other": 10
    }
  },
  "behavior_patterns": {
    "content_consumption_time": "evenings_and_weekends",
    "preferred_content_length": "10-15 minutes",
    "platform_usage": {
      "YouTube": 85,
      "TikTok": 45,
      "Instagram": 35
    },
    "engagement_preferences": [
      "educational_content",
      "practical_tutorials",
      "industry_news"
    ]
  },
  "monetization_insights": {
    "revenue_potential": "high",
    "primary_revenue_streams": [
      "course_sales",
      "consulting",
      "affiliate_marketing"
    ],
    "average_customer_value": 250,
    "conversion_rates": {
      "email_signup": 0.08,
      "course_purchase": 0.03,
      "consulting_inquiry": 0.01
    }
  },
  "growth_opportunities": [
    {
      "insight_type": "market_expansion",
      "title": "Emerging Asian Market",
      "description": "Significant growth potential in Southeast Asian markets",
      "impact_level": "high",
      "confidence_score": 0.82
    }
  ],
  "strategic_recommendations": [
    {
      "recommendation": "Focus on intermediate-level content",
      "priority": "high",
      "timeline": "immediate",
      "reasoning": "Gap in market for technical-but-accessible content"
    }
  ]
}
```

---

## 🔄 Automated Research Tasks API

### Create Research Task
Set up automated research and monitoring tasks.

**Endpoint:** `POST /research-tasks/create`

**Request Body:**
```json
{
  "task_type": "competitor_monitoring",
  "niche_id": "niche_12345",
  "channel_id": "UCYourChannelID",
  "task_config": {
    "competitor_channels": ["UCComp1", "UCComp2"],
    "metrics_to_track": [
      "subscriber_count",
      "upload_frequency",
      "engagement_rate"
    ],
    "alert_thresholds": {
      "subscriber_growth": 0.1,
      "new_video_frequency": 0.5
    }
  },
  "schedule_pattern": "daily",
  "priority_level": 4,
  "notifications": {
    "email": "your@email.com",
    "webhook": "https://your-site.com/webhook"
  }
}
```

**Response:**
```json
{
  "task_id": "task_12345",
  "task_type": "competitor_monitoring",
  "status": "active",
  "next_execution": "2024-01-16T10:30:00Z",
  "schedule_pattern": "daily",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Get Research Tasks
Retrieve automated research tasks.

**Endpoint:** `GET /research-tasks`

**Query Parameters:**
- `task_type` (string) - Filter by task type
- `status` (string) - Filter by status (active, paused, completed)
- `niche_id` (string) - Filter by niche

**Response:**
```json
{
  "tasks": [
    {
      "task_id": "task_12345",
      "task_type": "competitor_monitoring",
      "niche_id": "niche_12345",
      "status": "active",
      "last_execution": "2024-01-15T10:30:00Z",
      "next_execution": "2024-01-16T10:30:00Z",
      "execution_count": 25,
      "success_rate": 0.96
    }
  ],
  "total_tasks": 1,
  "active_tasks": 1,
  "paused_tasks": 0
}
```

---

## 📊 Analytics & Reporting API

### Get Analytics Dashboard
Comprehensive analytics dashboard data.

**Endpoint:** `GET /analytics/dashboard`

**Query Parameters:**
- `niche_id` (string) - Niche filter
- `time_range` (string) - Time range (7d, 30d, 90d)
- `include_predictions` (boolean) - Include future predictions

**Response:**
```json
{
  "dashboard_data": {
    "niche_overview": {
      "niche_name": "AI Tutorials",
      "overall_score": 0.78,
      "growth_trend": "positive",
      "market_position": "challenger"
    },
    "competitor_landscape": {
      "total_competitors": 25,
      "your_ranking": 8,
      "competitive_intensity": "medium",
      "market_share": 0.04
    },
    "trending_opportunities": [
      {
        "topic": "AI safety regulations",
        "opportunity_score": 0.85,
        "urgency": "high"
      }
    ],
    "content_performance": {
      "avg_views": 12500,
      "avg_engagement": 0.045,
      "top_performing_format": "tutorial",
      "growth_rate": 0.15
    },
    "seo_insights": {
      "avg_seo_score": 0.68,
      "keyword_rankings_improving": 8,
      "keyword_rankings_declining": 3,
      "traffic_trend": "increasing"
    },
    "kpi_summary": {
      "market_opportunity": 0.82,
      "competitive_position": 0.65,
      "content_quality": 0.78,
      "seo_performance": 0.68,
      "growth_potential": 0.85
    }
  },
  "action_recommendations": [
    {
      "category": "content",
      "recommendation": "Create content on AI safety regulations",
      "priority": "high",
      "estimated_impact": "high"
    }
  ],
  "alerts_and_notifications": [
    {
      "type": "opportunity",
      "message": "New trending topic detected: AI safety",
      "urgency": "high",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

## ⚠️ Error Responses

All API endpoints return standardized error responses:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "The request is invalid or malformed",
    "details": "Missing required field: niche_name",
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_12345"
  }
}
```

### Common Error Codes

- `INVALID_REQUEST` (400) - Malformed request
- `UNAUTHORIZED` (401) - Invalid API key
- `FORBIDDEN` (403) - Insufficient permissions
- `NOT_FOUND` (404) - Resource not found
- `RATE_LIMITED` (429) - Rate limit exceeded
- `INTERNAL_ERROR` (500) - Server error
- `SERVICE_UNAVAILABLE` (503) - Service temporarily unavailable

---

## 📊 Rate Limits

API endpoints have the following rate limits:

- **Analysis endpoints**: 100 requests/hour
- **Data retrieval endpoints**: 1000 requests/hour
- **Monitoring setup**: 50 requests/hour
- **Bulk operations**: 10 requests/hour

Rate limit headers are included in all responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248000
```

---

## 🔐 Authentication & Security

### API Key Management
- API keys can be generated in the platform dashboard
- Keys should be kept secure and rotated regularly
- Different permission levels available (read-only, full-access)

### Webhook Security
- Webhook payloads are signed using HMAC-SHA256
- Verify signatures to ensure authenticity
- Use HTTPS endpoints only

### Data Privacy
- All data is encrypted in transit and at rest
- GDPR and CCPA compliant
- Data retention policies configurable

---

*For additional support or questions about the API, please contact our technical support team.*