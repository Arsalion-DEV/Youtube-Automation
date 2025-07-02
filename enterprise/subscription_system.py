"""
Advanced Subscription and Premium Monetization System
Handles subscription tiers, usage-based billing, and premium features
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
import uuid
import stripe
from decimal import Decimal

logger = logging.getLogger(__name__)

class SubscriptionTier(Enum):
    """Subscription tiers with different feature sets"""
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"
    WHITE_LABEL = "white_label"

class BillingCycle(Enum):
    """Billing cycle options"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class UsageMetric(Enum):
    """Usage metrics for billing"""
    VIDEOS_GENERATED = "videos_generated"
    STORAGE_USED = "storage_used"
    API_CALLS = "api_calls"
    TEAM_MEMBERS = "team_members"
    AB_TESTS = "ab_tests"
    WHITE_LABEL_INSTANCES = "white_label_instances"

@dataclass
class SubscriptionPlan:
    """Subscription plan configuration"""
    id: str
    tier: SubscriptionTier
    name: str
    description: str
    base_price: Decimal
    billing_cycles: Dict[BillingCycle, Dict[str, Any]]  # cycle -> {multiplier, discount}
    features: Set[str]
    limits: Dict[str, int]
    usage_pricing: Dict[UsageMetric, Dict[str, Any]]  # metric -> {included, overage_price}
    is_active: bool
    created_at: datetime

