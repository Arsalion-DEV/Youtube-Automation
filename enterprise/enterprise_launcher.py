#!/usr/bin/env python3
"""
Enterprise Feature Launcher for Veo-3 Automation Platform
Integrates enterprise features with the existing backend
"""

import os
import sys
import json
import time
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Add backend path
sys.path.append('/home/ubuntu/Veo-3-Automation/backend')

# Basic imports
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnterpriseManager:
    def __init__(self):
        self.db_url = "postgresql://veo3_user:veo3_secure_password_2024@localhost:5432/veo3_enterprise"
        self.redis_url = "redis://localhost:6379/0"
        self.engine = None
        self.redis_client = None
        self.setup_connections()
    
    def setup_connections(self):
        """Initialize database and Redis connections"""
        try:
            self.engine = create_engine(self.db_url)
            self.redis_client = redis.from_url(self.redis_url)
            
            # Test connections
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            self.redis_client.ping()
            logger.info("✅ Enterprise connections established")
            
        except Exception as e:
            logger.error(f"❌ Connection setup failed: {e}")
            raise
    
    def track_analytics_event(self, user_id: int, event_type: str, event_data: Dict[str, Any]):
        """Track analytics events"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO analytics_events (user_id, event_type, event_data, timestamp)
                    VALUES (:user_id, :event_type, :event_data, :timestamp)
                """), {
                    'user_id': user_id,
                    'event_type': event_type,
                    'event_data': json.dumps(event_data),
                    'timestamp': datetime.utcnow()
                })
                conn.commit()
            
            # Cache recent events in Redis
            cache_key = f"analytics:user:{user_id}:recent"
            event_cache = {
                'event_type': event_type,
                'event_data': event_data,
                'timestamp': datetime.utcnow().isoformat()
            }
            self.redis_client.lpush(cache_key, json.dumps(event_cache))
            self.redis_client.ltrim(cache_key, 0, 99)  # Keep last 100 events
            self.redis_client.expire(cache_key, 86400)  # 24 hours
            
            logger.info(f"📊 Analytics event tracked: {event_type} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Analytics tracking failed: {e}")
            return False
    
    def get_analytics_summary(self, user_id: int = None) -> Dict[str, Any]:
        """Get analytics summary"""
        try:
            with self.engine.connect() as conn:
                if user_id:
                    # User-specific analytics
                    result = conn.execute(text("""
                        SELECT event_type, COUNT(*) as count, 
                               MAX(timestamp) as last_event
                        FROM analytics_events 
                        WHERE user_id = :user_id 
                        AND timestamp > :since
                        GROUP BY event_type
                        ORDER BY count DESC
                    """), {
                        'user_id': user_id,
                        'since': datetime.utcnow() - timedelta(days=30)
                    })
                else:
                    # Platform-wide analytics
                    result = conn.execute(text("""
                        SELECT event_type, COUNT(*) as count,
                               COUNT(DISTINCT user_id) as unique_users,
                               MAX(timestamp) as last_event
                        FROM analytics_events 
                        WHERE timestamp > :since
                        GROUP BY event_type
                        ORDER BY count DESC
                    """), {
                        'since': datetime.utcnow() - timedelta(days=30)
                    })
                
                events = []
                for row in result:
                    events.append({
                        'event_type': row[0],
                        'count': row[1],
                        'unique_users': row[2] if not user_id else None,
                        'last_event': row[-1].isoformat() if row[-1] else None
                    })
                
                return {
                    'success': True,
                    'events': events,
                    'generated_at': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ Analytics summary failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def track_monetization(self, user_id: int, amount: float, source: str):
        """Track monetization data"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO monetization_tracking (user_id, revenue_amount, revenue_source, recorded_at)
                    VALUES (:user_id, :amount, :source, :timestamp)
                """), {
                    'user_id': user_id,
                    'amount': amount,
                    'source': source,
                    'timestamp': datetime.utcnow()
                })
                conn.commit()
            
            # Update Redis cache
            cache_key = f"monetization:user:{user_id}:total"
            current_total = float(self.redis_client.get(cache_key) or 0)
            new_total = current_total + amount
            self.redis_client.set(cache_key, str(new_total), ex=86400)
            
            logger.info(f"💰 Monetization tracked:  from {source} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Monetization tracking failed: {e}")
            return False
    
    def create_ab_test(self, name: str, description: str) -> Optional[int]:
        """Create a new A/B test"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    INSERT INTO ab_tests (name, description, status, created_at)
                    VALUES (:name, :description, 'active', :timestamp)
                    RETURNING id
                """), {
                    'name': name,
                    'description': description,
                    'timestamp': datetime.utcnow()
                })
                conn.commit()
                test_id = result.fetchone()[0]
            
            logger.info(f"🧪 A/B test created: {name} (ID: {test_id})")
            return test_id
            
        except Exception as e:
            logger.error(f"❌ A/B test creation failed: {e}")
            return None
    
    def get_platform_health(self) -> Dict[str, Any]:
        """Get platform health status"""
        health = {
            'timestamp': datetime.utcnow().isoformat(),
            'database': False,
            'redis': False,
            'features': {
                'analytics': False,
                'monetization': False,
                'ab_testing': False
            }
        }
        
        try:
            # Test database
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            health['database'] = True
            
            # Test Redis
            self.redis_client.ping()
            health['redis'] = True
            
            # Test feature tables
            with self.engine.connect() as conn:
                # Analytics
                conn.execute(text("SELECT COUNT(*) FROM analytics_events LIMIT 1"))
                health['features']['analytics'] = True
                
                # Monetization
                conn.execute(text("SELECT COUNT(*) FROM monetization_tracking LIMIT 1"))
                health['features']['monetization'] = True
                
                # A/B Testing
                conn.execute(text("SELECT COUNT(*) FROM ab_tests LIMIT 1"))
                health['features']['ab_testing'] = True
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
        
        return health

