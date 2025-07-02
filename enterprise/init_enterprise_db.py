#!/usr/bin/env python3
import os
import sys
sys.path.append('/home/ubuntu/Veo-3-Automation/backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from enterprise_backend import Base, AnalyticsEvent, ABTest, ABTestVariant, MonetizationTracking, TeamMember, TeamPermission, WhiteLabelTenant, UserSubscription

def init_enterprise_database():
    # Database connection
    DATABASE_URL = "postgresql://veo3_user:veo3_secure_password_2024@localhost:5432/veo3_enterprise"
    
    try:
        engine = create_engine(DATABASE_URL)
        
        # Create all tables
        print("Creating enterprise database tables...")
        Base.metadata.create_all(engine)
        print("✅ Enterprise tables created successfully!")
        
        # Test connection
        Session = sessionmaker(bind=engine)
        session = Session()
        session.execute("SELECT 1")
        session.close()
        print("✅ Database connection test successful!")
        
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    success = init_enterprise_database()
    sys.exit(0 if success else 1)
