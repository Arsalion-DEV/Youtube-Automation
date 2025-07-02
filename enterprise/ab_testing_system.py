"""
Advanced A/B Testing System for YouTube Automation Platform
Comprehensive testing framework with statistical analysis
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
from scipy import stats
import sqlite3
from fastapi import HTTPException, APIRouter, Depends
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class TestStatus(Enum):
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TestType(Enum):
    TITLE = "title"
    THUMBNAIL = "thumbnail"
    DESCRIPTION = "description"
    UPLOAD_TIME = "upload_time"
    TAGS = "tags"
    CUSTOM = "custom"

class MetricType(Enum):
    VIEWS = "views"
    CTR = "ctr"
    WATCH_TIME = "watch_time"
    ENGAGEMENT = "engagement"
    SUBSCRIBERS = "subscribers"
    REVENUE = "revenue"
    LIKES = "likes"
    COMMENTS = "comments"
    SHARES = "shares"

@dataclass
class TestVariant:
    id: str
    name: str
    content: Dict[str, Any]
    traffic_allocation: float  # Percentage of traffic (0-100)
    
@dataclass
class TestMetrics:
    variant_id: str
    timestamp: datetime
    metric_type: MetricType
    value: float
    count: int = 1

@dataclass
class ABTest:
    id: str
    name: str
    description: str
    test_type: TestType
    status: TestStatus
    variants: List[TestVariant]
    primary_metric: MetricType
    secondary_metrics: List[MetricType]
    start_date: datetime
    end_date: Optional[datetime]
    min_sample_size: int
    confidence_level: float  # 0.95 for 95%
    created_by: str
    created_at: datetime
    channel_ids: List[str]
    target_audience: Optional[Dict[str, Any]] = None
    
class StatisticalAnalysis:
    """Advanced statistical analysis for A/B tests"""
    
    @staticmethod
    def calculate_sample_size(
        baseline_rate: float,
        minimum_detectable_effect: float,
        power: float = 0.8,
        alpha: float = 0.05
    ) -> int:
        """Calculate required sample size for A/B test"""
        # Using formula for comparing two proportions
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = stats.norm.ppf(power)
        
        p1 = baseline_rate
        p2 = baseline_rate * (1 + minimum_detectable_effect)
        p_pooled = (p1 + p2) / 2
        
        numerator = (z_alpha * np.sqrt(2 * p_pooled * (1 - p_pooled)) + 
                    z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
        denominator = (p2 - p1) ** 2
        
        return int(np.ceil(numerator / denominator))
    
    @staticmethod
    def calculate_confidence_interval(
        conversion_rate: float,
        sample_size: int,
        confidence_level: float = 0.95
    ) -> Tuple[float, float]:
        """Calculate confidence interval for conversion rate"""
        z_score = stats.norm.ppf(1 - (1 - confidence_level) / 2)
        standard_error = np.sqrt(conversion_rate * (1 - conversion_rate) / sample_size)
        margin_of_error = z_score * standard_error
        
        return (
            max(0, conversion_rate - margin_of_error),
            min(1, conversion_rate + margin_of_error)
        )
    
    @staticmethod
    def perform_t_test(
        variant_a_data: List[float],
        variant_b_data: List[float],
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """Perform independent t-test between two variants"""
        if len(variant_a_data) < 2 or len(variant_b_data) < 2:
            return {
                "statistic": None,
                "p_value": None,
                "confidence_interval": None,
                "significant": False,
                "power": None
            }
        
        # Perform Welch's t-test (unequal variances)
        statistic, p_value = stats.ttest_ind(
            variant_a_data, 
            variant_b_data, 
            equal_var=False
        )
        
        # Calculate effect size (Cohen's d)
        pooled_std = np.sqrt(
            ((len(variant_a_data) - 1) * np.var(variant_a_data, ddof=1) + 
             (len(variant_b_data) - 1) * np.var(variant_b_data, ddof=1)) /
            (len(variant_a_data) + len(variant_b_data) - 2)
        )
        
        cohens_d = (np.mean(variant_b_data) - np.mean(variant_a_data)) / pooled_std
        
        # Calculate confidence interval for the difference
        alpha = 1 - confidence_level
        df = len(variant_a_data) + len(variant_b_data) - 2
        t_critical = stats.t.ppf(1 - alpha/2, df)
        
        se_diff = pooled_std * np.sqrt(1/len(variant_a_data) + 1/len(variant_b_data))
        diff_mean = np.mean(variant_b_data) - np.mean(variant_a_data)
        
        ci_lower = diff_mean - t_critical * se_diff
        ci_upper = diff_mean + t_critical * se_diff
        
        return {
            "statistic": float(statistic),
            "p_value": float(p_value),
            "effect_size": float(cohens_d),
            "confidence_interval": [float(ci_lower), float(ci_upper)],
            "significant": p_value < (1 - confidence_level),
            "mean_difference": float(diff_mean),
            "improvement_percentage": float((diff_mean / np.mean(variant_a_data)) * 100) if np.mean(variant_a_data) != 0 else 0
        }

class ABTestManager:
    """Comprehensive A/B testing management system"""
    
    def __init__(self, db_path: str = "youtube_automation.db"):
        self.db_path = db_path
        self.analysis = StatisticalAnalysis()
        self.init_database()
    
    def init_database(self):
        """Initialize database tables for A/B testing"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # A/B Tests table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ab_tests (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    test_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    primary_metric TEXT NOT NULL,
                    secondary_metrics TEXT,
                    start_date DATETIME,
                    end_date DATETIME,
                    min_sample_size INTEGER,
                    confidence_level REAL,
                    created_by TEXT,
                    created_at DATETIME,
                    channel_ids TEXT,
                    target_audience TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Test variants table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_variants (
                    id TEXT PRIMARY KEY,
                    test_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    content TEXT NOT NULL,
                    traffic_allocation REAL NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (test_id) REFERENCES ab_tests (id)
                )
            """)
            
            # Test metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_id TEXT NOT NULL,
                    variant_id TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    metric_type TEXT NOT NULL,
                    value REAL NOT NULL,
                    count INTEGER DEFAULT 1,
                    session_id TEXT,
                    user_id TEXT,
                    video_id TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (test_id) REFERENCES ab_tests (id),
                    FOREIGN KEY (variant_id) REFERENCES test_variants (id)
                )
            """)
            
            # Test assignments table (tracks which users see which variants)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_assignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_id TEXT NOT NULL,
                    variant_id TEXT NOT NULL,
                    user_id TEXT,
                    session_id TEXT,
                    video_id TEXT,
                    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (test_id) REFERENCES ab_tests (id),
                    FOREIGN KEY (variant_id) REFERENCES test_variants (id)
                )
            """)
            
            conn.commit()
    
    async def create_test(
        self,
        name: str,
        description: str,
        test_type: TestType,
        variants: List[Dict[str, Any]],
        primary_metric: MetricType,
        secondary_metrics: List[MetricType],
        channel_ids: List[str],
        created_by: str,
        min_sample_size: Optional[int] = None,
        confidence_level: float = 0.95,
        target_audience: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new A/B test"""
        
        test_id = str(uuid.uuid4())
        
        # Validate traffic allocation
        total_allocation = sum(v.get('traffic_allocation', 0) for v in variants)
        if abs(total_allocation - 100.0) > 0.1:
            raise HTTPException(
                status_code=400,
                detail="Traffic allocation must sum to 100%"
            )
        
        # Calculate minimum sample size if not provided
        if min_sample_size is None:
            # Use default baseline rate and effect size
            min_sample_size = self.analysis.calculate_sample_size(
                baseline_rate=0.1,  # 10% baseline
                minimum_detectable_effect=0.2  # 20% improvement
            )
        
        # Create test variants
        test_variants = []
        for i, variant_data in enumerate(variants):
            variant_id = str(uuid.uuid4())
            variant = TestVariant(
                id=variant_id,
                name=variant_data['name'],
                content=variant_data['content'],
                traffic_allocation=variant_data['traffic_allocation']
            )
            test_variants.append(variant)
        
        # Create test object
        test = ABTest(
            id=test_id,
            name=name,
            description=description,
            test_type=test_type,
            status=TestStatus.DRAFT,
            variants=test_variants,
            primary_metric=primary_metric,
            secondary_metrics=secondary_metrics,
            start_date=datetime.utcnow(),
            end_date=None,
            min_sample_size=min_sample_size,
            confidence_level=confidence_level,
            created_by=created_by,
            created_at=datetime.utcnow(),
            channel_ids=channel_ids,
            target_audience=target_audience
        )
        
        # Save to database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert test
            cursor.execute("""
                INSERT INTO ab_tests (
                    id, name, description, test_type, status, primary_metric,
                    secondary_metrics, start_date, min_sample_size, confidence_level,
                    created_by, created_at, channel_ids, target_audience
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                test.id, test.name, test.description, test.test_type.value,
                test.status.value, test.primary_metric.value,
                json.dumps([m.value for m in test.secondary_metrics]),
                test.start_date, test.min_sample_size, test.confidence_level,
                test.created_by, test.created_at,
                json.dumps(test.channel_ids),
                json.dumps(test.target_audience) if test.target_audience else None
            ))
            
            # Insert variants
            for variant in test.variants:
                cursor.execute("""
                    INSERT INTO test_variants (id, test_id, name, content, traffic_allocation)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    variant.id, test.id, variant.name,
                    json.dumps(variant.content), variant.traffic_allocation
                ))
            
            conn.commit()
        
        logger.info(f"Created A/B test: {test_id} - {name}")
        return test_id
    
    async def start_test(self, test_id: str) -> bool:
        """Start an A/B test"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT status FROM ab_tests WHERE id = ?", (test_id,))
            result = cursor.fetchone()
            
            if not result:
                raise HTTPException(status_code=404, detail="Test not found")
            
            if result[0] != TestStatus.DRAFT.value:
                raise HTTPException(
                    status_code=400,
                    detail="Only draft tests can be started"
                )
            
            cursor.execute("""
                UPDATE ab_tests 
                SET status = ?, start_date = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (TestStatus.RUNNING.value, datetime.utcnow(), test_id))
            
            conn.commit()
        
        logger.info(f"Started A/B test: {test_id}")
        return True
    
    async def record_metric(
        self,
        test_id: str,
        variant_id: str,
        metric_type: MetricType,
        value: float,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        video_id: Optional[str] = None
    ) -> bool:
        """Record a metric for a test variant"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Verify test is running
            cursor.execute("SELECT status FROM ab_tests WHERE id = ?", (test_id,))
            result = cursor.fetchone()
            
            if not result or result[0] != TestStatus.RUNNING.value:
                return False
            
            # Record metric
            cursor.execute("""
                INSERT INTO test_metrics (
                    test_id, variant_id, timestamp, metric_type, value,
                    session_id, user_id, video_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                test_id, variant_id, datetime.utcnow(), metric_type.value,
                value, session_id, user_id, video_id
            ))
            
            conn.commit()
        
        return True
    
    async def assign_variant(
        self,
        test_id: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        video_id: Optional[str] = None
    ) -> Optional[str]:
        """Assign a user to a test variant"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get test details
            cursor.execute("""
                SELECT status FROM ab_tests WHERE id = ?
            """, (test_id,))
            test_result = cursor.fetchone()
            
            if not test_result or test_result[0] != TestStatus.RUNNING.value:
                return None
            
            # Check if user already assigned
            if user_id:
                cursor.execute("""
                    SELECT variant_id FROM test_assignments 
                    WHERE test_id = ? AND user_id = ?
                """, (test_id, user_id))
                existing = cursor.fetchone()
                if existing:
                    return existing[0]
            
            # Get variants and their allocations
            cursor.execute("""
                SELECT id, traffic_allocation FROM test_variants 
                WHERE test_id = ? ORDER BY traffic_allocation DESC
            """, (test_id,))
            variants = cursor.fetchall()
            
            if not variants:
                return None
            
            # Simple random assignment based on allocation
            import random
            rand_value = random.random() * 100
            cumulative = 0
            
            selected_variant = None
            for variant_id, allocation in variants:
                cumulative += allocation
                if rand_value <= cumulative:
                    selected_variant = variant_id
                    break
            
            if not selected_variant:
                selected_variant = variants[0][0]  # Fallback to first variant
            
            # Record assignment
            cursor.execute("""
                INSERT INTO test_assignments (test_id, variant_id, user_id, session_id, video_id)
                VALUES (?, ?, ?, ?, ?)
            """, (test_id, selected_variant, user_id, session_id, video_id))
            
            conn.commit()
            
            return selected_variant
    
    async def get_test_results(self, test_id: str) -> Dict[str, Any]:
        """Get comprehensive test results with statistical analysis"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get test details
            cursor.execute("""
                SELECT * FROM ab_tests WHERE id = ?
            """, (test_id,))
            test_row = cursor.fetchone()
            
            if not test_row:
                raise HTTPException(status_code=404, detail="Test not found")
            
            # Get variants
            cursor.execute("""
                SELECT * FROM test_variants WHERE test_id = ?
            """, (test_id,))
            variant_rows = cursor.fetchall()
            
            # Get metrics for each variant
            variant_results = {}
            for variant_row in variant_rows:
                variant_id = variant_row[0]
                variant_name = variant_row[2]
                
                cursor.execute("""
                    SELECT metric_type, value, timestamp FROM test_metrics 
                    WHERE test_id = ? AND variant_id = ?
                    ORDER BY timestamp
                """, (test_id, variant_id))
                metrics = cursor.fetchall()
                
                # Group metrics by type
                metrics_by_type = {}
                for metric_type, value, timestamp in metrics:
                    if metric_type not in metrics_by_type:
                        metrics_by_type[metric_type] = []
                    metrics_by_type[metric_type].append(value)
                
                # Calculate summary statistics
                variant_summary = {
                    "id": variant_id,
                    "name": variant_name,
                    "total_observations": len(metrics),
                    "metrics": {}
                }
                
                for metric_type, values in metrics_by_type.items():
                    variant_summary["metrics"][metric_type] = {
                        "count": len(values),
                        "mean": float(np.mean(values)),
                        "std": float(np.std(values)),
                        "min": float(np.min(values)),
                        "max": float(np.max(values)),
                        "median": float(np.median(values)),
                        "sum": float(np.sum(values))
                    }
                
                variant_results[variant_id] = variant_summary
            
            # Perform statistical comparisons
            comparisons = {}
            primary_metric = test_row[5]  # primary_metric column
            
            if len(variant_results) >= 2:
                variant_ids = list(variant_results.keys())
                control_id = variant_ids[0]  # Assume first variant is control
                
                for test_variant_id in variant_ids[1:]:
                    if (primary_metric in variant_results[control_id]["metrics"] and 
                        primary_metric in variant_results[test_variant_id]["metrics"]):
                        
                        # Get raw data for statistical test
                        cursor.execute("""
                            SELECT value FROM test_metrics 
                            WHERE test_id = ? AND variant_id = ? AND metric_type = ?
                        """, (test_id, control_id, primary_metric))
                        control_data = [row[0] for row in cursor.fetchall()]
                        
                        cursor.execute("""
                            SELECT value FROM test_metrics 
                            WHERE test_id = ? AND variant_id = ? AND metric_type = ?
                        """, (test_id, test_variant_id, primary_metric))
                        test_data = [row[0] for row in cursor.fetchall()]
                        
                        # Perform statistical test
                        comparison = self.analysis.perform_t_test(
                            control_data, test_data, float(test_row[9])  # confidence_level
                        )
                        
                        comparisons[f"{control_id}_vs_{test_variant_id}"] = comparison
            
            return {
                "test_id": test_id,
                "test_name": test_row[1],
                "status": test_row[4],
                "primary_metric": primary_metric,
                "confidence_level": test_row[9],
                "start_date": test_row[7],
                "end_date": test_row[8],
                "variants": variant_results,
                "statistical_comparisons": comparisons,
                "recommendations": self._generate_recommendations(variant_results, comparisons)
            }
    
    def _generate_recommendations(
        self, 
        variant_results: Dict[str, Any], 
        comparisons: Dict[str, Any]
    ) -> List[str]:
        """Generate AI-powered recommendations based on test results"""
        
        recommendations = []
        
        # Find the best performing variant
        if len(variant_results) >= 2:
            best_variant = None
            best_performance = float('-inf')
            
            for variant_id, results in variant_results.items():
                # Use primary metric mean as performance indicator
                for metric_type, stats in results["metrics"].items():
                    if stats["mean"] > best_performance:
                        best_performance = stats["mean"]
                        best_variant = results["name"]
            
            if best_variant:
                recommendations.append(f"Variant '{best_variant}' shows the best performance.")
        
        # Check for statistical significance
        significant_results = [comp for comp in comparisons.values() if comp.get("significant", False)]
        
        if significant_results:
            improvements = [comp["improvement_percentage"] for comp in significant_results]
            avg_improvement = np.mean(improvements)
            recommendations.append(
                f"Statistically significant improvement of {avg_improvement:.1f}% detected."
            )
        else:
            recommendations.append("No statistically significant differences detected yet.")
        
        # Sample size recommendations
        total_observations = sum(v["total_observations"] for v in variant_results.values())
        if total_observations < 1000:
            recommendations.append("Consider running the test longer to gather more data.")
        
        return recommendations