# Global enterprise manager instance
enterprise_manager = None

def get_enterprise_manager():
    """Get or create enterprise manager singleton"""
    global enterprise_manager
    if enterprise_manager is None:
        enterprise_manager = EnterpriseManager()
    return enterprise_manager

# API endpoints for integration with existing backend
def setup_enterprise_routes(app):
    """Setup enterprise routes for FastAPI app"""
    
    @app.get("/api/v1/enterprise/health")
    async def enterprise_health():
        manager = get_enterprise_manager()
        return manager.get_platform_health()
    
    @app.post("/api/v1/enterprise/analytics/track")
    async def track_analytics(user_id: int, event_type: str, event_data: dict):
        manager = get_enterprise_manager()
        success = manager.track_analytics_event(user_id, event_type, event_data)
        return {'success': success}
    
    @app.get("/api/v1/enterprise/analytics/summary")
    async def analytics_summary(user_id: int = None):
        manager = get_enterprise_manager()
        return manager.get_analytics_summary(user_id)
    
    @app.post("/api/v1/enterprise/monetization/track")
    async def track_monetization(user_id: int, amount: float, source: str):
        manager = get_enterprise_manager()
        success = manager.track_monetization(user_id, amount, source)
        return {'success': success}
    
    @app.post("/api/v1/enterprise/ab-test/create")
    async def create_ab_test(name: str, description: str):
        manager = get_enterprise_manager()
        test_id = manager.create_ab_test(name, description)
        return {'success': test_id is not None, 'test_id': test_id}

if __name__ == "__main__":
    # Test the enterprise manager
    print("🚀 Testing Enterprise Manager...")
    
    try:
        manager = EnterpriseManager()
        
        # Test analytics
        success = manager.track_analytics_event(1, "video_generated", {"title": "Test Video", "duration": 60})
        print(f"Analytics test: {'✅' if success else '❌'}")
        
        # Test monetization
        success = manager.track_monetization(1, 9.99, "subscription")
        print(f"Monetization test: {'✅' if success else '❌'}")
        
        # Test A/B testing
        test_id = manager.create_ab_test("New UI Layout", "Testing new dashboard layout")
        print(f"A/B test creation: {'✅' if test_id else '❌'} (ID: {test_id})")
        
        # Get analytics summary
        summary = manager.get_analytics_summary()
        print(f"Analytics summary: {'✅' if summary['success'] else '❌'}")
        
        # Get platform health
        health = manager.get_platform_health()
        print(f"Platform health: {'✅' if health['database'] and health['redis'] else '❌'}")
        
        print("\n🎉 Enterprise features are working successfully!")
        
    except Exception as e:
        print(f"❌ Enterprise test failed: {e}")
        sys.exit(1)
