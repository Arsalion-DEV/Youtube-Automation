"""
Advanced Monetization Tracking System
Comprehensive revenue tracking across all platforms with detailed analytics
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta, date
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
from fastapi import HTTPException, APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

class RevenueSource(Enum):
    YOUTUBE_ADSENSE = "youtube_adsense"
    YOUTUBE_MEMBERSHIPS = "youtube_memberships"
    YOUTUBE_SUPER_CHAT = "youtube_super_chat"
    YOUTUBE_SUPER_THANKS = "youtube_super_thanks"
    BRAND_SPONSORSHIPS = "brand_sponsorships"
    AFFILIATE_MARKETING = "affiliate_marketing"
    MERCHANDISE = "merchandise"
    COURSE_SALES = "course_sales"
    PATREON = "patreon"
    TWITCH_SUBS = "twitch_subs"
    TIKTOK_CREATOR_FUND = "tiktok_creator_fund"
    INSTAGRAM_REELS_PLAY = "instagram_reels_play"
    FACEBOOK_CREATOR_BONUS = "facebook_creator_bonus"
    CUSTOM = "custom"

class PaymentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PAID = "paid"
    FAILED = "failed"
    DISPUTED = "disputed"
    REFUNDED = "refunded"

class Currency(Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"
    JPY = "JPY"

@dataclass
class RevenueEntry:
    id: str
    channel_id: str
    source: RevenueSource
    amount: float
    currency: Currency
    description: str
    date_earned: date
    date_recorded: datetime
    payment_status: PaymentStatus
    payment_date: Optional[date]
    video_id: Optional[str] = None
    campaign_id: Optional[str] = None
    external_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class MonetizationGoal:
    id: str
    name: str
    target_amount: float
    currency: Currency
    period: str  # daily, weekly, monthly, yearly
    start_date: date
    end_date: date
    channels: List[str]
    sources: List[RevenueSource]
    created_by: str

@dataclass
class RevenueAnalytics:
    total_revenue: float
    revenue_by_source: Dict[str, float]
    revenue_by_period: Dict[str, float]
    growth_rate: float
    avg_per_video: float
    top_performing_videos: List[Dict[str, Any]]
    projected_revenue: float
    goal_progress: Dict[str, Any]

class CurrencyConverter:
    """Simple currency conversion service"""
    
    # Static exchange rates (in production, use real-time API)
    RATES = {
        Currency.USD: 1.0,
        Currency.EUR: 0.85,
        Currency.GBP: 0.73,
        Currency.CAD: 1.25,
        Currency.AUD: 1.35,
        Currency.JPY: 110.0
    }
    
    @classmethod
    def convert(cls, amount: float, from_currency: Currency, to_currency: Currency) -> float:
        """Convert amount from one currency to another"""
        if from_currency == to_currency:
            return amount
        
        # Convert to USD first, then to target currency
        usd_amount = amount / cls.RATES[from_currency]
        return usd_amount * cls.RATES[to_currency]
    
    @classmethod
    def to_usd(cls, amount: float, from_currency: Currency) -> float:
        """Convert any currency to USD"""
        return cls.convert(amount, from_currency, Currency.USD)

class MonetizationTracker:
    """Advanced monetization tracking and analytics system"""
    
    def __init__(self, db_path: str = "youtube_automation.db"):
        self.db_path = db_path
        self.converter = CurrencyConverter()
        self.init_database()
    
    def init_database(self):
        """Initialize database tables for monetization tracking"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Revenue entries table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS revenue_entries (
                    id TEXT PRIMARY KEY,
                    channel_id TEXT NOT NULL,
                    source TEXT NOT NULL,
                    amount REAL NOT NULL,
                    currency TEXT NOT NULL,
                    description TEXT,
                    date_earned DATE NOT NULL,
                    date_recorded DATETIME NOT NULL,
                    payment_status TEXT NOT NULL,
                    payment_date DATE,
                    video_id TEXT,
                    campaign_id TEXT,
                    external_id TEXT,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Monetization goals table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS monetization_goals (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    target_amount REAL NOT NULL,
                    currency TEXT NOT NULL,
                    period TEXT NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    channels TEXT,
                    sources TEXT,
                    created_by TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Revenue snapshots for historical tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS revenue_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    snapshot_date DATE NOT NULL,
                    channel_id TEXT NOT NULL,
                    total_revenue REAL NOT NULL,
                    revenue_breakdown TEXT NOT NULL,
                    metrics TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Platform integration settings
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS platform_integrations (
                    id TEXT PRIMARY KEY,
                    platform TEXT NOT NULL,
                    channel_id TEXT NOT NULL,
                    api_credentials TEXT,
                    last_sync DATETIME,
                    sync_status TEXT,
                    auto_sync_enabled BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    async def add_revenue_entry(
        self,
        channel_id: str,
        source: RevenueSource,
        amount: float,
        currency: Currency,
        description: str,
        date_earned: date,
        payment_status: PaymentStatus = PaymentStatus.PENDING,
        video_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
        external_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a new revenue entry"""
        
        entry_id = str(uuid.uuid4())
        
        entry = RevenueEntry(
            id=entry_id,
            channel_id=channel_id,
            source=source,
            amount=amount,
            currency=currency,
            description=description,
            date_earned=date_earned,
            date_recorded=datetime.utcnow(),
            payment_status=payment_status,
            payment_date=None,
            video_id=video_id,
            campaign_id=campaign_id,
            external_id=external_id,
            metadata=metadata
        )
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO revenue_entries (
                    id, channel_id, source, amount, currency, description,
                    date_earned, date_recorded, payment_status, payment_date,
                    video_id, campaign_id, external_id, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.id, entry.channel_id, entry.source.value, entry.amount,
                entry.currency.value, entry.description, entry.date_earned,
                entry.date_recorded, entry.payment_status.value, entry.payment_date,
                entry.video_id, entry.campaign_id, entry.external_id,
                json.dumps(entry.metadata) if entry.metadata else None
            ))
            
            conn.commit()
        
        logger.info(f"Added revenue entry: {entry_id} - ${amount} {currency.value} from {source.value}")
        return entry_id
    
    async def update_payment_status(
        self,
        entry_id: str,
        status: PaymentStatus,
        payment_date: Optional[date] = None
    ) -> bool:
        """Update payment status for a revenue entry"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE revenue_entries 
                SET payment_status = ?, payment_date = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status.value, payment_date, entry_id))
            
            if cursor.rowcount == 0:
                return False
            
            conn.commit()
        
        logger.info(f"Updated payment status for entry {entry_id} to {status.value}")
        return True
    
    async def create_monetization_goal(
        self,
        name: str,
        target_amount: float,
        currency: Currency,
        period: str,
        start_date: date,
        end_date: date,
        channels: List[str],
        sources: List[RevenueSource],
        created_by: str
    ) -> str:
        """Create a new monetization goal"""
        
        goal_id = str(uuid.uuid4())
        
        goal = MonetizationGoal(
            id=goal_id,
            name=name,
            target_amount=target_amount,
            currency=currency,
            period=period,
            start_date=start_date,
            end_date=end_date,
            channels=channels,
            sources=sources,
            created_by=created_by
        )
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO monetization_goals (
                    id, name, target_amount, currency, period, start_date,
                    end_date, channels, sources, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                goal.id, goal.name, goal.target_amount, goal.currency.value,
                goal.period, goal.start_date, goal.end_date,
                json.dumps(goal.channels), json.dumps([s.value for s in goal.sources]),
                goal.created_by
            ))
            
            conn.commit()
        
        logger.info(f"Created monetization goal: {goal_id} - {name}")
        return goal_id
    
    async def get_revenue_analytics(
        self,
        channel_ids: Optional[List[str]] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        currency: Currency = Currency.USD
    ) -> RevenueAnalytics:
        """Get comprehensive revenue analytics"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Build query conditions
            conditions = []
            params = []
            
            if channel_ids:
                conditions.append(f"channel_id IN ({','.join(['?' for _ in channel_ids])})")
                params.extend(channel_ids)
            
            if start_date:
                conditions.append("date_earned >= ?")
                params.append(start_date)
            
            if end_date:
                conditions.append("date_earned <= ?")
                params.append(end_date)
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            # Get all revenue entries
            cursor.execute(f"""
                SELECT * FROM revenue_entries WHERE {where_clause}
                ORDER BY date_earned DESC
            """, params)
            
            entries = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            if not entries:
                return RevenueAnalytics(
                    total_revenue=0,
                    revenue_by_source={},
                    revenue_by_period={},
                    growth_rate=0,
                    avg_per_video=0,
                    top_performing_videos=[],
                    projected_revenue=0,
                    goal_progress={}
                )
            
            # Convert to DataFrame for easier analysis
            df = pd.DataFrame(entries, columns=columns)
            
            # Convert all amounts to target currency
            df['amount_usd'] = df.apply(
                lambda row: self.converter.convert(
                    row['amount'], 
                    Currency(row['currency']), 
                    currency
                ), 
                axis=1
            )
            
            # Calculate total revenue
            total_revenue = df['amount_usd'].sum()
            
            # Revenue by source
            revenue_by_source = df.groupby('source')['amount_usd'].sum().to_dict()
            
            # Revenue by period (monthly)
            df['date_earned'] = pd.to_datetime(df['date_earned'])
            df['period'] = df['date_earned'].dt.to_period('M')
            revenue_by_period = df.groupby('period')['amount_usd'].sum().to_dict()
            revenue_by_period = {str(k): float(v) for k, v in revenue_by_period.items()}
            
            # Calculate growth rate (month-over-month)
            periods = sorted(revenue_by_period.keys())
            growth_rate = 0
            if len(periods) >= 2:
                current = revenue_by_period[periods[-1]]
                previous = revenue_by_period[periods[-2]]
                if previous > 0:
                    growth_rate = ((current - previous) / previous) * 100
            
            # Average revenue per video
            video_revenues = df[df['video_id'].notna()].groupby('video_id')['amount_usd'].sum()
            avg_per_video = video_revenues.mean() if len(video_revenues) > 0 else 0
            
            # Top performing videos
            top_videos = video_revenues.nlargest(5).to_dict()
            top_performing_videos = [
                {"video_id": vid, "revenue": float(rev)} 
                for vid, rev in top_videos.items()
            ]
            
            # Simple projection (based on current month trend)
            current_month_data = df[df['period'] == df['period'].max()]
            days_in_month = pd.Timestamp.now().days_in_month
            current_day = pd.Timestamp.now().day
            
            if len(current_month_data) > 0 and current_day > 0:
                daily_avg = current_month_data['amount_usd'].sum() / current_day
                projected_revenue = daily_avg * days_in_month
            else:
                projected_revenue = 0
            
            # Get goal progress
            goal_progress = await self._calculate_goal_progress(channel_ids, currency)
            
            return RevenueAnalytics(
                total_revenue=float(total_revenue),
                revenue_by_source={k: float(v) for k, v in revenue_by_source.items()},
                revenue_by_period=revenue_by_period,
                growth_rate=float(growth_rate),
                avg_per_video=float(avg_per_video),
                top_performing_videos=top_performing_videos,
                projected_revenue=float(projected_revenue),
                goal_progress=goal_progress
            )
    
    async def _calculate_goal_progress(
        self, 
        channel_ids: Optional[List[str]] = None,
        currency: Currency = Currency.USD
    ) -> Dict[str, Any]:
        """Calculate progress towards monetization goals"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get active goals
            cursor.execute("""
                SELECT * FROM monetization_goals 
                WHERE end_date >= date('now')
                ORDER BY end_date ASC
            """)
            
            goals = cursor.fetchall()
            goal_columns = [desc[0] for desc in cursor.description]
            
            goal_progress = {}
            
            for goal_row in goals:
                goal_dict = dict(zip(goal_columns, goal_row))
                goal_id = goal_dict['id']
                goal_channels = json.loads(goal_dict['channels'])
                goal_sources = json.loads(goal_dict['sources'])
                
                # Filter by channels if specified
                if channel_ids:
                    goal_channels = [c for c in goal_channels if c in channel_ids]
                
                if not goal_channels:
                    continue
                
                # Calculate current progress
                conditions = []
                params = []
                
                conditions.append(f"channel_id IN ({','.join(['?' for _ in goal_channels])})")
                params.extend(goal_channels)
                
                conditions.append(f"source IN ({','.join(['?' for _ in goal_sources])})")
                params.extend(goal_sources)
                
                conditions.append("date_earned >= ?")
                params.append(goal_dict['start_date'])
                
                conditions.append("date_earned <= ?")
                params.append(goal_dict['end_date'])
                
                where_clause = " AND ".join(conditions)
                
                cursor.execute(f"""
                    SELECT amount, currency FROM revenue_entries 
                    WHERE {where_clause}
                """, params)
                
                progress_entries = cursor.fetchall()
                
                # Convert to target currency and sum
                current_amount = 0
                for amount, entry_currency in progress_entries:
                    current_amount += self.converter.convert(
                        amount, Currency(entry_currency), Currency(goal_dict['currency'])
                    )
                
                target_amount = goal_dict['target_amount']
                progress_percentage = (current_amount / target_amount * 100) if target_amount > 0 else 0
                
                # Calculate days remaining
                start_date = datetime.strptime(goal_dict['start_date'], '%Y-%m-%d').date()
                end_date = datetime.strptime(goal_dict['end_date'], '%Y-%m-%d').date()
                today = date.today()
                
                total_days = (end_date - start_date).days
                days_elapsed = (today - start_date).days
                days_remaining = (end_date - today).days
                
                # Calculate required daily rate to meet goal
                required_daily_rate = 0
                if days_remaining > 0:
                    remaining_amount = target_amount - current_amount
                    required_daily_rate = max(0, remaining_amount / days_remaining)
                
                goal_progress[goal_id] = {
                    "name": goal_dict['name'],
                    "target_amount": target_amount,
                    "current_amount": current_amount,
                    "progress_percentage": min(100, progress_percentage),
                    "currency": goal_dict['currency'],
                    "days_remaining": max(0, days_remaining),
                    "required_daily_rate": required_daily_rate,
                    "on_track": progress_percentage >= (days_elapsed / total_days * 100) if total_days > 0 else False
                }
            
            return goal_progress
    
    async def sync_platform_revenue(self, channel_id: str, platform: str) -> Dict[str, Any]:
        """Sync revenue data from external platforms"""
        
        # This would integrate with platform APIs (YouTube Analytics, etc.)
        # For now, return mock data
        
        mock_entries = []
        
        if platform == "youtube":
            # Mock YouTube AdSense data
            mock_entries.extend([
                {
                    "source": RevenueSource.YOUTUBE_ADSENSE,
                    "amount": 125.45,
                    "currency": Currency.USD,
                    "description": "AdSense revenue for video views",
                    "date_earned": date.today() - timedelta(days=1),
                    "external_id": "yt_adsense_001"
                },
                {
                    "source": RevenueSource.YOUTUBE_MEMBERSHIPS,
                    "amount": 50.00,
                    "currency": Currency.USD,
                    "description": "Channel membership revenue",
                    "date_earned": date.today() - timedelta(days=1),
                    "external_id": "yt_memberships_001"
                }
            ])
        
        elif platform == "tiktok":
            # Mock TikTok Creator Fund data
            mock_entries.append({
                "source": RevenueSource.TIKTOK_CREATOR_FUND,
                "amount": 25.30,
                "currency": Currency.USD,
                "description": "TikTok Creator Fund payout",
                "date_earned": date.today() - timedelta(days=1),
                "external_id": "tt_creator_001"
            })
        
        # Add entries to database
        added_entries = []
        for entry_data in mock_entries:
            entry_id = await self.add_revenue_entry(
                channel_id=channel_id,
                **entry_data,
                payment_status=PaymentStatus.PAID
            )
            added_entries.append(entry_id)
        
        # Update sync status
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO platform_integrations 
                (id, platform, channel_id, last_sync, sync_status)
                VALUES (?, ?, ?, ?, ?)
            """, (
                f"{platform}_{channel_id}",
                platform,
                channel_id,
                datetime.utcnow(),
                "success"
            ))
            
            conn.commit()
        
        return {
            "platform": platform,
            "channel_id": channel_id,
            "entries_added": len(added_entries),
            "entry_ids": added_entries,
            "last_sync": datetime.utcnow().isoformat()
        }
    
    async def generate_revenue_report(
        self,
        channel_ids: Optional[List[str]] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        format: str = "json"
    ) -> Dict[str, Any]:
        """Generate comprehensive revenue report"""
        
        analytics = await self.get_revenue_analytics(channel_ids, start_date, end_date)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get top performing content
            cursor.execute("""
                SELECT video_id, SUM(amount) as total_revenue, COUNT(*) as revenue_entries
                FROM revenue_entries 
                WHERE video_id IS NOT NULL
                GROUP BY video_id
                ORDER BY total_revenue DESC
                LIMIT 10
            """)
            top_content = cursor.fetchall()
            
            # Get platform performance
            cursor.execute("""
                SELECT source, 
                       COUNT(*) as transaction_count,
                       SUM(amount) as total_amount,
                       AVG(amount) as avg_amount,
                       MIN(date_earned) as first_revenue,
                       MAX(date_earned) as last_revenue
                FROM revenue_entries
                GROUP BY source
                ORDER BY total_amount DESC
            """)
            platform_performance = cursor.fetchall()
            
        report = {
            "report_generated": datetime.utcnow().isoformat(),
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            },
            "analytics": asdict(analytics),
            "top_content": [
                {
                    "video_id": row[0],
                    "total_revenue": float(row[1]),
                    "revenue_entries": row[2]
                }
                for row in top_content
            ],
            "platform_performance": [
                {
                    "source": row[0],
                    "transaction_count": row[1],
                    "total_amount": float(row[2]),
                    "avg_amount": float(row[3]),
                    "first_revenue": row[4],
                    "last_revenue": row[5]
                }
                for row in platform_performance
            ]
        }
        
        return report

# FastAPI routes for monetization tracking
monetization_router = APIRouter(prefix="/api/v2/monetization", tags=["Monetization"])
monetization_tracker = MonetizationTracker()

class AddRevenueRequest(BaseModel):
    channel_id: str
    source: str
    amount: float
    currency: str
    description: str
    date_earned: str  # ISO date format
    video_id: Optional[str] = None
    campaign_id: Optional[str] = None
    external_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class CreateGoalRequest(BaseModel):
    name: str
    target_amount: float
    currency: str
    period: str
    start_date: str
    end_date: str
    channels: List[str]
    sources: List[str]

@monetization_router.post("/revenue")
async def add_revenue_entry(request: AddRevenueRequest):
    """Add a new revenue entry"""
    try:
        entry_id = await monetization_tracker.add_revenue_entry(
            channel_id=request.channel_id,
            source=RevenueSource(request.source),
            amount=request.amount,
            currency=Currency(request.currency),
            description=request.description,
            date_earned=datetime.fromisoformat(request.date_earned).date(),
            video_id=request.video_id,
            campaign_id=request.campaign_id,
            external_id=request.external_id,
            metadata=request.metadata
        )
        
        return {"success": True, "entry_id": entry_id}
        
    except Exception as e:
        logger.error(f"Error adding revenue entry: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@monetization_router.get("/analytics")
async def get_revenue_analytics(
    channel_ids: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    currency: str = "USD"
):
    """Get comprehensive revenue analytics"""
    try:
        channel_list = channel_ids.split(",") if channel_ids else None
        start = datetime.fromisoformat(start_date).date() if start_date else None
        end = datetime.fromisoformat(end_date).date() if end_date else None
        
        analytics = await monetization_tracker.get_revenue_analytics(
            channel_ids=channel_list,
            start_date=start,
            end_date=end,
            currency=Currency(currency)
        )
        
        return {"success": True, "data": asdict(analytics)}
        
    except Exception as e:
        logger.error(f"Error getting revenue analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@monetization_router.post("/goals")
async def create_monetization_goal(request: CreateGoalRequest, user_id: str = "default_user"):
    """Create a new monetization goal"""
    try:
        goal_id = await monetization_tracker.create_monetization_goal(
            name=request.name,
            target_amount=request.target_amount,
            currency=Currency(request.currency),
            period=request.period,
            start_date=datetime.fromisoformat(request.start_date).date(),
            end_date=datetime.fromisoformat(request.end_date).date(),
            channels=request.channels,
            sources=[RevenueSource(s) for s in request.sources],
            created_by=user_id
        )
        
        return {"success": True, "goal_id": goal_id}
        
    except Exception as e:
        logger.error(f"Error creating monetization goal: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@monetization_router.post("/sync/{platform}/{channel_id}")
async def sync_platform_revenue(platform: str, channel_id: str, background_tasks: BackgroundTasks):
    """Sync revenue data from external platforms"""
    try:
        # Run sync in background
        background_tasks.add_task(
            monetization_tracker.sync_platform_revenue,
            channel_id, platform
        )
        
        return {"success": True, "message": f"Sync started for {platform} channel {channel_id}"}
        
    except Exception as e:
        logger.error(f"Error starting platform sync: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@monetization_router.get("/report")
async def generate_revenue_report(
    channel_ids: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    format: str = "json"
):
    """Generate comprehensive revenue report"""
    try:
        channel_list = channel_ids.split(",") if channel_ids else None
        start = datetime.fromisoformat(start_date).date() if start_date else None
        end = datetime.fromisoformat(end_date).date() if end_date else None
        
        report = await monetization_tracker.generate_revenue_report(
            channel_ids=channel_list,
            start_date=start,
            end_date=end,
            format=format
        )
        
        return {"success": True, "data": report}
        
    except Exception as e:
        logger.error(f"Error generating revenue report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))