# FastAPI routes for A/B testing
ab_test_router = APIRouter(prefix="/api/v2/ab-testing", tags=["A/B Testing"])
ab_test_manager = ABTestManager()

class CreateTestRequest(BaseModel):
    name: str
    description: str
    test_type: str
    variants: List[Dict[str, Any]]
    primary_metric: str
    secondary_metrics: List[str]
    channel_ids: List[str]
    min_sample_size: Optional[int] = None
    confidence_level: float = 0.95
    target_audience: Optional[Dict[str, Any]] = None

@ab_test_router.post("/tests")
async def create_ab_test(request: CreateTestRequest, user_id: str = "default_user"):
    """Create a new A/B test"""
    try:
        test_id = await ab_test_manager.create_test(
            name=request.name,
            description=request.description,
            test_type=TestType(request.test_type),
            variants=request.variants,
            primary_metric=MetricType(request.primary_metric),
            secondary_metrics=[MetricType(m) for m in request.secondary_metrics],
            channel_ids=request.channel_ids,
            created_by=user_id,
            min_sample_size=request.min_sample_size,
            confidence_level=request.confidence_level,
            target_audience=request.target_audience
        )
        
        return {"success": True, "test_id": test_id}
        
    except Exception as e:
        logger.error(f"Error creating A/B test: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@ab_test_router.post("/tests/{test_id}/start")
async def start_ab_test(test_id: str):
    """Start an A/B test"""
    try:
        success = await ab_test_manager.start_test(test_id)
        return {"success": success}
    except Exception as e:
        logger.error(f"Error starting A/B test: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@ab_test_router.get("/tests/{test_id}/results")
async def get_test_results(test_id: str):
    """Get A/B test results with statistical analysis"""
    try:
        results = await ab_test_manager.get_test_results(test_id)
        return {"success": True, "data": results}
    except Exception as e:
        logger.error(f"Error getting test results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@ab_test_router.post("/tests/{test_id}/assign")
async def assign_test_variant(
    test_id: str,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    video_id: Optional[str] = None
):
    """Assign a user to a test variant"""
    try:
        variant_id = await ab_test_manager.assign_variant(
            test_id=test_id,
            user_id=user_id,
            session_id=session_id,
            video_id=video_id
        )
        return {"success": True, "variant_id": variant_id}
    except Exception as e:
        logger.error(f"Error assigning test variant: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@ab_test_router.post("/tests/{test_id}/metrics")
async def record_test_metric(
    test_id: str,
    variant_id: str,
    metric_type: str,
    value: float,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    video_id: Optional[str] = None
):
    """Record a metric for a test variant"""
    try:
        success = await ab_test_manager.record_metric(
            test_id=test_id,
            variant_id=variant_id,
            metric_type=MetricType(metric_type),
            value=value,
            user_id=user_id,
            session_id=session_id,
            video_id=video_id
        )
        return {"success": success}
    except Exception as e:
        logger.error(f"Error recording test metric: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))