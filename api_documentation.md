# YouTube Automation Platform - Complete API Documentation

## 🚀 API Overview

**Base URL**: `https://your-domain.com/api`  
**Authentication**: JWT Bearer Token  
**Content-Type**: `application/json` (unless specified otherwise)  
**API Version**: v2.0.0

---

## 🔐 Authentication Endpoints

### Register User
```http
POST /api/auth/register
```

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response**:
```json
{
  "success": true,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "user_id": "12345",
    "email": "user@example.com",
    "full_name": "John Doe",
    "created_at": "2025-06-30T19:00:00Z"
  }
}
```

### Login User
```http
POST /api/auth/login
```

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response**:
```json
{
  "success": true,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "user_id": "12345",
    "email": "user@example.com",
    "full_name": "John Doe"
  }
}
```

---

## 🧙‍♂️ AI Wizard Endpoints

### Analyze Niche
```http
POST /api/wizard/analyze-niche
Authorization: Bearer {token}
```

**Request Body**:
```json
{
  "niche": "tech reviews",
  "target_audience": "tech enthusiasts",
  "content_style": "educational"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "analysis": {
      "market_size": "Large",
      "competition_level": "High",
      "growth_potential": "Excellent",
      "recommended_keywords": ["smartphone review", "tech comparison", "gadget testing"],
      "content_opportunities": [
        "Unboxing videos",
        "Comparison reviews",
        "Tech tutorials"
      ]
    },
    "recommendations": {
      "posting_frequency": "2-3 times per week",
      "video_length": "8-12 minutes",
      "optimal_upload_times": ["18:00-20:00 UTC"]
    }
  }
}
```

### SEO Optimization
```http
POST /api/wizard/seo-optimization
Authorization: Bearer {token}
```

**Request Body**:
```json
{
  "title": "Best Smartphones 2025",
  "description": "Comprehensive review of top smartphones"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "optimized_title": "Best Smartphones 2025: Complete Buyer's Guide & Reviews",
    "optimized_description": "Discover the top smartphones of 2025! Our comprehensive review covers features, prices, and performance. Find your perfect phone today!",
    "suggested_tags": ["smartphones 2025", "phone review", "tech guide"],
    "seo_score": 85,
    "improvements": [
      "Include year in title for freshness",
      "Add call-to-action in description",
      "Use trending keywords"
    ]
  }
}
```

### Generate Branding
```http
POST /api/wizard/branding
Authorization: Bearer {token}
```

**Request Body**:
```json
{
  "channel_name": "TechReview Pro",
  "niche": "technology",
  "style_preference": "modern"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "logo_suggestions": [
      {
        "style": "minimalist",
        "colors": ["#1a1a1a", "#ff6b35"],
        "description": "Clean geometric design with tech accent color"
      }
    ],
    "color_palette": {
      "primary": "#ff6b35",
      "secondary": "#1a1a1a",
      "accent": "#00d4ff"
    },
    "typography": {
      "header_font": "Inter Bold",
      "body_font": "Inter Regular"
    },
    "banner_concepts": [
      "Tech circuit pattern background",
      "Gradient mesh with device silhouettes"
    ]
  }
}
```

### Complete Channel Setup
```http
POST /api/wizard/complete-setup
Authorization: Bearer {token}
```

**Request Body**:
```json
{
  "channel_name": "TechReview Pro",
  "niche": "technology",
  "target_audience": "tech enthusiasts",
  "content_style": "educational",
  "branding_preferences": {
    "color_scheme": "modern",
    "style": "professional"
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "channel_id": "ch_67890",
    "setup_complete": true,
    "recommendations": {
      "content_calendar": "Generated 30-day content plan",
      "seo_setup": "Optimized channel metadata",
      "branding": "Logo and banner assets created"
    },
    "next_steps": [
      "Upload channel banner",
      "Create first video",
      "Set up social media connections"
    ]
  }
}
```

---

## 📱 Social Media Platform Endpoints

### Get Available Platforms
```http
GET /api/social/platforms/available
```

**Response**:
```json
{
  "success": true,
  "data": {
    "platforms": [
      {
        "id": "facebook",
        "name": "Facebook",
        "description": "Share videos to Facebook pages and profiles",
        "oauth_url": "/api/social/oauth/facebook",
        "video_specs": {
          "max_size_mb": 4000,
          "max_duration_seconds": 240,
          "formats": ["mp4", "mov"],
          "aspect_ratios": ["16:9", "1:1", "4:5"]
        }
      },
      {
        "id": "twitter",
        "name": "Twitter/X",
        "description": "Post videos to Twitter timeline",
        "oauth_url": "/api/social/oauth/twitter",
        "video_specs": {
          "max_size_mb": 512,
          "max_duration_seconds": 140,
          "formats": ["mp4"],
          "aspect_ratios": ["16:9", "1:1"]
        }
      }
    ]
  }
}
```