@dataclass
class Subscription:
    """User subscription instance"""
    id: str
    user_id: str
    organization_id: str
    plan_id: str
    tier: SubscriptionTier
    billing_cycle: BillingCycle
    status: str  # active, past_due, canceled, trial
    current_period_start: datetime
    current_period_end: datetime
    trial_end: Optional[datetime]
    stripe_subscription_id: Optional[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

@dataclass
class UsageRecord:
    """Usage tracking record"""
    id: str
    subscription_id: str
    metric: UsageMetric
    quantity: int
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class Invoice:
    """Billing invoice"""
    id: str
    subscription_id: str
    amount: Decimal
    currency: str
    status: str  # draft, open, paid, void
    line_items: List[Dict[str, Any]]
    period_start: datetime
    period_end: datetime
    due_date: datetime
    stripe_invoice_id: Optional[str]
    created_at: datetime

class SubscriptionManager:
    """Manages subscription tiers and billing"""
    
    def __init__(self):
        # Initialize Stripe
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        
        # In-memory storage for demo - replace with database
        self.plans: Dict[str, SubscriptionPlan] = {}
        self.subscriptions: Dict[str, Subscription] = {}
        self.usage_records: List[UsageRecord] = []
        self.invoices: Dict[str, Invoice] = {}
        
        # Initialize default plans
        self._initialize_default_plans()
    
    def _initialize_default_plans(self):
        """Initialize default subscription plans"""
        
        # FREE Plan
        free_plan = SubscriptionPlan(
            id="plan_free",
            tier=SubscriptionTier.FREE,
            name="Free",
            description="Perfect for getting started with YouTube automation",
            base_price=Decimal("0.00"),
            billing_cycles={
                BillingCycle.MONTHLY: {"multiplier": 1, "discount": 0}
            },
            features={
                "basic_video_generation",
                "youtube_publishing",
                "basic_analytics",
                "community_support"
            },
            limits={
                "videos_per_month": 5,
                "storage_gb": 1,
                "team_members": 1,
                "channels": 1
            },
            usage_pricing={},
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        # STARTER Plan
        starter_plan = SubscriptionPlan(
            id="plan_starter",
            tier=SubscriptionTier.STARTER,
            name="Starter",
            description="Great for individual creators and small channels",
            base_price=Decimal("29.00"),
            billing_cycles={
                BillingCycle.MONTHLY: {"multiplier": 1, "discount": 0},
                BillingCycle.YEARLY: {"multiplier": 10, "discount": 20}  # 2 months free
            },
            features={
                "advanced_video_generation",
                "multi_platform_publishing",
                "advanced_analytics",
                "ai_optimization",
                "email_support",
                "video_templates"
            },
            limits={
                "videos_per_month": 50,
                "storage_gb": 10,
                "team_members": 3,
                "channels": 3,
                "ab_tests": 5
            },
            usage_pricing={
                UsageMetric.VIDEOS_GENERATED: {
                    "included": 50,
                    "overage_price": Decimal("0.99")
                }
            },
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        # PRO Plan
        pro_plan = SubscriptionPlan(
            id="plan_pro",
            tier=SubscriptionTier.PRO,
            name="Pro",
            description="Perfect for growing creators and small teams",
            base_price=Decimal("99.00"),
            billing_cycles={
                BillingCycle.MONTHLY: {"multiplier": 1, "discount": 0},
                BillingCycle.QUARTERLY: {"multiplier": 2.8, "discount": 7},
                BillingCycle.YEARLY: {"multiplier": 10, "discount": 20}
            },
            features={
                "premium_video_generation",
                "all_platform_publishing",
                "premium_analytics",
                "ab_testing",
                "priority_support",
                "custom_templates",
                "api_access",
                "advanced_ai_features",
                "team_collaboration"
            },
            limits={
                "videos_per_month": 200,
                "storage_gb": 50,
                "team_members": 10,
                "channels": 10,
                "ab_tests": 25
            },
            usage_pricing={
                UsageMetric.VIDEOS_GENERATED: {
                    "included": 200,
                    "overage_price": Decimal("0.79")
                },
                UsageMetric.TEAM_MEMBERS: {
                    "included": 10,
                    "overage_price": Decimal("15.00")
                }
            },
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        # BUSINESS Plan
        business_plan = SubscriptionPlan(
            id="plan_business",
            tier=SubscriptionTier.BUSINESS,
            name="Business",
            description="Ideal for agencies and growing businesses",
            base_price=Decimal("299.00"),
            billing_cycles={
                BillingCycle.MONTHLY: {"multiplier": 1, "discount": 0},
                BillingCycle.QUARTERLY: {"multiplier": 2.7, "discount": 10},
                BillingCycle.YEARLY: {"multiplier": 9, "discount": 25}
            },
            features={
                "enterprise_video_generation",
                "all_platform_publishing",
                "enterprise_analytics",
                "advanced_ab_testing",
                "dedicated_support",
                "custom_integrations",
                "white_label_branding",
                "team_management",
                "workflow_automation",
                "priority_processing"
            },
            limits={
                "videos_per_month": 1000,
                "storage_gb": 200,
                "team_members": 25,
                "channels": 25,
                "ab_tests": 100,
                "white_label_instances": 3
            },
            usage_pricing={
                UsageMetric.VIDEOS_GENERATED: {
                    "included": 1000,
                    "overage_price": Decimal("0.59")
                },
                UsageMetric.TEAM_MEMBERS: {
                    "included": 25,
                    "overage_price": Decimal("12.00")
                },
                UsageMetric.WHITE_LABEL_INSTANCES: {
                    "included": 3,
                    "overage_price": Decimal("99.00")
                }
            },
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        # ENTERPRISE Plan
        enterprise_plan = SubscriptionPlan(
            id="plan_enterprise",
            tier=SubscriptionTier.ENTERPRISE,
            name="Enterprise",
            description="For large organizations with custom needs",
            base_price=Decimal("999.00"),
            billing_cycles={
                BillingCycle.MONTHLY: {"multiplier": 1, "discount": 0},
                BillingCycle.QUARTERLY: {"multiplier": 2.5, "discount": 15},
                BillingCycle.YEARLY: {"multiplier": 8, "discount": 33}
            },
            features={
                "unlimited_video_generation",
                "all_platform_publishing",
                "enterprise_analytics",
                "unlimited_ab_testing",
                "white_label_solutions",
                "custom_development",
                "dedicated_account_manager",
                "24/7_priority_support",
                "sla_guarantee",
                "custom_integrations",
                "advanced_security",
                "compliance_features"
            },
            limits={
                "videos_per_month": -1,  # unlimited
                "storage_gb": 1000,
                "team_members": 100,
                "channels": 100,
                "ab_tests": -1,  # unlimited
                "white_label_instances": 10
            },
            usage_pricing={
                UsageMetric.TEAM_MEMBERS: {
                    "included": 100,
                    "overage_price": Decimal("10.00")
                },
                UsageMetric.STORAGE_USED: {
                    "included": 1000,  # GB
                    "overage_price": Decimal("0.50")  # per GB
                },
                UsageMetric.WHITE_LABEL_INSTANCES: {
                    "included": 10,
                    "overage_price": Decimal("79.00")
                }
            },
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        # Store plans
        for plan in [free_plan, starter_plan, pro_plan, business_plan, enterprise_plan]:
            self.plans[plan.id] = plan
    
    async def create_subscription(
        self,
        user_id: str,
        organization_id: str,
        plan_id: str,
        billing_cycle: BillingCycle,
        trial_days: Optional[int] = None,
        payment_method_id: Optional[str] = None
    ) -> str:
        """Create a new subscription"""
        try:
            if plan_id not in self.plans:
                raise ValueError(f"Plan {plan_id} not found")
            
            plan = self.plans[plan_id]
            subscription_id = str(uuid.uuid4())
            
            # Calculate dates
            start_date = datetime.utcnow()
            trial_end = None
            
            if trial_days:
                trial_end = start_date + timedelta(days=trial_days)
                period_end = trial_end
            else:
                period_end = self._calculate_period_end(start_date, billing_cycle)
            
            # Create Stripe subscription if not free plan
            stripe_subscription_id = None
            if plan.tier != SubscriptionTier.FREE:
                stripe_subscription_id = await self._create_stripe_subscription(
                    user_id, plan, billing_cycle, payment_method_id, trial_days
                )
            
            # Create subscription record
            subscription = Subscription(
                id=subscription_id,
                user_id=user_id,
                organization_id=organization_id,
                plan_id=plan_id,
                tier=plan.tier,
                billing_cycle=billing_cycle,
                status="trial" if trial_days else "active",
                current_period_start=start_date,
                current_period_end=period_end,
                trial_end=trial_end,
                stripe_subscription_id=stripe_subscription_id,
                metadata={},
                created_at=start_date,
                updated_at=start_date
            )
            
            self.subscriptions[subscription_id] = subscription
            
            logger.info(f"Subscription created: {subscription_id} for plan {plan_id}")
            return subscription_id
            
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            raise e
    
    async def _create_stripe_subscription(
        self,
        user_id: str,
        plan: SubscriptionPlan,
        billing_cycle: BillingCycle,
        payment_method_id: Optional[str] = None,
        trial_days: Optional[int] = None
    ) -> str:
        """Create Stripe subscription"""
        try:
            # Get or create Stripe customer
            customer_id = await self._get_or_create_stripe_customer(user_id)
            
            # Calculate price based on billing cycle
            cycle_config = plan.billing_cycles[billing_cycle]
            price = plan.base_price * Decimal(cycle_config["multiplier"])
            
            # Apply discount
            if cycle_config["discount"] > 0:
                discount_amount = price * (Decimal(cycle_config["discount"]) / 100)
                price = price - discount_amount
            
            # Create Stripe price object
            stripe_price = stripe.Price.create(
                unit_amount=int(price * 100),  # Convert to cents
                currency="usd",
                recurring={
                    "interval": billing_cycle.value,
                    "interval_count": 1 if billing_cycle != BillingCycle.QUARTERLY else 3
                },
                product_data={
                    "name": f"{plan.name} Plan - {billing_cycle.value.title()}"
                }
            )
            
            # Create subscription
            subscription_params = {
                "customer": customer_id,
                "items": [{"price": stripe_price.id}],
                "expand": ["latest_invoice.payment_intent"]
            }
            
            if trial_days:
                subscription_params["trial_period_days"] = trial_days
            
            if payment_method_id:
                subscription_params["default_payment_method"] = payment_method_id
            
            stripe_subscription = stripe.Subscription.create(**subscription_params)
            
            return stripe_subscription.id
            
        except Exception as e:
            logger.error(f"Error creating Stripe subscription: {e}")
            raise e
    
    async def _get_or_create_stripe_customer(self, user_id: str) -> str:
        """Get or create Stripe customer"""
        try:
            # In real implementation, check if customer already exists
            # For now, create new customer
            customer = stripe.Customer.create(
                metadata={"user_id": user_id}
            )
            return customer.id
            
        except Exception as e:
            logger.error(f"Error creating Stripe customer: {e}")
            raise e
    
    async def upgrade_subscription(
        self,
        subscription_id: str,
        new_plan_id: str,
        billing_cycle: Optional[BillingCycle] = None
    ) -> bool:
        """Upgrade or change subscription plan"""
        try:
            if subscription_id not in self.subscriptions:
                return False
            
            if new_plan_id not in self.plans:
                raise ValueError(f"Plan {new_plan_id} not found")
            
            subscription = self.subscriptions[subscription_id]
            new_plan = self.plans[new_plan_id]
            
            # Update subscription
            subscription.plan_id = new_plan_id
            subscription.tier = new_plan.tier
            
            if billing_cycle:
                subscription.billing_cycle = billing_cycle
            
            subscription.updated_at = datetime.utcnow()
            
            # Update Stripe subscription if applicable
            if subscription.stripe_subscription_id:
                await self._update_stripe_subscription(subscription, new_plan)
            
            logger.info(f"Subscription upgraded: {subscription_id} to {new_plan_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error upgrading subscription: {e}")
            raise e
    
    async def _update_stripe_subscription(self, subscription: Subscription, new_plan: SubscriptionPlan):
        """Update Stripe subscription"""
        try:
            # Calculate new price
            cycle_config = new_plan.billing_cycles[subscription.billing_cycle]
            price = new_plan.base_price * Decimal(cycle_config["multiplier"])
            
            if cycle_config["discount"] > 0:
                discount_amount = price * (Decimal(cycle_config["discount"]) / 100)
                price = price - discount_amount
            
            # Create new price
            stripe_price = stripe.Price.create(
                unit_amount=int(price * 100),
                currency="usd",
                recurring={
                    "interval": subscription.billing_cycle.value,
                    "interval_count": 1 if subscription.billing_cycle != BillingCycle.QUARTERLY else 3
                },
                product_data={
                    "name": f"{new_plan.name} Plan - {subscription.billing_cycle.value.title()}"
                }
            )
            
            # Update Stripe subscription
            stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                items=[{
                    "id": subscription.stripe_subscription_id,  # This would be the subscription item ID
                    "price": stripe_price.id
                }],
                proration_behavior="create_prorations"
            )
            
        except Exception as e:
            logger.error(f"Error updating Stripe subscription: {e}")
            raise e
    
    async def cancel_subscription(
        self,
        subscription_id: str,
        immediate: bool = False
    ) -> bool:
        """Cancel subscription"""
        try:
            if subscription_id not in self.subscriptions:
                return False
            
            subscription = self.subscriptions[subscription_id]
            
            if immediate:
                subscription.status = "canceled"
                subscription.current_period_end = datetime.utcnow()
            else:
                subscription.status = "cancel_at_period_end"
            
            subscription.updated_at = datetime.utcnow()
            
            # Cancel Stripe subscription
            if subscription.stripe_subscription_id:
                stripe.Subscription.modify(
                    subscription.stripe_subscription_id,
                    cancel_at_period_end=not immediate
                )
                
                if immediate:
                    stripe.Subscription.cancel(subscription.stripe_subscription_id)
            
            logger.info(f"Subscription canceled: {subscription_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error canceling subscription: {e}")
            raise e
    
    async def track_usage(
        self,
        subscription_id: str,
        metric: UsageMetric,
        quantity: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Track usage for billing"""
        try:
            usage_id = str(uuid.uuid4())
            
            usage_record = UsageRecord(
                id=usage_id,
                subscription_id=subscription_id,
                metric=metric,
                quantity=quantity,
                timestamp=datetime.utcnow(),
                metadata=metadata or {}
            )
            
            self.usage_records.append(usage_record)
            
            # Report to Stripe if metered billing
            subscription = self.subscriptions.get(subscription_id)
            if subscription and subscription.stripe_subscription_id:
                await self._report_stripe_usage(subscription, metric, quantity)
            
            return usage_id
            
        except Exception as e:
            logger.error(f"Error tracking usage: {e}")
            raise e
    
    async def _report_stripe_usage(
        self,
        subscription: Subscription,
        metric: UsageMetric,
        quantity: int
    ):
        """Report usage to Stripe for metered billing"""
        try:
            # This would report usage to Stripe's metered billing
            # Implementation depends on specific Stripe setup
            logger.info(f"Reported usage to Stripe: {metric.value} = {quantity}")
            
        except Exception as e:
            logger.error(f"Error reporting usage to Stripe: {e}")
    
    async def calculate_usage_billing(
        self,
        subscription_id: str,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """Calculate usage-based billing for a period"""
        try:
            if subscription_id not in self.subscriptions:
                return {}
            
            subscription = self.subscriptions[subscription_id]
            plan = self.plans[subscription.plan_id]
            
            # Get usage for period
            period_usage = {}
            for record in self.usage_records:
                if (record.subscription_id == subscription_id and
                    period_start <= record.timestamp <= period_end):
                    
                    metric = record.metric
                    if metric not in period_usage:
                        period_usage[metric] = 0
                    period_usage[metric] += record.quantity
            
            # Calculate overage charges
            line_items = []
            total_overage = Decimal("0.00")
            
            for metric, usage in period_usage.items():
                if metric in plan.usage_pricing:
                    pricing = plan.usage_pricing[metric]
                    included = pricing["included"]
                    overage_price = pricing["overage_price"]
                    
                    if usage > included:
                        overage_quantity = usage - included
                        overage_amount = overage_quantity * overage_price
                        total_overage += overage_amount
                        
                        line_items.append({
                            "metric": metric.value,
                            "usage": usage,
                            "included": included,
                            "overage_quantity": overage_quantity,
                            "overage_price": float(overage_price),
                            "overage_amount": float(overage_amount)
                        })
            
            return {
                "subscription_id": subscription_id,
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "base_amount": float(plan.base_price),
                "usage_amount": float(total_overage),
                "total_amount": float(plan.base_price + total_overage),
                "line_items": line_items
            }
            
        except Exception as e:
            logger.error(f"Error calculating usage billing: {e}")
            return {}
    
    async def get_subscription_status(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get subscription status and details"""
        try:
            if subscription_id not in self.subscriptions:
                return None
            
            subscription = self.subscriptions[subscription_id]
            plan = self.plans[subscription.plan_id]
            
            # Get current usage
            current_usage = await self._get_current_usage(subscription_id)
            
            return {
                "subscription_id": subscription_id,
                "status": subscription.status,
                "tier": subscription.tier.value,
                "plan_name": plan.name,
                "billing_cycle": subscription.billing_cycle.value,
                "current_period_start": subscription.current_period_start.isoformat(),
                "current_period_end": subscription.current_period_end.isoformat(),
                "trial_end": subscription.trial_end.isoformat() if subscription.trial_end else None,
                "features": list(plan.features),
                "limits": plan.limits,
                "current_usage": current_usage,
                "created_at": subscription.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting subscription status: {e}")
            return None
    
    async def _get_current_usage(self, subscription_id: str) -> Dict[str, int]:
        """Get current period usage"""
        try:
            subscription = self.subscriptions[subscription_id]
            period_start = subscription.current_period_start
            
            current_usage = {}
            for record in self.usage_records:
                if (record.subscription_id == subscription_id and
                    record.timestamp >= period_start):
                    
                    metric = record.metric.value
                    if metric not in current_usage:
                        current_usage[metric] = 0
                    current_usage[metric] += record.quantity
            
            return current_usage
            
        except Exception as e:
            logger.error(f"Error getting current usage: {e}")
            return {}
    
    def _calculate_period_end(self, start_date: datetime, billing_cycle: BillingCycle) -> datetime:
        """Calculate billing period end date"""
        if billing_cycle == BillingCycle.MONTHLY:
            return start_date + timedelta(days=30)
        elif billing_cycle == BillingCycle.QUARTERLY:
            return start_date + timedelta(days=90)
        elif billing_cycle == BillingCycle.YEARLY:
            return start_date + timedelta(days=365)
        else:
            raise ValueError(f"Unknown billing cycle: {billing_cycle}")
    
    async def get_available_plans(self) -> List[Dict[str, Any]]:
        """Get all available subscription plans"""
        try:
            plans = []
            for plan in self.plans.values():
                if plan.is_active:
                    plan_data = {
                        "id": plan.id,
                        "tier": plan.tier.value,
                        "name": plan.name,
                        "description": plan.description,
                        "base_price": float(plan.base_price),
                        "billing_cycles": {
                            cycle.value: {
                                "price": float(plan.base_price * Decimal(config["multiplier"])),
                                "discount": config["discount"]
                            }
                            for cycle, config in plan.billing_cycles.items()
                        },
                        "features": list(plan.features),
                        "limits": plan.limits,
                        "usage_pricing": {
                            metric.value: {
                                "included": pricing["included"],
                                "overage_price": float(pricing["overage_price"])
                            }
                            for metric, pricing in plan.usage_pricing.items()
                        }
                    }
                    plans.append(plan_data)
            
            return sorted(plans, key=lambda x: x["base_price"])
            
        except Exception as e:
            logger.error(f"Error getting available plans: {e}")
            return []
    
    async def process_webhook(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """Process Stripe webhook events"""
        try:
            if event_type == "invoice.payment_succeeded":
                await self._handle_payment_succeeded(event_data)
            elif event_type == "invoice.payment_failed":
                await self._handle_payment_failed(event_data)
            elif event_type == "customer.subscription.updated":
                await self._handle_subscription_updated(event_data)
            elif event_type == "customer.subscription.deleted":
                await self._handle_subscription_deleted(event_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return False
    
    async def _handle_payment_succeeded(self, event_data: Dict[str, Any]):
        """Handle successful payment"""
        try:
            stripe_subscription_id = event_data.get("subscription")
            
            # Find subscription
            for subscription in self.subscriptions.values():
                if subscription.stripe_subscription_id == stripe_subscription_id:
                    subscription.status = "active"
                    subscription.updated_at = datetime.utcnow()
                    break
            
            logger.info(f"Payment succeeded for subscription: {stripe_subscription_id}")
            
        except Exception as e:
            logger.error(f"Error handling payment success: {e}")
    
    async def _handle_payment_failed(self, event_data: Dict[str, Any]):
        """Handle failed payment"""
        try:
            stripe_subscription_id = event_data.get("subscription")
            
            # Find subscription
            for subscription in self.subscriptions.values():
                if subscription.stripe_subscription_id == stripe_subscription_id:
                    subscription.status = "past_due"
                    subscription.updated_at = datetime.utcnow()
                    break
            
            logger.info(f"Payment failed for subscription: {stripe_subscription_id}")
            
        except Exception as e:
            logger.error(f"Error handling payment failure: {e}")
    
    async def _handle_subscription_updated(self, event_data: Dict[str, Any]):
        """Handle subscription update"""
        try:
            stripe_subscription_id = event_data.get("id")
            status = event_data.get("status")
            
            # Find and update subscription
            for subscription in self.subscriptions.values():
                if subscription.stripe_subscription_id == stripe_subscription_id:
                    subscription.status = status
                    subscription.updated_at = datetime.utcnow()
                    break
            
            logger.info(f"Subscription updated: {stripe_subscription_id}")
            
        except Exception as e:
            logger.error(f"Error handling subscription update: {e}")
    
    async def _handle_subscription_deleted(self, event_data: Dict[str, Any]):
        """Handle subscription cancellation"""
        try:
            stripe_subscription_id = event_data.get("id")
            
            # Find and cancel subscription
            for subscription in self.subscriptions.values():
                if subscription.stripe_subscription_id == stripe_subscription_id:
                    subscription.status = "canceled"
                    subscription.updated_at = datetime.utcnow()
                    break
            
            logger.info(f"Subscription canceled: {stripe_subscription_id}")
            
        except Exception as e:
            logger.error(f"Error handling subscription deletion: {e}")