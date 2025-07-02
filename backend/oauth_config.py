"""
OAuth Configuration for Social Media Platforms
This file manages OAuth credentials and environment variables
"""

import os
from typing import Dict, Any

# OAuth Configuration
OAUTH_CONFIGS = {
    "facebook": {
        "app_id": os.getenv("FACEBOOK_APP_ID", ""),
        "app_secret": os.getenv("FACEBOOK_APP_SECRET", ""),
        "redirect_uri": os.getenv("FACEBOOK_REDIRECT_URI", "http://localhost:8001/api/social/oauth/facebook/callback"),
        "scopes": ["publish_to_groups", "publish_video", "pages_manage_posts"]
    },
    "twitter": {
        "api_key": os.getenv("TWITTER_API_KEY", ""),
        "api_secret": os.getenv("TWITTER_API_SECRET", ""),
        "access_token": os.getenv("TWITTER_ACCESS_TOKEN", ""),
        "access_token_secret": os.getenv("TWITTER_ACCESS_TOKEN_SECRET", ""),
        "redirect_uri": os.getenv("TWITTER_REDIRECT_URI", "http://localhost:8001/api/social/oauth/twitter/callback")
    },
    "instagram": {
        "app_id": os.getenv("INSTAGRAM_APP_ID", ""),
        "app_secret": os.getenv("INSTAGRAM_APP_SECRET", ""),
        "redirect_uri": os.getenv("INSTAGRAM_REDIRECT_URI", "http://localhost:8001/api/social/oauth/instagram/callback"),
        "scopes": ["user_profile", "user_media"]
    },
    "tiktok": {
        "client_key": os.getenv("TIKTOK_CLIENT_KEY", ""),
        "client_secret": os.getenv("TIKTOK_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("TIKTOK_REDIRECT_URI", "http://localhost:8001/api/social/oauth/tiktok/callback"),
        "scopes": ["video.upload", "user.info.basic"]
    },
    "linkedin": {
        "client_id": os.getenv("LINKEDIN_CLIENT_ID", ""),
        "client_secret": os.getenv("LINKEDIN_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8001/api/social/oauth/linkedin/callback"),
        "scopes": ["w_member_social", "r_liteprofile"]
    }
}

def get_oauth_config(platform: str) -> Dict[str, Any]:
    """Get OAuth configuration for a specific platform"""
    return OAUTH_CONFIGS.get(platform, {})

def validate_oauth_config(platform: str) -> bool:
    """Validate that OAuth configuration is complete for a platform"""
    config = get_oauth_config(platform)
    if not config:
        return False
    
    # Check that all required fields are present and non-empty
    required_fields = {
        "facebook": ["app_id", "app_secret"],
        "twitter": ["api_key", "api_secret"],
        "instagram": ["app_id", "app_secret"],
        "tiktok": ["client_key", "client_secret"],
        "linkedin": ["client_id", "client_secret"]
    }
    
    platform_requirements = required_fields.get(platform, [])
    return all(config.get(field) for field in platform_requirements)

def get_environment_template() -> str:
    """Get environment variable template for OAuth setup"""
    return """
# Social Media OAuth Configuration
# Facebook
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
FACEBOOK_REDIRECT_URI=http://your-domain.com/api/social/oauth/facebook/callback

# Twitter
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
TWITTER_REDIRECT_URI=http://your-domain.com/api/social/oauth/twitter/callback

# Instagram
INSTAGRAM_APP_ID=your_instagram_app_id
INSTAGRAM_APP_SECRET=your_instagram_app_secret
INSTAGRAM_REDIRECT_URI=http://your-domain.com/api/social/oauth/instagram/callback

# TikTok
TIKTOK_CLIENT_KEY=your_tiktok_client_key
TIKTOK_CLIENT_SECRET=your_tiktok_client_secret
TIKTOK_REDIRECT_URI=http://your-domain.com/api/social/oauth/tiktok/callback

# LinkedIn
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
LINKEDIN_REDIRECT_URI=http://your-domain.com/api/social/oauth/linkedin/callback
"""