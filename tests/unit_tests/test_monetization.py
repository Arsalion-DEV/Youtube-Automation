"""
Unit tests for Monetization management and revenue optimization
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import json

from modules.monetization.manager import MonetizationManager
from modules.monetization.revenue_optimizer import RevenueOptimizer
from modules.monetization.supporter_analytics import SupporterAnalytics
from modules.monetization.tier_management import TierManager
from modules.monetization.content_automation import ContentAutomation


class TestMonetizationManager:
    """Test monetization management functionality"""
    
    @pytest.fixture
    def monetization_manager(self):
        """Create monetization manager instance"""
        return MonetizationManager()
    
    def test_monetization_manager_initialization(self, monetization_manager):
        """Test monetization manager initializes correctly"""
        assert monetization_manager is not None
        assert hasattr(monetization_manager, 'setup_patreon_integration')
        assert hasattr(monetization_manager, 'setup_buymeacoffee_integration')
    
    @patch('modules.monetization.manager.requests.post')
    def test_patreon_integration(self, mock_post, monetization_manager):
        """Test Patreon API integration"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "id": "campaign_123",
                "attributes": {
                    "patron_count": 150,
                    "pledge_sum": 75000  # in cents
                }
            }
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = monetization_manager.fetch_patreon_data("test_token")
        
        assert result is not None
        assert result["patron_count"] == 150
        assert result["monthly_revenue"] == 750.00
    
    @patch('modules.monetization.manager.requests.get')
    def test_buymeacoffee_integration(self, mock_get, monetization_manager):
        """Test Buy Me A Coffee API integration"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "total_supporters": 75,
                "total_payments": 225.50,
                "recent_supporters": [
                    {"name": "John Doe", "amount": 5.00, "message": "Great content!"}
                ]
            }
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = monetization_manager.fetch_buymeacoffee_data("test_token")
        
        assert result is not None
        assert result["total_supporters"] == 75
        assert result["total_payments"] == 225.50
    
    def test_revenue_tracking(self, monetization_manager):
        """Test revenue tracking and aggregation"""
        revenue_sources = {
            "patreon": 750.00,
            "buymeacoffee": 225.50,
            "youtube_ad_revenue": 120.00,
            "sponsorships": 500.00
        }
        
        total_revenue = monetization_manager.calculate_total_revenue(revenue_sources)
        assert total_revenue == 1595.50
        
        breakdown = monetization_manager.get_revenue_breakdown(revenue_sources)
        assert breakdown["patreon"]["percentage"] > 40  # Patreon is the largest source


class TestRevenueOptimizer:
    """Test revenue optimization algorithms"""
    
    @pytest.fixture
    def revenue_optimizer(self):
        """Create revenue optimizer instance"""
        return RevenueOptimizer()
    
    def test_pricing_optimization(self, revenue_optimizer):
        """Test tier pricing optimization"""
        current_tiers = [
            {"name": "Basic", "price": 5.00, "subscribers": 100},
            {"name": "Premium", "price": 15.00, "subscribers": 50},
            {"name": "VIP", "price": 50.00, "subscribers": 10}
        ]
        
        market_data = {
            "competitor_pricing": [3.00, 8.00, 25.00],
            "audience_willingness_to_pay": {"low": 5.00, "medium": 12.00, "high": 30.00}
        }
        
        optimized_pricing = revenue_optimizer.optimize_tier_pricing(current_tiers, market_data)
        
        assert optimized_pricing is not None
        assert len(optimized_pricing) == len(current_tiers)
        assert "recommendations" in optimized_pricing
    
    def test_content_monetization_strategy(self, revenue_optimizer):
        """Test content monetization strategy optimization"""
        content_performance = {
            "tutorials": {"avg_views": 5000, "engagement": 8.0, "conversion_rate": 0.05},
            "reviews": {"avg_views": 3000, "engagement": 6.0, "conversion_rate": 0.03},
            "vlogs": {"avg_views": 2000, "engagement": 9.0, "conversion_rate": 0.07}
        }
        
        strategy = revenue_optimizer.optimize_content_strategy(content_performance)
        
        assert strategy is not None
        assert "prioritized_content_types" in strategy
        assert "revenue_potential" in strategy
    
    def test_subscriber_lifecycle_value(self, revenue_optimizer):
        """Test customer lifetime value calculation"""
        subscriber_data = {
            "monthly_churn_rate": 0.05,  # 5% monthly churn
            "average_monthly_payment": 10.00,
            "acquisition_cost": 15.00
        }
        
        clv = revenue_optimizer.calculate_customer_lifetime_value(subscriber_data)
        
        assert clv > 0
        assert clv > subscriber_data["acquisition_cost"]  # Should be profitable


class TestSupporterAnalytics:
    """Test supporter analytics and insights"""
    
    @pytest.fixture
    def supporter_analytics(self):
        """Create supporter analytics instance"""
        return SupporterAnalytics()
    
    def test_supporter_segmentation(self, supporter_analytics):
        """Test supporter segmentation analysis"""
        supporter_data = [
            {"id": 1, "monthly_amount": 5.00, "months_active": 12, "tier": "Basic"},
            {"id": 2, "monthly_amount": 15.00, "months_active": 6, "tier": "Premium"},
            {"id": 3, "monthly_amount": 50.00, "months_active": 24, "tier": "VIP"},
            {"id": 4, "monthly_amount": 5.00, "months_active": 2, "tier": "Basic"},
        ]
        
        segments = supporter_analytics.segment_supporters(supporter_data)
        
        assert segments is not None
        assert "high_value" in segments
        assert "long_term" in segments
        assert "at_risk" in segments
    
    def test_churn_prediction(self, supporter_analytics):
        """Test supporter churn prediction"""
        supporter_history = {
            "id": 123,
            "payment_history": [
                {"date": "2024-01-01", "amount": 10.00},
                {"date": "2024-02-01", "amount": 10.00},
                {"date": "2024-03-01", "amount": 0.00},  # Missed payment
            ],
            "engagement_history": [
                {"date": "2024-01-01", "interactions": 5},
                {"date": "2024-02-01", "interactions": 3},
                {"date": "2024-03-01", "interactions": 1},  # Declining engagement
            ]
        }
        
        churn_risk = supporter_analytics.predict_churn_risk(supporter_history)
        
        assert churn_risk is not None
        assert 0 <= churn_risk <= 1  # Should be a probability
        assert churn_risk > 0.5  # High risk based on declining engagement
    
    def test_supporter_journey_analysis(self, supporter_analytics):
        """Test supporter journey and conversion funnel"""
        funnel_data = {
            "visitors": 10000,
            "email_signups": 1000,
            "trial_users": 200,
            "paying_supporters": 50
        }
        
        analysis = supporter_analytics.analyze_conversion_funnel(funnel_data)
        
        assert analysis is not None
        assert "conversion_rates" in analysis
        assert "bottlenecks" in analysis
        assert analysis["conversion_rates"]["visitor_to_supporter"] < 0.01


class TestTierManager:
    """Test membership tier management"""
    
    @pytest.fixture
    def tier_manager(self):
        """Create tier manager instance"""
        return TierManager()
    
    def test_tier_creation(self, tier_manager):
        """Test creating new membership tiers"""
        tier_config = {
            "name": "Platinum",
            "price": 25.00,
            "benefits": [
                "Early access to videos",
                "Monthly Q&A session",
                "Discord access",
                "Custom badge"
            ],
            "perks": {
                "priority_support": True,
                "exclusive_content": True,
                "merchandise_discount": 20
            }
        }
        
        tier = tier_manager.create_tier(tier_config)
        
        assert tier is not None
        assert tier["name"] == "Platinum"
        assert tier["price"] == 25.00
        assert len(tier["benefits"]) == 4
    
    def test_tier_optimization(self, tier_manager):
        """Test automatic tier optimization"""
        existing_tiers = [
            {"name": "Basic", "price": 5.00, "subscribers": 150, "satisfaction": 7.5},
            {"name": "Premium", "price": 15.00, "subscribers": 75, "satisfaction": 8.2},
            {"name": "VIP", "price": 50.00, "subscribers": 25, "satisfaction": 9.1}
        ]
        
        optimization = tier_manager.optimize_tiers(existing_tiers)
        
        assert optimization is not None
        assert "recommendations" in optimization
        assert "new_tier_suggestions" in optimization
    
    def test_benefit_analysis(self, tier_manager):
        """Test tier benefit value analysis"""
        benefits = [
            {"name": "Early access", "perceived_value": 8.0, "cost": 0.50},
            {"name": "Exclusive content", "perceived_value": 9.5, "cost": 5.00},
            {"name": "Merchandise discount", "perceived_value": 6.0, "cost": 2.00}
        ]
        
        analysis = tier_manager.analyze_benefit_value(benefits)
        
        assert analysis is not None
        assert "value_score" in analysis
        assert "cost_effectiveness" in analysis


class TestContentAutomation:
    """Test automated content creation for supporters"""
    
    @pytest.fixture
    def content_automation(self):
        """Create content automation instance"""
        return ContentAutomation()
    
    def test_personalized_content_generation(self, content_automation):
        """Test personalized content generation for supporters"""
        supporter_profile = {
            "name": "John Doe",
            "tier": "Premium",
            "interests": ["AI", "programming", "tutorials"],
            "engagement_history": ["liked_tutorial_videos", "commented_on_ai_posts"]
        }
        
        content = content_automation.generate_personalized_content(supporter_profile)
        
        assert content is not None
        assert supporter_profile["name"] in content["message"]
        assert any(interest in content["message"].lower() for interest in supporter_profile["interests"])
    
    def test_reward_automation(self, content_automation):
        """Test automated reward distribution"""
        milestone_data = {
            "supporter_id": 123,
            "milestone_type": "6_month_anniversary",
            "tier": "Premium",
            "total_contributed": 90.00
        }
        
        reward = content_automation.generate_milestone_reward(milestone_data)
        
        assert reward is not None
        assert "reward_type" in reward
        assert "message" in reward
        assert "delivery_method" in reward
    
    def test_engagement_campaigns(self, content_automation):
        """Test automated engagement campaigns"""
        campaign_config = {
            "type": "feedback_request",
            "target_segments": ["Premium", "VIP"],
            "content_theme": "upcoming_content_ideas"
        }
        
        campaign = content_automation.create_engagement_campaign(campaign_config)
        
        assert campaign is not None
        assert "messages" in campaign
        assert "schedule" in campaign
        assert "success_metrics" in campaign