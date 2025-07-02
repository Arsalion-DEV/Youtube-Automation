#!/usr/bin/env python3
"""
Initialize AI Channel Wizard Database Tables
"""

import sqlite3
import os

def initialize_wizard_tables(db_path):
    """Initialize the AI wizard database tables"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Creating AI wizard database tables...")
        
        # Channel wizard configurations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS channel_wizard_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                channel_id TEXT NOT NULL,
                setup_config TEXT NOT NULL,
                seo_optimization TEXT,
                branding_data TEXT,
                competitor_analysis TEXT,
                content_strategy TEXT,
                setup_stage TEXT DEFAULT 'initial',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, channel_id)
            )
        ''')
        print("✓ Created channel_wizard_configs table")
        
        # AI-generated content ideas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_content_ideas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                content_type TEXT,
                keywords TEXT,
                estimated_performance TEXT,
                creation_date DATE,
                status TEXT DEFAULT 'suggested',
                ai_confidence REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✓ Created ai_content_ideas table")
        
        # Competitor tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS competitor_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT NOT NULL,
                competitor_channel_id TEXT NOT NULL,
                competitor_name TEXT,
                subscriber_count INTEGER,
                avg_views INTEGER,
                upload_frequency TEXT,
                content_analysis TEXT,
                last_analyzed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✓ Created competitor_tracking table")
        
        # SEO keyword tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS seo_keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT NOT NULL,
                keyword TEXT NOT NULL,
                search_volume INTEGER,
                competition_level TEXT,
                country_code TEXT,
                trend_data TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✓ Created seo_keywords table")
        
        conn.commit()
        print("\n🎉 AI wizard tables initialized successfully!")
        
        # Verify tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%wizard%' OR name IN ('ai_content_ideas', 'competitor_tracking', 'seo_keywords');")
        tables = cursor.fetchall()
        print(f"\nCreated tables: {[table[0] for table in tables]}")
        
    except Exception as e:
        print(f"❌ Error initializing AI wizard tables: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    # Use the database path from the server
    db_path = "/home/ubuntu/Veo-3-Automation/youtube_automation.db"
    initialize_wizard_tables(db_path)