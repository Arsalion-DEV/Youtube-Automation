#!/usr/bin/env python3
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def init_enterprise_database():
    DATABASE_URL = "postgresql://veo3_user:veo3_secure_password_2024@localhost:5432/veo3_enterprise"
    
    try:
        engine = create_engine(DATABASE_URL)
        
        # Test connection first
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
        
        # Create basic tables using raw SQL for now
        with engine.connect() as conn:
            # Analytics events table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS analytics_events (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER,
                    event_type VARCHAR(100),
                    event_data JSONB,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # A/B tests table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS ab_tests (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(200),
                    description TEXT,
                    status VARCHAR(50) DEFAULT 'draft',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Monetization tracking table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS monetization_tracking (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER,
                    revenue_amount DECIMAL(10,2),
                    revenue_source VARCHAR(100),
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Team management table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS team_members (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER,
                    team_id INTEGER,
                    role VARCHAR(50),
                    permissions JSONB,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # White label tenants table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS white_label_tenants (
                    id SERIAL PRIMARY KEY,
                    tenant_name VARCHAR(200),
                    custom_domain VARCHAR(200),
                    branding_config JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # User subscriptions table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS user_subscriptions (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER,
                    plan_name VARCHAR(100),
                    status VARCHAR(50),
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP
                );
            """))
            
            conn.commit()
            print("✅ Enterprise database tables created successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    success = init_enterprise_database()
    sys.exit(0 if success else 1)