### Get Connected Platforms
```http
GET /api/social/platforms/connected
Authorization: Bearer {token}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "platforms": [
      {
        "platform": "facebook",
        "connected": true,
        "configuration": {
          "page_name": "My Tech Channel",
          "page_id": "123456789"
        },
        "oauth_status": "connected"
      },
      {
        "platform": "twitter",
        "connected": false,
        "oauth_status": "disconnected"
      }
    ]
  }
}
```

### OAuth Callback Endpoints
```http
GET /api/social/oauth/{platform}/callback?code={auth_code}
```

Supported platforms: `facebook`, `twitter`, `instagram`, `tiktok`, `linkedin`

**Response**:
```json
{
  "success": true,
  "message": "Platform connected successfully",
  "platform": "facebook",
  "account_info": {
    "name": "Tech Channel Page",
    "id": "123456789"
  }
}
```

---

## 🎬 Publishing Endpoints

### Real-time Publishing
```http
POST /api/social/publish/realtime
Authorization: Bearer {token}
Content-Type: multipart/form-data
```

**Request Body (Form Data)**:
```
video: [FILE] (mp4, mov, avi)
title: "Amazing Tech Review"
description: "Check out this amazing new gadget!"
platforms: ["facebook", "twitter", "instagram"]
tags: ["tech", "review", "gadgets"]
```

**Response**:
```json
{
  "success": true,
  "job_id": "pub_12345",
  "message": "Publishing started successfully",
  "websocket_url": "/ws/user123"
}
```

### Get Publishing Job Status
```http
GET /api/social/publishing/status/{job_id}
Authorization: Bearer {token}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "pub_12345",
    "status": "publishing",
    "progress": 75,
    "platform_results": {
      "facebook": {
        "success": true,
        "platform_id": "fb_67890",
        "url": "https://facebook.com/posts/67890"
      },
      "twitter": {
        "success": false,
        "error": "Video too large for Twitter"
      }
    },
    "created_at": "2025-06-30T19:00:00Z",
    "completed_at": null
  }
}
```

### Retry Failed Publishing Job
```http
POST /api/social/publishing/retry/{job_id}
Authorization: Bearer {token}
```

**Response**:
```json
{
  "success": true,
  "message": "Publishing job retry started"
}
```

### Get User Publishing Jobs
```http
GET /api/social/publishing/jobs
Authorization: Bearer {token}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "jobs": [
      {
        "id": "pub_12345",
        "title": "Amazing Tech Review",
        "platforms": ["facebook", "twitter"],
        "status": "completed",
        "platform_results": {
          "facebook": {"success": true},
          "twitter": {"success": true}
        },
        "created_at": "2025-06-30T19:00:00Z",
        "completed_at": "2025-06-30T19:05:00Z",
        "progress": 100
      }
    ]
  }
}
```

---

## 📊 Analytics Endpoints

### Get Platform Analytics
```http
GET /api/social/analytics
Authorization: Bearer {token}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "total_posts": 45,
    "successful_posts": 42,
    "failed_posts": 3,
    "platforms_connected": 4,
    "recent_activity": [
      {
        "date": "2025-06-30",
        "posts": 3,
        "platforms": ["facebook", "twitter"],
        "success_rate": 100
      }
    ],
    "platform_breakdown": {
      "facebook": {
        "posts": 20,
        "success_rate": 95,
        "avg_engagement": 150
      },
      "twitter": {
        "posts": 18,
        "success_rate": 100,
        "avg_engagement": 75
      }
    }
  }
}
```

---

## 📈 User Progress Endpoints

### Get User Progress
```http
GET /api/user/progress/{user_id}
Authorization: Bearer {token}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "progress": [
      {
        "id": "channel-setup",
        "title": "Complete Channel Setup",
        "status": "completed",
        "progress": 100,
        "completed_at": "2025-06-30T18:00:00Z"
      },
      {
        "id": "first-video",
        "title": "Create Your First Video",
        "status": "in_progress",
        "progress": 60
      }
    ]
  }
}
```

### Save User Progress
```http
POST /api/user/progress/{user_id}
Authorization: Bearer {token}
```

**Request Body**:
```json
{
  "progress": [
    {
      "id": "channel-setup",
      "status": "completed",
      "progress": 100
    }
  ]
}
```

**Response**:
```json
{
  "success": true,
  "message": "Progress saved successfully"
}
```

---

## 🔌 WebSocket API

### Connection
```javascript
const ws = new WebSocket('wss://your-domain.com/ws/{user_id}');
```

### Message Types

#### Connection Confirmation
```json
{
  "type": "connection",
  "message": "Connected successfully"
}
```

