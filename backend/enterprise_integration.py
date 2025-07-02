#!/usr/bin/env python3
"""
Enterprise Integration Module
Integrates enterprise features with the existing Veo-3 backend
"""

import sys
import os
sys.path.append('/home/ubuntu/Veo-3-Automation/enterprise')

from enterprise_launcher import get_enterprise_manager, setup_enterprise_routes
from fastapi import FastAPI, APIRouter
import asyncio
import logging

logger = logging.getLogger(__name__)

def add_enterprise_features_to_app(app: FastAPI):
    """Add enterprise features to existing FastAPI app"""
    try:
        # Initialize enterprise manager
        manager = get_enterprise_manager()
        logger.info("✅ Enterprise manager initialized")
        
        # Setup enterprise routes
        setup_enterprise_routes(app)
        logger.info("✅ Enterprise routes added")
        
        # Add startup event to test enterprise features
        @app.on_event("startup")
        async def startup_enterprise():
            health = manager.get_platform_health()
            if health['database'] and health['redis']:
                logger.info("🚀 Enterprise features are online and healthy!")
            else:
                logger.warning("⚠️ Some enterprise features may not be available")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Enterprise integration failed: {e}")
        return False

def track_user_activity(user_id: int, activity_type: str, activity_data: dict):
    """Helper function to track user activity from anywhere in the app"""
    try:
        manager = get_enterprise_manager()
        return manager.track_analytics_event(user_id, activity_type, activity_data)
    except Exception as e:
        logger.error(f"Activity tracking failed: {e}")
        return False

def track_revenue(user_id: int, amount: float, source: str):
    """Helper function to track revenue from anywhere in the app"""
    try:
        manager = get_enterprise_manager()
        return manager.track_monetization(user_id, amount, source)
    except Exception as e:
        logger.error(f"Revenue tracking failed: {e}")
        return False

# Export functions for use in other modules
__all__ = ['add_enterprise_features_to_app', 'track_user_activity', 'track_revenue']