#### Publishing Updates
```json
{
  "type": "publishing_update",
  "data": {
    "job_id": "pub_12345",
    "status": "publishing",
    "platform": "facebook",
    "progress": 50,
    "message": "Publishing to Facebook...",
    "timestamp": "2025-06-30T19:02:30Z"
  }
}
```

#### Ping/Pong
```javascript
// Send ping to keep connection alive
ws.send('ping');

// Receive pong response
{
  "type": "pong"
}
```

---

## 🏥 System Health Endpoints

### Basic Health Check
```http
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "services": {
    "database": true,
    "social_media_manager": true,
    "realtime_publisher": true,
    "video_processor": true
  },
  "oauth_status": {
    "facebook": true,
    "twitter": true,
    "instagram": true,
    "tiktok": true,
    "linkedin": true
  }
}
```

### Detailed System Status
```http
GET /api/system/status
```

**Response**:
```json
{
  "status": "operational",
  "timestamp": "2025-06-30T19:00:00Z",
  "services": {
    "database": {
      "status": "healthy",
      "response_time_ms": 5
    },
    "video_processor": {
      "status": "healthy",
      "ffmpeg_available": true
    },
    "realtime_publisher": {
      "status": "healthy",
      "active_jobs": 12,
      "websocket_connections": 45
    }
  },
  "platform_status": {
    "facebook": {
      "oauth_configured": true,
      "api_healthy": true
    },
    "twitter": {
      "oauth_configured": true,
      "api_healthy": true
    }
  }
}
```

---

## ⚠️ Error Responses

### Standard Error Format
```json
{
  "success": false,
  "error": "Error description",
  "error_code": 400,
  "timestamp": "2025-06-30T19:00:00Z"
}
```

### Common HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

### Error Examples

#### Authentication Error
```json
{
  "success": false,
  "error": "Invalid or expired token",
  "error_code": 401,
  "timestamp": "2025-06-30T19:00:00Z"
}
```

#### Validation Error
```json
{
  "success": false,
  "error": "Validation failed",
  "error_code": 400,
  "details": {
    "email": "Invalid email format",
    "password": "Password must be at least 8 characters"
  },
  "timestamp": "2025-06-30T19:00:00Z"
}
```

#### Rate Limit Error
```json
{
  "success": false,
  "error": "Rate limit exceeded",
  "error_code": 429,
  "retry_after": 60,
  "timestamp": "2025-06-30T19:00:00Z"
}
```

---

## 🚦 Rate Limiting

### Default Limits
- **Publishing**: 10 requests per minute
- **API Calls**: 60 requests per minute
- **Authentication**: 5 login attempts per minute

### Rate Limit Headers
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1640995200
```

---

## 📝 SDK Examples

### JavaScript/TypeScript
```typescript
class YouTubeAutomationAPI {
  private baseURL = 'https://your-domain.com/api';
  private token: string;

  constructor(token: string) {
    this.token = token;
  }

  private async request(endpoint: string, options: RequestInit = {}) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    const data = await response.json();
    if (!data.success) {
      throw new Error(data.error);
    }
    return data.data;
  }

  async publishVideo(videoFile: File, title: string, platforms: string[]) {
    const formData = new FormData();
    formData.append('video', videoFile);
    formData.append('title', title);
    formData.append('platforms', JSON.stringify(platforms));

    return this.request('/social/publish/realtime', {
      method: 'POST',
      body: formData,
      headers: {}, // Don't set Content-Type for FormData
    });
  }

  async getPublishingJobs() {
    return this.request('/social/publishing/jobs');
  }
}
```

### Python
```python
import requests
from typing import List, Dict, Any

class YouTubeAutomationAPI:
    def __init__(self, token: str, base_url: str = "https://your-domain.com/api"):
        self.base_url = base_url
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })
    
    def publish_video(self, video_path: str, title: str, platforms: List[str]) -> Dict[str, Any]:
        with open(video_path, 'rb') as video_file:
            files = {'video': video_file}
            data = {
                'title': title,
                'platforms': json.dumps(platforms)
            }
            
            # Remove Content-Type header for multipart
            headers = {k: v for k, v in self.session.headers.items() 
                      if k.lower() != 'content-type'}
            
            response = self.session.post(
                f"{self.base_url}/social/publish/realtime",
                files=files,
                data=data,
                headers=headers
            )
            
            return response.json()
    
    def get_publishing_jobs(self) -> Dict[str, Any]:
        response = self.session.get(f"{self.base_url}/social/publishing/jobs")
        return response.json()
```

---

## 🔧 Testing & Development

### Test Environment
**Base URL**: `https://test.your-domain.com/api`

### Sandbox Mode
Add `?sandbox=true` to any endpoint to use test data without actual platform publishing.

### Mock Responses
Enable mock responses by setting header:
```http
X-Mock-Response: true
```

---

**API Documentation Version**: 2.0.0  
**Last Updated**: June 30, 2025  
**Support**: api-support@your-domain.com